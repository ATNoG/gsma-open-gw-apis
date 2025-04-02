from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import Response

from typing import Any
from collections.abc import Awaitable, Callable

from app import endpoints

app = FastAPI()
app.include_router(endpoints.router)


@app.middleware("http")
async def add_correlation_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    x_correlator = request.headers.get("x-correlator")

    response = await call_next(request)

    if x_correlator is not None:
        response.headers["x-correlator"] = x_correlator

    return response


# Add the x-correlator header to all operations and responses
def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="GSMA Open Gateway",
        version="0.1.0",
        routes=app.routes,
    )

    x_correlator_schema = {
        "type": "string",
        "pattern": "^[a-zA-Z0-9-]{0,55}$",
        "example": "b4333c46-49c0-4f62-80d7-f0ef930f1c46",
    }

    components = openapi_schema.setdefault("components", {})
    c_parameters = components.setdefault("parameters", {})
    c_parameters["x-correlator"] = {
        "name": "x-correlator",
        "in": "header",
        "description": "Correlation id for the different services",
        "required": False,
        "schema": x_correlator_schema,
    }
    c_headers = components.setdefault("headers", {})
    c_headers["x-correlator"] = {
        "description": "Correlation id for the different services",
        "schema": x_correlator_schema,
    }

    for _, path_schema in openapi_schema["paths"].items():
        for method in ["get", "put", "post", "delete"]:
            operation = path_schema.get(method)
            if operation is None:
                continue

            parameters = operation.setdefault("parameters", [])
            parameters.append({"$ref": "#/components/parameters/x-correlator"})

            responses = operation.setdefault("responses", {})
            for _, response in responses.items():
                headers = response.setdefault("headers", {})
                headers["x-correlator"] = {"$ref": "#/components/headers/x-correlator"}

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# This is needed as mypy isn't happy when assigning to a method
# mypy: ignore-errors
app.openapi = custom_openapi
