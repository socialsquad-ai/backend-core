"""
Unit tests for data_adapter/user.py

Tests cover all methods in the User model including:
- update_values
- get_by_email
- get_by_auth0_user_id
- get_or_create_user_from_auth0
- get_all_users
- get_details
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from data_adapter.user import User


class TestUpdateValues:
    """Test cases for update_values method"""

    def test_update_values_single_field(self):
        """Test updating a single field"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.name = "Old Name"

        # Bind the method to the instance
        mock_user.update_values = User.update_values.__get__(mock_user, User)

        # Act
        mock_user.update_values(name="New Name")

        # Assert
        assert mock_user.name == "New Name"
        mock_user.save.assert_called_once()

    def test_update_values_multiple_fields(self):
        """Test updating multiple fields at once"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.name = "Old Name"
        mock_user.email = "old@example.com"
        mock_user.status = "old_status"

        # Bind the method to the instance
        mock_user.update_values = User.update_values.__get__(mock_user, User)

        # Act
        mock_user.update_values(name="New Name", email="new@example.com", status="new_status")

        # Assert
        assert mock_user.name == "New Name"
        assert mock_user.email == "new@example.com"
        assert mock_user.status == "new_status"
        mock_user.save.assert_called_once()

    def test_update_values_no_fields(self):
        """Test calling update_values with no fields"""
        # Arrange
        mock_user = Mock(spec=User)

        # Bind the method to the instance
        mock_user.update_values = User.update_values.__get__(mock_user, User)

        # Act
        mock_user.update_values()

        # Assert
        mock_user.save.assert_called_once()


class TestGetByEmail:
    """Test cases for get_by_email method"""

    @patch.object(User, "select_query")
    def test_get_by_email_success(self, mock_select_query):
        """Test getting user by email"""
        # Arrange
        mock_user = Mock(email="test@example.com")
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = [mock_user]
        mock_select_query.return_value = mock_query

        # Act
        _result = User.get_by_email("test@example.com")

        # Assert
        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_query.where.return_value.limit.assert_called_once_with(1)

    @patch.object(User, "select_query")
    def test_get_by_email_not_found(self, mock_select_query):
        """Test getting user with non-existent email"""
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = User.get_by_email("nonexistent@example.com")

        # Assert
        assert result == []

    @patch.object(User, "select_query")
    def test_get_by_email_case_sensitivity(self, mock_select_query):
        """Test email lookup (exact match)"""
        # Arrange
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        User.get_by_email("Test@Example.com")

        # Assert
        mock_query.where.assert_called_once()


class TestGetByAuth0UserId:
    """Test cases for get_by_auth0_user_id method"""

    @patch.object(User, "select_query")
    def test_get_by_auth0_user_id_success(self, mock_select_query):
        """Test getting user by Auth0 user ID"""
        # Arrange
        mock_user = Mock(auth0_user_id="auth0|123456")
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = [mock_user]
        mock_select_query.return_value = mock_query

        # Act
        result = User.get_by_auth0_user_id("auth0|123456")

        # Assert
        assert result == mock_user

    @patch.object(User, "select_query")
    def test_get_by_auth0_user_id_not_found(self, mock_select_query):
        """Test getting user with invalid Auth0 ID"""
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = User.get_by_auth0_user_id("invalid_id")

        # Assert
        assert result is None

    @patch.object(User, "select_query")
    def test_get_by_auth0_user_id_returns_first_result(self, mock_select_query):
        """Test that method returns first result from list"""
        # Arrange
        mock_user1 = Mock(auth0_user_id="auth0|123")
        mock_user2 = Mock(auth0_user_id="auth0|123")
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = [mock_user1, mock_user2]
        mock_select_query.return_value = mock_query

        # Act
        result = User.get_by_auth0_user_id("auth0|123")

        # Assert
        assert result == mock_user1


class TestGetOrCreateUserFromAuth0:
    """Test cases for get_or_create_user_from_auth0 method"""

    @patch("data_adapter.user.parse_timestamp")
    @patch.object(User, "create")
    def test_get_or_create_user_email_password_signup(self, mock_create, mock_parse_timestamp):
        """Test creating user with email-password signup method"""
        # Arrange
        mock_user = Mock(id=1)
        mock_create.return_value = mock_user
        mock_parse_timestamp.return_value = datetime(2024, 1, 1, 12, 0, 0)

        # Act
        result = User.get_or_create_user_from_auth0(auth0_user_id="auth0|123", name="Test User", email="test@example.com", signup_method="email-password", email_verified=False, auth0_created_at="2024-01-01T12:00:00Z")

        # Assert
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["status"] == "verification_pending"
        assert call_kwargs["role"] == "brand"
        assert call_kwargs["content_categories"] == []
        assert result == mock_user

    @patch("data_adapter.user.parse_timestamp")
    @patch.object(User, "create")
    def test_get_or_create_user_google_signup(self, mock_create, mock_parse_timestamp):
        """Test creating user with Google signup method"""
        # Arrange
        mock_user = Mock(id=1)
        mock_create.return_value = mock_user
        mock_parse_timestamp.return_value = datetime(2024, 1, 1, 12, 0, 0)

        # Act
        _result = User.get_or_create_user_from_auth0(auth0_user_id="google|123", name="Google User", email="google@example.com", signup_method="google", email_verified=True, auth0_created_at="2024-01-01T12:00:00Z")

        # Assert
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["status"] == "onboarding"
        assert call_kwargs["email_verified"] is True

    @patch("data_adapter.user.parse_timestamp")
    @patch.object(User, "create")
    def test_get_or_create_user_facebook_signup(self, mock_create, mock_parse_timestamp):
        """Test creating user with Facebook signup method"""
        # Arrange
        mock_user = Mock(id=1)
        mock_create.return_value = mock_user
        mock_parse_timestamp.return_value = datetime(2024, 1, 1, 12, 0, 0)

        # Act
        _result = User.get_or_create_user_from_auth0(
            auth0_user_id="facebook|123", name="Facebook User", email="facebook@example.com", signup_method="facebook", email_verified=True, auth0_created_at="2024-01-01T12:00:00Z"
        )

        # Assert
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["status"] == "onboarding"
        assert call_kwargs["signup_method"] == "facebook"

    @patch("data_adapter.user.parse_timestamp")
    @patch.object(User, "create")
    def test_get_or_create_user_parses_timestamp(self, mock_create, mock_parse_timestamp):
        """Test that auth0_created_at is parsed correctly"""
        # Arrange
        mock_user = Mock(id=1)
        mock_create.return_value = mock_user
        parsed_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_parse_timestamp.return_value = parsed_time

        # Act
        _result = User.get_or_create_user_from_auth0(auth0_user_id="auth0|123", name="Test User", email="test@example.com", signup_method="email-password", email_verified=False, auth0_created_at="2024-01-01T12:00:00Z")

        # Assert
        mock_parse_timestamp.assert_called_once_with("2024-01-01T12:00:00Z")
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["auth0_created_at"] == parsed_time

    @patch("data_adapter.user.parse_timestamp")
    @patch.object(User, "create")
    def test_get_or_create_user_exception_handling(self, mock_create, mock_parse_timestamp):
        """Test exception is re-raised"""
        # Arrange
        mock_parse_timestamp.return_value = datetime(2024, 1, 1, 12, 0, 0)
        mock_create.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            User.get_or_create_user_from_auth0(auth0_user_id="auth0|123", name="Test User", email="test@example.com", signup_method="email-password", email_verified=False, auth0_created_at="2024-01-01T12:00:00Z")


class TestGetAllUsers:
    """Test cases for get_all_users method"""

    @patch.object(User, "select_query")
    def test_get_all_users_success(self, mock_select_query):
        """Test getting all users with limit"""
        # Arrange
        mock_users = [Mock(id=1), Mock(id=2), Mock(id=3)]
        mock_query = Mock()
        mock_query.limit.return_value = mock_users
        mock_select_query.return_value = mock_query

        # Act
        result = User.get_all_users()

        # Assert
        mock_select_query.assert_called_once()
        mock_query.limit.assert_called_once_with(100)
        assert result == mock_users

    @patch.object(User, "select_query")
    def test_get_all_users_empty_database(self, mock_select_query):
        """Test getting users when none exist"""
        # Arrange
        mock_query = Mock()
        mock_query.limit.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = User.get_all_users()

        # Assert
        assert result == []

    @patch.object(User, "select_query")
    def test_get_all_users_respects_limit(self, mock_select_query):
        """Test that get_all_users respects 100 user limit"""
        # Arrange
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        User.get_all_users()

        # Assert
        mock_query.limit.assert_called_once_with(100)


class TestGetDetails:
    """Test cases for get_details method"""

    def test_get_details_with_auth0_created_at(self):
        """Test get_details when auth0_created_at is set"""
        # Arrange
        auth0_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_user = Mock(spec=User)
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.signup_method = "google"
        mock_user.email_verified = True
        mock_user.auth0_created_at = auth0_time
        mock_user.created_at = datetime(2024, 1, 1, 12, 5, 0)
        mock_user.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_user.role = "brand"
        mock_user.content_categories = ["tech", "business"]
        mock_user.status = "active"

        # Bind the method to the instance
        mock_user.get_details = User.get_details.__get__(mock_user, User)

        # Act
        result = mock_user.get_details()

        # Assert
        assert result["name"] == "Test User"
        assert result["email"] == "test@example.com"
        assert result["signup_method"] == "google"
        assert result["email_verified"] is True
        assert result["created_at"] == auth0_time.isoformat()
        assert result["uuid"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["role"] == "brand"
        assert result["content_categories"] == ["tech", "business"]
        assert result["status"] == "active"

    def test_get_details_without_auth0_created_at(self):
        """Test get_details when auth0_created_at is None"""
        # Arrange
        created_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_user = Mock(spec=User)
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.signup_method = "email-password"
        mock_user.email_verified = False
        mock_user.auth0_created_at = None
        mock_user.created_at = created_time
        mock_user.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_user.role = "brand"
        mock_user.content_categories = []
        mock_user.status = "verification_pending"

        # Bind the method to the instance
        mock_user.get_details = User.get_details.__get__(mock_user, User)

        # Act
        result = mock_user.get_details()

        # Assert
        assert result["created_at"] == created_time.isoformat()
        assert result["email_verified"] is False

    def test_get_details_all_fields_present(self):
        """Test that get_details returns all required fields"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.name = "Test"
        mock_user.email = "test@test.com"
        mock_user.signup_method = "email-password"
        mock_user.email_verified = True
        mock_user.auth0_created_at = None
        mock_user.created_at = datetime.now()
        mock_user.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_user.role = "brand"
        mock_user.content_categories = []
        mock_user.status = "active"

        # Bind the method to the instance
        mock_user.get_details = User.get_details.__get__(mock_user, User)

        # Act
        result = mock_user.get_details()

        # Assert
        required_fields = ["name", "email", "signup_method", "email_verified", "created_at", "uuid", "role", "content_categories", "status"]
        for field in required_fields:
            assert field in result

    def test_get_details_empty_content_categories(self):
        """Test get_details with empty content categories"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.name = "Test"
        mock_user.email = "test@test.com"
        mock_user.signup_method = "email-password"
        mock_user.email_verified = True
        mock_user.auth0_created_at = None
        mock_user.created_at = datetime.now()
        mock_user.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_user.role = "brand"
        mock_user.content_categories = []
        mock_user.status = "onboarding"

        # Bind the method to the instance
        mock_user.get_details = User.get_details.__get__(mock_user, User)

        # Act
        result = mock_user.get_details()

        # Assert
        assert result["content_categories"] == []

    def test_get_details_multiple_content_categories(self):
        """Test get_details with multiple content categories"""
        # Arrange
        mock_user = Mock(spec=User)
        mock_user.name = "Test"
        mock_user.email = "test@test.com"
        mock_user.signup_method = "google"
        mock_user.email_verified = True
        mock_user.auth0_created_at = datetime.now()
        mock_user.created_at = datetime.now()
        mock_user.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_user.role = "brand"
        mock_user.content_categories = ["tech", "business", "finance", "marketing"]
        mock_user.status = "active"

        # Bind the method to the instance
        mock_user.get_details = User.get_details.__get__(mock_user, User)

        # Act
        result = mock_user.get_details()

        # Assert
        assert len(result["content_categories"]) == 4
        assert "tech" in result["content_categories"]
