"""
Unit tests for controller/webhook_controller.py

Tests cover all endpoint handlers including:
- verify_webhook
- accept_meta_webhook
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Response

from controller.webhook_controller import accept_meta_webhook, verify_webhook


class TestVerifyWebhook:
    """Test cases for verify_webhook endpoint"""

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.META_VERIFY_TOKEN", "test_verify_token")
    async def test_verify_webhook_success(self, mock_logger):
        """Test successful webhook verification"""
        # Act
        result = await verify_webhook(hub_mode="subscribe", hub_verify_token="test_verify_token", hub_challenge="challenge_123")

        # Assert
        assert isinstance(result, Response)
        assert result.body == b"challenge_123"
        assert result.media_type == "text/plain"
        mock_logger.create_info_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    async def test_verify_webhook_missing_mode(self, mock_logger):
        """Test webhook verification with missing hub_mode"""
        # Act
        result = await verify_webhook(hub_mode=None, hub_verify_token="test_token", hub_challenge="challenge_123")

        # Assert
        assert isinstance(result, Response)
        assert result.status_code == 400
        mock_logger.create_error_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    async def test_verify_webhook_missing_token(self, mock_logger):
        """Test webhook verification with missing verify_token"""
        # Act
        result = await verify_webhook(hub_mode="subscribe", hub_verify_token=None, hub_challenge="challenge_123")

        # Assert
        assert result.status_code == 400

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    async def test_verify_webhook_missing_challenge(self, mock_logger):
        """Test webhook verification with missing challenge"""
        # Act
        result = await verify_webhook(hub_mode="subscribe", hub_verify_token="test_token", hub_challenge=None)

        # Assert
        assert result.status_code == 400

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.META_VERIFY_TOKEN", "correct_token")
    async def test_verify_webhook_invalid_token(self, mock_logger):
        """Test webhook verification with invalid token"""
        # Act
        result = await verify_webhook(hub_mode="subscribe", hub_verify_token="wrong_token", hub_challenge="challenge_123")

        # Assert
        assert result.status_code == 403
        mock_logger.create_error_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.META_VERIFY_TOKEN", "test_token")
    async def test_verify_webhook_invalid_mode(self, mock_logger):
        """Test webhook verification with invalid mode"""
        # Act
        result = await verify_webhook(hub_mode="unsubscribe", hub_verify_token="test_token", hub_challenge="challenge_123")

        # Assert
        assert result.status_code == 403
        mock_logger.create_error_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.META_VERIFY_TOKEN", "test_token")
    async def test_verify_webhook_logs_challenge(self, mock_logger):
        """Test that successful verification logs the challenge"""
        # Act
        await verify_webhook(hub_mode="subscribe", hub_verify_token="test_token", hub_challenge="my_challenge")

        # Assert
        # Check that the challenge was logged
        calls = [str(call) for call in mock_logger.create_info_log.call_args_list]
        assert any("my_challenge" in str(call) for call in calls)


class TestAcceptMetaWebhook:
    """Test cases for accept_meta_webhook endpoint"""

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.process_meta_webhook")
    @patch("controller.webhook_controller.APIResponseFormat")
    async def test_accept_meta_webhook_success(self, mock_response_format, mock_process_webhook, mock_logger):
        """Test successful webhook acceptance"""
        # Arrange
        mock_request = AsyncMock()
        mock_request.json.return_value = {"object": "instagram", "entry": []}

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status": "success"}
        mock_response_format.return_value = mock_response_instance

        mock_process_webhook.return_value = None

        # Act
        result = await accept_meta_webhook(mock_request)

        # Assert
        assert result == {"status": "success"}
        mock_process_webhook.assert_called_once()
        mock_logger.create_info_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.process_meta_webhook")
    @patch("controller.webhook_controller.APIResponseFormat")
    async def test_accept_meta_webhook_logs_data(self, mock_response_format, mock_process_webhook, mock_logger):
        """Test that webhook data is logged"""
        # Arrange
        webhook_data = {"object": "instagram", "entry": [{"id": "123"}]}

        mock_request = AsyncMock()
        mock_request.json.return_value = webhook_data

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {}
        mock_response_format.return_value = mock_response_instance

        # Act
        await accept_meta_webhook(mock_request)

        # Assert
        mock_logger.create_info_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.process_meta_webhook")
    @patch("controller.webhook_controller.APIResponseFormat")
    async def test_accept_meta_webhook_calls_process_webhook(self, mock_response_format, mock_process_webhook, mock_logger):
        """Test that process_meta_webhook is called with webhook data"""
        # Arrange
        webhook_data = {"object": "instagram", "entry": [{"id": "entry_123"}]}

        mock_request = AsyncMock()
        mock_request.json.return_value = webhook_data

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {}
        mock_response_format.return_value = mock_response_instance

        # Act
        await accept_meta_webhook(mock_request)

        # Assert
        mock_process_webhook.assert_called_once_with(webhook_data)

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.process_meta_webhook")
    @patch("controller.webhook_controller.APIResponseFormat")
    async def test_accept_meta_webhook_returns_200_on_success(self, mock_response_format, mock_process_webhook, mock_logger):
        """Test that success returns 200 status code"""
        # Arrange
        mock_request = AsyncMock()
        mock_request.json.return_value = {"object": "instagram", "entry": []}

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await accept_meta_webhook(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200
        assert call_kwargs["message"] == "Webhook received successfully"
        assert call_kwargs["errors"] is None

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.process_meta_webhook")
    @patch("controller.webhook_controller.APIResponseFormat")
    async def test_accept_meta_webhook_handles_exception(self, mock_response_format, mock_process_webhook, mock_logger):
        """Test webhook endpoint handles exceptions"""
        # Arrange
        mock_request = AsyncMock()
        mock_request.json.return_value = {"object": "instagram", "entry": []}

        mock_process_webhook.side_effect = Exception("Processing error")

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"error": "failed"}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await accept_meta_webhook(mock_request)

        # Assert
        assert result == {"error": "failed"}
        mock_logger.create_error_log.assert_called_once()

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.process_meta_webhook")
    @patch("controller.webhook_controller.APIResponseFormat")
    async def test_accept_meta_webhook_returns_500_on_error(self, mock_response_format, mock_process_webhook, mock_logger):
        """Test that error returns 500 status code"""
        # Arrange
        mock_request = AsyncMock()
        mock_request.json.return_value = {"object": "instagram", "entry": []}

        mock_process_webhook.side_effect = Exception("Error")

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await accept_meta_webhook(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500
        assert call_kwargs["message"] == "Failed to process webhook"

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.process_meta_webhook")
    @patch("controller.webhook_controller.APIResponseFormat")
    async def test_accept_meta_webhook_includes_error_in_response(self, mock_response_format, mock_process_webhook, mock_logger):
        """Test that error is included in response errors array"""
        # Arrange
        mock_request = AsyncMock()
        mock_request.json.return_value = {"object": "instagram", "entry": []}

        error_message = "Database connection failed"
        mock_process_webhook.side_effect = Exception(error_message)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await accept_meta_webhook(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["errors"] == [error_message]

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.process_meta_webhook")
    @patch("controller.webhook_controller.APIResponseFormat")
    async def test_accept_meta_webhook_returns_webhook_data_on_success(self, mock_response_format, mock_process_webhook, mock_logger):
        """Test that webhook data is returned in response"""
        # Arrange
        webhook_data = {"object": "instagram", "entry": [{"id": "123"}]}

        mock_request = AsyncMock()
        mock_request.json.return_value = webhook_data

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await accept_meta_webhook(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["data"] == webhook_data

    @pytest.mark.asyncio
    @patch("controller.webhook_controller.LoggerUtil")
    @patch("controller.webhook_controller.process_meta_webhook")
    @patch("controller.webhook_controller.APIResponseFormat")
    async def test_accept_meta_webhook_returns_webhook_data_on_error(self, mock_response_format, mock_process_webhook, mock_logger):
        """Test that webhook data is returned even on error"""
        # Arrange
        webhook_data = {"object": "instagram", "entry": [{"id": "456"}]}

        mock_request = AsyncMock()
        mock_request.json.return_value = webhook_data

        mock_process_webhook.side_effect = Exception("Error")

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await accept_meta_webhook(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["data"] == webhook_data
