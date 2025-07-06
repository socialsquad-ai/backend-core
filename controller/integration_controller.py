from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from controller.util import APIResponseFormat
from usecases.integration_management import IntegrationManagement
from config.non_env import API_VERSION_V1
from fastapi import APIRouter
from decorators.user import require_authentication

integrations_router = APIRouter(
    prefix=f"{API_VERSION_V1}/integrations", tags=["integrations"]
)  # For different usecases, create different bases


@integrations_router.get("/")
async def get_all_integrations(request: Request):
    error_message, data, errors = IntegrationManagement.get_all_integrations(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@integrations_router.get("/{integration_uuid}")
async def get_integration(request: Request, integration_uuid: str):
    error_message, data, errors = IntegrationManagement.get_integration_by_uuid(
        request, integration_uuid
    )
    status_code = 200 if not error_message else 500
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
    status_code = 200 if not error_message else 500
    if status_code == 200:
        return RedirectResponse(url=data)
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@integrations_router.get("/{platform}/oauth/callback")
@require_authentication
async def handle_oauth_callback(request: Request, platform: str, code: str):
    error_message, data, errors = IntegrationManagement.handle_oauth_callback(
        platform, code, request
    )
    status_code = 200 if not error_message else 500
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
        request, integration_uuid
    )
    status_code = 200 if not error_message else 500
    return APIResponseFormat(
        status_code=status_code,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()
