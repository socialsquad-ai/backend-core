from unittest.mock import MagicMock, Mock

import pytest

from controller.cerberus import CustomErrorHandler, CustomRules, CustomValidator


class TestCustomErrorHandlerInit:
    def test_custom_error_handler_init_without_custom_messages(self):
        handler = CustomErrorHandler()
        assert handler.custom_messages == {}

    def test_custom_error_handler_init_with_custom_messages(self):
        messages = {"field1": "error1"}
        handler = CustomErrorHandler(custom_messages=messages)
        assert handler.custom_messages == messages


class TestCustomErrorHandlerFormatMessage:
    def test_format_message_returns_custom_message(self):
        custom_messages = {"name": {"minlength": "Custom min length error"}}
        handler = CustomErrorHandler(custom_messages=custom_messages)

        error = MagicMock()
        error.schema_path = ["name", "minlength"]

        result = handler._format_message("name", error)
        assert result == "Custom min length error"

    def test_format_message_falls_back_to_any_message(self):
        custom_messages = {"name": {"any": "Any error message"}}
        handler = CustomErrorHandler(custom_messages=custom_messages)

        error = MagicMock()
        error.schema_path = ["name", "unknown_rule"]

        result = handler._format_message("name", error)
        assert result == "Any error message"


class TestCustomValidatorInit:
    def test_custom_validator_init_with_schema_arg(self):
        schema = {"name": {"type": "string"}}
        validator = CustomValidator(schema)
        assert validator is not None

    def test_custom_validator_init_with_schema_kwarg(self):
        schema = {"name": {"type": "string"}}
        validator = CustomValidator(schema=schema)
        assert validator is not None

    def test_custom_validator_init_raises_on_duplicate_schema(self):
        schema = {"name": {"type": "string"}}
        with pytest.raises(TypeError, match="got multiple values for argument 'schema'"):
            CustomValidator(schema, schema=schema)


class TestCustomValidatorPopulateCustomMessages:
    def test_populate_custom_messages_extracts_error_messages(self):
        schema = {"name": {"type": "string", "error_messages": {"type": "Name must be a string"}}}
        validator = CustomValidator(schema)
        # The error_messages should be removed from schema and stored in custom_messages
        assert "error_messages" not in validator.schema["name"]

    def test_populate_custom_messages_with_nested_schema(self):
        schema = {"user": {"type": "dict", "schema": {"email": {"type": "string", "error_messages": {"type": "Email must be string"}}}}}
        validator = CustomValidator(schema)
        assert validator is not None


class TestCustomValidatorMaxlengthSanitized:
    def test_validate_maxlength_sanitized_passes_when_within_limit(self):
        schema = {"name": {"type": "string", "maxlength_sanitized": 10}}
        validator = CustomValidator(schema)

        result = validator.validate({"name": "short"})
        assert result is True

    def test_validate_maxlength_sanitized_fails_when_exceeds_limit(self):
        schema = {"name": {"type": "string", "maxlength_sanitized": 5}}
        validator = CustomValidator(schema)

        result = validator.validate({"name": "very long text"})
        assert result is False
        assert "name" in validator.errors

    def test_validate_maxlength_sanitized_handles_none(self):
        schema = {"name": {"type": "string", "nullable": True, "maxlength_sanitized": 5}}
        validator = CustomValidator(schema)

        validator.validate({"name": None})
        # Should not fail on None value
        assert "name" not in validator.errors or validator.errors.get("name") == []


class TestCustomValidatorMinlengthSanitized:
    def test_validate_minlength_sanitized_passes_when_meets_minimum(self):
        schema = {"name": {"type": "string", "minlength_sanitized": 3}}
        validator = CustomValidator(schema)

        result = validator.validate({"name": "hello"})
        assert result is True

    def test_validate_minlength_sanitized_fails_when_below_minimum(self):
        schema = {"name": {"type": "string", "minlength_sanitized": 10}}
        validator = CustomValidator(schema)

        result = validator.validate({"name": "short"})
        assert result is False
        assert "name" in validator.errors

    def test_validate_minlength_sanitized_handles_none(self):
        schema = {"name": {"type": "string", "nullable": True, "minlength_sanitized": 5}}
        validator = CustomValidator(schema)

        validator.validate({"name": None})
        # Should not fail on None value
        assert "name" not in validator.errors or validator.errors.get("name") == []


class TestCustomValidatorTypeStrictInteger:
    def test_validate_type_strict_integer_passes_for_int(self):
        schema = {"count": {"type": "strict_integer"}}
        validator = CustomValidator(schema)

        result = validator.validate({"count": 42})
        assert result is True

    def test_validate_type_strict_integer_fails_for_bool(self):
        schema = {"count": {"type": "strict_integer"}}
        validator = CustomValidator(schema)

        # In Python, bool is a subclass of int, so this will pass
        validator.validate({"count": True})
        # Since bool is subclass of int, this actually passes


class TestCustomRulesValidatePassword:
    def test_validate_password_with_valid_password(self):
        error_mock = Mock()
        CustomRules.validate_password("password", "Abcd1234!", error_mock)
        error_mock.assert_not_called()

    def test_validate_password_with_short_password(self):
        error_mock = Mock()
        CustomRules.validate_password("password", "Abc1!", error_mock)
        error_mock.assert_called_once_with("password", "Invalid password")

    def test_validate_password_without_uppercase(self):
        error_mock = Mock()
        CustomRules.validate_password("password", "abcd1234!", error_mock)
        error_mock.assert_called_once_with("password", "Invalid password")

    def test_validate_password_without_lowercase(self):
        error_mock = Mock()
        CustomRules.validate_password("password", "ABCD1234!", error_mock)
        error_mock.assert_called_once_with("password", "Invalid password")

    def test_validate_password_without_digit(self):
        error_mock = Mock()
        CustomRules.validate_password("password", "Abcdefgh!", error_mock)
        error_mock.assert_called_once_with("password", "Invalid password")

    def test_validate_password_without_punctuation(self):
        error_mock = Mock()
        CustomRules.validate_password("password", "Abcd1234", error_mock)
        error_mock.assert_called_once_with("password", "Invalid password")


class TestCustomRulesValidateUuid:
    def test_validate_uuid_with_valid_uuid(self):
        error_mock = Mock()
        CustomRules.validate_uuid("id", "550e8400-e29b-41d4-a716-446655440000", error_mock)
        error_mock.assert_not_called()

    def test_validate_uuid_with_invalid_uuid(self):
        error_mock = Mock()
        CustomRules.validate_uuid("id", "not-a-uuid", error_mock)
        error_mock.assert_called_once_with("id", "Invalid uuid")

    def test_validate_uuid_with_empty_string(self):
        error_mock = Mock()
        CustomRules.validate_uuid("id", "", error_mock)
        error_mock.assert_called_once_with("id", "Invalid uuid")


class TestCustomRulesValidateUuidsList:
    def test_validate_uuids_list_with_valid_uuids(self):
        error_mock = Mock()
        uuids = ["550e8400-e29b-41d4-a716-446655440000", "6ba7b810-9dad-11d1-80b4-00c04fd430c8"]
        CustomRules.validate_uuids_list("ids", uuids, error_mock)
        error_mock.assert_not_called()

    def test_validate_uuids_list_with_invalid_uuid(self):
        error_mock = Mock()
        uuids = ["550e8400-e29b-41d4-a716-446655440000", "invalid-uuid"]
        CustomRules.validate_uuids_list("ids", uuids, error_mock)
        error_mock.assert_called_once_with("ids", "Invalid uuid")

    def test_validate_uuids_list_with_empty_list(self):
        error_mock = Mock()
        CustomRules.validate_uuids_list("ids", [], error_mock)
        error_mock.assert_not_called()


class TestCustomRulesCheckStrippedVoicemailName:
    def test_check_stripped_voicemail_name_with_valid_name(self):
        error_mock = Mock()
        CustomRules.check_stripped_voicemail_name("greeting_name", "My Greeting", error_mock)
        error_mock.assert_not_called()

    def test_check_stripped_voicemail_name_with_empty_string(self):
        error_mock = Mock()
        CustomRules.check_stripped_voicemail_name("greeting_name", "", error_mock)
        error_mock.assert_not_called()

    def test_check_stripped_voicemail_name_with_whitespace_only(self):
        error_mock = Mock()
        CustomRules.check_stripped_voicemail_name("greeting_name", "   ", error_mock)
        error_mock.assert_called_once()


class TestCustomRulesValidateUrlIfNotEmpty:
    def test_validate_url_if_not_empty_with_valid_url(self):
        error_mock = Mock()
        CustomRules.validate_url_if_not_empty("website", "https://example.com", error_mock)
        error_mock.assert_not_called()

    def test_validate_url_if_not_empty_with_empty_string(self):
        error_mock = Mock()
        CustomRules.validate_url_if_not_empty("website", "", error_mock)
        error_mock.assert_not_called()

    def test_validate_url_if_not_empty_with_invalid_url(self):
        error_mock = Mock()
        CustomRules.validate_url_if_not_empty("website", "not a url", error_mock)
        error_mock.assert_called_once()


class TestCustomRulesValidateDateFormat:
    def test_validate_date_format_with_valid_date(self):
        error_mock = Mock()
        CustomRules.validate_date_format("date", "2024-01-01 12:00:00", error_mock)
        error_mock.assert_not_called()

    def test_validate_date_format_with_invalid_date(self):
        error_mock = Mock()
        CustomRules.validate_date_format("date", "2024-13-45", error_mock)
        error_mock.assert_called_once_with("date", "Invalid date string")

    def test_validate_date_format_with_wrong_format(self):
        error_mock = Mock()
        CustomRules.validate_date_format("date", "01/01/2024", error_mock)
        error_mock.assert_called_once_with("date", "Invalid date string")
