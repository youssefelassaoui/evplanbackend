from pydantic import BaseModel, Field
from typing import Optional
from typing import List


class Roles(BaseModel):
    roles: Optional[List[str]] = None


class TokenData(BaseModel):
    sid: Optional[str] = None
    sub: Optional[str] = None
    active: bool = False
    scope: Optional[str] = None
    realm_access: Roles = None
    groups: Optional[List[str]] = None


class UserInfo(BaseModel):
    access_token: str = Field(alias="accessToken")

    class Config:
        allow_population_by_field_name = True
