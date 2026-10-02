from pathlib import Path
import time

class RealDependencyError(RuntimeError): pass

def _deps():
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
    except ImportError as e:
        raise RealDependencyError("real mode requires torch, transformers, and accelerate") from e
    return torch,AutoModelForCausalLM,AutoTokenizer,TrainingArguments,Trainer

class HuggingFaceInferenceAdapter:
    def __init__(self, model_id, revision):
        _, AutoModel, AutoTokenizer, _, _ = _deps()
        self.tokenizer=AutoTokenizer.from_pretrained(model_id,revision=revision)
        self.model=AutoModel.from_pretrained(model_id,revision=revision,torch_dtype="auto",device_map="auto")
        self.model.eval()

    def generate(self,prompt,max_new_tokens,seed):
        torch,_,_,_,_= _deps()
        torch.manual_seed(seed)
        inputs=self.tokenizer(prompt,return_tensors="pt").to(self.model.device)
        start=time.perf_counter()
        with torch.inference_mode():
            out=self.model.generate(**inputs,max_new_tokens=max_new_tokens,do_sample=True)
        text=self.tokenizer.decode(out[0][inputs["input_ids"].shape[-1]:],skip_special_tokens=True)
        return {"text":text,"input_tokens":int(inputs["input_ids"].shape[-1]),"output_tokens":int(out.shape[-1]-inputs["input_ids"].shape[-1]),"wall_seconds":time.perf_counter()-start}

class HuggingFaceSFTAdapter:
    def train(self, model_id, revision, dataset_id, dataset_revision, output_dir, max_steps, seed, learning_rate, batch_size, gradient_accumulation, sequence_length):
        torch,AutoModel,AutoTokenizer,TrainingArguments,Trainer=_deps()
        try:
            from datasets import load_dataset
        except ImportError as e:
            raise RealDependencyError("real mode requires datasets") from e
        tokenizer=AutoTokenizer.from_pretrained(model_id,revision=revision)
        model=AutoModel.from_pretrained(model_id,revision=revision,torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32)
        ds=load_dataset(dataset_id,revision=dataset_revision,split="train")

        def render(row):
            if "messages" in row:
                return {"text":"\n".join(str(m.get("content","")) for m in row["messages"])}
            if "prompt" in row and "generation" in row:
                return {"text":str(row["prompt"])+"\n"+str(row["generation"])}
            raise ValueError("dataset row lacks a supported text representation")

        ds=ds.map(render)
        def tokenize(batch):
            return tokenizer(batch["text"],truncation=True,max_length=sequence_length)
        tok=ds.map(tokenize,batched=True,remove_columns=ds.column_names)
        args=TrainingArguments(output_dir=str(Path(output_dir)),max_steps=max_steps,learning_rate=learning_rate,per_device_train_batch_size=batch_size,gradient_accumulation_steps=gradient_accumulation,logging_steps=1,save_strategy="no",report_to=[],bf16=torch.cuda.is_available(),seed=seed)
        trainer=Trainer(model=model,args=args,train_dataset=tok,tokenizer=tokenizer)
        start=time.perf_counter(); trainer.train(); elapsed=time.perf_counter()-start
        trainer.save_model(output_dir); tokenizer.save_pretrained(output_dir)
        return {"checkpoint":str(output_dir),"wall_seconds":elapsed,"steps":max_steps}
