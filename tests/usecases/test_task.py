from unittest.mock import AsyncMock, patch

import pytest

from usecases.task import process_meta_comment_change, process_meta_webhook


class TestProcessMetaCommentChange:
    @patch("usecases.task.WebhookManagement.handle_incoming_comment")
    @pytest.mark.asyncio
    async def test_process_meta_comment_change_calls_webhook_management(self, mock_handle_comment):
        mock_handle_comment.return_value = AsyncMock()

        webhook_data = {
            "id": "comment_123",
            "platform_user_id": "user_456",
            "media": {"id": "post_789"},
            "from": {"id": "author_111", "username": "john_doe"},
            "text": "Great post!",
        }

        await process_meta_comment_change(webhook_data)

        mock_handle_comment.assert_called_once_with(
            webhook_id="comment_123",
            comment_data=webhook_data,
            platform="instagram",
            platform_user_id="user_456",
            post_id="post_789",
            comment_id="comment_123",
            parent_comment_id=None,
            author_id="author_111",
            author_username="john_doe",
            comment="Great post!",
        )

    @patch("usecases.task.WebhookManagement.handle_incoming_comment")
    @pytest.mark.asyncio
    async def test_process_meta_comment_change_with_parent_id(self, mock_handle_comment):
        mock_handle_comment.return_value = AsyncMock()

        webhook_data = {
            "id": "reply_123",
            "platform_user_id": "user_456",
            "media": {"id": "post_789"},
            "parent_id": "parent_comment_111",
            "from": {"id": "author_222", "username": "jane_doe"},
            "text": "Thanks!",
        }

        await process_meta_comment_change(webhook_data)

        call_kwargs = mock_handle_comment.call_args.kwargs
        assert call_kwargs["parent_comment_id"] == "parent_comment_111"


class TestProcessMetaWebhook:
    @patch("usecases.task.LoggerUtil.create_info_log")
    @pytest.mark.asyncio
    async def test_process_meta_webhook_ignores_non_instagram(self, mock_log):
        webhook_data = {"object": "facebook", "entry": []}

        result = await process_meta_webhook(webhook_data)

        assert result == "Ignore non-instagram webhook from meta"
        mock_log.assert_called_with("Ignore non-instagram webhook from meta")

    @patch("usecases.task.process_meta_comment_change")
    @patch("usecases.task.LoggerUtil.create_info_log")
    @pytest.mark.asyncio
    async def test_process_meta_webhook_processes_comment_change(self, mock_log, mock_process_comment):
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {
            "object": "instagram",
            "entry": [
                {
                    "id": "platform_user_123",
                    "changes": [
                        {
                            "field": "comments",
                            "value": {
                                "id": "comment_456",
                                "media": {"id": "post_789"},
                                "from": {"id": "author_111", "username": "user1"},
                                "text": "Nice!",
                            },
                        }
                    ],
                }
            ],
        }

        await process_meta_webhook(webhook_data)

        expected_data = {
            "id": "comment_456",
            "media": {"id": "post_789"},
            "from": {"id": "author_111", "username": "user1"},
            "text": "Nice!",
            "platform_user_id": "platform_user_123",
        }
        mock_process_comment.kiq.assert_called_once_with(expected_data)

    @patch("usecases.task.process_meta_comment_change")
    @patch("usecases.task.LoggerUtil.create_info_log")
    @pytest.mark.asyncio
    async def test_process_meta_webhook_ignores_non_comment_field(self, mock_log, mock_process_comment):
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {
            "object": "instagram",
            "entry": [
                {
                    "id": "platform_user_123",
                    "changes": [
                        {"field": "likes", "value": {"count": 5}},
                        {"field": "shares", "value": {"count": 2}},
                    ],
                }
            ],
        }

        await process_meta_webhook(webhook_data)

        mock_process_comment.kiq.assert_not_called()
        assert any("Ignore non-comment webhook from meta" in str(call) for call in mock_log.call_args_list)

    @patch("usecases.task.process_meta_comment_change")
    @patch("usecases.task.LoggerUtil.create_info_log")
    @pytest.mark.asyncio
    async def test_process_meta_webhook_processes_multiple_entries(self, mock_log, mock_process_comment):
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {
            "object": "instagram",
            "entry": [
                {
                    "id": "user_1",
                    "changes": [{"field": "comments", "value": {"id": "comment_1", "text": "First"}}],
                },
                {
                    "id": "user_2",
                    "changes": [{"field": "comments", "value": {"id": "comment_2", "text": "Second"}}],
                },
            ],
        }

        await process_meta_webhook(webhook_data)

        assert mock_process_comment.kiq.call_count == 2

    @patch("usecases.task.process_meta_comment_change")
    @patch("usecases.task.LoggerUtil.create_info_log")
    @pytest.mark.asyncio
    async def test_process_meta_webhook_injects_platform_user_id(self, mock_log, mock_process_comment):
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {
            "object": "instagram",
            "entry": [
                {
                    "id": "injected_platform_id",
                    "changes": [{"field": "comments", "value": {"id": "comment_1", "text": "Test"}}],
                }
            ],
        }

        await process_meta_webhook(webhook_data)

        called_data = mock_process_comment.kiq.call_args[0][0]
        assert called_data["platform_user_id"] == "injected_platform_id"
