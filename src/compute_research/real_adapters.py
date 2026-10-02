from pathlib import Path
import time,json,platform,sys
from .budget import BudgetViolation

class RealDependencyError(RuntimeError): pass
def _deps():
    try:
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        from datasets import load_dataset
    except ImportError as e: raise RealDependencyError("real mode requires torch, transformers, datasets") from e
    return torch,AutoModelForCausalLM,AutoTokenizer,load_dataset

class HuggingFaceSFTAdapter:
    def train(self,*,model_id,revision,dataset_id,dataset_revision,dataset_config,output_dir,token_budget,max_steps,batch_size,gradient_accumulation,sequence_length,learning_rate,seed,max_flops,max_wall_seconds,provenance):
        torch,AutoModel,AutoTokenizer,load_dataset=_deps()
        if batch_size!=1: raise ValueError("scientific token contract requires batch_size=1")
        torch.manual_seed(seed); tok=AutoTokenizer.from_pretrained(model_id,revision=revision)
        if tok.pad_token_id is None: tok.pad_token=tok.eos_token
        model=AutoModel.from_pretrained(model_id,revision=revision,torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32)
        ds=load_dataset(dataset_id,dataset_config,revision=dataset_revision,split="train").shuffle(seed=seed)
        optimizer=torch.optim.AdamW(model.parameters(),lr=learning_rate)
        model.train(); start=time.perf_counter(); realized_tokens=0; steps=0; micro=0; buffer=[]
        for row in ds:
            if realized_tokens>=token_budget: break
            text="\n".join(str(m.get("content","")) for m in row["messages"]) if "messages" in row else str(row.get("prompt",""))+"\n"+str(row.get("generation",""))
            ids=tok(text,return_tensors="pt",truncation=False)["input_ids"][0].tolist()
            buffer.extend(ids)
            while len(buffer)>=sequence_length and realized_tokens<token_budget:
                remaining=token_budget-realized_tokens
                take=min(sequence_length,remaining); chunk=buffer[:take]; buffer=buffer[take:]
                x=torch.tensor([chunk],device=model.device)
                out=model(input_ids=x,labels=x); out.loss.backward()
                realized_tokens+=take; micro+=1
                if micro>=gradient_accumulation or realized_tokens>=token_budget:
                    optimizer.step(); optimizer.zero_grad(set_to_none=True); steps+=1; micro=0
                elapsed=time.perf_counter()-start; est_flops=6*model.config.num_parameters*realized_tokens
                if steps>max_steps: raise BudgetViolation("training","optimizer_steps",steps,max_steps)
                if est_flops>max_flops: raise BudgetViolation("training","flops",est_flops,max_flops)
                if elapsed>max_wall_seconds: raise BudgetViolation("training","wall_seconds",elapsed,max_wall_seconds)
                if realized_tokens>=token_budget: break
        if realized_tokens<token_budget:
            remaining=token_budget-realized_tokens
            if remaining>0 and buffer:
                chunk=buffer[:remaining]; x=torch.tensor([chunk],device=model.device); out=model(input_ids=x,labels=x); out.loss.backward()
                realized_tokens+=len(chunk); micro+=1
        if micro: optimizer.step(); optimizer.zero_grad(set_to_none=True); steps+=1
        elapsed=time.perf_counter()-start; est_flops=6*model.config.num_parameters*realized_tokens
        if realized_tokens!=token_budget: raise BudgetViolation("training","token_budget_not_fully_consumed",realized_tokens,token_budget)
        if steps>max_steps: raise BudgetViolation("training","optimizer_steps",steps,max_steps)
        if est_flops>max_flops: raise BudgetViolation("training","flops",est_flops,max_flops)
        if elapsed>max_wall_seconds: raise BudgetViolation("training","wall_seconds",elapsed,max_wall_seconds)
        outdir=Path(output_dir); outdir.mkdir(parents=True,exist_ok=False); model.save_pretrained(outdir); tok.save_pretrained(outdir)
        meta={**provenance,"checkpoint_id":outdir.name,"training_tokens":realized_tokens,"optimizer_steps":steps,"estimated_training_flops":est_flops,"training_wall_seconds":elapsed,"environment":{"python":sys.version,"platform":platform.platform(),"torch":torch.__version__,"cuda":torch.cuda.is_available()}}
        (outdir/"provenance.json").write_text(json.dumps(meta,indent=2,sort_keys=True))
        return {"checkpoint":str(outdir),"training_tokens":realized_tokens,"optimizer_steps":steps,"estimated_training_flops":est_flops,"training_wall_seconds":elapsed}

class HuggingFaceInferenceAdapter:
    def __init__(self,model_id,revision,checkpoint=None):
        torch,AutoModel,AutoTokenizer,_=_deps(); self.torch=torch
        self.tokenizer=AutoTokenizer.from_pretrained(checkpoint or model_id,revision=None if checkpoint else revision)
        self.model=AutoModel.from_pretrained(checkpoint or model_id,torch_dtype="auto",device_map="auto"); self.model.eval()
    def count_input_tokens(self,prompt):
        return int(self.tokenizer(prompt,return_tensors="pt",truncation=True,max_length=16000)["input_ids"].shape[-1])
    def generate(self,prompt,max_new_tokens,seed):
        self.torch.manual_seed(seed); inputs=self.tokenizer(prompt,return_tensors="pt",truncation=True,max_length=16000).to(self.model.device)
        start=time.perf_counter()
        with self.torch.inference_mode(): out=self.model.generate(**inputs,max_new_tokens=max_new_tokens,min_new_tokens=max_new_tokens,do_sample=True,pad_token_id=self.tokenizer.pad_token_id)
        elapsed=time.perf_counter()-start
        return {"text":self.tokenizer.decode(out[0][inputs["input_ids"].shape[-1]:],skip_special_tokens=True),"input_tokens":int(inputs["input_ids"].shape[-1]),"output_tokens":int(out.shape[-1]-inputs["input_ids"].shape[-1]),"wall_seconds":elapsed}
