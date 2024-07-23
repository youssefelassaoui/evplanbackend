from fastapi import HTTPException
import json
from keycloak.exceptions import KeycloakError
from typing import List

from api.dependencies import create_keycloak_admin
from api.constants import KEYCLOAK_CLIENT_ID_FRONT


def get_users_list() -> List[dict]:
    try:
        keycloak_admin = create_keycloak_admin()
        return keycloak_admin.get_users()
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None


def update_user_password(user_id, password, temporaly) -> dict:
    try:
        keycloak_admin = create_keycloak_admin()
        return keycloak_admin.set_user_password(
            user_id=user_id, password=password, temporary=temporaly
        )
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None


def add_roles_to_user(user_id, roles):
    try:
        keycloak_admin = create_keycloak_admin()
        roles_dict = [role.dict() for role in roles]
        return keycloak_admin.assign_realm_roles(user_id=user_id, roles=roles_dict)
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None


def remove_roles_to_user(user_id, roles):
    try:
        keycloak_admin = create_keycloak_admin()
        roles_dict = [role.dict() for role in roles]
        return keycloak_admin.delete_realm_roles_of_user(
            user_id=user_id, roles=roles_dict
        )
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None


def update_user(user_id, payload) -> dict:
    try:
        keycloak_admin = create_keycloak_admin()
        return keycloak_admin.update_user(user_id=user_id, payload=payload.dict())
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None


def update_rol(user_id, payload) -> dict:
    try:
        keycloak_admin = create_keycloak_admin()
        return keycloak_admin.update_user(user_id=user_id, payload=payload)
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None


def create_user(user):
    try:
        keycloak_admin = create_keycloak_admin()
        return keycloak_admin.create_user(user.dict())
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None


def get_roles_list():
    try:
        keycloak_admin = create_keycloak_admin()
        return keycloak_admin.get_realm_roles()
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None


def get_users_by_role(role_name):
    try:
        keycloak_admin = create_keycloak_admin()
        return keycloak_admin.get_realm_role_members(role_name=role_name)
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None


def list_user_roles(user_id):
    try:
        keycloak_admin = create_keycloak_admin()
        return keycloak_admin.get_realm_roles_of_user(user_id=user_id)
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None

def get_users_session() -> dict:
    try:
        keycloak_admin = create_keycloak_admin()

        # get client
        clients = keycloak_admin.get_clients()
        client = next((c for c in clients if c['clientId'] == KEYCLOAK_CLIENT_ID_FRONT), None)

        return keycloak_admin.get_client_all_sessions(client['id'])
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None

def remove_session_to_user(user_id: str):
    try:
        keycloak_admin = create_keycloak_admin()
        return keycloak_admin.user_logout(user_id=user_id)
    except KeycloakError as ke:
        raise HTTPException(ke.response_code, json.loads(ke.response_body))
    finally:
        keycloak_admin = None
