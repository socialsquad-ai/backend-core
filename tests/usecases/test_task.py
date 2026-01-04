"""
Unit tests for usecases/task.py

Tests cover all functions including:
- process_meta_comment_change
- process_meta_webhook
"""

from unittest.mock import AsyncMock, patch

import pytest

from usecases.task import process_meta_comment_change, process_meta_webhook


class TestProcessMetaCommentChange:
    """Test cases for process_meta_comment_change task"""

    @pytest.mark.asyncio
    @patch("usecases.task.WebhookManagement.handle_incoming_comment")
    async def test_process_meta_comment_change_success(self, mock_handle_comment):
        """Test processing comment change with complete data"""
        # Arrange
        mock_handle_comment.return_value = {"status": "completed"}

        webhook_data = {"id": "comment_123", "platform_user_id": "user_123", "media": {"id": "post_123"}, "from": {"id": "author_123", "username": "test_user"}, "text": "Great post!", "parent_id": None}

        # Act
        await process_meta_comment_change(webhook_data)

        # Assert
        mock_handle_comment.assert_called_once()
        call_kwargs = mock_handle_comment.call_args[1]
        assert call_kwargs["webhook_id"] == "comment_123"
        assert call_kwargs["platform"] == "instagram"
        assert call_kwargs["platform_user_id"] == "user_123"
        assert call_kwargs["post_id"] == "post_123"
        assert call_kwargs["comment_id"] == "comment_123"
        assert call_kwargs["parent_comment_id"] is None
        assert call_kwargs["author_id"] == "author_123"
        assert call_kwargs["author_username"] == "test_user"
        assert call_kwargs["comment"] == "Great post!"

    @pytest.mark.asyncio
    @patch("usecases.task.WebhookManagement.handle_incoming_comment")
    async def test_process_meta_comment_change_with_parent_id(self, mock_handle_comment):
        """Test processing comment change with parent_id (reply to comment)"""
        # Arrange
        mock_handle_comment.return_value = {"status": "completed"}

        webhook_data = {"id": "reply_123", "platform_user_id": "user_123", "media": {"id": "post_123"}, "from": {"id": "author_456", "username": "another_user"}, "text": "Thanks!", "parent_id": "parent_comment_123"}

        # Act
        await process_meta_comment_change(webhook_data)

        # Assert
        call_kwargs = mock_handle_comment.call_args[1]
        assert call_kwargs["parent_comment_id"] == "parent_comment_123"

    @pytest.mark.asyncio
    @patch("usecases.task.WebhookManagement.handle_incoming_comment")
    async def test_process_meta_comment_change_passes_comment_data(self, mock_handle_comment):
        """Test that full comment_data is passed to handler"""
        # Arrange
        mock_handle_comment.return_value = {"status": "completed"}

        webhook_data = {"id": "comment_789", "platform_user_id": "user_789", "media": {"id": "post_789"}, "from": {"id": "author_789", "username": "user789"}, "text": "Nice!", "created_at": "2024-01-01T12:00:00Z"}

        # Act
        await process_meta_comment_change(webhook_data)

        # Assert
        call_kwargs = mock_handle_comment.call_args[1]
        assert call_kwargs["comment_data"] == webhook_data

    @pytest.mark.asyncio
    @patch("usecases.task.WebhookManagement.handle_incoming_comment")
    async def test_process_meta_comment_change_uses_instagram_platform(self, mock_handle_comment):
        """Test that platform is always set to instagram"""
        # Arrange
        mock_handle_comment.return_value = {"status": "completed"}

        webhook_data = {"id": "comment_123", "platform_user_id": "user_123", "media": {"id": "post_123"}, "from": {"id": "author_123", "username": "test"}, "text": "Test"}

        # Act
        await process_meta_comment_change(webhook_data)

        # Assert
        call_kwargs = mock_handle_comment.call_args[1]
        assert call_kwargs["platform"] == "instagram"


class TestProcessMetaWebhook:
    """Test cases for process_meta_webhook function"""

    @pytest.mark.asyncio
    @patch("usecases.task.LoggerUtil")
    async def test_process_meta_webhook_ignores_non_instagram(self, mock_logger):
        """Test that non-instagram webhooks are ignored"""
        # Arrange
        webhook_data = {"object": "facebook", "entry": []}

        # Act
        result = await process_meta_webhook(webhook_data)

        # Assert
        assert result == "Ignore non-instagram webhook from meta"
        mock_logger.create_info_log.assert_called_once_with("Ignore non-instagram webhook from meta")

    @pytest.mark.asyncio
    @patch("usecases.task.LoggerUtil")
    @patch("usecases.task.process_meta_comment_change")
    async def test_process_meta_webhook_ignores_non_comment_changes(self, mock_process_comment, mock_logger):
        """Test that non-comment field changes are ignored"""
        # Arrange
        webhook_data = {"object": "instagram", "entry": [{"id": "user_123", "changes": [{"field": "likes", "value": {"like_id": "like_123"}}]}]}

        # Act
        await process_meta_webhook(webhook_data)

        # Assert
        mock_logger.create_info_log.assert_called_with("Ignore non-comment webhook from meta")
        mock_process_comment.kiq.assert_not_called()

    @pytest.mark.asyncio
    @patch("usecases.task.LoggerUtil")
    @patch("usecases.task.process_meta_comment_change")
    async def test_process_meta_webhook_processes_comment_changes(self, mock_process_comment, mock_logger):
        """Test processing comment changes"""
        # Arrange
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {"object": "instagram", "entry": [{"id": "platform_user_123", "changes": [{"field": "comments", "value": {"id": "comment_123", "text": "Great post!"}}]}]}

        # Act
        await process_meta_webhook(webhook_data)

        # Assert
        mock_process_comment.kiq.assert_called_once()
        call_args = mock_process_comment.kiq.call_args[0][0]
        assert call_args["platform_user_id"] == "platform_user_123"
        assert call_args["id"] == "comment_123"

    @pytest.mark.asyncio
    @patch("usecases.task.LoggerUtil")
    @patch("usecases.task.process_meta_comment_change")
    async def test_process_meta_webhook_injects_platform_user_id(self, mock_process_comment, mock_logger):
        """Test that platform_user_id is injected into data"""
        # Arrange
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {"object": "instagram", "entry": [{"id": "entry_platform_user_456", "changes": [{"field": "comments", "value": {"id": "comment_456", "text": "Nice!"}}]}]}

        # Act
        await process_meta_webhook(webhook_data)

        # Assert
        call_args = mock_process_comment.kiq.call_args[0][0]
        assert call_args["platform_user_id"] == "entry_platform_user_456"

    @pytest.mark.asyncio
    @patch("usecases.task.LoggerUtil")
    @patch("usecases.task.process_meta_comment_change")
    async def test_process_meta_webhook_multiple_entries(self, mock_process_comment, mock_logger):
        """Test processing multiple entries"""
        # Arrange
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {
            "object": "instagram",
            "entry": [
                {"id": "user_1", "changes": [{"field": "comments", "value": {"id": "comment_1", "text": "Comment 1"}}]},
                {"id": "user_2", "changes": [{"field": "comments", "value": {"id": "comment_2", "text": "Comment 2"}}]},
            ],
        }

        # Act
        await process_meta_webhook(webhook_data)

        # Assert
        assert mock_process_comment.kiq.call_count == 2

    @pytest.mark.asyncio
    @patch("usecases.task.LoggerUtil")
    @patch("usecases.task.process_meta_comment_change")
    async def test_process_meta_webhook_multiple_changes_per_entry(self, mock_process_comment, mock_logger):
        """Test processing multiple changes in one entry"""
        # Arrange
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {
            "object": "instagram",
            "entry": [{"id": "user_1", "changes": [{"field": "comments", "value": {"id": "comment_1", "text": "Comment 1"}}, {"field": "comments", "value": {"id": "comment_2", "text": "Comment 2"}}]}],
        }

        # Act
        await process_meta_webhook(webhook_data)

        # Assert
        assert mock_process_comment.kiq.call_count == 2

    @pytest.mark.asyncio
    @patch("usecases.task.LoggerUtil")
    @patch("usecases.task.process_meta_comment_change")
    async def test_process_meta_webhook_logs_enqueue_message(self, mock_process_comment, mock_logger):
        """Test that enqueue message is logged"""
        # Arrange
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {"object": "instagram", "entry": [{"id": "user_xyz", "changes": [{"field": "comments", "value": {"id": "comment_xyz", "text": "Test"}}]}]}

        # Act
        await process_meta_webhook(webhook_data)

        # Assert
        # Check that log was called with platform_user_id
        calls = [str(call) for call in mock_logger.create_info_log.call_args_list]
        assert any("user_xyz" in str(call) for call in calls)

    @pytest.mark.asyncio
    @patch("usecases.task.LoggerUtil")
    @patch("usecases.task.process_meta_comment_change")
    async def test_process_meta_webhook_mixed_field_types(self, mock_process_comment, mock_logger):
        """Test processing entry with mixed field types"""
        # Arrange
        mock_process_comment.kiq = AsyncMock()

        webhook_data = {
            "object": "instagram",
            "entry": [
                {
                    "id": "user_1",
                    "changes": [{"field": "likes", "value": {"like_id": "like_1"}}, {"field": "comments", "value": {"id": "comment_1", "text": "Good"}}, {"field": "shares", "value": {"share_id": "share_1"}}],
                }
            ],
        }

        # Act
        await process_meta_webhook(webhook_data)

        # Assert
        # Only the comment change should be enqueued
        assert mock_process_comment.kiq.call_count == 1

    @pytest.mark.asyncio
    @patch("usecases.task.LoggerUtil")
    async def test_process_meta_webhook_empty_entries(self, mock_logger):
        """Test processing webhook with empty entries"""
        # Arrange
        webhook_data = {"object": "instagram", "entry": []}

        # Act
        result = await process_meta_webhook(webhook_data)

        # Assert
        # Should not raise an error, just process nothing
        assert result is None
