from fastapi import APIRouter
from usecases.user_management import UserManagement
from decorators.user import require_authentication
from decorators.common import validate_json_payload
from fastapi import Request
from controller.util import APIResponseFormat
from config.non_env import API_VERSION_V1

user_router = APIRouter(
    prefix=f"{API_VERSION_V1}/users",
    tags=["user"],
)


@user_router.post("/")
@require_authentication
@validate_json_payload(
    {
        "email": {"type": "string", "required": True},
        "timezone": {"type": "string", "required": True},
        "password": {"type": "string", "required": True},
    }
)
async def create_user(request: Request):
    error_message, data, errors = UserManagement.create_user(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@user_router.get("/{user_id}")
@require_authentication
async def get_user(request: Request, user_id: int):
    error_message, data, errors = UserManagement.get_user_by_id(request, user_id)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()
