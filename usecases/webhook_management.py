from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from config.non_env import (
    CREATE_REPLY_AGENT,
    DELETE_COMMENT_AGENT,
    DETECT_INTENT_AGENT,
    IGNORE_COMMENT_AGENT,
)
from data_adapter.dm_automations import DmAutomationRule
from data_adapter.integration import Integration
from data_adapter.personas import Persona
from data_adapter.posts import Post
from data_adapter.user import User
from data_adapter.webhook_logs import WebhookLog
from logger.logging import LoggerUtil
from usecases.ssq_agent import SSQAgent
from utils.platform_service import PlatformService


class WebhookManagement:
    @classmethod
    async def handle_incoming_comment(
        cls,
        webhook_id: str,
        comment_data: Dict,
        platform: str,
        platform_user_id: str,
        post_id: str,
        comment_id: str,
        parent_comment_id: Optional[str],
        author_id: str,
        author_username: str,
        comment: str,
    ) -> Dict:
        """
        Handle an incoming comment according to the defined flow with retry and webhook logging.
        """
        LoggerUtil.create_info_log(f"Starting processing for webhook {webhook_id}, comment {comment_id}")

        integration = Integration.get_by_platform_user_id(platform_user_id, platform)
        if not integration:
            LoggerUtil.create_error_log(f"No integration found for platform_user_id {platform_user_id} on platform {platform}")
            return {"status": "error", "reason": f"No integration found for platform_user_id {platform_user_id}"}

        user = integration.user
        user_id = user.id

        webhook_log = await cls._log_webhook(
            webhook_id=webhook_id,
            event_type="comment_created",
            payload=comment_data,
            integration=integration,
            post_id=post_id,
        )

        try:
            post, user, integration = await cls._validate_post_and_user(post_id, platform, user_id)
            if not all([post, user, integration]):
                return {"status": "skipped", "reason": "Invalid post, account, or integration"}

            if author_id == integration.platform_user_id:
                return {"status": "skipped", "reason": "Comment from user's account"}

            if not post.engagement_enabled:
                return {"status": "skipped", "reason": "Post engagement not enabled"}

            if not await cls._is_within_engagement_period(comment_data, post):
                return {"status": "skipped", "reason": "Outside engagement period or time window"}

            if await cls._is_offensive_content(comment, platform):
                await cls._handle_offensive_comment(comment_id, platform, integration)
                webhook_log.mark_completed({"action": "comment_deleted"})
                return {"status": "completed", "action": "comment_deleted"}

            if await cls._should_ignore_comment(comment, platform, post.ignore_instructions):
                webhook_log.mark_completed({"action": "comment_ignored"})
                return {"status": "skipped", "action": "comment_ignored"}

            persona = cls._get_active_persona(user)
            if not persona:
                webhook_log.mark_failed("No active persona")
                return {"status": "error", "reason": "No active persona"}

            reply = await cls._generate_reply(comment, platform, persona)
            if not reply:
                raise ValueError("Failed to generate reply")

            result = await cls._handle_reply(user=user, comment_id=comment_id, reply=reply, integration=integration)

            await cls._handle_comment_to_dm_rules(post, comment, comment_id, author_id, integration)

            webhook_log.mark_completed(result)
            return {"status": "completed", **result}

        except Exception as e:
            error_msg = f"Error processing comment {comment_id}: {str(e)}"
            LoggerUtil.create_error_log(error_msg)
            webhook_log.mark_failed(error_msg)
            raise

    @classmethod
    async def handle_incoming_message(
        cls, webhook_id: str, message_data: Dict, platform: str, platform_user_id: str, sender_id: str, message: str
    ):
        from usecases.task import send_dm_task

        LoggerUtil.create_info_log(f"Starting processing for message webhook {webhook_id}")

        integration = Integration.get_by_platform_user_id(platform_user_id, platform)
        if not integration:
            LoggerUtil.create_error_log(f"No integration found for platform_user_id {platform_user_id}")
            return

        await cls._log_webhook(
            webhook_id=webhook_id,
            event_type="message_created",
            payload=message_data,
            integration=integration,
        )

        if sender_id == integration.platform_user_id:
            LoggerUtil.create_info_log("Ignoring message from page itself.")
            return

        rules = DmAutomationRule.get_by_integration_and_trigger(integration.id, "dm")
        for rule in rules:
            if rule.trigger_text.lower() in message.lower():
                LoggerUtil.create_info_log(f"Found matching DM rule {rule.id}. Triggering DM.")
                await send_dm_task.kiq(
                    platform=platform,
                    recipient_id=sender_id,
                    message=rule.dm_response,
                    access_token=integration.access_token,
                )
                break

    @classmethod
    async def _handle_comment_to_dm_rules(
        cls, post: Post, comment_text: str, comment_id: str, author_id: str, integration: Integration
    ):
        from usecases.task import reply_to_comment_task, send_dm_task

        rules = DmAutomationRule.get_by_post_id(post.post_id)
        for rule in rules:
            matched = False
            if rule.match_type == "EXACT_TEXT":
                if rule.trigger_text.lower() in comment_text.lower():
                    matched = True
            elif rule.match_type == "AI_INTENT":
                intent_agent = SSQAgent(
                    DETECT_INTENT_AGENT,
                    integration.platform,
                    f"Does the following comment: '{comment_text}' mean '{rule.trigger_text}'? Respond with only 'yes' or 'no'.",
                )
                response = await intent_agent.generate_response(comment_text)
                if response and "yes" in response.lower():
                    matched = True

            if matched:
                LoggerUtil.create_info_log(f"Found matching comment-to-DM rule {rule.id}.")
                await send_dm_task.kiq(
                    platform=integration.platform,
                    recipient_id=author_id,
                    message=rule.dm_response,
                    access_token=integration.access_token,
                )
                if rule.comment_reply:
                    await reply_to_comment_task.kiq(
                        platform=integration.platform,
                        comment_id=comment_id,
                        message=rule.comment_reply,
                        access_token=integration.access_token,
                    )
                break

    @classmethod
    def _get_active_persona(cls, user: User) -> Optional[Persona]:
        try:
            return Persona.select().where(Persona.user == user).order_by(Persona.updated_at.desc()).first()
        except Exception as e:
            LoggerUtil.create_error_log(f"Error fetching active persona: {str(e)}")
            return None

    @classmethod
    async def _log_webhook(
        cls, webhook_id: str, event_type: str, payload: Dict, integration: Integration, post_id: str = None
    ) -> WebhookLog:
        post = None
        if post_id:
            post, _ = Post.get_or_create(post_id=post_id, defaults={"integration": integration})

        webhook_log, created = WebhookLog.get_or_create(
            webhook_id=webhook_id,
            defaults={"integration": integration, "post": post, "event_type": event_type, "payload": payload},
        )

        if not created and webhook_log.status == "completed":
            LoggerUtil.create_info_log(f"Webhook {webhook_id} already processed")
            return webhook_log

        webhook_log.mark_processing()
        return webhook_log

    @classmethod
    async def _validate_post_and_user(
        cls, post_id: str, platform: str, user_id: str
    ) -> Tuple[Optional[Post], Optional[User], Optional[Integration]]:
        try:
            user = User.get_by_id(user_id)
            if not user or user.is_deleted:
                return None, None, None

            post = Post.get_by_post_id(post_id).first()
            if not post or not post.engagement_enabled:
                return None, None, None

            integration = (
                Integration.select().join(User, on=(User.id == Integration.user)).where((User.id == user_id) & (Integration.platform == platform)).first()
            )
            if not integration:
                return None, None, None

            return post, user, integration
        except Exception as e:
            LoggerUtil.create_error_log(f"Error validating post and user: {str(e)}")
            return None, None, None

    @classmethod
    async def _is_within_engagement_period(cls, comment_data: Dict, post: Post) -> bool:
        return True

    @classmethod
    async def _is_offensive_content(cls, text: str, platform: str) -> bool:
        try:
            delete_agent = SSQAgent(DELETE_COMMENT_AGENT, platform, "")
            return await delete_agent.generate_response(text)
        except Exception as e:
            LoggerUtil.create_error_log(f"Error checking offensive content: {str(e)}")
            return False

    @classmethod
    async def _should_ignore_comment(cls, text: str, platform: str, ignore_instructions: str = "") -> bool:
        try:
            ignore_agent = SSQAgent(IGNORE_COMMENT_AGENT, platform, ignore_instructions)
            return await ignore_agent.generate_response(text)
        except Exception as e:
            LoggerUtil.create_error_log(f"Error checking if comment should be ignored: {str(e)}")
            return False

    @classmethod
    async def _generate_reply(cls, comment_text: str, platform: str, persona: Persona) -> Optional[str]:
        try:
            reply_agent = SSQAgent(CREATE_REPLY_AGENT, platform, persona.instructions)
            return await reply_agent.generate_response(comment_text)
        except Exception as e:
            LoggerUtil.create_error_log(f"Error generating reply: {str(e)}")
            return None

    @classmethod
    async def _handle_offensive_comment(cls, comment_id: str, platform: str, integration: Integration) -> None:
        try:
            await PlatformService.delete_comment(
                platform=platform, comment_id=comment_id, access_token=integration.access_token
            )
        except Exception as e:
            LoggerUtil.create_error_log(f"Error deleting offensive comment {comment_id}: {str(e)}")
            raise

    @classmethod
    async def _handle_reply(cls, user: User, comment_id: str, reply: str, integration: Integration) -> Dict:
        try:
            approval_needed = getattr(user, "approval_needed", False)
            if approval_needed:
                return {"action": "pending_approval", "comment_id": comment_id, "reply": reply, "status": "pending"}

            success = await PlatformService.reply_to_comment(
                platform=integration.platform,
                comment_id=comment_id,
                message=reply,
                access_token=integration.access_token,
            )
            return {
                "action": "reply_posted" if success else "reply_failed",
                "comment_id": comment_id,
                "reply": reply,
                "status": "posted" if success else "failed",
            }
        except Exception as e:
            LoggerUtil.create_error_log(f"Error handling reply: {str(e)}")
            raise
