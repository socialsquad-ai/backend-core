from fastapi import APIRouter, Request

from config.non_env import API_VERSION_V1
from controller.util import APIResponseFormat
from decorators.common import validate_json_payload
from usecases.auth_management import AuthManagement
from utils.status_codes import RESPONSE_400, RESPONSE_429, RESPONSE_500

auth_router = APIRouter(
    prefix=f"{API_VERSION_V1}/auth",
    tags=["Authentication"],
)


@auth_router.post(
    "/resend-verification",
    summary="Resend Email Verification",
    description="Resend the email verification link to a user who has signed up but not verified "
    "their email. For security reasons, this endpoint returns a generic success message regardless of whether the email exists.",
    responses={
        200: {"description": "Request processed (email sent if account exists and unverified)"},
        400: {"description": "Email already verified or invalid request"},
        429: {"description": "Too many requests - rate limited by Auth0"},
        500: {"description": "Internal server error"},
    },
)
@validate_json_payload(
    {
        "email": {"type": "string", "required": True},
    }
)
async def resend_verification_email(request: Request):
    """Resend verification email to a user."""
    error_message, data, errors = await AuthManagement.resend_verification_email()

    if errors:
        # Determine status code based on error type
        if "Rate limited" in errors:
            status_code = RESPONSE_429
        elif "already verified" in error_message.lower():
            status_code = RESPONSE_400
        else:
            status_code = RESPONSE_500

        return APIResponseFormat(
            status_code=status_code,
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
