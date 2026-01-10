import datetime
import uuid
from unittest.mock import patch

from utils.util import (
    is_local_env,
    is_valid_uuid_v4,
    parse_timestamp,
    sanitize_string_input,
)


class TestIsLocalEnv:
    """Test cases for is_local_env function"""

    @patch("utils.util.APP_ENVIRONMENT", "local")
    def test_is_local_env_returns_true_when_local(self):
        # Arrange & Act
        result = is_local_env()

        # Assert
        assert result is True

    @patch("utils.util.APP_ENVIRONMENT", "production")
    def test_is_local_env_returns_false_when_production(self):
        # Arrange & Act
        result = is_local_env()

        # Assert
        assert result is False

    @patch("utils.util.APP_ENVIRONMENT", "staging")
    def test_is_local_env_returns_false_when_staging(self):
        # Arrange & Act
        result = is_local_env()

        # Assert
        assert result is False

    @patch("utils.util.APP_ENVIRONMENT", "testing")
    def test_is_local_env_returns_false_when_testing(self):
        # Arrange & Act
        result = is_local_env()

        # Assert
        assert result is False

    @patch("utils.util.APP_ENVIRONMENT", "")
    def test_is_local_env_returns_false_when_empty_string(self):
        # Arrange & Act
        result = is_local_env()

        # Assert
        assert result is False


class TestSanitizeStringInput:
    """Test cases for sanitize_string_input function"""

    def test_sanitize_string_input_removes_extra_spaces(self):
        # Arrange
        input_string = "hello    world"

        # Act
        result = sanitize_string_input(input_string)

        # Assert
        assert result == "hello world"

    def test_sanitize_string_input_removes_newlines(self):
        # Arrange
        input_string = "hello\nworld\n"

        # Act
        result = sanitize_string_input(input_string)

        # Assert
        assert result == "hello world"

    def test_sanitize_string_input_removes_tabs(self):
        # Arrange
        input_string = "hello\t\tworld"

        # Act
        result = sanitize_string_input(input_string)

        # Assert
        assert result == "hello world"

    def test_sanitize_string_input_removes_mixed_whitespace(self):
        # Arrange
        input_string = "  hello  \n\t  world  \n  "

        # Act
        result = sanitize_string_input(input_string)

        # Assert
        assert result == "hello world"

    def test_sanitize_string_input_with_single_word(self):
        # Arrange
        input_string = "  hello  "

        # Act
        result = sanitize_string_input(input_string)

        # Assert
        assert result == "hello"

    def test_sanitize_string_input_with_empty_string(self):
        # Arrange
        input_string = ""

        # Act
        result = sanitize_string_input(input_string)

        # Assert
        assert result == ""

    def test_sanitize_string_input_with_whitespace_only(self):
        # Arrange
        input_string = "   \n\t  "

        # Act
        result = sanitize_string_input(input_string)

        # Assert
        assert result == ""

    def test_sanitize_string_input_with_non_string_returns_empty(self):
        # Arrange
        input_value = 123

        # Act
        result = sanitize_string_input(input_value)

        # Assert
        assert result == ""

    def test_sanitize_string_input_with_none_returns_empty(self):
        # Arrange
        input_value = None

        # Act
        result = sanitize_string_input(input_value)

        # Assert
        assert result == ""

    def test_sanitize_string_input_with_list_returns_empty(self):
        # Arrange
        input_value = ["hello", "world"]

        # Act
        result = sanitize_string_input(input_value)

        # Assert
        assert result == ""

    def test_sanitize_string_input_preserves_normal_text(self):
        # Arrange
        input_string = "Hello World Test"

        # Act
        result = sanitize_string_input(input_string)

        # Assert
        assert result == "Hello World Test"


class TestIsValidUuidV4:
    """Test cases for is_valid_uuid_v4 function"""

    def test_is_valid_uuid_v4_returns_true_for_valid_uuid(self):
        # Arrange
        valid_uuid = str(uuid.uuid4())

        # Act
        result = is_valid_uuid_v4(valid_uuid)

        # Assert
        assert result is True

    def test_is_valid_uuid_v4_returns_false_for_invalid_uuid(self):
        # Arrange
        invalid_uuid = "not-a-uuid"

        # Act
        result = is_valid_uuid_v4(invalid_uuid)

        # Assert
        assert result is False

    def test_is_valid_uuid_v4_returns_false_for_empty_string(self):
        # Arrange
        invalid_uuid = ""

        # Act
        result = is_valid_uuid_v4(invalid_uuid)

        # Assert
        assert result is False

    def test_is_valid_uuid_v4_returns_false_for_uuid_v1(self):
        # Arrange - UUID v1 format
        invalid_uuid = str(uuid.uuid1())

        # Act
        result = is_valid_uuid_v4(invalid_uuid)

        # Assert
        assert result is False

    def test_is_valid_uuid_v4_returns_false_for_malformed_uuid(self):
        # Arrange
        invalid_uuid = "123e4567-e89b-12d3-a456-426614174000-extra"

        # Act
        result = is_valid_uuid_v4(invalid_uuid)

        # Assert
        assert result is False

    def test_is_valid_uuid_v4_returns_false_for_numeric_string(self):
        # Arrange
        invalid_uuid = "123456789"

        # Act
        result = is_valid_uuid_v4(invalid_uuid)

        # Assert
        assert result is False

    def test_is_valid_uuid_v4_returns_true_for_uppercase_uuid(self):
        # Arrange
        valid_uuid = str(uuid.uuid4()).upper()

        # Act
        result = is_valid_uuid_v4(valid_uuid)

        # Assert
        assert result is True


class TestParseTimestamp:
    """Test cases for parse_timestamp function"""

    def test_parse_timestamp_with_iso_format_utc(self):
        # Arrange
        timestamp_str = "2025-11-09T11:19:46.759112+00:00"

        # Act
        result = parse_timestamp(timestamp_str)

        # Assert
        assert result is not None
        assert isinstance(result, datetime.datetime)
        assert result.year == 2025
        assert result.month == 11
        assert result.day == 9
        assert result.hour == 11
        assert result.minute == 19
        assert result.second == 46
        assert result.microsecond == 759112

    def test_parse_timestamp_with_z_suffix(self):
        # Arrange
        timestamp_str = "2025-11-09T11:19:46Z"

        # Act
        result = parse_timestamp(timestamp_str)

        # Assert
        assert result is not None
        assert isinstance(result, datetime.datetime)
        assert result.year == 2025
        assert result.month == 11
        assert result.day == 9
        assert result.hour == 11
        assert result.minute == 19
        assert result.second == 46

    def test_parse_timestamp_with_datetime_object(self):
        # Arrange
        dt = datetime.datetime(2025, 11, 9, 11, 19, 46)

        # Act
        result = parse_timestamp(dt)

        # Assert
        assert result is dt
        assert result.year == 2025
        assert result.month == 11
        assert result.day == 9

    def test_parse_timestamp_with_none_returns_none(self):
        # Arrange
        timestamp_value = None

        # Act
        result = parse_timestamp(timestamp_value)

        # Assert
        assert result is None

    def test_parse_timestamp_with_invalid_string_returns_none(self):
        # Arrange
        invalid_timestamp = "not-a-timestamp"

        # Act
        result = parse_timestamp(invalid_timestamp)

        # Assert
        assert result is None

    def test_parse_timestamp_with_empty_string_returns_none(self):
        # Arrange
        invalid_timestamp = ""

        # Act
        result = parse_timestamp(invalid_timestamp)

        # Assert
        assert result is None

    def test_parse_timestamp_with_malformed_date_returns_none(self):
        # Arrange
        invalid_timestamp = "2025-13-40T25:61:61Z"

        # Act
        result = parse_timestamp(invalid_timestamp)

        # Assert
        assert result is None

    def test_parse_timestamp_with_numeric_value_returns_none(self):
        # Arrange
        invalid_timestamp = 123456789

        # Act
        result = parse_timestamp(invalid_timestamp)

        # Assert
        assert result is None

    def test_parse_timestamp_with_iso_format_no_microseconds(self):
        # Arrange
        timestamp_str = "2025-11-09T11:19:46+00:00"

        # Act
        result = parse_timestamp(timestamp_str)

        # Assert
        assert result is not None
        assert isinstance(result, datetime.datetime)
        assert result.year == 2025
        assert result.month == 11
        assert result.day == 9
        assert result.hour == 11
        assert result.minute == 19
        assert result.second == 46
        assert result.microsecond == 0

    def test_parse_timestamp_with_different_timezone(self):
        # Arrange
        timestamp_str = "2025-11-09T11:19:46+05:30"

        # Act
        result = parse_timestamp(timestamp_str)

        # Assert
        assert result is not None
        assert isinstance(result, datetime.datetime)
        assert result.year == 2025
        assert result.month == 11
        assert result.day == 9
