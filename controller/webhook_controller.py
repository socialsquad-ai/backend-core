from fastapi import APIRouter, Query, Request, Response, status
from typing import Optional
from config.non_env import API_VERSION_V1, META_VERIFY_TOKEN
from controller.util import APIResponseFormat
from logger.logging import LoggerUtil
from utils.status_codes import RESPONSE_200, RESPONSE_500
from usecases.task_management import process_meta_webhook

webhook_router = APIRouter(
    prefix=f"{API_VERSION_V1}/webhooks",
    tags=["webhook"],
)


@webhook_router.get("/meta", response_model=None)
async def verify_webhook(
    hub_mode: Optional[str] = Query(default=None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(default=None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(default=None, alias="hub.challenge"),
):
    """
    Handle GET request from Meta for webhook verification.
    This endpoint is called during the initial webhook setup.
    """
    if hub_mode is None or hub_verify_token is None or hub_challenge is None:
        LoggerUtil.create_error_log("Webhook verification failed: Missing parameters")
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    if hub_verify_token != META_VERIFY_TOKEN:
        LoggerUtil.create_error_log("Webhook verification failed: Invalid token")
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    if hub_mode != "subscribe":
        LoggerUtil.create_error_log("Webhook verification failed: Invalid mode")
        return Response(status_code=status.HTTP_403_FORBIDDEN)

    LoggerUtil.create_info_log(f"Webhook verified with challenge: {hub_challenge}")
    return Response(content=hub_challenge, media_type="text/plain")


@webhook_router.post("/meta")
async def accept_meta_webhook(request: Request):
    """
    Handle POST requests from Meta for webhook events.
    """
    webhook_data = await request.json()
    try:
        # Log the incoming webhook data
        LoggerUtil.create_info_log(f"Received webhook: {webhook_data}")

        # Process the webhook and enqueue tasks for comment changes
        await process_meta_webhook(webhook_data)

        return APIResponseFormat(
            status_code=RESPONSE_200,
            message="Webhook received successfully",
            data=webhook_data,
            errors=None,
        ).get_json()
    except Exception as e:
        # Return error if task enqueuing fails, this will make the provider retry the webhook
        LoggerUtil.create_error_log(f"Error processing webhook: {str(e)}")
        return APIResponseFormat(
            status_code=RESPONSE_500,
            message="Failed to process webhook",
            data=webhook_data,
            errors=[str(e)],
        ).get_json()
