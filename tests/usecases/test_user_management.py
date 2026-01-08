from unittest.mock import Mock, patch

from peewee import IntegrityError

from usecases.user_management import UserManagement


class TestUserManagementGetProfile:
    @patch("usecases.user_management.get_context_user")
    def test_get_profile_returns_user_details(self, mock_get_context_user):
        mock_user = Mock()
        mock_user.get_details.return_value = {"name": "John", "email": "john@example.com"}
        mock_get_context_user.return_value = mock_user

        mock_request = Mock()
        error, data, errors = UserManagement.get_profile(mock_request)

        assert error == ""
        assert data == {"name": "John", "email": "john@example.com"}
        assert errors is None

    @patch("usecases.user_management.get_context_user")
    def test_get_profile_returns_error_when_no_user(self, mock_get_context_user):
        mock_get_context_user.return_value = None

        mock_request = Mock()
        error, data, errors = UserManagement.get_profile(mock_request)

        assert error == "Not found"
        assert data is None
        assert errors is None


class TestUserManagementCreateUser:
    @patch("data_adapter.db.ssq_db.is_closed", return_value=False)
    @patch("data_adapter.db.ssq_db.connect")
    @patch("data_adapter.db.ssq_db.begin")
    @patch("data_adapter.db.ssq_db.commit")
    @patch("usecases.user_management.User.get_or_create_user_from_auth0")
    @patch("usecases.user_management.get_request_json_post_payload")
    def test_create_user_success(self, mock_get_payload, mock_get_or_create, mock_commit, mock_begin, mock_connect, mock_is_closed):
        mock_get_payload.return_value = {
            "email": "test@example.com",
            "auth0_user_id": "auth0|123",
            "name": "Test User",
            "signup_method": "google",
            "email_verified": True,
            "auth0_created_at": "2024-01-01T00:00:00Z",
        }

        mock_user = Mock()
        mock_user.get_details.return_value = {"email": "test@example.com"}
        mock_get_or_create.return_value = mock_user

        mock_request = Mock()
        error, data, errors = UserManagement.create_user(mock_request)

        assert error == ""
        assert data == {"email": "test@example.com"}
        assert errors is None

    @patch("data_adapter.db.ssq_db.is_closed", return_value=False)
    @patch("data_adapter.db.ssq_db.connect")
    @patch("data_adapter.db.ssq_db.begin")
    @patch("data_adapter.db.ssq_db.commit")
    @patch("usecases.user_management.User.get_or_create_user_from_auth0")
    @patch("usecases.user_management.get_request_json_post_payload")
    def test_create_user_uses_email_prefix_when_no_name(self, mock_get_payload, mock_get_or_create, mock_commit, mock_begin, mock_connect, mock_is_closed):
        mock_get_payload.return_value = {
            "email": "john.doe@example.com",
            "auth0_user_id": "auth0|123",
            "signup_method": "email-password",
            "email_verified": False,
        }

        mock_user = Mock()
        mock_user.get_details.return_value = {}
        mock_get_or_create.return_value = mock_user

        mock_request = Mock()
        UserManagement.create_user(mock_request)

        call_args = mock_get_or_create.call_args[0]
        assert call_args[1] == "john.doe"  # name extracted from email

    @patch("data_adapter.db.ssq_db.is_closed", return_value=False)
    @patch("data_adapter.db.ssq_db.connect")
    @patch("data_adapter.db.ssq_db.begin")
    @patch("data_adapter.db.ssq_db.commit")
    @patch("usecases.user_management.User.get_or_create_user_from_auth0")
    @patch("usecases.user_management.get_request_json_post_payload")
    def test_create_user_handles_integrity_error(self, mock_get_payload, mock_get_or_create, mock_commit, mock_begin, mock_connect, mock_is_closed):
        mock_get_payload.return_value = {
            "email": "duplicate@example.com",
            "auth0_user_id": "auth0|123",
            "signup_method": "google",
            "email_verified": True,
        }

        mock_get_or_create.side_effect = IntegrityError()

        mock_request = Mock()
        error, data, errors = UserManagement.create_user(mock_request)

        assert error == ""
        assert data is None
        assert errors == "User already exists"

    @patch("data_adapter.db.ssq_db.is_closed", return_value=False)
    @patch("data_adapter.db.ssq_db.connect")
    @patch("data_adapter.db.ssq_db.begin")
    @patch("data_adapter.db.ssq_db.commit")
    @patch("usecases.user_management.User.get_or_create_user_from_auth0")
    @patch("usecases.user_management.get_request_json_post_payload")
    def test_create_user_handles_generic_exception(self, mock_get_payload, mock_get_or_create, mock_commit, mock_begin, mock_connect, mock_is_closed):
        mock_get_payload.return_value = {
            "email": "test@example.com",
            "auth0_user_id": "auth0|123",
            "signup_method": "google",
            "email_verified": True,
        }

        mock_get_or_create.side_effect = Exception("Database error")

        mock_request = Mock()
        error, data, errors = UserManagement.create_user(mock_request)

        assert error == ""
        assert data is None
        assert errors == "Database error"


class TestUserManagementGetUserByEmail:
    @patch("usecases.user_management.User.get_by_email")
    @patch("usecases.user_management.get_request_json_post_payload")
    def test_get_user_by_email_returns_user(self, mock_get_payload, mock_get_by_email):
        mock_get_payload.return_value = {"email": "test@example.com"}

        mock_user = Mock()
        mock_user.get_details.return_value = {"email": "test@example.com", "name": "Test"}
        mock_get_by_email.return_value = [mock_user]

        mock_request = Mock()
        error, data, errors = UserManagement.get_user_by_email(mock_request)

        assert error == ""
        assert data == {"email": "test@example.com", "name": "Test"}
        assert errors is None

    @patch("usecases.user_management.User.get_by_email")
    @patch("usecases.user_management.get_request_json_post_payload")
    def test_get_user_by_email_returns_not_found(self, mock_get_payload, mock_get_by_email):
        mock_get_payload.return_value = {"email": "nonexistent@example.com"}
        mock_get_by_email.return_value = None

        mock_request = Mock()
        error, data, errors = UserManagement.get_user_by_email(mock_request)

        assert error == "Not found"
        assert data is None
        assert errors is None


class TestUserManagementGetUserByUuid:
    @patch("usecases.user_management.User.get_by_uuid")
    @patch("usecases.user_management.is_valid_uuid_v4")
    def test_get_user_by_uuid_returns_user(self, mock_is_valid, mock_get_by_uuid):
        mock_is_valid.return_value = True

        mock_user = Mock()
        mock_user.get_details.return_value = {"uuid": "valid-uuid", "name": "Test"}
        mock_get_by_uuid.return_value = [mock_user]

        mock_request = Mock()
        error, data, errors = UserManagement.get_user_by_uuid(mock_request, "valid-uuid")

        assert error == ""
        assert data == {"user": {"uuid": "valid-uuid", "name": "Test"}}
        assert errors is None

    @patch("usecases.user_management.User.get_by_uuid")
    @patch("usecases.user_management.is_valid_uuid_v4")
    def test_get_user_by_uuid_invalid_uuid(self, mock_is_valid, mock_get_by_uuid):
        mock_is_valid.return_value = False

        mock_request = Mock()
        error, data, errors = UserManagement.get_user_by_uuid(mock_request, "invalid")

        assert error == "Invalid ID"
        assert data is None
        assert errors is None

    @patch("usecases.user_management.User.get_by_uuid")
    @patch("usecases.user_management.is_valid_uuid_v4")
    def test_get_user_by_uuid_not_found(self, mock_is_valid, mock_get_by_uuid):
        mock_is_valid.return_value = True
        mock_get_by_uuid.return_value = None

        mock_request = Mock()
        error, data, errors = UserManagement.get_user_by_uuid(mock_request, "valid-uuid")

        assert error == "Not found"
        assert data is None
        assert errors is None


class TestUserManagementGetUsers:
    @patch("usecases.user_management.User.get_all_users")
    def test_get_users_returns_list(self, mock_get_all_users):
        mock_user1 = Mock()
        mock_user1.get_details.return_value = {"uuid": "uuid1", "name": "User1"}
        mock_user2 = Mock()
        mock_user2.get_details.return_value = {"uuid": "uuid2", "name": "User2"}

        mock_get_all_users.return_value = [mock_user1, mock_user2]

        mock_request = Mock()
        error, data, errors = UserManagement.get_users(mock_request)

        assert error == ""
        assert data == {"users": [{"uuid": "uuid1", "name": "User1"}, {"uuid": "uuid2", "name": "User2"}]}
        assert errors is None

    @patch("usecases.user_management.User.get_all_users")
    def test_get_users_returns_error_when_no_users(self, mock_get_all_users):
        mock_get_all_users.return_value = None

        mock_request = Mock()
        error, data, errors = UserManagement.get_users(mock_request)

        assert error == "No users found"
        assert data is None
        assert errors is None
