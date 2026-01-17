from typing import Dict

from config.non_env import Platform
from logger.logging import LoggerUtil
from server.pg_broker import broker
from usecases.webhook_management import WebhookManagement
from utils.platform_service import PlatformService


@broker.task
async def process_meta_comment_change(webhook_data: Dict):
    """Process a comment change event from Meta webhook."""
    await WebhookManagement.handle_incoming_comment(
        webhook_id=webhook_data["id"],
        comment_data=webhook_data,
        platform=Platform.INSTAGRAM,
        platform_user_id=webhook_data["platform_user_id"],
        post_id=webhook_data["media"]["id"],
        comment_id=webhook_data["id"],
        parent_comment_id=webhook_data.get("parent_id", None),
        author_id=webhook_data["from"]["id"],
        author_username=webhook_data["from"]["username"],
        comment=webhook_data["text"],
    )


@broker.task
async def process_meta_message_change(webhook_data: Dict):
    """Process a message change event from Meta webhook."""
    # This task will be called for each message event in the webhook.
    await WebhookManagement.handle_incoming_message(
        webhook_id=webhook_data["message"]["mid"],
        message_data=webhook_data,
        platform=Platform.INSTAGRAM,
        platform_user_id=webhook_data["recipient"]["id"],
        sender_id=webhook_data["sender"]["id"],
        message=webhook_data["message"]["text"],
    )


@broker.task
async def send_dm_task(platform: str, recipient_id: str, message: str, access_token: str):
    """Sends a direct message using the platform service."""
    await PlatformService.send_direct_message(platform, recipient_id, message, access_token)


@broker.task
async def reply_to_comment_task(platform: str, comment_id: str, message: str, access_token: str):
    """Replies to a comment using the platform service."""
    await PlatformService.reply_to_comment(platform, comment_id, message, access_token)


async def process_meta_webhook(webhook_data: Dict):
    """
    Process incoming instagram webhook from Meta.
    This function now handles both 'comments' and 'messages'.
    """
    if webhook_data.get("object") != "instagram":
        LoggerUtil.create_info_log("Ignore non-instagram webhook from meta")
        return "Ignore non-instagram webhook from meta"

    entries = webhook_data.get("entry", [])
    for entry in entries:
        # Handle comment changes
        changes = entry.get("changes", [])
        for change in changes:
            if change.get("field") == "comments":
                data = change["value"]
                data["platform_user_id"] = entry["id"]
                LoggerUtil.create_info_log(f"Enqueuing comment change task for platform_user_id {data['platform_user_id']}")
                await process_meta_comment_change.kiq(data)

        # Handle direct messages
        messaging = entry.get("messaging", [])
        for message_event in messaging:
            if message_event.get("message") and message_event["message"].get("text"):
                # We only process text messages for now
                LoggerUtil.create_info_log(f"Enqueuing message change task for recipient {message_event['recipient']['id']}")
                await process_meta_message_change.kiq(message_event)
