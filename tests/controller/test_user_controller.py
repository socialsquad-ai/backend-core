"""
Unit tests for controller/user_controller.py

Tests cover all endpoint handlers including:
- create_user
- get_profile
- get_user
- get_users
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock the decorators before importing the controller
sys.modules["decorators.user"] = MagicMock()
sys.modules["decorators.user"].require_authentication = lambda f: f

sys.modules["decorators.common"] = MagicMock()
sys.modules["decorators.common"].require_internal_authentication = lambda f: f
sys.modules["decorators.common"].validate_json_payload = lambda schema: lambda f: f

from controller.user_controller import create_user, get_profile, get_user, get_users  # noqa: E402


class TestCreateUser:
    """Test cases for create_user endpoint"""

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.create_user")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_create_user_success(self, mock_response_format, mock_create_user):
        """Test successful user creation"""
        # Arrange
        mock_request = Mock()
        user_data = {"uuid": "123e4567-e89b-12d3-a456-426614174000", "email": "test@example.com", "name": "Test User", "auth0_user_id": "auth0|123456", "signup_method": "google-oauth2", "email_verified": True}
        mock_create_user.return_value = ("", user_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": user_data, "errors": None}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await create_user(mock_request)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": user_data, "errors": None}
        mock_create_user.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.create_user")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_create_user_returns_200_on_success(self, mock_response_format, mock_create_user):
        """Test that create_user returns 200 status code on success"""
        # Arrange
        mock_request = Mock()
        mock_create_user.return_value = ("", {"uuid": "test-uuid"}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await create_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.create_user")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_create_user_with_integrity_error(self, mock_response_format, mock_create_user):
        """Test user creation when user already exists (IntegrityError)"""
        # Arrange
        mock_request = Mock()
        error_message = "User already exists"
        mock_create_user.return_value = ("", None, error_message)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 409, "message": "", "data": None, "errors": error_message}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await create_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 409
        assert call_kwargs["errors"] == error_message
        assert result["status_code"] == 409

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.create_user")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_create_user_with_general_error(self, mock_response_format, mock_create_user):
        """Test user creation with general error"""
        # Arrange
        mock_request = Mock()
        error_message = "Database connection failed"
        mock_create_user.return_value = ("", None, error_message)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await create_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 409
        assert call_kwargs["message"] == ""
        assert call_kwargs["errors"] == error_message

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.create_user")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_create_user_passes_request(self, mock_response_format, mock_create_user):
        """Test that request is passed to UserManagement"""
        # Arrange
        mock_request = Mock()
        mock_request.headers = {"X-Internal-API-Key": "test-key"}
        mock_create_user.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await create_user(mock_request)

        # Assert
        mock_create_user.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.create_user")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_create_user_returns_correct_data_structure(self, mock_response_format, mock_create_user):
        """Test that create_user returns correctly formatted response"""
        # Arrange
        mock_request = Mock()
        user_data = {"uuid": "123e4567-e89b-12d3-a456-426614174000", "email": "newuser@example.com"}
        mock_create_user.return_value = ("User created successfully", user_data, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await create_user(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == "User created successfully"
        assert call_kwargs["data"] == user_data
        assert call_kwargs["errors"] is None


class TestGetProfile:
    """Test cases for get_profile endpoint"""

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_profile")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_profile_success(self, mock_response_format, mock_get_profile):
        """Test successful profile retrieval"""
        # Arrange
        mock_request = Mock()
        profile_data = {"uuid": "123e4567-e89b-12d3-a456-426614174000", "email": "user@example.com", "name": "Test User", "email_verified": True}
        mock_get_profile.return_value = ("", profile_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": profile_data, "errors": None}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_profile(mock_request)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": profile_data, "errors": None}
        mock_get_profile.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_profile")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_profile_returns_200(self, mock_response_format, mock_get_profile):
        """Test that get_profile always returns 200 status code"""
        # Arrange
        mock_request = Mock()
        mock_get_profile.return_value = ("", {"uuid": "test-uuid"}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_profile(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_profile")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_profile_with_complete_user_data(self, mock_response_format, mock_get_profile):
        """Test get_profile with complete user data"""
        # Arrange
        mock_request = Mock()
        complete_profile = {
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "name": "Complete User",
            "auth0_user_id": "auth0|987654",
            "signup_method": "email",
            "email_verified": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        mock_get_profile.return_value = ("", complete_profile, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_profile(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["data"] == complete_profile
        assert call_kwargs["errors"] is None

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_profile")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_profile_passes_request(self, mock_response_format, mock_get_profile):
        """Test that request is passed to UserManagement"""
        # Arrange
        mock_request = Mock()
        mock_request.headers = {"Authorization": "Bearer token"}
        mock_get_profile.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_profile(mock_request)

        # Assert
        mock_get_profile.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_profile")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_profile_with_custom_message(self, mock_response_format, mock_get_profile):
        """Test get_profile with custom message"""
        # Arrange
        mock_request = Mock()
        mock_get_profile.return_value = ("Profile retrieved successfully", {"uuid": "test"}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_profile(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == "Profile retrieved successfully"


class TestGetUser:
    """Test cases for get_user endpoint"""

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_user_by_uuid")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_user_success(self, mock_response_format, mock_get_user_by_uuid):
        """Test successful user retrieval by UUID"""
        # Arrange
        mock_request = Mock()
        user_uuid = "123e4567-e89b-12d3-a456-426614174000"
        user_data = {"user": {"uuid": user_uuid, "email": "test@example.com", "name": "Test User"}}
        mock_get_user_by_uuid.return_value = ("", user_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": user_data, "errors": None}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_user(mock_request, user_uuid)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": user_data, "errors": None}
        mock_get_user_by_uuid.assert_called_once_with(mock_request, user_uuid)

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_user_by_uuid")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_user_returns_200_on_success(self, mock_response_format, mock_get_user_by_uuid):
        """Test that get_user returns 200 status code on success"""
        # Arrange
        mock_request = Mock()
        user_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_get_user_by_uuid.return_value = ("", {"user": {}}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_user(mock_request, user_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_user_by_uuid")
    @patch("controller.user_controller.APIResponseFormat")
    @patch("controller.user_controller.RESOURCE_NOT_FOUND", "Not found")
    async def test_get_user_not_found(self, mock_response_format, mock_get_user_by_uuid):
        """Test get_user when user is not found"""
        # Arrange
        mock_request = Mock()
        user_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_get_user_by_uuid.return_value = ("Not found", None, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 404, "message": "Not found", "data": None, "errors": None}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_user(mock_request, user_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 404
        assert call_kwargs["message"] == "Not found"
        assert result["status_code"] == 404

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_user_by_uuid")
    @patch("controller.user_controller.APIResponseFormat")
    @patch("controller.user_controller.INVALID_RESOURCE_ID", "Invalid ID")
    async def test_get_user_invalid_uuid(self, mock_response_format, mock_get_user_by_uuid):
        """Test get_user with invalid UUID format"""
        # Arrange
        mock_request = Mock()
        invalid_uuid = "invalid-uuid-format"
        mock_get_user_by_uuid.return_value = ("Invalid ID", None, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 400, "message": "Invalid ID", "data": None, "errors": None}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_user(mock_request, invalid_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 400
        assert call_kwargs["message"] == "Invalid ID"
        assert result["status_code"] == 400

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_user_by_uuid")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_user_passes_uuid_parameter(self, mock_response_format, mock_get_user_by_uuid):
        """Test that user_uuid parameter is passed to UserManagement"""
        # Arrange
        mock_request = Mock()
        user_uuid = "987e6543-e89b-12d3-a456-426614174999"
        mock_get_user_by_uuid.return_value = ("", {"user": {}}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_user(mock_request, user_uuid)

        # Assert
        mock_get_user_by_uuid.assert_called_once_with(mock_request, user_uuid)

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_user_by_uuid")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_user_with_complete_user_data(self, mock_response_format, mock_get_user_by_uuid):
        """Test get_user returns complete user data structure"""
        # Arrange
        mock_request = Mock()
        user_uuid = "123e4567-e89b-12d3-a456-426614174000"
        complete_user_data = {
            "user": {
                "uuid": user_uuid,
                "email": "complete@example.com",
                "name": "Complete User",
                "auth0_user_id": "auth0|123456",
                "email_verified": True,
                "signup_method": "google-oauth2",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }
        mock_get_user_by_uuid.return_value = ("", complete_user_data, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_user(mock_request, user_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["data"] == complete_user_data
        assert "user" in call_kwargs["data"]

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_user_by_uuid")
    @patch("controller.user_controller.APIResponseFormat")
    @patch("controller.user_controller.RESOURCE_NOT_FOUND", "Not found")
    async def test_get_user_not_found_returns_404(self, mock_response_format, mock_get_user_by_uuid):
        """Test that get_user returns 404 when user not found"""
        # Arrange
        mock_request = Mock()
        user_uuid = "999e9999-e99b-99d9-a999-999999999999"
        mock_get_user_by_uuid.return_value = ("Not found", None, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_user(mock_request, user_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 404
        assert call_kwargs["data"] is None

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_user_by_uuid")
    @patch("controller.user_controller.APIResponseFormat")
    @patch("controller.user_controller.INVALID_RESOURCE_ID", "Invalid ID")
    async def test_get_user_invalid_uuid_returns_400(self, mock_response_format, mock_get_user_by_uuid):
        """Test that get_user returns 400 for invalid UUID"""
        # Arrange
        mock_request = Mock()
        invalid_uuid = "not-a-uuid"
        mock_get_user_by_uuid.return_value = ("Invalid ID", None, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_user(mock_request, invalid_uuid)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 400
        assert call_kwargs["data"] is None


class TestGetUsers:
    """Test cases for get_users endpoint"""

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_users")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_users_success(self, mock_response_format, mock_get_users):
        """Test successful retrieval of all users"""
        # Arrange
        mock_request = Mock()
        users_data = {
            "users": [
                {"uuid": "123e4567-e89b-12d3-a456-426614174000", "email": "user1@example.com", "name": "User One"},
                {"uuid": "223e4567-e89b-12d3-a456-426614174001", "email": "user2@example.com", "name": "User Two"},
            ]
        }
        mock_get_users.return_value = ("", users_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": users_data, "errors": None}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_users(mock_request)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": users_data, "errors": None}
        mock_get_users.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_users")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_users_returns_200(self, mock_response_format, mock_get_users):
        """Test that get_users always returns 200 status code"""
        # Arrange
        mock_request = Mock()
        mock_get_users.return_value = ("", {"users": []}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_users(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_users")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_users_with_empty_list(self, mock_response_format, mock_get_users):
        """Test get_users when no users exist"""
        # Arrange
        mock_request = Mock()
        mock_get_users.return_value = ("No users found", None, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "No users found", "data": None, "errors": None}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_users(mock_request)

        # Assert
        assert result["message"] == "No users found"
        assert result["data"] is None

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_users")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_users_with_multiple_users(self, mock_response_format, mock_get_users):
        """Test get_users with multiple users"""
        # Arrange
        mock_request = Mock()
        users_data = {"users": [{"uuid": f"uuid-{i}", "email": f"user{i}@example.com", "name": f"User {i}"} for i in range(5)]}
        mock_get_users.return_value = ("", users_data, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_users(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["data"] == users_data
        assert len(call_kwargs["data"]["users"]) == 5

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_users")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_users_passes_request(self, mock_response_format, mock_get_users):
        """Test that request is passed to UserManagement"""
        # Arrange
        mock_request = Mock()
        mock_request.headers = {"Authorization": "Bearer token"}
        mock_get_users.return_value = ("", {"users": []}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_users(mock_request)

        # Assert
        mock_get_users.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_users")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_users_returns_correct_data_structure(self, mock_response_format, mock_get_users):
        """Test that get_users returns correctly formatted response"""
        # Arrange
        mock_request = Mock()
        users_data = {"users": [{"uuid": "123e4567-e89b-12d3-a456-426614174000", "email": "user@example.com", "name": "Test User", "auth0_user_id": "auth0|123", "email_verified": True}]}
        mock_get_users.return_value = ("", users_data, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_users(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert "users" in call_kwargs["data"]
        assert isinstance(call_kwargs["data"]["users"], list)
        assert call_kwargs["errors"] is None

    @pytest.mark.asyncio
    @patch("controller.user_controller.UserManagement.get_users")
    @patch("controller.user_controller.APIResponseFormat")
    async def test_get_users_with_custom_message(self, mock_response_format, mock_get_users):
        """Test get_users with custom success message"""
        # Arrange
        mock_request = Mock()
        mock_get_users.return_value = ("Users retrieved successfully", {"users": []}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_users(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == "Users retrieved successfully"
