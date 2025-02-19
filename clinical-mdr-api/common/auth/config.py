from os import environ

from common.utils import strtobool

JWT_LEEWAY_SECONDS = 10
OAUTH_ENABLED = strtobool(environ.get("OAUTH_ENABLED", "1"))
OAUTH_RBAC_ENABLED = strtobool(environ.get("OAUTH_RBAC_ENABLED", "1"))
OAUTH_API_APP_ID = environ.get("OAUTH_API_APP_ID")
OAUTH_API_APP_SECRET = environ.get("OAUTH_API_APP_SECRET")
OAUTH_API_APP_ID_URI = (
    environ.get("OAUTH_API_APP_ID_URI") or f"api://{OAUTH_API_APP_ID}"
)
OUR_SCOPES = {
    f"{OAUTH_API_APP_ID_URI}/API.call": "Make calls to the API",
}
OAUTH_METADATA_URL = environ.get("OAUTH_METADATA_URL")
OAUTH_AUTHORIZATION_URL = environ.get("OAUTH_AUTHORIZATION_URL", "")  # Deprecated.
OAUTH_TOKEN_URL = environ.get("OAUTH_TOKEN_URL", "")  # Deprecated.

SWAGGER_UI_INIT_OAUTH = (
    {
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": environ.get("OAUTH_SWAGGER_APP_ID") or OAUTH_API_APP_ID,
        "scopes": (
            ["openid", "profile", "email", "offline_access"] + list(OUR_SCOPES.keys())
        ),
        "additionalQueryStringParams": {
            "response_mode": "fragment",
        },
    }
    if OAUTH_ENABLED
    else None
)
