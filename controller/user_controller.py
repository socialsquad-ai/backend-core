from fastapi import APIRouter, Request

from config.non_env import API_VERSION_V1
from controller.util import APIResponseFormat
from decorators.common import require_internal_authentication, validate_json_payload
from decorators.user import require_authentication
from usecases.user_management import UserManagement
from utils.error_messages import INVALID_RESOURCE_ID, RESOURCE_NOT_FOUND
from utils.status_codes import RESPONSE_400, RESPONSE_404, RESPONSE_409

user_router = APIRouter(
    prefix=f"{API_VERSION_V1}/users",
    tags=["Users"],
)


@user_router.post(
    "/",
    summary="Create User (Internal)",
    description="Create a new user account from Auth0 webhook. This endpoint is for internal service-to-service calls only and requires the internal API key.",
    responses={
        200: {"description": "User created successfully"},
        401: {"description": "Invalid or missing internal API key"},
        409: {"description": "User already exists with this email or Auth0 ID"},
    },
    openapi_extra={"security": [{"InternalAPIKey": []}]},
)
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
    """Create a new user from Auth0 authentication data."""
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


@user_router.post(
    "/verify-email",
    summary="Mark Email as Verified (Internal)",
    description="Mark a user's email as verified after Auth0 email verification. This endpoint is for internal service-to-service calls only (Auth0 Action webhook) and requires the internal API key.",
    responses={
        200: {"description": "Email marked as verified successfully"},
        401: {"description": "Invalid or missing internal API key"},
        404: {"description": "User not found with the provided auth0_user_id"},
    },
    openapi_extra={"security": [{"InternalAPIKey": []}]},
)
@require_internal_authentication
@validate_json_payload(
    {
        "auth0_user_id": {"type": "string", "required": True},
    }
)
async def mark_email_verified(request: Request):
    """Mark a user's email as verified from Auth0 post-email-verification hook."""
    error_message, data, errors = UserManagement.mark_email_verified()
    if errors:
        return APIResponseFormat(
            status_code=RESPONSE_404,
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


@user_router.get(
    "/profile",
    summary="Get Current User Profile",
    description="Retrieve the profile information of the currently authenticated user.",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Authentication required"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
async def get_profile(request: Request):
    """Get the authenticated user's profile."""
    error_message, data, errors = UserManagement.get_profile(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@user_router.get(
    "/{user_uuid}",
    summary="Get User by UUID",
    description="Retrieve a specific user's information by their UUID.",
    responses={
        200: {"description": "User found and returned"},
        400: {"description": "Invalid UUID format"},
        401: {"description": "Authentication required"},
        404: {"description": "User not found"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
async def get_user(request: Request, user_uuid: str):
    """Get a user by their UUID."""
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


@user_router.get(
    "/",
    summary="List All Users",
    description="Retrieve a list of all users in the system.",
    responses={
        200: {"description": "List of users retrieved successfully"},
        401: {"description": "Authentication required"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
async def get_users(request: Request):
    """Get all users in the system."""
    error_message, data, errors = UserManagement.get_users(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()
