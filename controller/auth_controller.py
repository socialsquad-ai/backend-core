from fastapi import APIRouter, Request

from config.non_env import API_VERSION_V1
from controller.util import APIResponseFormat
from decorators.common import validate_json_payload
from logger.logging import LoggerUtil
from utils.auth0_service import Auth0ManagementService

auth_router = APIRouter(
    prefix=f"{API_VERSION_V1}/auth",
    tags=["Authentication"],
)


@auth_router.post(
    "/resend-verification",
    summary="Resend Email Verification",
    description="""
    Resend the email verification link to a user who has signed up but not verified their email.

    **Note:** For security reasons, this endpoint returns a generic success message regardless
    of whether the email exists in the system. This prevents email enumeration attacks.

    **Rate Limiting:** Auth0 may rate limit verification email requests. If you receive a
    rate limit error, please wait a few minutes before trying again.
    """,
    responses={
        200: {"description": "Request processed (email sent if account exists and unverified)"},
        400: {"description": "Invalid email format or service not configured"},
        429: {"description": "Too many requests - rate limited"},
        500: {"description": "Internal server error"},
    },
)
@validate_json_payload(
    {
        "email": {"type": "string", "required": True},
    }
)
async def resend_verification_email(request: Request):
    """
    Resend verification email to a user.

    This endpoint does not require authentication since users who need to verify
    their email cannot log in yet.
    """
    try:
        payload = request.state.payload
        email = payload.get("email")

        LoggerUtil.create_info_log(f"Resend verification requested for email: {email}")

        mgmt_service = Auth0ManagementService()
        result = await mgmt_service.resend_verification_email(email)

        status_code = 200 if result["success"] else 400

        return APIResponseFormat(
            status_code=status_code,
            message=result["message"],
            data={"success": result["success"]},
            errors=None if result["success"] else [result["message"]],
        ).get_json()

    except Exception as e:
        LoggerUtil.create_error_log(f"Error in resend_verification_email: {e}")
        return APIResponseFormat(
            status_code=500,
            message="An unexpected error occurred. Please try again later.",
            data=None,
            errors=[str(e)],
        ).get_json()
