from pydantic import BaseModel

class RestrictionIn(BaseModel):
    rule_id: int
    restriction_type_id: int
    comparison_operator_id: int
    value: str
    is_active: bool