from pydantic import BaseModel


class UpdatePassword(BaseModel):
    type: str
    temporary: bool
    value: str
