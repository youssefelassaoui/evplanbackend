from pydantic import BaseModel
from typing import List


class Credentials(BaseModel):
    value: str
    type: str = "password"


class UpdateUser(BaseModel):
    email: str
    username: str
    enabled: bool
    firstName: str
    lastName: str


class User(UpdateUser):
    credentials: List[Credentials]
