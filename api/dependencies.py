from broadcaster import Broadcast
from keycloak import KeycloakOpenID, KeycloakAdmin
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from api.database import SessionLocal
from api.models.schemas.token_data import TokenData
from api.constants import (
    KEYCLOAK_TOKEN_AUTH_URL,
    KEYCLOAK_AUTH_URL,
    KEYCLOAK_REALM_ID,
    KEYCLOAK_CLIENT_ID_BACK,
    KEYCLOAK_SECRET_KEY_BACK,
    KEYCLOAK_ADMIN_ROLE,
    KEYCLOAK_DEFAULT_ROLE
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=KEYCLOAK_TOKEN_AUTH_URL)

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_AUTH_URL,
    client_id=KEYCLOAK_CLIENT_ID_BACK,
    realm_name=KEYCLOAK_REALM_ID,
    client_secret_key=KEYCLOAK_SECRET_KEY_BACK,
    verify=True,
)


def create_keycloak_admin():
    kc_admin = KeycloakAdmin(
        server_url=KEYCLOAK_AUTH_URL,
        client_id=KEYCLOAK_CLIENT_ID_BACK,
        realm_name=KEYCLOAK_REALM_ID,
        user_realm_name=KEYCLOAK_REALM_ID,
        client_secret_key=KEYCLOAK_SECRET_KEY_BACK,
        verify=True,
    )
    kc_admin.realm_name = KEYCLOAK_REALM_ID
    return kc_admin


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
)

def get_raw_token(token: str = Depends(oauth2_scheme)):
    return token

def get_query_token(token: str = Depends(oauth2_scheme)):
    return TokenData.parse_obj(keycloak_openid.introspect(token))


def authorization(token: TokenData = Depends(get_query_token)):
    if token is None:
        raise credentials_exception

    if token.active == False:
        raise credentials_exception

    return token


def role_authorization(token: TokenData = Depends(authorization)):
    if token.realm_access is None:
        raise credentials_exception

    if token.realm_access.roles is None:
        raise credentials_exception

    return token


def admin_authorization(token: TokenData = Depends(role_authorization)):
    if not KEYCLOAK_ADMIN_ROLE in token.realm_access.roles:
        raise credentials_exception

    return token

def default_authorization(token: TokenData = Depends(role_authorization)):
    if (not KEYCLOAK_ADMIN_ROLE in token.realm_access.roles and not KEYCLOAK_DEFAULT_ROLE in token.realm_access.roles):
        raise credentials_exception
    
    return token


def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
