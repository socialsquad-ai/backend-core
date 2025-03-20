from fastapi import APIRouter
from usecases.user_management import UserManagement
from decorators.user import require_authentication
from decorators.common import validate_post_payload
from fastapi import Request
from controller.util import APIResponseFormat

user_router = APIRouter(
    prefix="/users",
    tags=["user"],
)


@user_router.post("/create")
@require_authentication
@validate_post_payload(
    {
        "email": {"type": "string", "required": True},
        "timezone": {"type": "string", "required": True},
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


@user_router.get("/get")
@require_authentication
async def get_user(request: Request):
    error_message, data, errors = UserManagement.get_user_by_email(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()
