from utils import error_messages


class TestErrorMessages:
    def test_resource_not_found_constant(self):
        assert error_messages.RESOURCE_NOT_FOUND == "Not found"

    def test_invalid_resource_id_constant(self):
        assert error_messages.INVALID_RESOURCE_ID == "Invalid ID"

    def test_invalid_pagination_parameters_constant(self):
        assert error_messages.INVALID_PAGINATION_PARAMETERS == "Invalid pagination parameters. Page must be >= 1 and page size between 1-100"

    def test_persona_already_exists_constant(self):
        assert error_messages.PERSONA_ALREADY_EXISTS == "Persona already exists"

    def test_integration_not_found_constant(self):
        assert error_messages.INTEGRATION_NOT_FOUND == "Integration not found"

    def test_unsupported_platform_constant(self):
        assert error_messages.UNSUPPORTED_PLATFORM == "Unsupported platform"

    def test_user_not_found_constant(self):
        assert error_messages.USER_NOT_FOUND == "User not found"

    def test_all_error_messages_are_strings(self):
        assert isinstance(error_messages.RESOURCE_NOT_FOUND, str)
        assert isinstance(error_messages.INVALID_RESOURCE_ID, str)
        assert isinstance(error_messages.INVALID_PAGINATION_PARAMETERS, str)
        assert isinstance(error_messages.PERSONA_ALREADY_EXISTS, str)
        assert isinstance(error_messages.INTEGRATION_NOT_FOUND, str)
        assert isinstance(error_messages.UNSUPPORTED_PLATFORM, str)
        assert isinstance(error_messages.USER_NOT_FOUND, str)

    def test_error_messages_are_not_empty(self):
        assert len(error_messages.RESOURCE_NOT_FOUND) > 0
        assert len(error_messages.INVALID_RESOURCE_ID) > 0
        assert len(error_messages.INVALID_PAGINATION_PARAMETERS) > 0
        assert len(error_messages.PERSONA_ALREADY_EXISTS) > 0
        assert len(error_messages.INTEGRATION_NOT_FOUND) > 0
        assert len(error_messages.UNSUPPORTED_PLATFORM) > 0
        assert len(error_messages.USER_NOT_FOUND) > 0
