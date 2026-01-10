from unittest.mock import patch

from fastapi.responses import JSONResponse

from controller.util import APIResponseFormat, api_response_format


class TestApiResponseFormat:
    """Test cases for api_response_format function"""

    def test_api_response_format_with_all_parameters(self):
        # Arrange
        api_id = "test-api-123"
        message = "Success"
        data = {"key": "value"}
        errors = ["error1", "error2"]

        # Act
        result = api_response_format(api_id, message, data, errors)

        # Assert
        assert result == {
            "message": "Success",
            "data": {"key": "value"},
            "errors": ["error1", "error2"],
        }

    def test_api_response_format_with_minimal_parameters(self):
        # Arrange
        api_id = "test-api-123"
        message = "Success"

        # Act
        result = api_response_format(api_id, message)

        # Assert
        assert result == {"message": "Success", "data": None, "errors": None}

    def test_api_response_format_with_none_data(self):
        # Arrange
        api_id = "test-api-123"
        message = "No data"

        # Act
        result = api_response_format(api_id, message, data=None, errors=None)

        # Assert
        assert result["data"] is None
        assert result["errors"] is None


class TestAPIResponseFormat:
    """Test cases for APIResponseFormat class"""

    @patch("controller.util.get_context_api_id")
    def test_api_response_format_initialization(self, mock_get_api_id):
        # Arrange
        mock_get_api_id.return_value = "context-api-123"

        # Act
        response = APIResponseFormat(
            status_code=200,
            message="Success",
            data={"result": "test"},
            errors=None,
        )

        # Assert
        assert response.status_code == 200
        assert response.message == "Success"
        assert response.data == {"result": "test"}
        assert response.errors is None
        assert response.api_id == "context-api-123"

    @patch("controller.util.get_context_api_id")
    def test_api_response_format_get_json(self, mock_get_api_id):
        # Arrange
        mock_get_api_id.return_value = "test-api-456"
        response = APIResponseFormat(
            status_code=201,
            message="Created",
            data={"id": 123},
        )

        # Act
        json_response = response.get_json()

        # Assert
        assert isinstance(json_response, JSONResponse)
        assert json_response.status_code == 201

    @patch("controller.util.get_context_api_id")
    def test_api_response_format_with_errors(self, mock_get_api_id):
        # Arrange
        mock_get_api_id.return_value = "error-api-789"
        errors = [{"field": "email", "message": "Invalid format"}]

        # Act
        response = APIResponseFormat(
            status_code=400,
            message="Validation failed",
            errors=errors,
        )

        # Assert
        assert response.errors == errors
        assert response.status_code == 400

    @patch("controller.util.get_context_api_id")
    def test_api_response_format_empty_data(self, mock_get_api_id):
        # Arrange
        mock_get_api_id.return_value = "api-empty"

        # Act
        response = APIResponseFormat(status_code=200, message="OK")

        # Assert
        assert response.data is None
        assert response.errors is None

    @patch("controller.util.get_context_api_id")
    def test_api_response_format_complex_data(self, mock_get_api_id):
        # Arrange
        mock_get_api_id.return_value = "api-complex"
        complex_data = {
            "users": [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}],
            "total": 2,
            "page": 1,
        }

        # Act
        response = APIResponseFormat(status_code=200, message="Success", data=complex_data)

        # Assert
        assert response.data == complex_data
        assert response.data["total"] == 2
