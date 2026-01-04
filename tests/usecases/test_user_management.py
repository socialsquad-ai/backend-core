"""
Unit tests for usecases/user_management.py

Tests cover all methods in the UserManagement class including:
- get_profile
- create_user
- get_user_by_email
- get_user_by_uuid
- get_users
"""

import datetime
from unittest.mock import Mock, patch

from peewee import IntegrityError

from usecases.user_management import UserManagement
from utils.error_messages import INVALID_RESOURCE_ID, RESOURCE_NOT_FOUND


class TestGetProfile:
    """Test cases for get_profile method"""

    @patch("usecases.user_management.get_context_user")
    def test_get_profile_success(self, mock_get_context_user):
        """Test get_profile with valid user context"""
        # Arrange
        mock_user = Mock()
        mock_user.get_details.return_value = {"name": "John Doe", "email": "john@example.com", "uuid": "test-uuid", "role": "brand", "status": "active"}
        mock_get_context_user.return_value = mock_user
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_profile(mock_request)

        # Assert
        assert error_message == ""
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["uuid"] == "test-uuid"
        assert errors is None
        mock_get_context_user.assert_called_once()
        mock_user.get_details.assert_called_once()

    @patch("usecases.user_management.get_context_user")
    def test_get_profile_no_user_in_context(self, mock_get_context_user):
        """Test get_profile when no user in context"""
        # Arrange
        mock_get_context_user.return_value = None
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_profile(mock_request)

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None
        mock_get_context_user.assert_called_once()

    @patch("usecases.user_management.get_context_user")
    def test_get_profile_with_all_user_fields(self, mock_get_context_user):
        """Test get_profile returns all user detail fields"""
        # Arrange
        mock_user = Mock()
        mock_user.get_details.return_value = {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "signup_method": "google",
            "email_verified": True,
            "created_at": "2025-01-01T00:00:00",
            "uuid": "test-uuid-123",
            "role": "brand",
            "content_categories": ["tech", "lifestyle"],
            "status": "active",
        }
        mock_get_context_user.return_value = mock_user
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_profile(mock_request)

        # Assert
        assert error_message == ""
        assert data["signup_method"] == "google"
        assert data["email_verified"] is True
        assert data["content_categories"] == ["tech", "lifestyle"]
        assert errors is None


class TestCreateUser:
    """Test cases for create_user method"""

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_create_user_success_with_all_fields(self, mock_user, mock_get_payload):
        """Test create_user with all required and optional fields"""
        # Arrange
        mock_payload = {"email": "newuser@example.com", "auth0_user_id": "auth0|123456", "name": "New User", "signup_method": "google", "email_verified": True, "auth0_created_at": "2025-01-01T00:00:00"}
        mock_get_payload.return_value = mock_payload

        mock_user_instance = Mock()
        mock_user_instance.get_details.return_value = {"name": "New User", "email": "newuser@example.com", "uuid": "new-uuid"}
        mock_user.get_or_create_user_from_auth0.return_value = mock_user_instance
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.create_user(mock_request)

        # Assert
        assert error_message == ""
        assert data["name"] == "New User"
        assert data["email"] == "newuser@example.com"
        assert errors is None
        mock_user.get_or_create_user_from_auth0.assert_called_once_with("auth0|123456", "New User", "newuser@example.com", "google", True, "2025-01-01T00:00:00")

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_create_user_success_without_optional_fields(self, mock_user, mock_get_payload):
        """Test create_user without optional name and auth0_created_at fields"""
        # Arrange
        mock_payload = {"email": "test@example.com", "auth0_user_id": "auth0|789", "signup_method": "email-password", "email_verified": False}
        mock_get_payload.return_value = mock_payload

        mock_user_instance = Mock()
        mock_user_instance.get_details.return_value = {"name": "test", "email": "test@example.com", "uuid": "test-uuid"}
        mock_user.get_or_create_user_from_auth0.return_value = mock_user_instance
        mock_request = Mock()

        # Act
        with patch("usecases.user_management.datetime") as mock_datetime:
            mock_now = datetime.datetime(2025, 1, 4, 12, 0, 0, tzinfo=datetime.timezone.utc)
            mock_datetime.datetime.now.return_value = mock_now
            mock_datetime.timezone.utc = datetime.timezone.utc
            error_message, data, errors = UserManagement.create_user(mock_request)

        # Assert
        assert error_message == ""
        assert data["name"] == "test"
        assert errors is None
        # Verify name defaults to email prefix
        call_args = mock_user.get_or_create_user_from_auth0.call_args[0]
        assert call_args[0] == "auth0|789"
        assert call_args[1] == "test"  # Defaults to email prefix
        assert call_args[2] == "test@example.com"

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_create_user_defaults_name_from_email(self, mock_user, mock_get_payload):
        """Test create_user defaults name to email prefix when not provided"""
        # Arrange
        mock_payload = {"email": "john.doe@example.com", "auth0_user_id": "auth0|456", "signup_method": "facebook", "email_verified": True}
        mock_get_payload.return_value = mock_payload

        mock_user_instance = Mock()
        mock_user_instance.get_details.return_value = {"name": "john.doe"}
        mock_user.get_or_create_user_from_auth0.return_value = mock_user_instance
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.create_user(mock_request)

        # Assert
        call_args = mock_user.get_or_create_user_from_auth0.call_args[0]
        assert call_args[1] == "john.doe"  # Name should default to email prefix

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_create_user_integrity_error_user_already_exists(self, mock_user, mock_get_payload):
        """Test create_user when user already exists (IntegrityError)"""
        # Arrange
        mock_payload = {"email": "existing@example.com", "auth0_user_id": "auth0|existing", "signup_method": "email-password", "email_verified": True}
        mock_get_payload.return_value = mock_payload
        mock_user.get_or_create_user_from_auth0.side_effect = IntegrityError("Duplicate key")
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.create_user(mock_request)

        # Assert
        assert error_message == ""
        assert data is None
        assert errors == "User already exists"

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_create_user_generic_exception(self, mock_user, mock_get_payload):
        """Test create_user when generic exception occurs"""
        # Arrange
        mock_payload = {"email": "error@example.com", "auth0_user_id": "auth0|error", "signup_method": "email-password", "email_verified": False}
        mock_get_payload.return_value = mock_payload
        mock_user.get_or_create_user_from_auth0.side_effect = Exception("Database connection failed")
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.create_user(mock_request)

        # Assert
        assert error_message == ""
        assert data is None
        assert errors == "Database connection failed"

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_create_user_with_different_signup_methods(self, mock_user, mock_get_payload):
        """Test create_user with different signup methods"""
        # Test different signup methods
        signup_methods = ["email-password", "google", "facebook", "github"]

        for method in signup_methods:
            # Arrange
            mock_payload = {"email": f"user_{method}@example.com", "auth0_user_id": f"auth0|{method}", "signup_method": method, "email_verified": True}
            mock_get_payload.return_value = mock_payload

            mock_user_instance = Mock()
            mock_user_instance.get_details.return_value = {"email": f"user_{method}@example.com"}
            mock_user.get_or_create_user_from_auth0.return_value = mock_user_instance
            mock_request = Mock()

            # Act
            error_message, data, errors = UserManagement.create_user(mock_request)

            # Assert
            assert error_message == ""
            assert errors is None
            call_args = mock_user.get_or_create_user_from_auth0.call_args[0]
            assert call_args[3] == method  # Verify signup_method is passed correctly

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_create_user_transaction_rollback_on_error(self, mock_user, mock_get_payload):
        """Test that @ssq_db.atomic() decorator handles transaction rollback"""
        # Note: This test verifies exception is properly converted to string for JSON serialization
        # Arrange
        mock_payload = {"email": "test@example.com", "auth0_user_id": "auth0|test", "signup_method": "email-password", "email_verified": False}
        mock_get_payload.return_value = mock_payload

        # Create a complex exception object
        exception = ValueError("Complex error with special chars: {}, []")
        mock_user.get_or_create_user_from_auth0.side_effect = exception
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.create_user(mock_request)

        # Assert
        assert error_message == ""
        assert data is None
        # Verify exception is converted to string (JSON serializable)
        assert isinstance(errors, str)
        assert "Complex error with special chars" in errors


class TestGetUserByEmail:
    """Test cases for get_user_by_email method"""

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_get_user_by_email_success(self, mock_user, mock_get_payload):
        """Test get_user_by_email with existing user"""
        # Arrange
        mock_payload = {"email": "found@example.com"}
        mock_get_payload.return_value = mock_payload

        mock_user_instance = Mock()
        mock_user_instance.get_details.return_value = {"name": "Found User", "email": "found@example.com", "uuid": "found-uuid"}
        mock_user.get_by_email.return_value = [mock_user_instance]
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_email(mock_request)

        # Assert
        assert error_message == ""
        assert data["name"] == "Found User"
        assert data["email"] == "found@example.com"
        assert errors is None
        mock_user.get_by_email.assert_called_once_with("found@example.com")
        mock_user_instance.get_details.assert_called_once()

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_get_user_by_email_user_not_found(self, mock_user, mock_get_payload):
        """Test get_user_by_email when user does not exist"""
        # Arrange
        mock_payload = {"email": "notfound@example.com"}
        mock_get_payload.return_value = mock_payload
        mock_user.get_by_email.return_value = None
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_email(mock_request)

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None
        mock_user.get_by_email.assert_called_once_with("notfound@example.com")

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_get_user_by_email_empty_list(self, mock_user, mock_get_payload):
        """Test get_user_by_email when query returns empty list"""
        # Arrange
        mock_payload = {"email": "empty@example.com"}
        mock_get_payload.return_value = mock_payload
        mock_user.get_by_email.return_value = []
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_email(mock_request)

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_get_user_by_email_multiple_users_returns_first(self, mock_user, mock_get_payload):
        """Test get_user_by_email returns first user when multiple exist"""
        # Arrange
        mock_payload = {"email": "duplicate@example.com"}
        mock_get_payload.return_value = mock_payload

        mock_user1 = Mock()
        mock_user1.get_details.return_value = {"name": "First User", "email": "duplicate@example.com"}
        mock_user2 = Mock()
        mock_user2.get_details.return_value = {"name": "Second User", "email": "duplicate@example.com"}

        mock_user.get_by_email.return_value = [mock_user1, mock_user2]
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_email(mock_request)

        # Assert
        assert error_message == ""
        assert data["name"] == "First User"
        assert errors is None
        # Verify only first user's get_details is called
        mock_user1.get_details.assert_called_once()
        mock_user2.get_details.assert_not_called()

    @patch("usecases.user_management.get_request_json_post_payload")
    @patch("usecases.user_management.User")
    def test_get_user_by_email_with_special_characters(self, mock_user, mock_get_payload):
        """Test get_user_by_email with email containing special characters"""
        # Arrange
        special_email = "user+test@sub.example.com"
        mock_payload = {"email": special_email}
        mock_get_payload.return_value = mock_payload

        mock_user_instance = Mock()
        mock_user_instance.get_details.return_value = {"email": special_email}
        mock_user.get_by_email.return_value = [mock_user_instance]
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_email(mock_request)

        # Assert
        assert error_message == ""
        assert data["email"] == special_email
        mock_user.get_by_email.assert_called_once_with(special_email)


class TestGetUserByUuid:
    """Test cases for get_user_by_uuid method"""

    @patch("usecases.user_management.is_valid_uuid_v4")
    @patch("usecases.user_management.User")
    def test_get_user_by_uuid_success(self, mock_user, mock_is_valid_uuid):
        """Test get_user_by_uuid with valid UUID and existing user"""
        # Arrange
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_is_valid_uuid.return_value = True

        mock_user_instance = Mock()
        mock_user_instance.get_details.return_value = {"name": "UUID User", "email": "uuid@example.com", "uuid": valid_uuid}
        mock_user.get_by_uuid.return_value = [mock_user_instance]
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_uuid(mock_request, valid_uuid)

        # Assert
        assert error_message == ""
        assert "user" in data
        assert data["user"]["name"] == "UUID User"
        assert data["user"]["uuid"] == valid_uuid
        assert errors is None
        mock_is_valid_uuid.assert_called_once_with(valid_uuid)
        mock_user.get_by_uuid.assert_called_once_with(valid_uuid)

    @patch("usecases.user_management.is_valid_uuid_v4")
    @patch("usecases.user_management.User")
    def test_get_user_by_uuid_invalid_uuid_format(self, mock_user, mock_is_valid_uuid):
        """Test get_user_by_uuid with invalid UUID format"""
        # Arrange
        invalid_uuid = "not-a-valid-uuid"
        mock_is_valid_uuid.return_value = False
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_uuid(mock_request, invalid_uuid)

        # Assert
        assert error_message == INVALID_RESOURCE_ID
        assert data is None
        assert errors is None
        mock_is_valid_uuid.assert_called_once_with(invalid_uuid)
        # User.get_by_uuid should not be called for invalid UUID
        mock_user.get_by_uuid.assert_not_called()

    @patch("usecases.user_management.is_valid_uuid_v4")
    @patch("usecases.user_management.User")
    def test_get_user_by_uuid_user_not_found(self, mock_user, mock_is_valid_uuid):
        """Test get_user_by_uuid when user does not exist"""
        # Arrange
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_is_valid_uuid.return_value = True
        mock_user.get_by_uuid.return_value = None
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_uuid(mock_request, valid_uuid)

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None
        mock_user.get_by_uuid.assert_called_once_with(valid_uuid)

    @patch("usecases.user_management.is_valid_uuid_v4")
    @patch("usecases.user_management.User")
    def test_get_user_by_uuid_empty_list(self, mock_user, mock_is_valid_uuid):
        """Test get_user_by_uuid when query returns empty list"""
        # Arrange
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_is_valid_uuid.return_value = True
        mock_user.get_by_uuid.return_value = []
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_uuid(mock_request, valid_uuid)

        # Assert
        assert error_message == RESOURCE_NOT_FOUND
        assert data is None
        assert errors is None

    @patch("usecases.user_management.is_valid_uuid_v4")
    @patch("usecases.user_management.User")
    def test_get_user_by_uuid_validation_happens_before_query(self, mock_user, mock_is_valid_uuid):
        """Test that UUID validation happens before database query"""
        # Arrange
        invalid_uuid = "12345"
        mock_is_valid_uuid.return_value = False
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_uuid(mock_request, invalid_uuid)

        # Assert
        assert error_message == INVALID_RESOURCE_ID
        # Verify validation was called
        mock_is_valid_uuid.assert_called_once()
        # Verify database query was NOT called (optimization check)
        mock_user.get_by_uuid.assert_not_called()

    @patch("usecases.user_management.is_valid_uuid_v4")
    @patch("usecases.user_management.User")
    def test_get_user_by_uuid_returns_first_user_from_list(self, mock_user, mock_is_valid_uuid):
        """Test get_user_by_uuid returns first user when list has multiple items"""
        # Arrange
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_is_valid_uuid.return_value = True

        mock_user1 = Mock()
        mock_user1.get_details.return_value = {"name": "First User"}
        mock_user2 = Mock()
        mock_user2.get_details.return_value = {"name": "Second User"}

        mock_user.get_by_uuid.return_value = [mock_user1, mock_user2]
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_uuid(mock_request, valid_uuid)

        # Assert
        assert error_message == ""
        assert data["user"]["name"] == "First User"
        mock_user1.get_details.assert_called_once()
        mock_user2.get_details.assert_not_called()

    @patch("usecases.user_management.is_valid_uuid_v4")
    @patch("usecases.user_management.User")
    def test_get_user_by_uuid_with_uuid_v1_format(self, mock_user, mock_is_valid_uuid):
        """Test get_user_by_uuid rejects non-v4 UUIDs"""
        # Arrange - UUID v1 format (not v4)
        uuid_v1 = "550e8400-e29b-11d4-a716-446655440000"
        mock_is_valid_uuid.return_value = False  # is_valid_uuid_v4 only accepts v4
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_user_by_uuid(mock_request, uuid_v1)

        # Assert
        assert error_message == INVALID_RESOURCE_ID
        assert data is None
        mock_user.get_by_uuid.assert_not_called()


class TestGetUsers:
    """Test cases for get_users method"""

    @patch("usecases.user_management.User")
    def test_get_users_success(self, mock_user):
        """Test get_users returns list of users"""
        # Arrange
        mock_user1 = Mock()
        mock_user1.get_details.return_value = {"name": "User 1", "email": "user1@example.com", "uuid": "uuid-1"}
        mock_user2 = Mock()
        mock_user2.get_details.return_value = {"name": "User 2", "email": "user2@example.com", "uuid": "uuid-2"}
        mock_user3 = Mock()
        mock_user3.get_details.return_value = {"name": "User 3", "email": "user3@example.com", "uuid": "uuid-3"}

        mock_user.get_all_users.return_value = [mock_user1, mock_user2, mock_user3]
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_users(mock_request)

        # Assert
        assert error_message == ""
        assert "users" in data
        assert len(data["users"]) == 3
        assert data["users"][0]["name"] == "User 1"
        assert data["users"][1]["name"] == "User 2"
        assert data["users"][2]["name"] == "User 3"
        assert errors is None
        mock_user.get_all_users.assert_called_once()

    @patch("usecases.user_management.User")
    def test_get_users_no_users_found(self, mock_user):
        """Test get_users when no users exist"""
        # Arrange
        mock_user.get_all_users.return_value = None
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_users(mock_request)

        # Assert
        assert error_message == "No users found"
        assert data is None
        assert errors is None
        mock_user.get_all_users.assert_called_once()

    @patch("usecases.user_management.User")
    def test_get_users_empty_list(self, mock_user):
        """Test get_users when database returns empty list"""
        # Arrange
        mock_user.get_all_users.return_value = []
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_users(mock_request)

        # Assert
        assert error_message == "No users found"
        assert data is None
        assert errors is None

    @patch("usecases.user_management.User")
    def test_get_users_single_user(self, mock_user):
        """Test get_users with single user in database"""
        # Arrange
        mock_user_instance = Mock()
        mock_user_instance.get_details.return_value = {"name": "Only User", "email": "only@example.com"}
        mock_user.get_all_users.return_value = [mock_user_instance]
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_users(mock_request)

        # Assert
        assert error_message == ""
        assert len(data["users"]) == 1
        assert data["users"][0]["name"] == "Only User"
        assert errors is None

    @patch("usecases.user_management.User")
    def test_get_users_calls_get_details_for_each_user(self, mock_user):
        """Test get_users calls get_details for each user"""
        # Arrange
        mock_users = [Mock(), Mock(), Mock(), Mock(), Mock()]
        for i, user in enumerate(mock_users):
            user.get_details.return_value = {"name": f"User {i}"}

        mock_user.get_all_users.return_value = mock_users
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_users(mock_request)

        # Assert
        assert len(data["users"]) == 5
        # Verify get_details was called for each user
        for user in mock_users:
            user.get_details.assert_called_once()

    @patch("usecases.user_management.User")
    def test_get_users_preserves_user_order(self, mock_user):
        """Test get_users preserves order of users from database"""
        # Arrange
        mock_users = []
        for i in range(10):
            mock_user_instance = Mock()
            mock_user_instance.get_details.return_value = {"name": f"User {i}", "order": i}
            mock_users.append(mock_user_instance)

        mock_user.get_all_users.return_value = mock_users
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_users(mock_request)

        # Assert
        assert len(data["users"]) == 10
        for i, user_data in enumerate(data["users"]):
            assert user_data["order"] == i

    @patch("usecases.user_management.User")
    def test_get_users_with_all_user_fields(self, mock_user):
        """Test get_users returns all user detail fields for each user"""
        # Arrange
        mock_user_instance = Mock()
        mock_user_instance.get_details.return_value = {
            "name": "Complete User",
            "email": "complete@example.com",
            "signup_method": "google",
            "email_verified": True,
            "created_at": "2025-01-01T00:00:00",
            "uuid": "complete-uuid",
            "role": "brand",
            "content_categories": ["tech"],
            "status": "active",
        }
        mock_user.get_all_users.return_value = [mock_user_instance]
        mock_request = Mock()

        # Act
        error_message, data, errors = UserManagement.get_users(mock_request)

        # Assert
        assert error_message == ""
        user = data["users"][0]
        assert user["name"] == "Complete User"
        assert user["email"] == "complete@example.com"
        assert user["signup_method"] == "google"
        assert user["email_verified"] is True
        assert user["role"] == "brand"
        assert user["content_categories"] == ["tech"]
        assert user["status"] == "active"
