from dataclasses import dataclass,asdict
from typing import Optional

@dataclass
class Quantity:
    value: Optional[float]; status:str; source:str=""
    def __post_init__(self):
        if self.status not in {"measured","estimated","derived","unavailable"}: raise ValueError(self.status)
        if self.status=="unavailable" and self.value is not None: raise ValueError("unavailable quantity must have null value")

@dataclass
class ComputeRecord:
    training_tokens:Quantity; inference_input_tokens:Quantity; inference_output_tokens:Quantity
    training_flops:Quantity; inference_flops:Quantity; total_flops:Quantity
    optimizer_steps:Quantity; model_calls:Quantity; candidates:Quantity; execution_steps:Quantity
    training_wall_seconds:Quantity; inference_wall_seconds:Quantity; total_wall_seconds:Quantity; monetary_cost_proxy:Quantity
    def to_dict(self): return asdict(self)
    def validate(self):
        if self.total_flops.status=="derived" and self.training_flops.value is not None and self.inference_flops.value is not None:
            if self.total_flops.value != self.training_flops.value+self.inference_flops.value: raise ValueError("invalid total FLOPs")
