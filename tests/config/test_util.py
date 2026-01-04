"""
Unit tests for config/util.py

Tests cover all methods of the Environment class:
- get_string
- get_int
- get_bool
- get_float
- get_list
- get_dict

Each method is tested for:
- Valid input (environment variable exists with correct value)
- Invalid input (malformed values causing exceptions)
- Default value returns when env var doesn't exist
- Error logging when invalid values are provided
"""

from unittest.mock import patch

from config.non_env import ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE
from config.util import Environment


class TestGetString:
    """Test cases for Environment.get_string method"""

    @patch("os.getenv")
    def test_get_string_with_existing_env_var(self, mock_getenv):
        """Test get_string when environment variable exists"""
        # Arrange
        mock_getenv.return_value = "test_value"

        # Act
        result = Environment.get_string("TEST_CONFIG")

        # Assert
        assert result == "test_value"
        mock_getenv.assert_called_once_with("TEST_CONFIG", "")

    @patch("os.getenv")
    def test_get_string_with_default_value(self, mock_getenv):
        """Test get_string with custom default value"""
        # Arrange
        mock_getenv.return_value = "custom_default"

        # Act
        result = Environment.get_string("MISSING_CONFIG", default="custom_default")

        # Assert
        assert result == "custom_default"
        mock_getenv.assert_called_once_with("MISSING_CONFIG", "custom_default")

    @patch("os.getenv")
    def test_get_string_with_missing_env_var_returns_default(self, mock_getenv):
        """Test get_string returns default when env var doesn't exist"""
        # Arrange
        mock_getenv.return_value = ""

        # Act
        result = Environment.get_string("MISSING_CONFIG")

        # Assert
        assert result == ""
        mock_getenv.assert_called_once_with("MISSING_CONFIG", "")

    @patch("os.getenv")
    def test_get_string_converts_to_string(self, mock_getenv):
        """Test get_string converts value to string"""
        # Arrange
        mock_getenv.return_value = 12345

        # Act
        result = Environment.get_string("TEST_CONFIG")

        # Assert
        assert result == "12345"
        assert isinstance(result, str)

    @patch("os.getenv")
    def test_get_string_with_empty_string(self, mock_getenv):
        """Test get_string with empty string value"""
        # Arrange
        mock_getenv.return_value = ""

        # Act
        result = Environment.get_string("EMPTY_CONFIG")

        # Assert
        assert result == ""


class TestGetInt:
    """Test cases for Environment.get_int method"""

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_int_with_valid_integer(self, mock_getenv, mock_logger):
        """Test get_int with valid integer value"""
        # Arrange
        mock_getenv.return_value = "42"

        # Act
        result = Environment.get_int("TEST_INT")

        # Assert
        assert result == 42
        assert isinstance(result, int)
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_int_with_negative_integer(self, mock_getenv, mock_logger):
        """Test get_int with negative integer value"""
        # Arrange
        mock_getenv.return_value = "-100"

        # Act
        result = Environment.get_int("TEST_INT")

        # Assert
        assert result == -100
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_int_with_default_value(self, mock_getenv, mock_logger):
        """Test get_int with custom default value"""
        # Arrange
        mock_getenv.return_value = "999"

        # Act
        result = Environment.get_int("MISSING_INT", default=999)

        # Assert
        assert result == 999
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_int_with_invalid_value_returns_default(self, mock_getenv, mock_logger):
        """Test get_int returns default when value is invalid"""
        # Arrange
        mock_getenv.return_value = "not_an_integer"

        # Act
        result = Environment.get_int("INVALID_INT", default=10)

        # Assert
        assert result == 10
        expected_error = "{}:{}::Invalid int value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, "not_an_integer", "INVALID_INT")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_int_with_float_string(self, mock_getenv, mock_logger):
        """Test get_int with float string value"""
        # Arrange
        mock_getenv.return_value = "42.5"

        # Act
        result = Environment.get_int("FLOAT_INT")

        # Assert
        # eval("42.5") returns 42.5, then int(42.5) = 42
        assert result == 42
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_int_with_empty_string_returns_default(self, mock_getenv, mock_logger):
        """Test get_int with empty string returns default"""
        # Arrange
        mock_getenv.return_value = ""

        # Act
        result = Environment.get_int("EMPTY_INT", default=5)

        # Assert
        assert result == 5
        expected_error = "{}:{}::Invalid int value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, "", "EMPTY_INT")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_int_logs_error_on_exception(self, mock_getenv, mock_logger):
        """Test get_int logs error when exception occurs"""
        # Arrange
        mock_getenv.return_value = "invalid"

        # Act
        result = Environment.get_int("BAD_INT", default=0)

        # Assert
        assert result == 0
        assert mock_logger.call_count == 1
        error_msg = mock_logger.call_args[0][0]
        assert ALERT_MESSAGE_PREPEND in error_msg
        assert CONFIG_ERROR_LOG_MESSAGE in error_msg
        assert "invalid" in error_msg
        assert "BAD_INT" in error_msg


class TestGetBool:
    """Test cases for Environment.get_bool method"""

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_bool_with_true_value(self, mock_getenv, mock_logger):
        """Test get_bool with True value"""
        # Arrange
        mock_getenv.return_value = "True"

        # Act
        result = Environment.get_bool("TEST_BOOL")

        # Assert
        assert result is True
        assert isinstance(result, bool)
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_bool_with_false_value(self, mock_getenv, mock_logger):
        """Test get_bool with False value"""
        # Arrange
        mock_getenv.return_value = "False"

        # Act
        result = Environment.get_bool("TEST_BOOL")

        # Assert
        assert result is False
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_bool_with_one(self, mock_getenv, mock_logger):
        """Test get_bool with numeric 1 (truthy)"""
        # Arrange
        mock_getenv.return_value = "1"

        # Act
        result = Environment.get_bool("TEST_BOOL")

        # Assert
        assert result is True
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_bool_with_zero(self, mock_getenv, mock_logger):
        """Test get_bool with numeric 0 (falsy)"""
        # Arrange
        mock_getenv.return_value = "0"

        # Act
        result = Environment.get_bool("TEST_BOOL")

        # Assert
        assert result is False
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_bool_with_custom_default(self, mock_getenv, mock_logger):
        """Test get_bool with custom default value"""
        # Arrange
        mock_getenv.return_value = "True"

        # Act
        result = Environment.get_bool("TEST_BOOL", default=True)

        # Assert
        assert result is True
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_bool_with_invalid_value_returns_default(self, mock_getenv, mock_logger):
        """Test get_bool returns default when value is invalid"""
        # Arrange
        mock_getenv.return_value = "not_a_boolean"

        # Act
        result = Environment.get_bool("INVALID_BOOL", default=True)

        # Assert
        assert result is True
        expected_error = "{}:{}::Invalid bool value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, "not_a_boolean", "INVALID_BOOL")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_bool_with_empty_string_returns_default(self, mock_getenv, mock_logger):
        """Test get_bool with empty string returns default"""
        # Arrange
        mock_getenv.return_value = ""

        # Act
        result = Environment.get_bool("EMPTY_BOOL", default=False)

        # Assert
        assert result is False
        expected_error = "{}:{}::Invalid bool value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, "", "EMPTY_BOOL")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_bool_logs_error_on_exception(self, mock_getenv, mock_logger):
        """Test get_bool logs error when exception occurs"""
        # Arrange
        mock_getenv.return_value = "invalid"

        # Act
        result = Environment.get_bool("BAD_BOOL", default=False)

        # Assert
        assert result is False
        assert mock_logger.call_count == 1
        error_msg = mock_logger.call_args[0][0]
        assert ALERT_MESSAGE_PREPEND in error_msg
        assert CONFIG_ERROR_LOG_MESSAGE in error_msg
        assert "invalid" in error_msg
        assert "BAD_BOOL" in error_msg


class TestGetFloat:
    """Test cases for Environment.get_float method"""

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_float_with_valid_float(self, mock_getenv, mock_logger):
        """Test get_float with valid float value"""
        # Arrange
        mock_getenv.return_value = "3.14"

        # Act
        result = Environment.get_float("TEST_FLOAT")

        # Assert
        assert result == 3.14
        assert isinstance(result, float)
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_float_with_integer_value(self, mock_getenv, mock_logger):
        """Test get_float with integer value"""
        # Arrange
        mock_getenv.return_value = "42"

        # Act
        result = Environment.get_float("TEST_FLOAT")

        # Assert
        assert result == 42.0
        assert isinstance(result, float)
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_float_with_negative_float(self, mock_getenv, mock_logger):
        """Test get_float with negative float value"""
        # Arrange
        mock_getenv.return_value = "-99.99"

        # Act
        result = Environment.get_float("TEST_FLOAT")

        # Assert
        assert result == -99.99
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_float_with_scientific_notation(self, mock_getenv, mock_logger):
        """Test get_float with scientific notation"""
        # Arrange
        mock_getenv.return_value = "1.5e2"

        # Act
        result = Environment.get_float("TEST_FLOAT")

        # Assert
        assert result == 150.0
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_float_with_custom_default(self, mock_getenv, mock_logger):
        """Test get_float with custom default value"""
        # Arrange
        mock_getenv.return_value = "2.5"

        # Act
        result = Environment.get_float("TEST_FLOAT", default=2.5)

        # Assert
        assert result == 2.5
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_float_with_invalid_value_returns_default(self, mock_getenv, mock_logger):
        """Test get_float returns default when value is invalid"""
        # Arrange
        mock_getenv.return_value = "not_a_float"

        # Act
        result = Environment.get_float("INVALID_FLOAT", default=1.0)

        # Assert
        assert result == 1.0
        expected_error = "{}:{}::Invalid float value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, "not_a_float", "INVALID_FLOAT")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_float_with_empty_string_returns_default(self, mock_getenv, mock_logger):
        """Test get_float with empty string returns default"""
        # Arrange
        mock_getenv.return_value = ""

        # Act
        result = Environment.get_float("EMPTY_FLOAT", default=0.0)

        # Assert
        assert result == 0.0
        expected_error = "{}:{}::Invalid float value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, "", "EMPTY_FLOAT")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_float_logs_error_on_exception(self, mock_getenv, mock_logger):
        """Test get_float logs error when exception occurs"""
        # Arrange
        mock_getenv.return_value = "invalid"

        # Act
        result = Environment.get_float("BAD_FLOAT", default=0.0)

        # Assert
        assert result == 0.0
        assert mock_logger.call_count == 1
        error_msg = mock_logger.call_args[0][0]
        assert ALERT_MESSAGE_PREPEND in error_msg
        assert CONFIG_ERROR_LOG_MESSAGE in error_msg
        assert "invalid" in error_msg
        assert "BAD_FLOAT" in error_msg

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_float_with_zero(self, mock_getenv, mock_logger):
        """Test get_float with zero value"""
        # Arrange
        mock_getenv.return_value = "0"

        # Act
        result = Environment.get_float("ZERO_FLOAT")

        # Assert
        assert result == 0.0
        mock_logger.assert_not_called()


class TestGetList:
    """Test cases for Environment.get_list method"""

    @patch("os.getenv")
    def test_get_list_with_comma_separated_values(self, mock_getenv):
        """Test get_list with comma-separated values"""
        # Arrange
        mock_getenv.return_value = "value1,value2,value3"

        # Act
        result = Environment.get_list("TEST_LIST")

        # Assert
        assert result == ["value1", "value2", "value3"]
        assert isinstance(result, list)

    @patch("os.getenv")
    def test_get_list_with_single_value(self, mock_getenv):
        """Test get_list with single value (no comma)"""
        # Arrange
        mock_getenv.return_value = "single_value"

        # Act
        result = Environment.get_list("TEST_LIST")

        # Assert
        assert result == ["single_value"]

    @patch("os.getenv")
    def test_get_list_with_empty_string(self, mock_getenv):
        """Test get_list with empty string"""
        # Arrange
        mock_getenv.return_value = ""

        # Act
        result = Environment.get_list("EMPTY_LIST")

        # Assert
        assert result == [""]

    @patch("os.getenv")
    def test_get_list_with_spaces_in_values(self, mock_getenv):
        """Test get_list preserves spaces in values"""
        # Arrange
        mock_getenv.return_value = "value 1,value 2,value 3"

        # Act
        result = Environment.get_list("TEST_LIST")

        # Assert
        assert result == ["value 1", "value 2", "value 3"]

    @patch("os.getenv")
    def test_get_list_with_custom_default(self, mock_getenv):
        """Test get_list with custom default value"""
        # Arrange
        mock_getenv.return_value = "default1,default2"

        # Act
        result = Environment.get_list("TEST_LIST", default="default1,default2")

        # Assert
        assert result == ["default1", "default2"]

    @patch("os.getenv")
    def test_get_list_with_trailing_comma(self, mock_getenv):
        """Test get_list with trailing comma"""
        # Arrange
        mock_getenv.return_value = "value1,value2,"

        # Act
        result = Environment.get_list("TEST_LIST")

        # Assert
        assert result == ["value1", "value2", ""]

    @patch("os.getenv")
    def test_get_list_with_leading_comma(self, mock_getenv):
        """Test get_list with leading comma"""
        # Arrange
        mock_getenv.return_value = ",value1,value2"

        # Act
        result = Environment.get_list("TEST_LIST")

        # Assert
        assert result == ["", "value1", "value2"]

    @patch("os.getenv")
    def test_get_list_with_empty_values(self, mock_getenv):
        """Test get_list with consecutive commas (empty values)"""
        # Arrange
        mock_getenv.return_value = "value1,,value2"

        # Act
        result = Environment.get_list("TEST_LIST")

        # Assert
        assert result == ["value1", "", "value2"]


class TestGetDict:
    """Test cases for Environment.get_dict method"""

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_valid_dict(self, mock_getenv, mock_logger):
        """Test get_dict with valid dictionary string"""
        # Arrange
        mock_getenv.return_value = '{"key1": "value1", "key2": "value2"}'

        # Act
        result = Environment.get_dict("TEST_DICT")

        # Assert
        assert result == {"key1": "value1", "key2": "value2"}
        assert isinstance(result, dict)
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_empty_dict(self, mock_getenv, mock_logger):
        """Test get_dict with empty dictionary"""
        # Arrange
        mock_getenv.return_value = "{}"

        # Act
        result = Environment.get_dict("TEST_DICT")

        # Assert
        assert result == {}
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_nested_dict(self, mock_getenv, mock_logger):
        """Test get_dict with nested dictionary"""
        # Arrange
        mock_getenv.return_value = '{"outer": {"inner": "value"}}'

        # Act
        result = Environment.get_dict("TEST_DICT")

        # Assert
        assert result == {"outer": {"inner": "value"}}
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_custom_default(self, mock_getenv, mock_logger):
        """Test get_dict with custom default value"""
        # Arrange
        mock_getenv.return_value = '{"default": "value"}'

        # Act
        result = Environment.get_dict("TEST_DICT", default='{"default": "value"}')

        # Assert
        assert result == {"default": "value"}
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_invalid_value_returns_default(self, mock_getenv, mock_logger):
        """Test get_dict returns default when value is invalid"""
        # Arrange
        mock_getenv.return_value = "not_a_dict"

        # Act
        result = Environment.get_dict("INVALID_DICT", default='{"error": "default"}')

        # Assert
        assert result == {"error": "default"}
        expected_error = "{}:{}::Invalid dict value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, "not_a_dict", "INVALID_DICT")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_list_instead_of_dict_returns_default(self, mock_getenv, mock_logger):
        """Test get_dict returns default when value is a list instead of dict"""
        # Arrange
        mock_getenv.return_value = "[1, 2, 3]"

        # Act
        result = Environment.get_dict("LIST_NOT_DICT", default="{}")

        # Assert
        assert result == {}
        expected_error = "{}:{}::Invalid dict value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, "[1, 2, 3]", "LIST_NOT_DICT")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_malformed_json_returns_default(self, mock_getenv, mock_logger):
        """Test get_dict returns default when JSON is malformed"""
        # Arrange
        mock_getenv.return_value = '{"incomplete":'

        # Act
        result = Environment.get_dict("MALFORMED_DICT", default="{}")

        # Assert
        assert result == {}
        expected_error = "{}:{}::Invalid dict value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, '{"incomplete":', "MALFORMED_DICT")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_empty_string_returns_default(self, mock_getenv, mock_logger):
        """Test get_dict with empty string returns default"""
        # Arrange
        mock_getenv.return_value = ""

        # Act
        result = Environment.get_dict("EMPTY_DICT", default="{}")

        # Assert
        assert result == {}
        expected_error = "{}:{}::Invalid dict value:{} for {}".format(ALERT_MESSAGE_PREPEND, CONFIG_ERROR_LOG_MESSAGE, "", "EMPTY_DICT")
        mock_logger.assert_called_once_with(expected_error)

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_logs_error_on_exception(self, mock_getenv, mock_logger):
        """Test get_dict logs error when exception occurs"""
        # Arrange
        mock_getenv.return_value = "invalid"

        # Act
        result = Environment.get_dict("BAD_DICT", default="{}")

        # Assert
        assert result == {}
        assert mock_logger.call_count == 1
        error_msg = mock_logger.call_args[0][0]
        assert ALERT_MESSAGE_PREPEND in error_msg
        assert CONFIG_ERROR_LOG_MESSAGE in error_msg
        assert "invalid" in error_msg
        assert "BAD_DICT" in error_msg

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_numeric_keys(self, mock_getenv, mock_logger):
        """Test get_dict with numeric keys"""
        # Arrange
        mock_getenv.return_value = '{"1": "one", "2": "two"}'

        # Act
        result = Environment.get_dict("NUMERIC_KEYS_DICT")

        # Assert
        assert result == {"1": "one", "2": "two"}
        mock_logger.assert_not_called()

    @patch("config.util.LoggerUtil.create_error_log")
    @patch("os.getenv")
    def test_get_dict_with_mixed_value_types(self, mock_getenv, mock_logger):
        """Test get_dict with mixed value types"""
        # Arrange
        mock_getenv.return_value = '{"string": "text", "number": 42, "bool": true, "null": null}'

        # Act
        result = Environment.get_dict("MIXED_DICT")

        # Assert
        assert result == {"string": "text", "number": 42, "bool": True, "null": None}
        mock_logger.assert_not_called()
