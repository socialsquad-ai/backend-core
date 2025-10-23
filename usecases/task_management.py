from logger.logging import LoggerUtil
from server.pg_broker import broker
from usecases.webhook_management import WebhookManagement
from typing import Dict
from config.non_env import PLATFORM_INSTAGRAM


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
            LoggerUtil.create_info_log(
                f"Enqueuing comment change task for id {entry['id']}"
            )
            await process_meta_comment_change.kiq(data)


@broker.task
async def process_meta_comment_change(webhook_data: Dict):
    await WebhookManagement.handle_incoming_comment(
        webhook_id=webhook_data["id"],
        comment_data=webhook_data,
        platform=PLATFORM_INSTAGRAM,
        post_id=webhook_data["media"]["id"],
        comment_id=webhook_data["id"],
        parent_comment_id=webhook_data["parent_id"],
        author_id=webhook_data["from"]["id"],
        author_username=webhook_data["from"]["username"],
        comment=webhook_data["text"],
    )
