from fastapi import APIRouter, Depends, HTTPException
from typing import List

from api.models.schemas.token_data import TokenData
from api.models.schemas.auth.user import UpdateUser, User
from api.models.schemas.auth.update_role import UpdateRole
from api.models.schemas.auth.update_password import UpdatePassword
from api.dependencies import admin_authorization
from api.services.auth import (
    add_roles_to_user as add_roles_to_user_service,
    remove_roles_to_user as remove_roles_to_user_service,
    get_users_list as get_users_list_service,
    update_user as update_user_service,
    update_user_password as update_user_password_service,
    create_user as create_user_service,
    list_user_roles as list_user_roles_service,
    get_roles_list as get_roles_list_service,
    get_users_by_role as get_users_by_role_service,
    get_users_session as get_users_session_service,
    remove_session_to_user as remove_session_to_user_service
)

# router = APIRouter(prefix="/auth", tags=["Auth"], include_in_schema=False)
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/users")
async def get_users_list(user: TokenData = Depends(admin_authorization)):
    return get_users_list_service()


@router.get("/roles")
async def get_users_list(user: TokenData = Depends(admin_authorization)):
    return get_roles_list_service()


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    payload: UpdateUser,
    user: TokenData = Depends(admin_authorization),
):
    return update_user_service(user_id=user_id, payload=payload)


@router.put("/users/{user_id}/reset-password")
async def add_role_to_user(
    user_id: str, data: UpdatePassword, user: TokenData = Depends(admin_authorization)
):
    if data is None or data.type != "password":
        raise HTTPException(400, "Not valid credentials type")
    return update_user_password_service(
        user_id=user_id, password=data.value, temporaly=data.temporary
    )


@router.post("/users/{user_id}/role-mappings/realm")
async def add_roles_to_user(
    user_id: str,
    roles: List[UpdateRole],
    user: TokenData = Depends(admin_authorization),
):
    if roles is None:
        raise HTTPException(400, "Not roles list")
    return add_roles_to_user_service(user_id=user_id, roles=roles)


@router.get("/users/{user_id}/role-mappings/realm")
async def list_user_roles(
    user_id: str,
    user: TokenData = Depends(admin_authorization),
):
    return list_user_roles_service(user_id=user_id)


@router.delete("/users/{user_id}/role-mappings/realm")
async def remove_roles_to_user(
    user_id: str,
    roles: List[UpdateRole],
    user: TokenData = Depends(admin_authorization),
):
    if roles is None:
        raise HTTPException(400, "Not roles list")
    return remove_roles_to_user_service(user_id=user_id, roles=roles)


@router.post("/users")
async def create_user(
    new_user: User,
    user: TokenData = Depends(admin_authorization),
):
    return create_user_service(user=new_user)


@router.get("/roles/{role_name}/users")
async def get_users_by_role(
    role_name: str, user: TokenData = Depends(admin_authorization)
):
    return get_users_by_role_service(role_name)

@router.get("/users/session")
async def get_users_session(user: TokenData = Depends(admin_authorization)):
    return get_users_session_service()

@router.delete("/users/session/{user_id}")
async def remove_session_to_user(
    user_id: str, user: TokenData = Depends(admin_authorization)
):
    return remove_session_to_user_service(user_id=user_id)