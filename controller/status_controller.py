from fastapi import APIRouter, Request

from config.non_env import API_VERSION_V1
from controller.util import APIResponseFormat
from decorators.common import validate_json_payload
from decorators.user import require_authentication
from usecases.status_management import StatusManagement

status_router = APIRouter(
    prefix=f"{API_VERSION_V1}/status",
    tags=["Status"],
)


@status_router.get(
    "/",
    summary="Health Check",
    description="Basic health check endpoint to verify the API service is running. Returns service status information.",
    responses={
        200: {"description": "Service is healthy and operational"},
        500: {"description": "Service is experiencing issues"},
    },
)
async def get_status(request: Request):
    """Check if the API service is running and healthy."""
    error_message, data, errors = StatusManagement.get_status(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@status_router.get(
    "/deep",
    summary="Deep Health Check",
    description="Comprehensive health check that validates database connections and dependent services. Requires authentication.",
    responses={
        200: {"description": "All systems operational"},
        401: {"description": "Authentication required"},
        500: {"description": "One or more systems are not operational"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
@validate_json_payload(
    {
        "example_key": {"type": "string", "required": True},
    }
)
async def get_deep_status(request: Request):
    """Perform a deep health check on all dependent services."""
    error_message, data, errors = StatusManagement.get_deep_status(request)
    status_code = 200 if not error_message else 500
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()
