from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from data_adapter.user import Account, User
from data_adapter.personas import Persona
from data_adapter.integration import Integration
from data_adapter.posts import Post
from data_adapter.webhook_logs import WebhookLog
from usecases.ssq_agent import SSQAgent
from config.non_env import (
    CREATE_REPLY_AGENT,
    DELETE_COMMENT_AGENT,
    IGNORE_COMMENT_AGENT,
)
from logger.logging import LoggerUtil


class WebhookManagement:
    @classmethod
    async def handle_incoming_comment(
        cls,
        webhook_id: str,
        comment_data: Dict,
        platform: str,
        post_id: str,
        comment_id: str,
        parent_comment_id: str,
        author_id: str,
        author_username: str,
        comment: str,
    ) -> Dict:
        """
        Handle an incoming comment according to the defined flow with retry and webhook logging.

        Args:
            webhook_id: Unique ID for the webhook event
            comment_data: Dictionary containing comment details including 'text'
            platform: The social media platform (e.g., 'instagram', 'youtube')
            post_id: The ID of the post where the comment was made
            comment_id: The ID of the comment
            parent_comment_id: The ID of the parent comment
            author_id: The ID of the comment author
            author_username: The username of the comment author
            comment: The comment text

        Returns:
            Dict containing response details or error information
        """
        LoggerUtil.create_info_log(
            f"Starting processing for webhook {webhook_id}, comment {comment_id}"
        )
        account_id = 2
        persona_id = "34d5b364-8c69-4d2f-8d6c-2e57bf564f16"

        # Log the incoming webhook
        webhook_log = await cls._log_webhook(
            webhook_id=webhook_id,
            platform=platform,
            post_id=post_id,
            event_type="comment_created",
            payload=comment_data,
            account_id=account_id,
        )

        try:
            # 1. Check if post is selected for engagement
            post, account, integration = await cls._validate_post_and_account(
                post_id, platform, account_id
            )
            if not all([post, account, integration]):
                return {
                    "status": "skipped",
                    "reason": "Invalid post, account, or integration",
                }

            # 2. Check if comment from user's account -- ignore in that case
            if author_id == integration.platform_user_id:
                return {
                    "status": "skipped",
                    "reason": "Comment from user's account",
                }

            # 3. Check if post is enabled for engagement
            if not post.engagement_enabled:
                return {
                    "status": "skipped",
                    "reason": "Post engagement not enabled",
                }

            # 4. Check if comment is within engagement period and time window
            engagement_period_hours = (
                post.engagement_start_hours - post.engagement_end_hours
            )
            if not await cls._is_within_engagement_period(
                comment_data, post, engagement_period_hours
            ):
                return {
                    "status": "skipped",
                    "reason": "Outside engagement period or time window",
                }

            # 3. Check if comment is offensive/abusive
            if await cls._is_offensive_content(comment_data["text"], platform):
                await cls._handle_offensive_comment(comment_id, platform, integration)
                webhook_log.mark_completed({"action": "comment_deleted"})
                return {"status": "completed", "action": "comment_deleted"}

            # 4. Check if comment should be ignored
            if await cls._should_ignore_comment(
                comment_data["text"], platform, post.ignore_instructions
            ):
                webhook_log.mark_completed({"action": "comment_ignored"})
                return {"status": "skipped", "action": "comment_ignored"}

            # 5. Generate reply using persona
            reply = await cls._generate_reply(
                comment_data["text"], platform, persona_id
            )
            if not reply:
                raise ValueError("Failed to generate reply")

            # 6. Handle reply based on account settings
            result = await cls._handle_reply(
                account=account,
                comment_id=comment_id,
                reply=reply,
                integration=integration,
            )

            webhook_log.mark_completed(result)
            return {"status": "completed", **result}

        except Exception as e:
            error_msg = f"Error processing comment {comment_id}: {str(e)}"
            LoggerUtil.create_error_log(error_msg)
            webhook_log.mark_failed(error_msg)
            raise  # Will be caught by retry decorator

    @classmethod
    async def _log_webhook(
        cls,
        webhook_id: str,
        platform: str,
        post_id: str,
        event_type: str,
        payload: Dict,
        account_id: int,
    ) -> WebhookLog:
        """Log incoming webhook for auditing and retry purposes"""
        integration = (
            Integration.select()
            .join(User, on=(User.id == Integration.user))
            .join(Account, on=(Account.id == User.account))
            .where((Account.id == account_id) & (Integration.platform == platform))
            .first()
        )

        if not integration:
            raise ValueError(
                f"No integration found for platform {platform} and account {account_id}"
            )

        # Get or create post record
        post, _ = Post.get_or_create(
            post_id=post_id,
            defaults={"integration": integration, "engagement_enabled": True},
        )

        # Create or update webhook log
        webhook_log, created = WebhookLog.get_or_create(
            webhook_id=webhook_id,
            defaults={
                "integration": integration,
                "post": post,
                "event_type": event_type,
                "payload": payload,
            },
        )

        if not created and webhook_log.status == "completed":
            LoggerUtil.create_info_log(f"Webhook {webhook_id} already processed")
            return webhook_log

        webhook_log.mark_processing()
        return webhook_log

    @classmethod
    async def _validate_post_and_account(
        cls, post_id: str, platform: str, account_id: str
    ) -> Tuple[Optional[Post], Optional[Account], Optional[Integration]]:
        """Validate post, account and integration"""
        try:
            account = Account.get_by_id(account_id)
            if not account or account.is_deleted:
                LoggerUtil.create_info_log(
                    f"Account {account_id} not found or inactive"
                )
                return None, None, None

            post = Post.get_by_post_id(post_id)
            if not post or not post[0].engagement_enabled:
                LoggerUtil.create_info_log(
                    f"Post {post_id} not found or engagement not enabled"
                )
                return None, None, None

            integration = (
                Integration.select()
                .join(User, on=(User.id == Integration.user))
                .join(Account, on=(Account.id == User.account))
                .where((Account.id == account_id) & (Integration.platform == platform))
            )

            if not integration:
                LoggerUtil.create_info_log(
                    f"No integration found for platform {platform} and account {account_id}"
                )
                return None, None, None

            return post[0], account, integration[0]

        except Exception as e:
            LoggerUtil.create_error_log(f"Error validating post and account: {str(e)}")
            return None, None, None

    @classmethod
    async def _is_within_engagement_period(
        cls, comment_data: Dict, post: Post, engagement_period_hours: int
    ) -> bool:
        """Check if comment is within engagement period and time window"""
        try:
            comment_time = datetime.fromisoformat(
                comment_data.get("created_at", datetime.utcnow().isoformat())
            )
            post_time = datetime.fromisoformat(
                comment_data.get("post_created_at", datetime.utcnow().isoformat())
            )

            # Check engagement period
            if comment_time - post_time > timedelta(hours=engagement_period_hours):
                LoggerUtil.create_info_log(
                    "Comment is outside engagement period: %s > %s hours",
                    comment_time - post_time,
                    engagement_period_hours,
                )
                return False

            # Check time window if enabled
            if post.engagement_start_hours and post.engagement_end_hours:
                comment_time_local = comment_time.time()
                if not (
                    post.engagement_start_hours
                    <= comment_time_local
                    <= post.engagement_end_hours
                ):
                    LoggerUtil.create_info_log(
                        "Comment is outside engagement time window: %s not between %s and %s",
                        comment_time_local,
                        post.engagement_start_hours,
                        post.engagement_end_hours,
                    )
                    return False

            return True

        except Exception as e:
            LoggerUtil.create_error_log(f"Error checking engagement period: {str(e)}")
            return False

    @classmethod
    async def _is_offensive_content(cls, text: str, platform: str) -> bool:
        """Check if content is offensive/abusive"""
        try:
            delete_agent = SSQAgent(DELETE_COMMENT_AGENT, platform, "")
            return await delete_agent.generate_response(text)
        except Exception as e:
            LoggerUtil.create_error_log(f"Error checking offensive content: {str(e)}")
            return False

    @classmethod
    async def _should_ignore_comment(
        cls, text: str, platform: str, ignore_instructions: str = ""
    ) -> bool:
        """Check if comment should be ignored based on content and ignore instructions"""
        try:
            ignore_agent = SSQAgent(IGNORE_COMMENT_AGENT, platform, ignore_instructions)
            return await ignore_agent.generate_response(text)
        except Exception as e:
            LoggerUtil.create_error_log(
                f"Error checking if comment should be ignored: {str(e)}"
            )
            return False

    @classmethod
    async def _generate_reply(
        cls, comment_text: str, platform: str, persona_id: str
    ) -> Optional[str]:
        """Generate a reply using the specified persona"""
        try:
            persona = Persona.get_by_uuid(persona_id).first()
            if not persona:
                raise ValueError(f"Persona {persona_id} not found")

            reply_agent = SSQAgent(CREATE_REPLY_AGENT, platform, persona.instructions)
            return await reply_agent.generate_response(comment_text)

        except Exception as e:
            LoggerUtil.create_error_log(f"Error generating reply: {str(e)}")
            return None

    @classmethod
    async def _handle_offensive_comment(
        cls, comment_id: str, platform: str, integration: Integration
    ) -> None:
        """Handle offensive comment (e.g., delete it)"""
        try:
            LoggerUtil.create_info_log(f"Deleting offensive comment {comment_id}")
            # In a real implementation, call platform API to delete comment
            # await platform_api.delete_comment(
            #     access_token=integration.access_token,
            #     comment_id=comment_id
            # )
        except Exception as e:
            LoggerUtil.create_error_log(
                f"Error deleting offensive comment {comment_id}: {str(e)}"
            )
            raise

    @classmethod
    async def _handle_reply(
        cls,
        account: Account,
        comment_id: str,
        reply: str,
        integration: Integration,
    ) -> Dict:
        """Handle reply based on account settings"""
        try:
            # 7. Check if approval is needed
            if account.approval_needed:
                LoggerUtil.create_info_log(
                    f"Approval needed for reply to comment {comment_id}"
                )
                # In a real implementation, store the pending reply in the database
                # and send notification to admin
                return {
                    "action": "pending_approval",
                    "comment_id": comment_id,
                    "reply": reply,
                    "status": "pending",
                }

            # Post reply directly if no approval needed
            LoggerUtil.create_info_log(f"Posting reply to comment {comment_id}")
            import requests

            requests.post(
                f"https://graph.instagram.com/{comment_id}/replies?message={reply}",
                headers={"Authorization": f"Bearer {integration.access_token}"},
            )

            return {
                "action": "reply_posted",
                "comment_id": comment_id,
                "reply": reply,
                "status": "posted",
            }

        except Exception as e:
            LoggerUtil.create_error_log(f"Error handling reply: {str(e)}")
            raise
