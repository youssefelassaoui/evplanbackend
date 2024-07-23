from os import getenv
from dotenv import load_dotenv

load_dotenv()

# CORS_ORIGINS
CORS_ORIGINS = getenv("CORS_ORIGINS").split(",")
# DATABASE
SQLALCHEMY_DATABASE_URL = (
    "postgresql://"
    + getenv("DB_USER")
    + ":"
    + getenv("DB_PASSWORD")
    + "@"
    + getenv("DB_HOST")
    + "/"
    + getenv("DB_DATABASE")
)
# KEYCLOAK
KEYCLOAK_REALM_ID = getenv("KEYCLOAK_REALM_ID")
KEYCLOAK_CLIENT_ID_BACK = getenv("KEYCLOAK_CLIENT_ID_BACK")
KEYCLOAK_SECRET_KEY_BACK = getenv("KEYCLOAK_SECRET_KEY_BACK")
KEYCLOAK_CLIENT_ID_FRONT = getenv("KEYCLOAK_CLIENT_ID_FRONT")
KEYCLOAK_BASE_URL = getenv("KEYCLOAK_BASE_URL")
KEYCLOAK_AUTH_URL = "/".join([KEYCLOAK_BASE_URL, ""]) + "/"
KEYCLOAK_TOKEN_AUTH_URL = "/".join(
    [
        KEYCLOAK_BASE_URL,
        "auth",
        "realms",
        KEYCLOAK_REALM_ID,
        "protocol",
        "openid-connect",
        "token",
    ]
)
KEYCLOAK_ADMIN_REMOVE_USERS_URL = "/".join(
    [KEYCLOAK_BASE_URL, "auth", "admin", "realms", KEYCLOAK_REALM_ID, "users"]
)
KEYCLOAK_ADMIN_ROLES_URL = "/".join(
    [KEYCLOAK_BASE_URL, "auth", "admin", "realms", KEYCLOAK_REALM_ID, "roles"]
)

KEYCLOAK_ADMIN_ROLE = "administrador"
KEYCLOAK_DEFAULT_ROLE = "default-roles-evplan"
KEYCLOAK_COMERCIAL_ROLE = "comercial"

COORDINATE_SYSTEM=getenv("COORDINATE_SYSTEM")
