from pydantic import BaseModel
from datetime import datetime

class AlgorithmIn(BaseModel):
    name: str
    is_active: bool

class AlgorithmOut(BaseModel):
    id: int
    name: str
    user_name: str
    is_active: bool
    num_searchs: int

class AlgorithmSearchsOut(BaseModel):
    algorithm_id: int
    algorithm: str
    user_name: str
    location_num: int
    polygon_size: int
    selection_type: str
    created_at: datetime
    num_import: int
    num_export: int