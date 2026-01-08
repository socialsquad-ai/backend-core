import pytest

from utils.exceptions import CustomBadRequest, CustomUnauthorized


class TestCustomUnauthorized:
    """Test cases for CustomUnauthorized exception"""

    def test_custom_unauthorized_default_detail(self):
        # Arrange & Act
        exception = CustomUnauthorized()

        # Assert
        assert exception.detail == "Unauthorized access"
        assert isinstance(exception, Exception)

    def test_custom_unauthorized_custom_detail(self):
        # Arrange
        custom_message = "Token has expired"

        # Act
        exception = CustomUnauthorized(detail=custom_message)

        # Assert
        assert exception.detail == custom_message

    def test_custom_unauthorized_can_be_raised(self):
        # Arrange & Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            raise CustomUnauthorized(detail="Authentication failed")

        assert exc_info.value.detail == "Authentication failed"

    def test_custom_unauthorized_empty_detail(self):
        # Arrange & Act
        exception = CustomUnauthorized(detail="")

        # Assert
        assert exception.detail == ""

    def test_custom_unauthorized_with_special_characters(self):
        # Arrange
        detail = "User not found: @#$%^&*()"

        # Act
        exception = CustomUnauthorized(detail=detail)

        # Assert
        assert exception.detail == detail


class TestCustomBadRequest:
    """Test cases for CustomBadRequest exception"""

    def test_custom_bad_request_default_detail(self):
        # Arrange & Act
        exception = CustomBadRequest()

        # Assert
        assert exception.detail == "Bad Request"
        assert exception.errors is None
        assert isinstance(exception, Exception)

    def test_custom_bad_request_custom_detail(self):
        # Arrange
        custom_message = "Invalid payload format"

        # Act
        exception = CustomBadRequest(detail=custom_message)

        # Assert
        assert exception.detail == custom_message
        assert exception.errors is None

    def test_custom_bad_request_with_errors(self):
        # Arrange
        errors = {"field1": ["error message 1"], "field2": ["error message 2"]}

        # Act
        exception = CustomBadRequest(detail="Validation failed", errors=errors)

        # Assert
        assert exception.detail == "Validation failed"
        assert exception.errors == errors

    def test_custom_bad_request_can_be_raised(self):
        # Arrange & Act & Assert
        with pytest.raises(CustomBadRequest) as exc_info:
            raise CustomBadRequest(detail="Invalid input")

        assert exc_info.value.detail == "Invalid input"
        assert exc_info.value.errors is None

    def test_custom_bad_request_with_empty_errors_dict(self):
        # Arrange
        errors = {}

        # Act
        exception = CustomBadRequest(detail="Test", errors=errors)

        # Assert
        assert exception.detail == "Test"
        assert exception.errors == {}

    def test_custom_bad_request_with_nested_errors(self):
        # Arrange
        errors = {
            "user": {
                "email": ["Invalid email format", "Email already exists"],
                "password": ["Password too weak"],
            }
        }

        # Act
        exception = CustomBadRequest(detail="Validation error", errors=errors)

        # Assert
        assert exception.detail == "Validation error"
        assert exception.errors == errors
        assert exception.errors["user"]["email"][0] == "Invalid email format"

    def test_custom_bad_request_empty_detail(self):
        # Arrange & Act
        exception = CustomBadRequest(detail="")

        # Assert
        assert exception.detail == ""
        assert exception.errors is None

    def test_custom_bad_request_errors_none_by_default(self):
        # Arrange & Act
        exception = CustomBadRequest(detail="Test detail")

        # Assert
        assert exception.errors is None

    def test_custom_bad_request_with_special_characters_in_detail(self):
        # Arrange
        detail = "Invalid input: @#$%^&*()"

        # Act
        exception = CustomBadRequest(detail=detail)

        # Assert
        assert exception.detail == detail
