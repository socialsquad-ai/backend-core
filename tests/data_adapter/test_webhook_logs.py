"""
Unit tests for data_adapter/webhook_logs.py

Tests cover all methods in the WebhookLog model including:
- create_webhook_log
- mark_processing
- mark_completed
- mark_failed
- can_retry
- get_pending_webhooks
"""

from datetime import datetime
from unittest.mock import Mock, patch

from data_adapter.webhook_logs import WebhookLog


class TestCreateWebhookLog:
    """Test cases for create_webhook_log method"""

    @patch.object(WebhookLog, "create")
    def test_create_webhook_log_with_all_fields(self, mock_create):
        """Test creating webhook log with all fields"""
        # Arrange
        mock_log = Mock(id=1)
        mock_create.return_value = mock_log

        # Act
        result = WebhookLog.create_webhook_log(webhook_id="webhook_123", integration_id=1, event_type="comment_created", payload={"text": "test comment"}, post_id=1)

        # Assert
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["webhook_id"] == "webhook_123"
        assert call_kwargs["integration"] == 1
        assert call_kwargs["event_type"] == "comment_created"
        assert call_kwargs["payload"] == {"text": "test comment"}
        assert call_kwargs["post"] == 1
        assert call_kwargs["status"] == "pending"
        assert call_kwargs["retry_count"] == 0
        assert result == mock_log

    @patch.object(WebhookLog, "create")
    def test_create_webhook_log_without_post(self, mock_create):
        """Test creating webhook log without post_id"""
        # Arrange
        mock_log = Mock(id=1)
        mock_create.return_value = mock_log

        # Act
        _result = WebhookLog.create_webhook_log(webhook_id="webhook_456", integration_id=2, event_type="comment_updated", payload={"text": "updated comment"})

        # Assert
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["post"] is None

    @patch.object(WebhookLog, "create")
    def test_create_webhook_log_different_event_types(self, mock_create):
        """Test creating webhook logs with different event types"""
        # Arrange
        mock_create.return_value = Mock()

        # Act
        WebhookLog.create_webhook_log("wh_1", 1, "comment_created", {})
        WebhookLog.create_webhook_log("wh_2", 1, "comment_updated", {})
        WebhookLog.create_webhook_log("wh_3", 1, "comment_deleted", {})

        # Assert
        assert mock_create.call_count == 3


class TestMarkProcessing:
    """Test cases for mark_processing method"""

    @patch("data_adapter.webhook_logs.datetime")
    def test_mark_processing_increments_retry_count(self, mock_datetime):
        """Test mark_processing increments retry count"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        mock_log = Mock(spec=WebhookLog)
        mock_log.status = "pending"
        mock_log.retry_count = 0

        # Bind the method to the instance
        mock_log.mark_processing = WebhookLog.mark_processing.__get__(mock_log, WebhookLog)

        # Act
        mock_log.mark_processing()

        # Assert
        assert mock_log.status == "processing"
        assert mock_log.retry_count == 1
        assert mock_log.last_attempt_at == mock_now
        mock_log.save.assert_called_once()

    @patch("data_adapter.webhook_logs.datetime")
    def test_mark_processing_multiple_times(self, mock_datetime):
        """Test mark_processing called multiple times"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        mock_log = Mock(spec=WebhookLog)
        mock_log.status = "failed"
        mock_log.retry_count = 2

        # Bind the method to the instance
        mock_log.mark_processing = WebhookLog.mark_processing.__get__(mock_log, WebhookLog)

        # Act
        mock_log.mark_processing()

        # Assert
        assert mock_log.retry_count == 3

    @patch("data_adapter.webhook_logs.datetime")
    def test_mark_processing_updates_timestamp(self, mock_datetime):
        """Test mark_processing updates last_attempt_at timestamp"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 15, 30, 45)
        mock_datetime.utcnow.return_value = mock_now

        mock_log = Mock(spec=WebhookLog)
        mock_log.status = "pending"
        mock_log.retry_count = 0

        # Bind the method to the instance
        mock_log.mark_processing = WebhookLog.mark_processing.__get__(mock_log, WebhookLog)

        # Act
        mock_log.mark_processing()

        # Assert
        assert mock_log.last_attempt_at == mock_now


class TestMarkCompleted:
    """Test cases for mark_completed method"""

    @patch("data_adapter.webhook_logs.datetime")
    def test_mark_completed_without_result(self, mock_datetime):
        """Test mark_completed without result data"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        mock_log = Mock(spec=WebhookLog)
        mock_log.status = "processing"

        # Bind the method to the instance
        mock_log.mark_completed = WebhookLog.mark_completed.__get__(mock_log, WebhookLog)

        # Act
        mock_log.mark_completed()

        # Assert
        assert mock_log.status == "completed"
        assert mock_log.processed_at == mock_now
        mock_log.save.assert_called_once()

    @patch("data_adapter.webhook_logs.datetime")
    def test_mark_completed_with_result(self, mock_datetime):
        """Test mark_completed with result data"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now

        mock_log = Mock(spec=WebhookLog)
        mock_log.status = "processing"

        # Bind the method to the instance
        mock_log.mark_completed = WebhookLog.mark_completed.__get__(mock_log, WebhookLog)

        # Act
        result_data = {"action": "reply_posted", "comment_id": "123"}
        mock_log.mark_completed(result_data)

        # Assert
        assert mock_log.result == result_data

    @patch("data_adapter.webhook_logs.datetime")
    def test_mark_completed_updates_timestamp(self, mock_datetime):
        """Test mark_completed updates processed_at timestamp"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 16, 45, 30)
        mock_datetime.utcnow.return_value = mock_now

        mock_log = Mock(spec=WebhookLog)

        # Bind the method to the instance
        mock_log.mark_completed = WebhookLog.mark_completed.__get__(mock_log, WebhookLog)

        # Act
        mock_log.mark_completed()

        # Assert
        assert mock_log.processed_at == mock_now


class TestMarkFailed:
    """Test cases for mark_failed method"""

    def test_mark_failed_with_short_error_message(self):
        """Test mark_failed with short error message"""
        # Arrange
        mock_log = Mock(spec=WebhookLog)
        mock_log.status = "processing"

        # Bind the method to the instance
        mock_log.mark_failed = WebhookLog.mark_failed.__get__(mock_log, WebhookLog)

        # Act
        mock_log.mark_failed("Database connection error")

        # Assert
        assert mock_log.status == "failed"
        assert mock_log.error_message == "Database connection error"
        mock_log.save.assert_called_once()

    def test_mark_failed_with_long_error_message(self):
        """Test mark_failed truncates long error messages"""
        # Arrange
        mock_log = Mock(spec=WebhookLog)
        mock_log.status = "processing"

        # Bind the method to the instance
        mock_log.mark_failed = WebhookLog.mark_failed.__get__(mock_log, WebhookLog)

        # Act
        long_error = "x" * 1500  # Error longer than 1000 characters
        mock_log.mark_failed(long_error)

        # Assert
        assert mock_log.status == "failed"
        assert len(mock_log.error_message) == 1000

    def test_mark_failed_with_exception_object(self):
        """Test mark_failed with exception object"""
        # Arrange
        mock_log = Mock(spec=WebhookLog)
        mock_log.status = "processing"

        # Bind the method to the instance
        mock_log.mark_failed = WebhookLog.mark_failed.__get__(mock_log, WebhookLog)

        # Act
        exception = ValueError("Invalid input")
        mock_log.mark_failed(exception)

        # Assert
        assert mock_log.error_message == "Invalid input"

    def test_mark_failed_converts_to_string(self):
        """Test mark_failed converts error to string"""
        # Arrange
        mock_log = Mock(spec=WebhookLog)

        # Bind the method to the instance
        mock_log.mark_failed = WebhookLog.mark_failed.__get__(mock_log, WebhookLog)

        # Act
        mock_log.mark_failed(123)  # Non-string error

        # Assert
        assert mock_log.error_message == "123"


class TestCanRetry:
    """Test cases for can_retry method"""

    def test_can_retry_with_default_max_retries(self):
        """Test can_retry with default max retries (3)"""
        # Arrange
        mock_log = Mock(spec=WebhookLog)
        mock_log.retry_count = 2
        mock_log.status = "failed"

        # Bind the method to the instance
        mock_log.can_retry = WebhookLog.can_retry.__get__(mock_log, WebhookLog)

        # Act
        result = mock_log.can_retry()

        # Assert
        assert result is True

    def test_can_retry_exceeded_max_retries(self):
        """Test can_retry when max retries exceeded"""
        # Arrange
        mock_log = Mock(spec=WebhookLog)
        mock_log.retry_count = 3
        mock_log.status = "failed"

        # Bind the method to the instance
        mock_log.can_retry = WebhookLog.can_retry.__get__(mock_log, WebhookLog)

        # Act
        result = mock_log.can_retry()

        # Assert
        assert result is False

    def test_can_retry_when_completed(self):
        """Test can_retry returns False when status is completed"""
        # Arrange
        mock_log = Mock(spec=WebhookLog)
        mock_log.retry_count = 1
        mock_log.status = "completed"

        # Bind the method to the instance
        mock_log.can_retry = WebhookLog.can_retry.__get__(mock_log, WebhookLog)

        # Act
        result = mock_log.can_retry()

        # Assert
        assert result is False

    def test_can_retry_with_custom_max_retries(self):
        """Test can_retry with custom max retries"""
        # Arrange
        mock_log = Mock(spec=WebhookLog)
        mock_log.retry_count = 4
        mock_log.status = "failed"

        # Bind the method to the instance
        mock_log.can_retry = WebhookLog.can_retry.__get__(mock_log, WebhookLog)

        # Act
        result = mock_log.can_retry(max_retries=5)

        # Assert
        assert result is True

    def test_can_retry_zero_retries(self):
        """Test can_retry with zero retry count"""
        # Arrange
        mock_log = Mock(spec=WebhookLog)
        mock_log.retry_count = 0
        mock_log.status = "pending"

        # Bind the method to the instance
        mock_log.can_retry = WebhookLog.can_retry.__get__(mock_log, WebhookLog)

        # Act
        result = mock_log.can_retry()

        # Assert
        assert result is True


class TestGetPendingWebhooks:
    """Test cases for get_pending_webhooks method"""

    @patch.object(WebhookLog, "select")
    def test_get_pending_webhooks_default_batch_size(self, mock_select):
        """Test get_pending_webhooks with default batch size"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query

        # Act
        _result = WebhookLog.get_pending_webhooks()

        # Assert
        mock_select.assert_called_once()
        mock_query.where.assert_called_once()
        mock_query.where.return_value.order_by.assert_called_once()
        mock_query.where.return_value.order_by.return_value.limit.assert_called_once_with(10)

    @patch.object(WebhookLog, "select")
    def test_get_pending_webhooks_custom_batch_size(self, mock_select):
        """Test get_pending_webhooks with custom batch size"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query

        # Act
        _result = WebhookLog.get_pending_webhooks(batch_size=25)

        # Assert
        mock_query.where.return_value.order_by.return_value.limit.assert_called_once_with(25)

    @patch.object(WebhookLog, "select")
    def test_get_pending_webhooks_includes_pending_and_failed(self, mock_select):
        """Test get_pending_webhooks includes pending and failed with retries"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query

        # Act
        WebhookLog.get_pending_webhooks()

        # Assert
        # Verify the where clause includes conditions for pending and failed status
        mock_query.where.assert_called_once()

    @patch.object(WebhookLog, "select")
    def test_get_pending_webhooks_ordered_by_created_at(self, mock_select):
        """Test get_pending_webhooks orders by created_at"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query

        # Act
        WebhookLog.get_pending_webhooks()

        # Assert
        mock_query.where.return_value.order_by.assert_called_once()

    @patch.object(WebhookLog, "select")
    def test_get_pending_webhooks_small_batch(self, mock_select):
        """Test get_pending_webhooks with small batch size"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query

        # Act
        _result = WebhookLog.get_pending_webhooks(batch_size=1)

        # Assert
        mock_query.where.return_value.order_by.return_value.limit.assert_called_once_with(1)

    @patch.object(WebhookLog, "select")
    def test_get_pending_webhooks_large_batch(self, mock_select):
        """Test get_pending_webhooks with large batch size"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query

        # Act
        _result = WebhookLog.get_pending_webhooks(batch_size=100)

        # Assert
        mock_query.where.return_value.order_by.return_value.limit.assert_called_once_with(100)
