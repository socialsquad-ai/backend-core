from fastapi import APIRouter
from usecases.user_management import UserManagement
from decorators.user import require_authentication
from decorators.common import validate_json_payload, require_internal_authentication
from fastapi import Request
from controller.util import APIResponseFormat
from config.non_env import API_VERSION_V1, API_VERSION_V2
from utils.error_messages import RESOURCE_NOT_FOUND, INVALID_RESOURCE_ID
from utils.status_codes import RESPONSE_404, RESPONSE_400, RESPONSE_409

user_router = APIRouter(
    prefix=f"{API_VERSION_V1}/users",
    tags=["user"],
)


@user_router.post("/")
@require_internal_authentication
@validate_json_payload(
    {
        "email": {"type": "string", "required": True},
        "auth0_user_id": {"type": "string", "required": True},
        "name": {"type": "string", "required": False},
        "signup_method": {"type": "string", "required": True},
        "email_verified": {"type": "boolean", "required": True},
        "auth0_created_at": {"type": "string", "required": False},
    }
)
async def create_user(request: Request):
    error_message, data, errors = UserManagement.create_user(request)
    if errors:
        return APIResponseFormat(
            status_code=RESPONSE_409,
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
