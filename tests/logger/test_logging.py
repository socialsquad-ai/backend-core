from unittest.mock import call, patch

from logger.logging import LoggerUtil


class TestLoggerUtilCreateInfoLog:
    """Test cases for LoggerUtil.create_info_log method"""

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_info_log_with_normal_message(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api-123",
            "thread_id": "test-thread-456",
        }
        message = "Test info message"

        # Act
        LoggerUtil.create_info_log(message)

        # Assert
        mock_get_metadata.assert_called_once()
        mock_logger.bind.assert_called_once_with(api_id="test-api-123", thread_id="test-thread-456")
        mock_logger.bind.return_value.info.assert_called_once_with(message)

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_info_log_truncates_long_message(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        long_message = "x" * 6000  # Message longer than 5000 characters

        # Act
        LoggerUtil.create_info_log(long_message)

        # Assert
        # Should be truncated to 5000 characters
        called_message = mock_logger.bind.return_value.info.call_args[0][0]
        assert len(called_message) == 5000

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_info_log_with_empty_message(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = ""

        # Act
        LoggerUtil.create_info_log(message)

        # Assert
        mock_logger.bind.return_value.info.assert_called_once_with("")

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_info_log_with_special_characters(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = "Test message with special chars: @#$%^&*()!"

        # Act
        LoggerUtil.create_info_log(message)

        # Assert
        mock_logger.bind.return_value.info.assert_called_once_with(message)

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_info_log_with_newlines(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = "Line 1\nLine 2\nLine 3"

        # Act
        LoggerUtil.create_info_log(message)

        # Assert
        mock_logger.bind.return_value.info.assert_called_once_with(message)

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_info_log_with_unicode_characters(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = "Unicode test: 你好 🌟 مرحبا"

        # Act
        LoggerUtil.create_info_log(message)

        # Assert
        mock_logger.bind.return_value.info.assert_called_once_with(message)

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_info_log_with_exactly_5000_chars(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = "x" * 5000

        # Act
        LoggerUtil.create_info_log(message)

        # Assert
        called_message = mock_logger.bind.return_value.info.call_args[0][0]
        assert len(called_message) == 5000

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_info_log_with_empty_metadata(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {"api_id": "", "thread_id": ""}
        message = "Test message"

        # Act
        LoggerUtil.create_info_log(message)

        # Assert
        mock_logger.bind.assert_called_once_with(api_id="", thread_id="")
        mock_logger.bind.return_value.info.assert_called_once_with(message)


class TestLoggerUtilCreateErrorLog:
    """Test cases for LoggerUtil.create_error_log method"""

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_error_log_with_normal_message(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api-789",
            "thread_id": "test-thread-012",
        }
        message = "Test error message"

        # Act
        LoggerUtil.create_error_log(message)

        # Assert
        mock_get_metadata.assert_called_once()
        mock_logger.bind.assert_called_once_with(api_id="test-api-789", thread_id="test-thread-012")
        mock_logger.bind.return_value.error.assert_called_once_with(message)

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_error_log_truncates_long_message(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        long_message = "e" * 7000  # Message longer than 5000 characters

        # Act
        LoggerUtil.create_error_log(long_message)

        # Assert
        # Should be truncated to 5000 characters
        called_message = mock_logger.bind.return_value.error.call_args[0][0]
        assert len(called_message) == 5000

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_error_log_with_exception_details(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = "Error occurred: ValueError: Invalid input"

        # Act
        LoggerUtil.create_error_log(message)

        # Assert
        mock_logger.bind.return_value.error.assert_called_once_with(message)

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_error_log_with_empty_message(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = ""

        # Act
        LoggerUtil.create_error_log(message)

        # Assert
        mock_logger.bind.return_value.error.assert_called_once_with("")

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_error_log_with_stack_trace(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = "Error:\nTraceback (most recent call last):\n  File test.py, line 10"

        # Act
        LoggerUtil.create_error_log(message)

        # Assert
        mock_logger.bind.return_value.error.assert_called_once_with(message)

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_error_log_with_formatted_string(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        error_code = 500
        error_type = "InternalServerError"
        message = f"Error {error_code}: {error_type}"

        # Act
        LoggerUtil.create_error_log(message)

        # Assert
        mock_logger.bind.return_value.error.assert_called_once_with("Error 500: InternalServerError")

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_error_log_with_json_data(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = 'Error processing: {"error": "invalid", "code": 400}'

        # Act
        LoggerUtil.create_error_log(message)

        # Assert
        mock_logger.bind.return_value.error.assert_called_once_with(message)

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_create_error_log_with_exactly_5000_chars(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }
        message = "e" * 5000

        # Act
        LoggerUtil.create_error_log(message)

        # Assert
        called_message = mock_logger.bind.return_value.error.call_args[0][0]
        assert len(called_message) == 5000


class TestLoggerUtilMultipleCalls:
    """Test cases for multiple logging calls"""

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_multiple_info_logs_in_sequence(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }

        # Act
        LoggerUtil.create_info_log("First message")
        LoggerUtil.create_info_log("Second message")
        LoggerUtil.create_info_log("Third message")

        # Assert
        assert mock_get_metadata.call_count == 3
        assert mock_logger.bind.call_count == 3
        assert mock_logger.bind.return_value.info.call_count == 3

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_mixed_info_and_error_logs(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.return_value = {
            "api_id": "test-api",
            "thread_id": "test-thread",
        }

        # Act
        LoggerUtil.create_info_log("Info message")
        LoggerUtil.create_error_log("Error message")
        LoggerUtil.create_info_log("Another info")

        # Assert
        assert mock_logger.bind.return_value.info.call_count == 2
        assert mock_logger.bind.return_value.error.call_count == 1

    @patch("logger.logging.logger")
    @patch("logger.logging.get_request_metadata")
    def test_logs_with_changing_metadata(self, mock_get_metadata, mock_logger):
        # Arrange
        mock_get_metadata.side_effect = [
            {"api_id": "api-1", "thread_id": "thread-1"},
            {"api_id": "api-2", "thread_id": "thread-2"},
        ]

        # Act
        LoggerUtil.create_info_log("First request")
        LoggerUtil.create_info_log("Second request")

        # Assert
        calls = mock_logger.bind.call_args_list
        assert calls[0] == call(api_id="api-1", thread_id="thread-1")
        assert calls[1] == call(api_id="api-2", thread_id="thread-2")
