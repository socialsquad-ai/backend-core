from typing import Optional

from fastapi import APIRouter, Query, Request, Response, status

from config.non_env import API_VERSION_V1, META_VERIFY_TOKEN
from controller.util import APIResponseFormat
from logger.logging import LoggerUtil
from usecases.task import process_meta_webhook
from utils.status_codes import RESPONSE_200, RESPONSE_500

webhook_router = APIRouter(
    prefix=f"{API_VERSION_V1}/webhooks",
    tags=["Webhooks"],
)


@webhook_router.get(
    "/meta",
    summary="Meta Webhook Verification",
    description="Handle GET request from Meta for webhook verification during initial setup. Meta sends hub.mode, hub.verify_token, and hub.challenge parameters. Returns the challenge token if verification succeeds.",
    response_model=None,
    responses={
        200: {"description": "Webhook verified successfully, returns challenge token"},
        400: {"description": "Missing required query parameters"},
        403: {"description": "Invalid verification token or mode"},
    },
    openapi_extra={"security": [{"MetaWebhookVerification": []}]},
)
async def verify_webhook(
    hub_mode: Optional[str] = Query(default=None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(default=None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(default=None, alias="hub.challenge"),
):
    """Verify Meta webhook subscription during initial setup."""
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


@webhook_router.post(
    "/meta",
    summary="Receive Meta Webhook Events",
    description="Handle POST requests from Meta for webhook events (comments, reactions, etc.). Events are processed asynchronously via TaskIQ. No authentication required as Meta signs requests.",
    responses={
        200: {"description": "Webhook received and queued for processing"},
        500: {"description": "Failed to process or queue webhook"},
    },
)
async def accept_meta_webhook(request: Request):
    """Receive and process Meta webhook events asynchronously."""
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
