from logger.logging import LoggerUtil
from server.pg_broker import broker
from usecases.webhook_management import (WebhookManagement)
from typing import Dict
from config.non_env import PLATFORM_INSTAGRAM


@broker.task
async def process_meta_comment_change(webhook_data: Dict):
    """Process a comment change event from Meta webhook."""
    await WebhookManagement.handle_incoming_comment(
        webhook_id=webhook_data["id"],
        comment_data=webhook_data,
        platform=PLATFORM_INSTAGRAM,
        platform_user_id=webhook_data["platform_user_id"],
        post_id=webhook_data["media"]["id"],
        comment_id=webhook_data["id"],
        parent_comment_id=webhook_data.get("parent_id", None),
        author_id=webhook_data["from"]["id"],
        author_username=webhook_data["from"]["username"],
        comment=webhook_data["text"],
    )


async def process_meta_webhook(webhook_data: Dict):
    """
    Process incoming instagram webhook from Meta.
    """
    if webhook_data["object"] != "instagram":
        LoggerUtil.create_info_log("Ignore non-instagram webhook from meta")
        return "Ignore non-instagram webhook from meta"

    entries = webhook_data["entry"]
    for entry in entries:
        changes = entry["changes"]
        for change in changes:
            if change["field"] != "comments":
                LoggerUtil.create_info_log("Ignore non-comment webhook from meta")
                continue
            data = change["value"]
            # Inject platform_user_id from entry into the data
            data["platform_user_id"] = entry["id"]
            LoggerUtil.create_info_log(
                f"Enqueuing comment change task for platform_user_id {data['platform_user_id']}"
            )
            await process_meta_comment_change.kiq(data)
