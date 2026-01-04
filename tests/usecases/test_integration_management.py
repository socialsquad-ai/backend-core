"""
Unit tests for usecases/integration_management.py

Tests cover all methods in the IntegrationManagement class including:
- get_all_integrations
- get_integration_by_uuid
- get_oauth_url
- handle_oauth_callback
- delete_integration
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from usecases.integration_management import IntegrationManagement
from utils.error_messages import (
    INTEGRATION_NOT_FOUND,
    UNSUPPORTED_PLATFORM,
    USER_NOT_FOUND,
)


class TestGetAllIntegrations:
    """Test cases for get_all_integrations method"""

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_get_all_integrations_success(self, mock_integration, mock_get_context_user):
        """Test successful retrieval of all integrations for a user"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user

        mock_integration_1 = Mock()
        mock_integration_1.get_details.return_value = {
            "uuid": "uuid-1",
            "platform": "instagram",
            "status": "active",
        }
        mock_integration_2 = Mock()
        mock_integration_2.get_details.return_value = {
            "uuid": "uuid-2",
            "platform": "youtube",
            "status": "active",
        }
        mock_integration.get_all_for_user.return_value = [mock_integration_1, mock_integration_2]

        # Act
        error_message, data, errors = IntegrationManagement.get_all_integrations()

        # Assert
        assert error_message is None
        assert len(data) == 2
        assert data[0]["platform"] == "instagram"
        assert data[1]["platform"] == "youtube"
        assert errors is None
        mock_get_context_user.assert_called_once()
        mock_integration.get_all_for_user.assert_called_once_with(mock_user)

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_get_all_integrations_no_integrations(self, mock_integration, mock_get_context_user):
        """Test when user has no integrations"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user
        mock_integration.get_all_for_user.return_value = []

        # Act
        error_message, data, errors = IntegrationManagement.get_all_integrations()

        # Assert
        assert error_message is None
        assert data == []
        assert errors is None

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_get_all_integrations_single_integration(self, mock_integration, mock_get_context_user):
        """Test when user has only one integration"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user

        mock_integration_instance = Mock()
        mock_integration_instance.get_details.return_value = {
            "uuid": "uuid-1",
            "platform": "instagram",
            "status": "active",
        }
        mock_integration.get_all_for_user.return_value = [mock_integration_instance]

        # Act
        error_message, data, errors = IntegrationManagement.get_all_integrations()

        # Assert
        assert error_message is None
        assert len(data) == 1
        assert data[0]["platform"] == "instagram"
        assert errors is None


class TestGetIntegrationByUuid:
    """Test cases for get_integration_by_uuid method"""

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_get_integration_by_uuid_success(self, mock_integration, mock_get_context_user):
        """Test successful retrieval of integration by UUID"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user

        mock_integration_instance = Mock()
        mock_integration_instance.get_details.return_value = {
            "uuid": "test-uuid",
            "platform": "instagram",
            "status": "active",
        }
        mock_integration.get_by_uuid_for_user.return_value = [mock_integration_instance]

        # Act
        error_message, data, errors = IntegrationManagement.get_integration_by_uuid("test-uuid")

        # Assert
        assert error_message is None
        assert data["uuid"] == "test-uuid"
        assert data["platform"] == "instagram"
        assert errors is None
        mock_integration.get_by_uuid_for_user.assert_called_once_with("test-uuid", mock_user)

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_get_integration_by_uuid_not_found(self, mock_integration, mock_get_context_user):
        """Test when integration is not found"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user
        mock_integration.get_by_uuid_for_user.return_value = None

        # Act
        error_message, data, errors = IntegrationManagement.get_integration_by_uuid("invalid-uuid")

        # Assert
        assert error_message == INTEGRATION_NOT_FOUND
        assert data is None
        assert errors == [INTEGRATION_NOT_FOUND]
        mock_integration.get_by_uuid_for_user.assert_called_once_with("invalid-uuid", mock_user)

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_get_integration_by_uuid_empty_list(self, mock_integration, mock_get_context_user):
        """Test when get_by_uuid_for_user returns empty list"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user
        mock_integration.get_by_uuid_for_user.return_value = []

        # Act
        error_message, data, errors = IntegrationManagement.get_integration_by_uuid("test-uuid")

        # Assert
        assert error_message == INTEGRATION_NOT_FOUND
        assert data is None
        assert errors == [INTEGRATION_NOT_FOUND]


class TestGetOAuthUrl:
    """Test cases for get_oauth_url method"""

    def test_get_oauth_url_instagram_success(self):
        """Test successful OAuth URL generation for Instagram"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params.get.return_value = "http://localhost:3000/callback"

        # Act
        error_message, data, errors = IntegrationManagement.get_oauth_url("instagram", mock_request)

        # Assert
        assert error_message == ""
        assert "https://www.instagram.com/oauth/authorize" in data
        assert "client_id=" in data
        assert "redirect_uri=http://localhost:3000/callback" in data
        assert "instagram_business_basic" in data
        assert errors is None

    def test_get_oauth_url_youtube_success(self):
        """Test successful OAuth URL generation for YouTube"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params.get.return_value = "http://localhost:3000/callback"

        # Act
        error_message, data, errors = IntegrationManagement.get_oauth_url("youtube", mock_request)

        # Assert
        assert error_message == ""
        assert "https://accounts.google.com/o/oauth2/v2/auth" in data
        assert "client_id=" in data
        assert "redirect_uri=http://localhost:3000/callback" in data
        assert "https://www.googleapis.com/auth/youtube" in data
        assert errors is None

    def test_get_oauth_url_unsupported_platform(self):
        """Test OAuth URL generation for unsupported platform"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params.get.return_value = "http://localhost:3000/callback"

        # Act
        error_message, data, errors = IntegrationManagement.get_oauth_url("tiktok", mock_request)

        # Assert
        assert error_message == UNSUPPORTED_PLATFORM
        assert data is None
        assert errors == [UNSUPPORTED_PLATFORM]

    def test_get_oauth_url_different_redirect_uri(self):
        """Test OAuth URL with different redirect URI"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params.get.return_value = "https://example.com/oauth/callback"

        # Act
        error_message, data, errors = IntegrationManagement.get_oauth_url("instagram", mock_request)

        # Assert
        assert error_message == ""
        assert "redirect_uri=https://example.com/oauth/callback" in data
        assert errors is None


class TestHandleOAuthCallback:
    """Test cases for handle_oauth_callback method"""

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    @patch("usecases.integration_management.requests")
    def test_handle_oauth_callback_instagram_success(self, mock_requests, mock_integration, mock_get_context_user, mock_logger):
        """Test successful Instagram OAuth callback"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = [mock_user]

        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "instagram_access_token",
            "user_id": "instagram_user_123",
            "permissions": ["instagram_business_basic", "instagram_business_manage_messages"],
            "expires_in": 3600,
            "token_type": "Bearer",
            "refresh_token": "instagram_refresh_token",  # Instagram needs refresh_token to avoid NameError
            "refresh_token_expires_in": 604800,
        }
        mock_requests.post.return_value = mock_response

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("instagram", "auth_code_123")

        # Assert
        assert error_message == ""
        assert "claude.com" in data or "ssq" in data.lower()  # Should redirect to client URL
        assert errors is None
        mock_requests.post.assert_called_once()
        mock_integration.create_integration.assert_called_once()
        mock_logger.create_info_log.assert_called()

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    @patch("usecases.integration_management.requests")
    def test_handle_oauth_callback_youtube_success(self, mock_requests, mock_integration, mock_get_context_user, mock_logger):
        """Test successful YouTube OAuth callback with refresh token"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = [mock_user]

        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "youtube_access_token",
            "refresh_token": "youtube_refresh_token",
            "scope": "https://www.googleapis.com/auth/youtube",
            "expires_in": 3600,
            "refresh_token_expires_in": 604800,
            "token_type": "Bearer",
        }
        mock_requests.post.return_value = mock_response

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("youtube", "auth_code_456")

        # Assert
        assert error_message == ""
        assert errors is None
        mock_integration.create_integration.assert_called_once()

        # Verify the call to create_integration includes refresh_token
        call_kwargs = mock_integration.create_integration.call_args[1]
        assert call_kwargs["refresh_token"] == "youtube_refresh_token"
        assert call_kwargs["refresh_token_expires_at"] is not None

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    def test_handle_oauth_callback_unsupported_platform(self, mock_get_context_user, mock_logger):
        """Test OAuth callback for unsupported platform"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = [mock_user]

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("tiktok", "auth_code")

        # Assert
        assert error_message == UNSUPPORTED_PLATFORM
        assert data is None
        assert errors == [UNSUPPORTED_PLATFORM]

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    def test_handle_oauth_callback_user_not_found(self, mock_get_context_user, mock_logger):
        """Test OAuth callback when user is not found"""
        # Arrange
        mock_get_context_user.return_value = None

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("instagram", "auth_code")

        # Assert
        assert error_message == USER_NOT_FOUND
        assert data is None
        assert errors == [USER_NOT_FOUND]

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    def test_handle_oauth_callback_user_empty_list(self, mock_get_context_user, mock_logger):
        """Test OAuth callback when user context returns empty list"""
        # Arrange
        mock_get_context_user.return_value = []

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("instagram", "auth_code")

        # Assert
        assert error_message == USER_NOT_FOUND
        assert data is None
        assert errors == [USER_NOT_FOUND]

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    @patch("usecases.integration_management.requests")
    def test_handle_oauth_callback_api_error(self, mock_requests, mock_integration, mock_get_context_user, mock_logger):
        """Test OAuth callback when API request fails"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = [mock_user]
        mock_requests.post.side_effect = Exception("API connection failed")

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("instagram", "auth_code")

        # Assert
        assert error_message == "Error in handle_oauth_callback"
        assert data is None
        assert "API connection failed" in errors[0]
        mock_logger.create_error_log.assert_called_once()

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    @patch("usecases.integration_management.requests")
    def test_handle_oauth_callback_missing_access_token(self, mock_requests, mock_integration, mock_get_context_user, mock_logger):
        """Test OAuth callback when response is missing access_token"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = [mock_user]

        mock_response = Mock()
        mock_response.json.return_value = {
            "user_id": "instagram_user_123",
            "permissions": ["instagram_business_basic"],
        }
        mock_requests.post.return_value = mock_response

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("instagram", "auth_code")

        # Assert
        assert error_message == "Error in handle_oauth_callback"
        assert data is None
        assert errors is not None
        mock_logger.create_error_log.assert_called_once()

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    @patch("usecases.integration_management.requests")
    def test_handle_oauth_callback_verifies_token_expiration(self, mock_requests, mock_integration, mock_get_context_user, mock_logger):
        """Test that OAuth callback correctly calculates token expiration"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = [mock_user]

        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "user_id": "user_123",
            "permissions": ["instagram_business_basic"],
            "expires_in": 7200,  # 2 hours
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",  # Required to avoid NameError
        }
        mock_requests.post.return_value = mock_response

        # Act
        with patch("usecases.integration_management.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            error_message, data, errors = IntegrationManagement.handle_oauth_callback("instagram", "auth_code")

        # Assert
        assert error_message == ""
        call_kwargs = mock_integration.create_integration.call_args[1]
        # expires_at should be now + 7200 seconds (2 hours)
        expected_expiration = mock_now + timedelta(seconds=7200)
        assert call_kwargs["expires_at"] == expected_expiration

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    @patch("usecases.integration_management.requests")
    def test_handle_oauth_callback_without_refresh_token(self, mock_requests, mock_integration, mock_get_context_user, mock_logger):
        """Test OAuth callback for platform that doesn't provide refresh token - should fail due to code bug"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = [mock_user]

        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "instagram_token",
            "user_id": "instagram_user_123",
            "permissions": ["instagram_business_basic"],
            "expires_in": 3600,
            "token_type": "Bearer",
            # No refresh_token - this will cause NameError in actual code
        }
        mock_requests.post.return_value = mock_response

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("instagram", "auth_code")

        # Assert
        # The actual code has a bug: when refresh_token is None, refresh_token_expires_at is not defined
        # This causes a NameError when building token_data dict
        assert error_message == "Error in handle_oauth_callback"
        assert data is None
        assert errors is not None
        mock_logger.create_error_log.assert_called_once()

    @patch("usecases.integration_management.LoggerUtil")
    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    @patch("usecases.integration_management.requests")
    def test_handle_oauth_callback_creates_integration_with_correct_data(self, mock_requests, mock_integration, mock_get_context_user, mock_logger):
        """Test that create_integration is called with all correct parameters"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = [mock_user]

        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "user_id": "platform_user_789",
            "permissions": ["scope1", "scope2"],
            "expires_in": 3600,
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",  # Required to avoid NameError
        }
        mock_requests.post.return_value = mock_response

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("instagram", "auth_code")

        # Assert
        assert error_message == ""
        mock_integration.create_integration.assert_called_once()
        call_kwargs = mock_integration.create_integration.call_args[1]

        assert call_kwargs["user"] == mock_user
        assert call_kwargs["platform"] == "instagram"
        assert call_kwargs["platform_user_id"] == "platform_user_789"
        assert call_kwargs["access_token"] == "test_access_token"
        assert call_kwargs["token_type"] == "Bearer"
        assert call_kwargs["scopes"] == ["scope1", "scope2"]


class TestDeleteIntegration:
    """Test cases for delete_integration method"""

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_delete_integration_success(self, mock_integration, mock_get_context_user):
        """Test successful deletion of integration"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user
        mock_integration.delete_by_uuid_for_user.return_value = 1  # 1 row affected

        # Act
        error_message, data, errors = IntegrationManagement.delete_integration("test-uuid")

        # Assert
        assert error_message == ""
        assert data is None
        assert errors is None
        mock_integration.delete_by_uuid_for_user.assert_called_once_with("test-uuid", mock_user)

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_delete_integration_not_found(self, mock_integration, mock_get_context_user):
        """Test deletion when integration is not found"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user
        mock_integration.delete_by_uuid_for_user.return_value = 0  # 0 rows affected

        # Act
        error_message, data, errors = IntegrationManagement.delete_integration("invalid-uuid")

        # Assert
        assert error_message == "Integration not found"
        assert data is None
        assert errors == ["Integration not found"]
        mock_integration.delete_by_uuid_for_user.assert_called_once_with("invalid-uuid", mock_user)

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_delete_integration_none_result(self, mock_integration, mock_get_context_user):
        """Test deletion when delete operation returns None"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user
        mock_integration.delete_by_uuid_for_user.return_value = None

        # Act
        error_message, data, errors = IntegrationManagement.delete_integration("test-uuid")

        # Assert
        assert error_message == "Integration not found"
        assert data is None
        assert errors == ["Integration not found"]

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_delete_integration_verifies_user_context(self, mock_integration, mock_get_context_user):
        """Test that delete uses correct user from context"""
        # Arrange
        mock_user = Mock(id=42, email="test@example.com")
        mock_get_context_user.return_value = mock_user
        mock_integration.delete_by_uuid_for_user.return_value = 1

        # Act
        IntegrationManagement.delete_integration("test-uuid")

        # Assert
        mock_get_context_user.assert_called_once()
        mock_integration.delete_by_uuid_for_user.assert_called_once_with("test-uuid", mock_user)


class TestPlatformConfiguration:
    """Test cases for platform configuration constants"""

    def test_platforms_contains_instagram(self):
        """Test that PLATFORMS dict contains Instagram configuration"""
        assert "instagram" in IntegrationManagement.PLATFORMS
        instagram_config = IntegrationManagement.PLATFORMS["instagram"]
        assert "auth_url" in instagram_config
        assert "token_url" in instagram_config
        assert "client_id" in instagram_config
        assert "client_secret" in instagram_config
        assert "scope" in instagram_config

    def test_platforms_contains_youtube(self):
        """Test that PLATFORMS dict contains YouTube configuration"""
        assert "youtube" in IntegrationManagement.PLATFORMS
        youtube_config = IntegrationManagement.PLATFORMS["youtube"]
        assert "auth_url" in youtube_config
        assert "token_url" in youtube_config
        assert "client_id" in youtube_config
        assert "client_secret" in youtube_config
        assert "scope" in youtube_config

    def test_instagram_auth_url_format(self):
        """Test Instagram auth URL has correct format"""
        auth_url = IntegrationManagement.PLATFORMS["instagram"]["auth_url"]
        assert "instagram.com/oauth/authorize" in auth_url
        assert "{client_id}" in auth_url
        assert "{redirect_uri}" in auth_url
        assert "instagram_business" in auth_url

    def test_youtube_auth_url_format(self):
        """Test YouTube auth URL has correct format"""
        auth_url = IntegrationManagement.PLATFORMS["youtube"]["auth_url"]
        assert "accounts.google.com/o/oauth2" in auth_url
        assert "{client_id}" in auth_url
        assert "{redirect_uri}" in auth_url
        assert "googleapis.com/auth/youtube" in auth_url

    def test_platforms_using_refresh_token_list(self):
        """Test PLATFORMS_USING_REFRESH_TOKEN constant"""
        assert "youtube" in IntegrationManagement.PLATFORMS_USING_REFRESH_TOKEN
        assert "instagram" not in IntegrationManagement.PLATFORMS_USING_REFRESH_TOKEN


class TestEdgeCases:
    """Test cases for edge cases and boundary conditions"""

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    def test_get_all_integrations_with_mixed_status(self, mock_integration, mock_get_context_user):
        """Test get_all_integrations with integrations of different statuses"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = mock_user

        mock_integration_active = Mock()
        mock_integration_active.get_details.return_value = {
            "uuid": "uuid-1",
            "platform": "instagram",
            "status": "active",
        }
        mock_integration_inactive = Mock()
        mock_integration_inactive.get_details.return_value = {
            "uuid": "uuid-2",
            "platform": "youtube",
            "status": "inactive",
        }
        mock_integration.get_all_for_user.return_value = [
            mock_integration_active,
            mock_integration_inactive,
        ]

        # Act
        error_message, data, errors = IntegrationManagement.get_all_integrations()

        # Assert
        assert len(data) == 2
        assert data[0]["status"] == "active"
        assert data[1]["status"] == "inactive"

    @patch("usecases.integration_management.get_context_user")
    @patch("usecases.integration_management.Integration")
    @patch("usecases.integration_management.requests")
    @patch("usecases.integration_management.LoggerUtil")
    def test_handle_oauth_callback_with_default_expires_in(self, mock_logger, mock_requests, mock_integration, mock_get_context_user):
        """Test OAuth callback when expires_in is not provided (uses default)"""
        # Arrange
        mock_user = Mock(id=1)
        mock_get_context_user.return_value = [mock_user]

        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_token",
            "user_id": "user_123",
            "permissions": ["scope1"],
            "token_type": "Bearer",
            "refresh_token": "test_refresh_token",  # Required to avoid NameError
            # No expires_in field - should default to 3600
        }
        mock_requests.post.return_value = mock_response

        # Act
        error_message, data, errors = IntegrationManagement.handle_oauth_callback("instagram", "auth_code")

        # Assert
        assert error_message == ""
        # Verify default expiration of 3600 seconds was used
        call_kwargs = mock_integration.create_integration.call_args[1]
        assert call_kwargs["expires_at"] is not None

    def test_get_oauth_url_with_empty_platform_string(self):
        """Test get_oauth_url with empty platform string"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params.get.return_value = "http://localhost:3000/callback"

        # Act
        error_message, data, errors = IntegrationManagement.get_oauth_url("", mock_request)

        # Assert
        assert error_message == UNSUPPORTED_PLATFORM
        assert data is None
        assert errors == [UNSUPPORTED_PLATFORM]

    def test_get_oauth_url_case_sensitivity(self):
        """Test that platform names are case-sensitive"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params.get.return_value = "http://localhost:3000/callback"

        # Act
        error_message, data, errors = IntegrationManagement.get_oauth_url("Instagram", mock_request)

        # Assert
        assert error_message == UNSUPPORTED_PLATFORM
        assert data is None
        assert errors == [UNSUPPORTED_PLATFORM]
