# RESTful API endpoints used by consumers that want to extract data from StudyBuilder
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Security, status
from fastapi.encoders import jsonable_encoder
from fastapi.middleware import Middleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from neomodel import config as neomodel_config
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import AlwaysOnSampler
from pydantic import ValidationError
from starlette_context.middleware import RawContextMiddleware

from common import config, exceptions
from common.auth.config import OAUTH_ENABLED, SWAGGER_UI_INIT_OAUTH
from common.auth.dependencies import dummy_user_auth, validate_token
from common.auth.discovery import reconfigure_with_openid_discovery
from common.models.error import ErrorResponse
from common.telemetry.traceback_middleware import ExceptionTracebackMiddleware
from consumer_api.shared.common import get_api_version
from consumer_api.system.routes import router as system_router
from consumer_api.v1.main import router as v1_router

# from consumer_api.v2.main import router as v2_router

log = logging.getLogger(__name__)


def default_logging_config():
    """Configure logging if it has not been configured already."""

    loglevel = os.environ.get("LOG_LEVEL", "INFO")

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {loglevel}")

    # logging.basicConfig() does nothing if the root logger already has handlers configured
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)-17s - %(levelname)s - %(message)s",
    )


# Set logging defaults once at start-app if it was not already configured ex. UVICORN_LOG_CONFIG
default_logging_config()


# Configure Neo4J connection on startup
neo4j_dsn = os.getenv("NEO4J_DSN")
if neo4j_dsn:
    neomodel_config.DATABASE_URL = neo4j_dsn
    log.info("Neo4j DSN set to: %s", neo4j_dsn.split("@")[-1])


# Global dependencies, in order of execution
global_dependencies = []
if OAUTH_ENABLED:
    global_dependencies.append(Security(validate_token))
else:
    global_dependencies.append(Security(dummy_user_auth))
    log.warning(
        "WARNING: Authentication is disabled. "
        "See OAUTH_ENABLED and OAUTH_RBAC_ENABLED environment variables."
    )


# Middlewares - please don't use app.add_middleware() as that inserts them to the beginning of the list
middlewares = [
    # Context middleware - must come before TracingMiddleware
    Middleware(RawContextMiddleware)
]


# Azure Application Insights integration for tracing
if config.APPINSIGHTS_CONNECTION:
    _EXPORTER = AzureExporter(
        connection_string=config.APPINSIGHTS_CONNECTION, enable_local_storage=False
    )
else:
    _EXPORTER = None

# Tracing middleware
if not config.TRACING_DISABLED:
    # pylint: disable=wrong-import-position,ungrouped-imports
    from common.telemetry.request_metrics import patch_neomodel_database
    from common.telemetry.tracing_middleware import TracingMiddleware

    middlewares.append(
        Middleware(
            TracingMiddleware,
            sampler=AlwaysOnSampler(),
            exporter=_EXPORTER,
            exclude_paths=["/system/healthcheck"],
        )
    )

    patch_neomodel_database()


# Convert all uncaught exceptions to response before returning to TracingMiddleware
# All other exceptions (except Exception) can be caught by ExceptionMiddleware
# provided that an exception handler is defined below with @app.exception_handler()
# Refer to: fastapi.applications.FastAPI.build_middleware_stack()
middlewares.append(Middleware(ExceptionTracebackMiddleware))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if OAUTH_ENABLED:
        # Reconfiguring Swagger UI settings with OpenID Connect discovery
        await reconfigure_with_openid_discovery()
    yield


app = FastAPI(
    version=get_api_version(),
    title="StudyBuilder Consumer API",
    dependencies=global_dependencies,
    lifespan=lifespan,
    swagger_ui_init_oauth=SWAGGER_UI_INIT_OAUTH,
    middleware=middlewares,
    swagger_ui_parameters={"docExpansion": "none"},
    description="""
## NOTICE

This license information is applicable to the swagger documentation of the clinical-mdr-api, that is the openapi.json.

## License Terms (MIT)

Copyright (C) 2022 Novo Nordisk A/S, Danish company registration no. 24256790

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Licenses and Acknowledgements for Incorporated Software

This component contains software licensed under different licenses when compiled, please refer to the third-party-licenses.md file for further information and full license texts.

## Authentication

Supports OAuth2 [Authorization Code Flow](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1),
at paths described in the OpenID Connect Discovery metadata document (whose URL is defined by the `OAUTH_METADATA_URL` environment variable).

Microsoft Identity Platform documentation can be read 
([here](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)).

## System information:

System information is provided by a separate [System Information](./system/docs) sub-app which doesn't require authentication.
""",
)

# TODO: This is a temporary workaround as schemathesis doesnt support openapi 3.1.0 yet; this should be removed when schemathesis supports 3.1.0
app.openapi_version = "3.0.2"


@app.exception_handler(exceptions.MDRApiBaseException)
def consumer_api_exception_handler(
    request: Request, exception: exceptions.MDRApiBaseException
):
    """Returns an HTTP error code associated to given exception."""

    log.info("Error response %s: %s", exception.status_code, exception.msg)

    return JSONResponse(
        status_code=exception.status_code,
        content=jsonable_encoder(ErrorResponse(request, exception)),
        headers=exception.headers,
    )


@app.exception_handler(ValidationError)
def pydantic_validation_error_handler(request: Request, exception: ValidationError):
    """Returns `400 Bad Request` http error status code in case Pydantic detects validation issues
    with supplied payloads or parameters."""

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(ErrorResponse(request, exception)),
    )


app.include_router(v1_router, prefix="/v1", tags=["V1"])
# app.include_router(v2_router, prefix="/v2", tags=["V2"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["servers"] = [{"url": config.OPENAPI_SCHEMA_API_ROOT_PATH}]

    if OAUTH_ENABLED:
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}

        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {}

        # Add 'BearerJwtAuth' security schema globally
        openapi_schema["components"]["securitySchemes"]["BearerJwtAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",  # optional, arbitrary value for documentation purposes
            "in": "header",
            "name": "Authorization",
            "description": "Access token that will be sent as `Authorization: Bearer {token}` header in all requests",
        }

        # Add 'BearerJwtAuth' security method to all endpoints
        api_router = [route for route in app.routes if isinstance(route, APIRoute)]
        for route in api_router:
            path = getattr(route, "path")
            methods = [method.lower() for method in getattr(route, "methods")]

            for method in methods:
                endpoint_security: list[any] = openapi_schema["paths"][path][
                    method
                ].get("security", [])
                endpoint_security.append({"BearerJwtAuth": []})
                openapi_schema["paths"][path][method]["security"] = endpoint_security

    # Add `400 Bad Request` error response to all endpoints
    for path, path_item in openapi_schema["paths"].items():
        for method, operation in path_item.items():
            if "responses" not in operation:
                operation["responses"] = {}
            if "400" not in operation["responses"]:
                operation["responses"]["400"] = {
                    "description": "Bad Request",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                        }
                    },
                }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


system_app = FastAPI(
    middleware=None,
    title="System info sub-application",
    version="1.0",
    description="Sub-application of system-info related endpoints that are exempt from authentication requirements.",
)

system_app.include_router(system_router, tags=["System"])

app.mount("/system", system_app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "consumer_api.consumer_api:app",
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", "8008")),
        reload=True,
    )
