from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

from data_adapter.webhook_logs import WebhookLog


class TestWebhookLogCreateWebhookLog:
    @patch.object(WebhookLog, "create")
    def test_create_webhook_log_with_all_params(self, mock_create):
        mock_log = Mock()
        mock_create.return_value = mock_log

        result = WebhookLog.create_webhook_log(webhook_id="webhook_123", integration_id=1, event_type="comment_created", payload={"test": "data"}, post_id=2)

        assert result == mock_log
        mock_create.assert_called_once_with(webhook_id="webhook_123", integration=1, post=2, event_type="comment_created", payload={"test": "data"}, status="pending", retry_count=0)

    @patch.object(WebhookLog, "create")
    def test_create_webhook_log_without_post_id(self, mock_create):
        mock_log = Mock()
        mock_create.return_value = mock_log

        result = WebhookLog.create_webhook_log(webhook_id="webhook_456", integration_id=3, event_type="comment_updated", payload={"data": "test"})

        assert result == mock_log
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["post"] is None


class TestWebhookLogMarkProcessing:
    @patch("data_adapter.webhook_logs.datetime")
    @patch.object(WebhookLog, "save")
    def test_mark_processing_updates_status_and_counts(self, mock_save, mock_datetime):
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = now

        log = WebhookLog()
        log.status = "pending"
        log.retry_count = 0
        log.last_attempt_at = None

        log.mark_processing()

        assert log.status == "processing"
        assert log.retry_count == 1
        assert log.last_attempt_at == now
        mock_save.assert_called_once()


class TestWebhookLogMarkCompleted:
    @patch("data_adapter.webhook_logs.datetime")
    @patch.object(WebhookLog, "save")
    def test_mark_completed_without_result(self, mock_save, mock_datetime):
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = now

        log = WebhookLog()
        log.status = "processing"
        log.processed_at = None

        log.mark_completed()

        assert log.status == "completed"
        assert log.processed_at == now
        mock_save.assert_called_once()

    @patch("data_adapter.webhook_logs.datetime")
    @patch.object(WebhookLog, "save")
    def test_mark_completed_with_result(self, mock_save, mock_datetime):
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = now

        log = WebhookLog()
        log.status = "processing"
        log.processed_at = None

        log.mark_completed(result={"success": True})

        assert log.status == "completed"
        assert log.processed_at == now
        assert log.result == {"success": True}
        mock_save.assert_called_once()


class TestWebhookLogMarkFailed:
    @patch.object(WebhookLog, "save")
    def test_mark_failed_sets_error_message(self, mock_save):
        log = WebhookLog()
        log.status = "processing"
        log.error_message = None

        log.mark_failed("Test error message")

        assert log.status == "failed"
        assert log.error_message == "Test error message"
        mock_save.assert_called_once()

    @patch.object(WebhookLog, "save")
    def test_mark_failed_truncates_long_error_message(self, mock_save):
        log = WebhookLog()
        log.status = "processing"
        log.error_message = None

        long_error = "Error" * 300  # Create a very long error message
        log.mark_failed(long_error)

        assert log.status == "failed"
        assert len(log.error_message) == 1000
        mock_save.assert_called_once()


class TestWebhookLogCanRetry:
    def test_can_retry_returns_true_when_retries_available(self):
        log = WebhookLog()
        log.retry_count = 2
        log.status = "failed"

        result = log.can_retry(max_retries=3)

        assert result is True

    def test_can_retry_returns_false_when_max_retries_reached(self):
        log = WebhookLog()
        log.retry_count = 3
        log.status = "failed"

        result = log.can_retry(max_retries=3)

        assert result is False

    def test_can_retry_returns_false_when_completed(self):
        log = WebhookLog()
        log.retry_count = 1
        log.status = "completed"

        result = log.can_retry(max_retries=3)

        assert result is False

    def test_can_retry_with_custom_max_retries(self):
        log = WebhookLog()
        log.retry_count = 4
        log.status = "failed"

        result = log.can_retry(max_retries=5)

        assert result is True


class TestWebhookLogGetPendingWebhooks:
    @patch.object(WebhookLog, "select")
    def test_get_pending_webhooks_with_default_batch_size(self, mock_select):
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = []

        WebhookLog.get_pending_webhooks()

        mock_select.assert_called_once()
        mock_query.limit.assert_called_once_with(10)

    @patch.object(WebhookLog, "select")
    def test_get_pending_webhooks_with_custom_batch_size(self, mock_select):
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = []

        WebhookLog.get_pending_webhooks(batch_size=25)

        mock_query.limit.assert_called_once_with(25)
