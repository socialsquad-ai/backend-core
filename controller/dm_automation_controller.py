from fastapi import APIRouter, Request

from config.non_env import API_VERSION_V1
from controller.cerberus import dm_automation_rule_schema, update_dm_automation_rule_schema
from controller.util import APIResponseFormat
from decorators.common import validate_json_payload
from decorators.user import require_authentication
from usecases.dm_automation_management import DmAutomationManagement
from utils.contextvar import get_context_user, get_request_json_post_payload
from utils.exceptions import CustomBadRequest, ResourceNotFound, CustomUnauthorized
from utils.status_codes import RESPONSE_200, RESPONSE_201, RESPONSE_400, RESPONSE_403, RESPONSE_404

dm_automation_router = APIRouter(
    prefix=f"{API_VERSION_V1}",
    tags=["DM Automations"],
)


@dm_automation_router.post(
    "/integrations/{integration_uuid}/dm-automations",
    summary="Create DM Automation Rule for an Integration",
    description="Create a new DM automation rule for an integration, triggered by direct messages ('dm').",
    status_code=RESPONSE_201,
)
@require_authentication
@validate_json_payload(dm_automation_rule_schema)
async def create_integration_dm_rule(request: Request, integration_uuid: str):
    user = get_context_user()
    payload = get_request_json_post_payload()

    try:
        if payload.get("trigger_type") != "dm":
            raise CustomBadRequest("This endpoint only supports 'dm' trigger type.")

        rule = DmAutomationManagement.create_dm_automation_rule(user, payload, integration_uuid=integration_uuid)
        return APIResponseFormat(status_code=RESPONSE_201, message="Rule created successfully.", data=rule).get_json()
    except (ResourceNotFound, CustomBadRequest) as e:
        return APIResponseFormat(status_code=RESPONSE_400, message=str(e)).get_json()
    except CustomUnauthorized as e:
        return APIResponseFormat(status_code=RESPONSE_403, message=str(e)).get_json()


@dm_automation_router.get(
    "/integrations/{integration_uuid}/dm-automations",
    summary="Get DM Automation Rules for an Integration",
    description="Retrieve all active DM automation rules for a specific integration that are triggered by direct messages.",
)
@require_authentication
async def get_integration_dm_rules(request: Request, integration_uuid: str):
    user = get_context_user()
    try:
        rules = DmAutomationManagement.get_dm_automation_rules_for_integration(user, integration_uuid)
        return APIResponseFormat(status_code=RESPONSE_200, message="Rules retrieved successfully.", data=rules).get_json()
    except ResourceNotFound as e:
        return APIResponseFormat(status_code=RESPONSE_404, message=str(e)).get_json()
    except CustomUnauthorized as e:
        return APIResponseFormat(status_code=RESPONSE_403, message=str(e)).get_json()


@dm_automation_router.post(
    "/posts/{post_id}/dm-automations",
    summary="Create DM Automation Rule for a Post",
    description="Create a new DM automation rule for a specific post, triggered by comments.",
    status_code=RESPONSE_201,
)
@require_authentication
@validate_json_payload(dm_automation_rule_schema)
async def create_post_dm_rule(request: Request, post_id: str):
    user = get_context_user()
    payload = get_request_json_post_payload()

    try:
        if payload.get("trigger_type") != "comment":
            raise CustomBadRequest("This endpoint only supports 'comment' trigger type.")
        payload["post_id"] = post_id

        rule = DmAutomationManagement.create_dm_automation_rule(user, payload)
        return APIResponseFormat(status_code=RESPONSE_201, message="Rule created successfully.", data=rule).get_json()
    except (ResourceNotFound, CustomBadRequest) as e:
        return APIResponseFormat(status_code=RESPONSE_400, message=str(e)).get_json()
    except CustomUnauthorized as e:
        return APIResponseFormat(status_code=RESPONSE_403, message=str(e)).get_json()


@dm_automation_router.get(
    "/posts/{post_id}/dm-automations",
    summary="Get DM Automation Rules for a Post",
    description="Retrieve all active DM automation rules for a specific post.",
)
@require_authentication
async def get_post_dm_rules(request: Request, post_id: str):
    user = get_context_user()
    try:
        rules = DmAutomationManagement.get_dm_automation_rules_for_post(user, post_id)
        return APIResponseFormat(status_code=RESPONSE_200, message="Rules retrieved successfully.", data=rules).get_json()
    except ResourceNotFound as e:
        return APIResponseFormat(status_code=RESPONSE_404, message=str(e)).get_json()
    except CustomUnauthorized as e:
        return APIResponseFormat(status_code=RESPONSE_403, message=str(e)).get_json()


@dm_automation_router.put(
    "/dm-automations/{rule_uuid}",
    summary="Update a DM Automation Rule",
    description="Update the settings of an existing DM automation rule.",
)
@require_authentication
@validate_json_payload(update_dm_automation_rule_schema)
async def update_dm_rule(request: Request, rule_uuid: str):
    user = get_context_user()
    payload = get_request_json_post_payload()
    try:
        rule = DmAutomationManagement.update_dm_automation_rule(user, rule_uuid, payload)
        return APIResponseFormat(status_code=RESPONSE_200, message="Rule updated successfully.", data=rule).get_json()
    except (ResourceNotFound, CustomBadRequest) as e:
        return APIResponseFormat(status_code=RESPONSE_400, message=str(e)).get_json()
    except CustomUnauthorized as e:
        return APIResponseFormat(status_code=RESPONSE_403, message=str(e)).get_json()


@dm_automation_router.delete(
    "/dm-automations/{rule_uuid}",
    summary="Delete a DM Automation Rule",
    description="Delete an existing DM automation rule (soft delete).",
)
@require_authentication
async def delete_dm_rule(request: Request, rule_uuid: str):
    user = get_context_user()
    try:
        DmAutomationManagement.delete_dm_automation_rule(user, rule_uuid)
        return APIResponseFormat(status_code=RESPONSE_200, message="Rule deleted successfully.").get_json()
    except ResourceNotFound as e:
        return APIResponseFormat(status_code=RESPONSE_404, message=str(e)).get_json()
    except CustomUnauthorized as e:
        return APIResponseFormat(status_code=RESPONSE_403, message=str(e)).get_json()
