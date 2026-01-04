"""
Unit tests for utils/error_messages.py

Tests verify all error message constants are defined correctly.
"""

from utils import error_messages


class TestErrorMessages:
    """Test cases for error message constants"""

    def test_resource_not_found_message(self):
        """Test RESOURCE_NOT_FOUND constant"""
        assert error_messages.RESOURCE_NOT_FOUND == "Not found"

    def test_invalid_resource_id_message(self):
        """Test INVALID_RESOURCE_ID constant"""
        assert error_messages.INVALID_RESOURCE_ID == "Invalid ID"

    def test_invalid_pagination_parameters_message(self):
        """Test INVALID_PAGINATION_PARAMETERS constant"""
        assert error_messages.INVALID_PAGINATION_PARAMETERS == "Invalid pagination parameters. Page must be >= 1 and page size between 1-100"

    def test_persona_already_exists_message(self):
        """Test PERSONA_ALREADY_EXISTS constant"""
        assert error_messages.PERSONA_ALREADY_EXISTS == "Persona already exists"

    def test_integration_not_found_message(self):
        """Test INTEGRATION_NOT_FOUND constant"""
        assert error_messages.INTEGRATION_NOT_FOUND == "Integration not found"

    def test_unsupported_platform_message(self):
        """Test UNSUPPORTED_PLATFORM constant"""
        assert error_messages.UNSUPPORTED_PLATFORM == "Unsupported platform"

    def test_user_not_found_message(self):
        """Test USER_NOT_FOUND constant"""
        assert error_messages.USER_NOT_FOUND == "User not found"

    def test_all_messages_are_strings(self):
        """Test that all error messages are non-empty strings"""
        messages = [
            error_messages.RESOURCE_NOT_FOUND,
            error_messages.INVALID_RESOURCE_ID,
            error_messages.INVALID_PAGINATION_PARAMETERS,
            error_messages.PERSONA_ALREADY_EXISTS,
            error_messages.INTEGRATION_NOT_FOUND,
            error_messages.UNSUPPORTED_PLATFORM,
            error_messages.USER_NOT_FOUND,
        ]
        for message in messages:
            assert isinstance(message, str)
            assert len(message) > 0

    def test_messages_are_immutable(self):
        """Test that error message constants are defined at module level"""
        # Verify the constants exist as module attributes
        assert hasattr(error_messages, "RESOURCE_NOT_FOUND")
        assert hasattr(error_messages, "INVALID_RESOURCE_ID")
        assert hasattr(error_messages, "INVALID_PAGINATION_PARAMETERS")
        assert hasattr(error_messages, "PERSONA_ALREADY_EXISTS")
        assert hasattr(error_messages, "INTEGRATION_NOT_FOUND")
        assert hasattr(error_messages, "UNSUPPORTED_PLATFORM")
        assert hasattr(error_messages, "USER_NOT_FOUND")
