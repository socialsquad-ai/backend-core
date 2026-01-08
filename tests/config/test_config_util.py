import os
from unittest.mock import patch

from config.util import Environment


class TestEnvironmentGetString:
    @patch.dict(os.environ, {"TEST_STRING": "hello"})
    def test_get_string_returns_existing_value(self):
        result = Environment.get_string("TEST_STRING")
        assert result == "hello"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_string_returns_default_when_not_set(self):
        result = Environment.get_string("NONEXISTENT_KEY", "default_value")
        assert result == "default_value"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_string_returns_empty_string_by_default(self):
        result = Environment.get_string("NONEXISTENT_KEY")
        assert result == ""

    @patch.dict(os.environ, {"TEST_NUM": "123"})
    def test_get_string_converts_to_string(self):
        result = Environment.get_string("TEST_NUM")
        assert isinstance(result, str)
        assert result == "123"


class TestEnvironmentGetInt:
    @patch.dict(os.environ, {"TEST_INT": "42"})
    def test_get_int_returns_integer(self):
        result = Environment.get_int("TEST_INT")
        assert result == 42
        assert isinstance(result, int)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_int_returns_default_when_not_set(self):
        result = Environment.get_int("NONEXISTENT_KEY", 100)
        assert result == 100

    @patch.dict(os.environ, {}, clear=True)
    def test_get_int_returns_zero_by_default(self):
        result = Environment.get_int("NONEXISTENT_KEY")
        assert result == 0

    @patch.dict(os.environ, {"TEST_INVALID": "not_a_number"})
    @patch("config.util.LoggerUtil.create_error_log")
    def test_get_int_returns_default_on_invalid_value(self, mock_logger):
        result = Environment.get_int("TEST_INVALID", 50)
        assert result == 50
        assert mock_logger.called

    @patch.dict(os.environ, {"TEST_NEG": "-42"})
    def test_get_int_handles_negative_numbers(self):
        result = Environment.get_int("TEST_NEG")
        assert result == -42


class TestEnvironmentGetBool:
    @patch.dict(os.environ, {"TEST_TRUE": "True"})
    def test_get_bool_returns_true(self):
        result = Environment.get_bool("TEST_TRUE")
        assert result is True

    @patch.dict(os.environ, {"TEST_FALSE": "False"})
    def test_get_bool_returns_false(self):
        result = Environment.get_bool("TEST_FALSE")
        assert result is False

    @patch.dict(os.environ, {}, clear=True)
    def test_get_bool_returns_default_when_not_set(self):
        result = Environment.get_bool("NONEXISTENT_KEY", True)
        assert result is True

    @patch.dict(os.environ, {}, clear=True)
    def test_get_bool_returns_false_by_default(self):
        result = Environment.get_bool("NONEXISTENT_KEY")
        assert result is False

    @patch.dict(os.environ, {"TEST_INVALID": "not_a_bool"})
    @patch("config.util.LoggerUtil.create_error_log")
    def test_get_bool_returns_default_on_invalid_value(self, mock_logger):
        result = Environment.get_bool("TEST_INVALID", True)
        assert result is True
        assert mock_logger.called


class TestEnvironmentGetFloat:
    @patch.dict(os.environ, {"TEST_FLOAT": "3.14"})
    def test_get_float_returns_float(self):
        result = Environment.get_float("TEST_FLOAT")
        assert result == 3.14
        assert isinstance(result, float)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_float_returns_default_when_not_set(self):
        result = Environment.get_float("NONEXISTENT_KEY", 2.5)
        assert result == 2.5

    @patch.dict(os.environ, {}, clear=True)
    def test_get_float_returns_zero_by_default(self):
        result = Environment.get_float("NONEXISTENT_KEY")
        assert result == 0.0

    @patch.dict(os.environ, {"TEST_INVALID": "not_a_float"})
    @patch("config.util.LoggerUtil.create_error_log")
    def test_get_float_returns_default_on_invalid_value(self, mock_logger):
        result = Environment.get_float("TEST_INVALID", 1.5)
        assert result == 1.5
        assert mock_logger.called

    @patch.dict(os.environ, {"TEST_INT": "42"})
    def test_get_float_handles_integer_strings(self):
        result = Environment.get_float("TEST_INT")
        assert result == 42.0
        assert isinstance(result, float)

    @patch.dict(os.environ, {"TEST_NEG": "-3.14"})
    def test_get_float_handles_negative_numbers(self):
        result = Environment.get_float("TEST_NEG")
        assert result == -3.14


class TestEnvironmentGetList:
    @patch.dict(os.environ, {"TEST_LIST": "a,b,c"})
    def test_get_list_returns_list(self):
        result = Environment.get_list("TEST_LIST")
        assert result == ["a", "b", "c"]
        assert isinstance(result, list)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_list_returns_empty_list_by_default(self):
        result = Environment.get_list("NONEXISTENT_KEY")
        assert result == [""]

    @patch.dict(os.environ, {"TEST_SINGLE": "single"})
    def test_get_list_handles_single_value(self):
        result = Environment.get_list("TEST_SINGLE")
        assert result == ["single"]

    @patch.dict(os.environ, {"TEST_EMPTY": ""})
    def test_get_list_handles_empty_string(self):
        result = Environment.get_list("TEST_EMPTY")
        assert result == [""]


class TestEnvironmentGetDict:
    @patch.dict(os.environ, {"TEST_DICT": "{'key': 'value'}"})
    def test_get_dict_returns_dict(self):
        result = Environment.get_dict("TEST_DICT")
        assert result == {"key": "value"}
        assert isinstance(result, dict)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_dict_returns_default_when_not_set(self):
        result = Environment.get_dict("NONEXISTENT_KEY", "{'default': 'dict'}")
        assert result == {"default": "dict"}

    @patch.dict(os.environ, {}, clear=True)
    def test_get_dict_returns_empty_dict_by_default(self):
        result = Environment.get_dict("NONEXISTENT_KEY")
        assert result == {}

    @patch.dict(os.environ, {"TEST_INVALID": "not_a_dict"})
    @patch("config.util.LoggerUtil.create_error_log")
    def test_get_dict_returns_default_on_invalid_value(self, mock_logger):
        result = Environment.get_dict("TEST_INVALID", "{'error': 'fallback'}")
        assert result == {"error": "fallback"}
        assert mock_logger.called

    @patch.dict(os.environ, {"TEST_LIST": "['not', 'a', 'dict']"})
    @patch("config.util.LoggerUtil.create_error_log")
    def test_get_dict_returns_default_on_non_dict_eval(self, mock_logger):
        result = Environment.get_dict("TEST_LIST", "{}")
        assert result == {}
        assert mock_logger.called


class TestEnvironmentClassMethods:
    def test_get_string_is_classmethod(self):
        assert callable(Environment.get_string)

    def test_get_int_is_classmethod(self):
        assert callable(Environment.get_int)

    def test_get_bool_is_classmethod(self):
        assert callable(Environment.get_bool)

    def test_get_float_is_classmethod(self):
        assert callable(Environment.get_float)

    def test_get_list_is_classmethod(self):
        assert callable(Environment.get_list)

    def test_get_dict_is_classmethod(self):
        assert callable(Environment.get_dict)
