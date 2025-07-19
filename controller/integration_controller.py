from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from controller.util import APIResponseFormat
from usecases.integration_management import IntegrationManagement
from config.non_env import API_VERSION_V1
from fastapi import APIRouter
from decorators.user import require_authentication
from utils.error_messages import INTEGRATION_NOT_FOUND, UNSUPPORTED_PLATFORM

integrations_router = APIRouter(
    prefix=f"{API_VERSION_V1}/integrations", tags=["integrations"]
)  # For different usecases, create different bases


@integrations_router.get("/")
@require_authentication
async def get_all_integrations(request: Request):
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


@integrations_router.get("/{integration_uuid}")
@require_authentication
async def get_integration(request: Request, integration_uuid: str):
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


@integrations_router.get("/{platform}/oauth")
@require_authentication
async def get_oauth_url(request: Request, platform: str):
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


@integrations_router.get("/{platform}/oauth/callback")
async def handle_oauth_callback(request: Request, platform: str, code: str):
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


@integrations_router.delete("/{integration_uuid}")
@require_authentication
async def delete_integration(request: Request, integration_uuid: str):
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
