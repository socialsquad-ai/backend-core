from fastapi import APIRouter
from usecases.user_management import UserManagement
from decorators.user import require_authentication
from decorators.common import validate_json_payload
from fastapi import Request
from controller.util import APIResponseFormat
from config.non_env import API_VERSION_V1, API_VERSION_V2
from utils.error_messages import RESOURCE_NOT_FOUND, INVALID_RESOURCE_ID
from utils.status_codes import RESPONSE_404, RESPONSE_400

user_router = APIRouter(
    prefix=f"{API_VERSION_V1}/users",
    tags=["user"],
)
user_router_v2 = APIRouter(
    prefix=f"{API_VERSION_V2}/users",
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


@user_router.get("/{user_uuid}")
@require_authentication
async def get_user(request: Request, user_uuid: str):
    error_message, data, errors = UserManagement.get_user_by_uuid(request, user_uuid)
    if error_message == RESOURCE_NOT_FOUND:
        return APIResponseFormat(
            status_code=RESPONSE_404,
            message=error_message,
            data=data,
            errors=errors,
        ).get_json()
    if error_message == INVALID_RESOURCE_ID:
        return APIResponseFormat(
            status_code=RESPONSE_400,
            message=error_message,
            data=data,
            errors=errors,
        ).get_json()

    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@user_router.get("/")
@require_authentication
async def get_users(request: Request):
    error_message, data, errors = UserManagement.get_users(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@user_router_v2.get("/")
@require_authentication
async def get_users_v2(request: Request):
    error_message, data, errors = UserManagement.get_users_v2(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()
