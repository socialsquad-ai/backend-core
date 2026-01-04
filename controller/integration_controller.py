from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from controller.util import APIResponseFormat
from usecases.integration_management import IntegrationManagement
from config.non_env import API_VERSION_V1
from fastapi import APIRouter
from decorators.user import require_authentication
from utils.error_messages import INTEGRATION_NOT_FOUND, UNSUPPORTED_PLATFORM

integrations_router = APIRouter(
    prefix=f"{API_VERSION_V1}/integrations",
    tags=["Integrations"],
)


@integrations_router.get(
    "/",
    summary="List All Integrations",
    description="Retrieve all social media platform integrations for the current user.",
    responses={
        200: {"description": "List of integrations retrieved successfully"},
        401: {"description": "Authentication required"},
        500: {"description": "Internal server error"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
async def get_all_integrations(request: Request):
    """Get all connected platform integrations."""
    error_message, data, errors = IntegrationManagement.get_all_integrations()
    if not error_message:
        status_code = 200
    else:
        status_code = 500
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@integrations_router.get(
    "/{integration_uuid}",
    summary="Get Integration by UUID",
    description="Retrieve details of a specific integration by its UUID.",
    responses={
        200: {"description": "Integration details retrieved successfully"},
        401: {"description": "Authentication required"},
        404: {"description": "Integration not found"},
        500: {"description": "Internal server error"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
async def get_integration(request: Request, integration_uuid: str):
    """Get a specific integration by UUID."""
    error_message, data, errors = IntegrationManagement.get_integration_by_uuid(
        integration_uuid
    )
    if not error_message:
        status_code = 200
    elif error_message == INTEGRATION_NOT_FOUND:
        status_code = 404
    else:
        status_code = 500
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@integrations_router.get(
    "/{platform}/oauth",
    summary="Initiate OAuth Flow",
    description="Start the OAuth authorization flow for a social media platform. Redirects user to the platform's authorization page.",
    responses={
        302: {"description": "Redirect to platform OAuth authorization page"},
        400: {"description": "Unsupported platform"},
        401: {"description": "Authentication required"},
        500: {"description": "Internal server error"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
async def get_oauth_url(request: Request, platform: str):
    """Initiate OAuth flow for a social media platform."""
    error_message, data, errors = IntegrationManagement.get_oauth_url(platform, request)
    if not error_message:
        status_code = 200
    elif error_message == UNSUPPORTED_PLATFORM:
        status_code = 400
    else:
        status_code = 500
    if status_code == 200:
        return RedirectResponse(url=data)
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@integrations_router.get(
    "/{platform}/oauth/callback",
    summary="OAuth Callback Handler",
    description="Handle OAuth callback from social media platforms. Exchanges authorization code for access tokens and creates the integration. No authentication required as this is called by the OAuth provider.",
    responses={
        302: {"description": "Redirect to frontend after successful integration"},
        500: {"description": "Failed to complete OAuth flow"},
    },
)
async def handle_oauth_callback(request: Request, platform: str, code: str):
    """Handle OAuth callback and exchange code for tokens."""
    error_message, data, errors = IntegrationManagement.handle_oauth_callback(
        platform, code, request
    )
    status_code = 200 if not error_message else 500
    if status_code == 200:
        return RedirectResponse(url=data)
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@integrations_router.delete(
    "/{integration_uuid}",
    summary="Delete Integration",
    description="Remove a social media platform integration. This performs a soft delete and revokes platform access.",
    responses={
        200: {"description": "Integration deleted successfully"},
        401: {"description": "Authentication required"},
        500: {"description": "Failed to delete integration"},
    },
    openapi_extra={"security": [{"Auth0Bearer": []}]},
)
@require_authentication
async def delete_integration(request: Request, integration_uuid: str):
    """Delete a platform integration."""
    error_message, data, errors = IntegrationManagement.delete_integration(
        integration_uuid
    )
    status_code = 200 if not error_message else 500
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()
