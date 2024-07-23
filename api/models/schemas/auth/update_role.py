from pydantic import BaseModel


class UpdateRole(BaseModel):
    id: str
    name: str
