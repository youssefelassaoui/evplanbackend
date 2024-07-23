from pydantic import BaseModel, Field
from typing import List, Optional

class GeometriaRequest(BaseModel):
    type: str
    coordinates: list

class AreaSelected(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None
    num_hexagons: int = Field(ge=1, le=1000)
    distance_buffer: int = Field(ge=1, le=1000) #metters
    geometry: GeometriaRequest
    geometries: Optional[List[GeometriaRequest]] = []

class RoadSelected(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None
    num_hexagons: int = Field(ge=1, le=1000)
    distance_buffer: int = Field(ge=1, le=1000) #metters
    geometry: Optional[GeometriaRequest] = None
    geometries: List[GeometriaRequest]
