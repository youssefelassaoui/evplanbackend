from pydantic import BaseModel

class RuleIn(BaseModel):
    element_id: int
    score: float
    is_active: bool