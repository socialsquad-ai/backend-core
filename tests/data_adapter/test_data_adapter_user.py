from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from data_adapter.user import User


class TestUserUpdateValues:
    @patch.object(User, "save")
    def test_update_values_sets_attributes(self, mock_save):
        user = User()
        user.update_values(name="John Doe", email="john@example.com")

        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        mock_save.assert_called_once()

    @patch.object(User, "save")
    def test_update_values_multiple_attributes(self, mock_save):
        user = User()
        user.update_values(name="Jane", email="jane@example.com", status="active", role="admin")

        assert user.name == "Jane"
        assert user.email == "jane@example.com"
        assert user.status == "active"
        assert user.role == "admin"
        mock_save.assert_called_once()

    @patch.object(User, "save")
    def test_update_values_calls_save(self, mock_save):
        user = User()
        user.update_values(name="Test")

        mock_save.assert_called_once()


class TestUserGetByEmail:
    @patch.object(User, "select_query")
    def test_get_by_email_queries_correctly(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = []

        User.get_by_email("test@example.com")

        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_where.limit.assert_called_once_with(1)

    @patch.object(User, "select_query")
    def test_get_by_email_returns_result(self, mock_select_query):
        mock_user = Mock()
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = [mock_user]

        result = User.get_by_email("test@example.com")

        assert result == [mock_user]


class TestUserGetByAuth0UserId:
    @patch.object(User, "select_query")
    def test_get_by_auth0_user_id_returns_user_when_found(self, mock_select_query):
        mock_user = Mock()
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = [mock_user]

        result = User.get_by_auth0_user_id("auth0|123")

        assert result == mock_user
        mock_select_query.assert_called_once()

    @patch.object(User, "select_query")
    def test_get_by_auth0_user_id_returns_none_when_not_found(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = []

        result = User.get_by_auth0_user_id("auth0|nonexistent")

        assert result is None

    @patch.object(User, "select_query")
    def test_get_by_auth0_user_id_limits_to_one(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = []

        User.get_by_auth0_user_id("auth0|123")

        mock_where.limit.assert_called_once_with(1)


class TestUserGetOrCreateUserFromAuth0:
    @patch("data_adapter.user.parse_timestamp")
    @patch.object(User, "create")
    def test_get_or_create_user_from_auth0_with_email_password(self, mock_create, mock_parse_timestamp):
        mock_user = Mock()
        mock_create.return_value = mock_user
        mock_parse_timestamp.return_value = datetime(2024, 1, 1)

        result = User.get_or_create_user_from_auth0(auth0_user_id="auth0|123", name="John Doe", email="john@example.com", signup_method="email-password", email_verified=False, auth0_created_at="2024-01-01T00:00:00Z")

        assert result == mock_user
        mock_create.assert_called_once_with(
            auth0_user_id="auth0|123",
            name="John Doe",
            email="john@example.com",
            signup_method="email-password",
            email_verified=False,
            auth0_created_at=datetime(2024, 1, 1),
            status="verification_pending",
            role="brand",
            content_categories=[],
        )

    @patch("data_adapter.user.parse_timestamp")
    @patch.object(User, "create")
    def test_get_or_create_user_from_auth0_with_oauth(self, mock_create, mock_parse_timestamp):
        mock_user = Mock()
        mock_create.return_value = mock_user
        mock_parse_timestamp.return_value = datetime(2024, 1, 1)

        result = User.get_or_create_user_from_auth0(auth0_user_id="google|123", name="Jane Doe", email="jane@example.com", signup_method="google", email_verified=True, auth0_created_at="2024-01-01T00:00:00Z")

        assert result == mock_user
        mock_create.assert_called_once_with(
            auth0_user_id="google|123",
            name="Jane Doe",
            email="jane@example.com",
            signup_method="google",
            email_verified=True,
            auth0_created_at=datetime(2024, 1, 1),
            status="onboarding",
            role="brand",
            content_categories=[],
        )

    @patch("data_adapter.user.parse_timestamp")
    @patch.object(User, "create")
    def test_get_or_create_user_from_auth0_raises_exception_on_error(self, mock_create, mock_parse_timestamp):
        mock_parse_timestamp.return_value = datetime(2024, 1, 1)
        mock_create.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            User.get_or_create_user_from_auth0(auth0_user_id="auth0|123", name="John Doe", email="john@example.com", signup_method="email-password", email_verified=False, auth0_created_at="2024-01-01T00:00:00Z")


class TestUserGetAllUsers:
    @patch.object(User, "select_query")
    def test_get_all_users_limits_to_100(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.limit.return_value = []

        User.get_all_users()

        mock_select_query.assert_called_once()
        mock_query.limit.assert_called_once_with(100)

    @patch.object(User, "select_query")
    def test_get_all_users_returns_result(self, mock_select_query):
        mock_users = [Mock(), Mock()]
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.limit.return_value = mock_users

        result = User.get_all_users()

        assert result == mock_users


class TestUserGetDetails:
    def test_get_details_returns_dict_with_auth0_created_at(self):
        user = User()
        user.name = "John Doe"
        user.email = "john@example.com"
        user.signup_method = "google"
        user.email_verified = True
        user.auth0_created_at = datetime(2024, 1, 1, 12, 0, 0)
        user.created_at = datetime(2024, 1, 2, 12, 0, 0)
        user.uuid = "test-uuid-123"
        user.role = "brand"
        user.content_categories = ["tech", "gaming"]
        user.status = "active"

        result = user.get_details()

        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"
        assert result["signup_method"] == "google"
        assert result["email_verified"] is True
        assert result["created_at"] == "2024-01-01T12:00:00"
        assert result["uuid"] == "test-uuid-123"
        assert result["role"] == "brand"
        assert result["content_categories"] == ["tech", "gaming"]
        assert result["status"] == "active"

    def test_get_details_uses_created_at_when_auth0_created_at_is_none(self):
        user = User()
        user.name = "Jane Doe"
        user.email = "jane@example.com"
        user.signup_method = "email-password"
        user.email_verified = False
        user.auth0_created_at = None
        user.created_at = datetime(2024, 1, 2, 12, 0, 0)
        user.uuid = "test-uuid-456"
        user.role = "admin"
        user.content_categories = []
        user.status = "pending"

        result = user.get_details()

        assert result["created_at"] == "2024-01-02T12:00:00"
        assert result["name"] == "Jane Doe"

    def test_get_details_returns_all_required_fields(self):
        user = User()
        user.name = "Test User"
        user.email = "test@example.com"
        user.signup_method = "email-password"
        user.email_verified = True
        user.auth0_created_at = datetime(2024, 1, 1)
        user.created_at = datetime(2024, 1, 1)
        user.uuid = "uuid-123"
        user.role = "brand"
        user.content_categories = ["sports"]
        user.status = "active"

        result = user.get_details()

        assert "name" in result
        assert "email" in result
        assert "signup_method" in result
        assert "email_verified" in result
        assert "created_at" in result
        assert "uuid" in result
        assert "role" in result
        assert "content_categories" in result
        assert "status" in result
