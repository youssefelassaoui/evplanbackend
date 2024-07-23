from pydantic import BaseModel

class ElementIn(BaseModel):
    algorithm_id: int
    entity_type_id: int
    is_active: bool