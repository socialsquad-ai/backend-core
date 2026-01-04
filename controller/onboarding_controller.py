from fastapi import APIRouter, Request

from decorators.user import require_authentication
from decorators.common import validate_json_payload
from usecases.onboarding_management import OnboardingManagement
from controller.util import APIResponseFormat
from config.non_env import API_VERSION_V1
from utils.status_codes import RESPONSE_200, RESPONSE_500
from utils.contextvar import get_context_user, get_request_json_post_payload

onboarding_router = APIRouter(
    prefix=f"{API_VERSION_V1}/onboarding",
    tags=["Onboarding"],
)


@onboarding_router.post(
    "/",
    summary="Complete User Onboarding",
    description="Complete the onboarding process for a new user by creating their initial AI persona. This sets up the user's preferences for automated social media interactions.",
    responses={
        200: {
            "description": "User onboarded successfully with initial persona created"
        },
        400: {"description": "Invalid request payload"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to complete onboarding"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
@validate_json_payload(
    {
        "persona_name": {"type": "string", "required": True},
        "tone": {"type": "string", "required": True},
        "style": {"type": "string", "required": True},
        "instructions": {"type": "string", "required": True},
        "role": {"type": "string", "required": True},
        "content_categories": {"type": "list", "required": True},
        "personal_details": {"type": "string", "required": False},
    }
)
async def onboard_user(request: Request):
    """Complete user onboarding with initial persona setup."""
    user = get_context_user()
    payload = get_request_json_post_payload()
    error_message, data, errors = OnboardingManagement.onboard_user(
        user=user,
        persona_name=payload["persona_name"],
        tone=payload["tone"],
        style=payload["style"],
        instructions=payload["instructions"],
        content_categories=payload["content_categories"],
        role=payload["role"],
        personal_details=payload.get("personal_details"),
    )
    status_code = RESPONSE_200 if not error_message else RESPONSE_500
    message = "User onboarded successfully" if not error_message else error_message
    return APIResponseFormat(
        status_code=status_code,
        message=message,
        data=data,
        errors=errors,
    ).get_json()
