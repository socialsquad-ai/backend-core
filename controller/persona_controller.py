from fastapi import APIRouter, Query, Request

from decorators.user import require_authentication
from decorators.common import validate_json_payload
from usecases.persona_management import PersonaManagement
from controller.util import APIResponseFormat
from config.non_env import API_VERSION_V1
from utils.status_codes import RESPONSE_200, RESPONSE_404, RESPONSE_400, RESPONSE_500
from utils.error_messages import (
    RESOURCE_NOT_FOUND,
    INVALID_PAGINATION_PARAMETERS,
    PERSONA_ALREADY_EXISTS,
)
from utils.contextvar import get_context_user, get_request_json_post_payload

persona_router = APIRouter(prefix=f"{API_VERSION_V1}/personas", tags=["personas"])


@persona_router.get("/templates")
@require_authentication
async def get_persona_templates(request: Request):
    """
    Get all persona templates
    """
    error_message, data, errors = PersonaManagement.get_persona_templates()
    status_code = RESPONSE_200 if not error_message else RESPONSE_500
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@persona_router.get("/")
@require_authentication
async def get_personas(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """
    Get paginated list of personas for the current user
    """
    user = get_context_user()
    error_message, data, errors = PersonaManagement.get_user_personas(
        user, page, page_size
    )
    if not error_message:
        status_code = RESPONSE_200
    elif error_message == INVALID_PAGINATION_PARAMETERS:
        status_code = RESPONSE_400
    else:
        status_code = RESPONSE_500
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@persona_router.post("/")
@require_authentication
@validate_json_payload(
    {
        "name": {"type": "string", "required": True},
        "tone": {"type": "string", "required": True},
        "style": {"type": "string", "required": True},
        "instructions": {"type": "string", "required": True},
        "role": {"type": "string", "required": True},
        "content_categories": {"type": "list", "required": True},
        "personal_details": {"type": "string", "required": False},
    }
)
async def create_persona(request: Request):
    """
    Create a new persona for the current user
    """
    user = get_context_user()
    payload = get_request_json_post_payload()
    error_message, data, errors = PersonaManagement.create_persona(
        user=user,
        name=payload["name"],
        tone=payload["tone"],
        style=payload["style"],
        instructions=payload["instructions"],
        content_categories=payload["content_categories"],
        role=payload["role"],
        personal_details=payload.get("personal_details"),
    )
    status_code = 201 if not error_message else 500
    message = "Persona created successfully" if not error_message else error_message
    return APIResponseFormat(
        status_code=status_code,
        message=message,
        data=data,
        errors=errors,
    ).get_json()


@persona_router.put("/{persona_uuid}")
@require_authentication
@validate_json_payload(
    {
        "name": {"type": "string", "required": True},
        "tone": {"type": "string", "required": True},
        "style": {"type": "string", "required": True},
        "instructions": {"type": "string", "required": True},
        "personal_details": {"type": "string", "required": False},
    }
)
async def update_persona(
    request: Request,
    persona_uuid: str,
):
    """
    Update an existing persona for the current user
    """
    user = get_context_user()
    payload = get_request_json_post_payload()
    error_message, data, errors = PersonaManagement.update_persona(
        user=user, persona_uuid=persona_uuid, **payload
    )
    if not error_message:
        status_code = 200
        message = "Persona updated successfully"
    elif error_message == RESOURCE_NOT_FOUND:
        status_code = RESPONSE_404
        message = error_message
    elif error_message == PERSONA_ALREADY_EXISTS:
        status_code = RESPONSE_400
        message = error_message
    else:
        status_code = RESPONSE_500
        message = error_message
    return APIResponseFormat(
        status_code=status_code,
        message=message,
        data=data,
        errors=errors,
    ).get_json()


@persona_router.delete("/{persona_uuid}")
@require_authentication
async def delete_persona(
    request: Request,
    persona_uuid: str,
):
    """
    Delete a persona (soft delete)
    """
    user = get_context_user()
    error_message, data, errors = PersonaManagement.delete_persona(persona_uuid, user)
    if error_message:
        status_code = (
            RESPONSE_404 if error_message == RESOURCE_NOT_FOUND else RESPONSE_500
        )
        message = error_message
    else:
        status_code = 200
        message = "Persona deleted successfully"
    return APIResponseFormat(
        status_code=status_code,
        message=message,
        data=data,
        errors=errors,
    ).get_json()
