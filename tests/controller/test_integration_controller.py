"""
Unit tests for controller/integration_controller.py

Tests cover all endpoint handlers including:
- get_all_integrations
- get_integration
- get_oauth_url
- handle_oauth_callback
- delete_integration
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.responses import RedirectResponse

# Mock the decorators before importing the controller
sys.modules["decorators.user"] = MagicMock()
sys.modules["decorators.user"].require_authentication = lambda f: f

sys.modules["decorators.common"] = MagicMock()
sys.modules["decorators.common"].validate_json_payload = lambda schema: lambda f: f

from controller.integration_controller import delete_integration, get_all_integrations, get_integration, get_oauth_url, handle_oauth_callback  # noqa: E402


class TestGetAllIntegrations:
    """Test cases for get_all_integrations endpoint"""

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_all_integrations")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_all_integrations_success(self, mock_response_format, mock_get_all_integrations):
        """Test successful retrieval of all integrations"""
        # Arrange
        mock_request = Mock()
        integrations_data = [{"uuid": "uuid1", "platform": "instagram", "status": "active"}, {"uuid": "uuid2", "platform": "facebook", "status": "active"}]
        mock_get_all_integrations.return_value = ("", integrations_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": integrations_data}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_all_integrations(mock_request)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": integrations_data}
        mock_get_all_integrations.assert_called_once()

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_all_integrations")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_all_integrations_returns_200_on_success(self, mock_response_format, mock_get_all_integrations):
        """Test that endpoint returns 200 status code on success"""
        # Arrange
        mock_request = Mock()
        mock_get_all_integrations.return_value = ("", [], None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_all_integrations(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_all_integrations")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_all_integrations_returns_500_on_error(self, mock_response_format, mock_get_all_integrations):
        """Test that endpoint returns 500 status code on error"""
        # Arrange
        mock_request = Mock()
        mock_get_all_integrations.return_value = ("Database error", None, ["DB connection failed"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_all_integrations(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_all_integrations")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_all_integrations_with_empty_list(self, mock_response_format, mock_get_all_integrations):
        """Test retrieval when user has no integrations"""
        # Arrange
        mock_request = Mock()
        mock_get_all_integrations.return_value = ("", [], None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": []}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_all_integrations(mock_request)

        # Assert
        assert result["data"] == []
        assert result["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_all_integrations")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_all_integrations_includes_errors(self, mock_response_format, mock_get_all_integrations):
        """Test that errors are included in response"""
        # Arrange
        mock_request = Mock()
        error_list = ["Error 1", "Error 2"]
        mock_get_all_integrations.return_value = ("Failed to fetch integrations", None, error_list)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_all_integrations(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["errors"] == error_list
        assert call_kwargs["message"] == "Failed to fetch integrations"


class TestGetIntegration:
    """Test cases for get_integration endpoint"""

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_integration_by_uuid")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_integration_success(self, mock_response_format, mock_get_integration):
        """Test successful retrieval of a specific integration"""
        # Arrange
        mock_request = Mock()
        integration_uuid = "test-uuid-123"
        integration_data = {"uuid": integration_uuid, "platform": "instagram", "status": "active"}
        mock_get_integration.return_value = ("", integration_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": integration_data}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_integration(mock_request, integration_uuid)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": integration_data}
        mock_get_integration.assert_called_once_with(integration_uuid)

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_integration_by_uuid")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_integration_returns_200_on_success(self, mock_response_format, mock_get_integration):
        """Test that endpoint returns 200 status code on success"""
        # Arrange
        mock_request = Mock()
        mock_get_integration.return_value = ("", {"uuid": "test"}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_integration(mock_request, "test-uuid")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_integration_by_uuid")
    @patch("controller.integration_controller.APIResponseFormat")
    @patch("controller.integration_controller.INTEGRATION_NOT_FOUND", "Integration not found")
    async def test_get_integration_returns_404_when_not_found(self, mock_response_format, mock_get_integration):
        """Test that endpoint returns 404 when integration not found"""
        # Arrange
        mock_request = Mock()
        mock_get_integration.return_value = ("Integration not found", None, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_integration(mock_request, "nonexistent-uuid")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 404

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_integration_by_uuid")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_integration_returns_500_on_other_errors(self, mock_response_format, mock_get_integration):
        """Test that endpoint returns 500 on non-404 errors"""
        # Arrange
        mock_request = Mock()
        mock_get_integration.return_value = ("Database error", None, ["Connection failed"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_integration(mock_request, "test-uuid")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_integration_by_uuid")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_integration_passes_uuid_correctly(self, mock_response_format, mock_get_integration):
        """Test that the correct UUID is passed to management layer"""
        # Arrange
        mock_request = Mock()
        test_uuid = "specific-uuid-456"
        mock_get_integration.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_integration(mock_request, test_uuid)

        # Assert
        mock_get_integration.assert_called_once_with(test_uuid)


class TestGetOAuthURL:
    """Test cases for get_oauth_url endpoint"""

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_oauth_url")
    async def test_get_oauth_url_success(self, mock_get_oauth_url):
        """Test successful OAuth URL generation and redirect"""
        # Arrange
        mock_request = Mock()
        platform = "instagram"
        oauth_url = "https://instagram.com/oauth/authorize?client_id=test"
        mock_get_oauth_url.return_value = ("", oauth_url, None)

        # Act
        result = await get_oauth_url(mock_request, platform)

        # Assert
        assert isinstance(result, RedirectResponse)
        assert result.headers["location"] == oauth_url
        mock_get_oauth_url.assert_called_once_with(platform, mock_request)

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_oauth_url")
    async def test_get_oauth_url_redirect_response(self, mock_get_oauth_url):
        """Test that successful call returns RedirectResponse"""
        # Arrange
        mock_request = Mock()
        oauth_url = "https://facebook.com/oauth/authorize"
        mock_get_oauth_url.return_value = ("", oauth_url, None)

        # Act
        result = await get_oauth_url(mock_request, "facebook")

        # Assert
        assert isinstance(result, RedirectResponse)
        assert result.status_code == 307  # Default redirect status

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_oauth_url")
    @patch("controller.integration_controller.APIResponseFormat")
    @patch("controller.integration_controller.UNSUPPORTED_PLATFORM", "Unsupported platform")
    async def test_get_oauth_url_returns_400_for_unsupported_platform(self, mock_response_format, mock_get_oauth_url):
        """Test that endpoint returns 400 for unsupported platform"""
        # Arrange
        mock_request = Mock()
        mock_get_oauth_url.return_value = ("Unsupported platform", None, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 400, "message": "Unsupported platform"}
        mock_response_format.return_value = mock_response_instance

        # Act
        _result = await get_oauth_url(mock_request, "invalid_platform")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 400

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_oauth_url")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_oauth_url_returns_500_on_other_errors(self, mock_response_format, mock_get_oauth_url):
        """Test that endpoint returns 500 on non-platform errors"""
        # Arrange
        mock_request = Mock()
        mock_get_oauth_url.return_value = ("Configuration error", None, ["Missing API key"])

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {}
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_oauth_url(mock_request, "instagram")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_oauth_url")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_get_oauth_url_includes_error_message(self, mock_response_format, mock_get_oauth_url):
        """Test that error message is included in error response"""
        # Arrange
        mock_request = Mock()
        error_message = "OAuth configuration missing"
        mock_get_oauth_url.return_value = (error_message, None, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_oauth_url(mock_request, "instagram")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == error_message

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.get_oauth_url")
    async def test_get_oauth_url_passes_platform_and_request(self, mock_get_oauth_url):
        """Test that platform and request are passed to management layer"""
        # Arrange
        mock_request = Mock()
        test_platform = "facebook"
        mock_get_oauth_url.return_value = ("", "https://test.com", None)

        # Act
        await get_oauth_url(mock_request, test_platform)

        # Assert
        mock_get_oauth_url.assert_called_once_with(test_platform, mock_request)


class TestHandleOAuthCallback:
    """Test cases for handle_oauth_callback endpoint"""

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.handle_oauth_callback")
    async def test_handle_oauth_callback_success(self, mock_handle_callback):
        """Test successful OAuth callback handling"""
        # Arrange
        mock_request = Mock()
        platform = "instagram"
        code = "auth_code_123"
        redirect_url = "https://frontend.app/integrations?success=true"
        mock_handle_callback.return_value = ("", redirect_url, None)

        # Act
        result = await handle_oauth_callback(mock_request, platform, code)

        # Assert
        assert isinstance(result, RedirectResponse)
        assert result.headers["location"] == redirect_url
        mock_handle_callback.assert_called_once_with(platform, code, mock_request)

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.handle_oauth_callback")
    async def test_handle_oauth_callback_redirect_response(self, mock_handle_callback):
        """Test that successful callback returns RedirectResponse"""
        # Arrange
        mock_request = Mock()
        redirect_url = "https://frontend.app/success"
        mock_handle_callback.return_value = ("", redirect_url, None)

        # Act
        result = await handle_oauth_callback(mock_request, "facebook", "code123")

        # Assert
        assert isinstance(result, RedirectResponse)
        assert result.headers["location"] == redirect_url

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.handle_oauth_callback")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_handle_oauth_callback_returns_500_on_error(self, mock_response_format, mock_handle_callback):
        """Test that endpoint returns 500 on callback error"""
        # Arrange
        mock_request = Mock()
        mock_handle_callback.return_value = ("Failed to exchange token", None, ["Invalid code"])

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {}
        mock_response_format.return_value = mock_response_instance

        # Act
        await handle_oauth_callback(mock_request, "instagram", "invalid_code")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.handle_oauth_callback")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_handle_oauth_callback_includes_error_message(self, mock_response_format, mock_handle_callback):
        """Test that error message is included in error response"""
        # Arrange
        mock_request = Mock()
        error_message = "Token exchange failed"
        mock_handle_callback.return_value = (error_message, None, ["Network error"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await handle_oauth_callback(mock_request, "facebook", "code")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == error_message
        assert call_kwargs["errors"] == ["Network error"]

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.handle_oauth_callback")
    async def test_handle_oauth_callback_passes_parameters_correctly(self, mock_handle_callback):
        """Test that platform, code, and request are passed correctly"""
        # Arrange
        mock_request = Mock()
        test_platform = "instagram"
        test_code = "authorization_code_xyz"
        mock_handle_callback.return_value = ("", "https://test.com", None)

        # Act
        await handle_oauth_callback(mock_request, test_platform, test_code)

        # Assert
        mock_handle_callback.assert_called_once_with(test_platform, test_code, mock_request)

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.handle_oauth_callback")
    async def test_handle_oauth_callback_with_different_platforms(self, mock_handle_callback):
        """Test callback handling works for different platforms"""
        # Arrange
        mock_request = Mock()
        platforms = ["instagram", "facebook", "twitter"]

        for platform in platforms:
            mock_handle_callback.return_value = ("", f"https://redirect.com/{platform}", None)

            # Act
            result = await handle_oauth_callback(mock_request, platform, "code123")

            # Assert
            assert isinstance(result, RedirectResponse)
            mock_handle_callback.assert_called_with(platform, "code123", mock_request)


class TestDeleteIntegration:
    """Test cases for delete_integration endpoint"""

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.delete_integration")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_delete_integration_success(self, mock_response_format, mock_delete_integration):
        """Test successful integration deletion"""
        # Arrange
        mock_request = Mock()
        integration_uuid = "uuid-to-delete"
        success_data = {"message": "Integration deleted successfully"}
        mock_delete_integration.return_value = ("", success_data, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": success_data}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await delete_integration(mock_request, integration_uuid)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": success_data}
        mock_delete_integration.assert_called_once_with(integration_uuid)

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.delete_integration")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_delete_integration_returns_200_on_success(self, mock_response_format, mock_delete_integration):
        """Test that endpoint returns 200 status code on success"""
        # Arrange
        mock_request = Mock()
        mock_delete_integration.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await delete_integration(mock_request, "test-uuid")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.delete_integration")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_delete_integration_returns_500_on_error(self, mock_response_format, mock_delete_integration):
        """Test that endpoint returns 500 status code on error"""
        # Arrange
        mock_request = Mock()
        mock_delete_integration.return_value = ("Failed to delete integration", None, ["Error detail"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await delete_integration(mock_request, "test-uuid")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.delete_integration")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_delete_integration_includes_error_message(self, mock_response_format, mock_delete_integration):
        """Test that error message is included in error response"""
        # Arrange
        mock_request = Mock()
        error_message = "Integration not found for deletion"
        mock_delete_integration.return_value = (error_message, None, ["UUID invalid"])

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await delete_integration(mock_request, "invalid-uuid")

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == error_message
        assert call_kwargs["errors"] == ["UUID invalid"]

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.delete_integration")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_delete_integration_passes_uuid_correctly(self, mock_response_format, mock_delete_integration):
        """Test that the correct UUID is passed to management layer"""
        # Arrange
        mock_request = Mock()
        test_uuid = "specific-uuid-to-delete"
        mock_delete_integration.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await delete_integration(mock_request, test_uuid)

        # Assert
        mock_delete_integration.assert_called_once_with(test_uuid)

    @pytest.mark.asyncio
    @patch("controller.integration_controller.IntegrationManagement.delete_integration")
    @patch("controller.integration_controller.APIResponseFormat")
    async def test_delete_integration_handles_empty_data(self, mock_response_format, mock_delete_integration):
        """Test deletion handling when data is None or empty"""
        # Arrange
        mock_request = Mock()
        mock_delete_integration.return_value = ("", None, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": None}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await delete_integration(mock_request, "test-uuid")

        # Assert
        assert result["data"] is None
        assert result["status_code"] == 200
