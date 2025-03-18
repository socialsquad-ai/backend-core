from fastapi import Request
from controller.util import APIResponseFormat
from usecases.status_management import StatusManagement
from config.non_env import API_VERSION_V1
from fastapi import APIRouter
from decorators.user import require_authentication
from decorators.common import validate_post_payload

status_router = APIRouter(
    prefix=f"{API_VERSION_V1}/status", tags=["status"]
)  # For different usecases, create different bases


@status_router.get("/")
async def get_status(request: Request):
    error_message, data, errors = StatusManagement.get_status(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@status_router.get("/deep")
@require_authentication
@validate_post_payload(
    {
        "example_key": {"type": "string", "required": True},
    }
)
async def get_deep_status(request: Request):
    error_message, data, errors = StatusManagement.get_deep_status(request)
    status_code = 200 if not error_message else 500
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()
