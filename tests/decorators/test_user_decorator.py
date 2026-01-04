from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import Request

from decorators.user import require_authentication
from utils.exceptions import CustomUnauthorized


class TestRequireAuthentication:
    """Test cases for require_authentication decorator"""

    @pytest.mark.asyncio
    @patch("decorators.user.Auth0Service")
    @patch("decorators.user.User.get_by_auth0_user_id")
    @patch("decorators.user.set_context_user")
    @patch("decorators.user.LoggerUtil.create_info_log")
    async def test_require_authentication_with_valid_token(
        self,
        mock_logger_info,
        mock_set_context_user,
        mock_get_user,
        mock_auth0_service,
    ):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer valid-token"
        mock_request.state = Mock()

        mock_auth0_instance = MagicMock()
        mock_auth0_instance.validate_token.return_value = {
            "sub": "auth0|user123",
            "email": "test@example.com",
        }
        mock_auth0_service.return_value = mock_auth0_instance

        mock_user = Mock()
        mock_get_user.return_value = mock_user

        @require_authentication
        async def test_func(request: Request):
            return "success"

        # Act
        result = await test_func(request=mock_request)

        # Assert
        assert result == "success"
        mock_auth0_instance.validate_token.assert_called_once_with("Bearer valid-token")
        mock_set_context_user.assert_called_once_with(mock_user)
        assert mock_request.state.user == {
            "sub": "auth0|user123",
            "email": "test@example.com",
        }
        mock_logger_info.assert_called_once()

    @pytest.mark.asyncio
    @patch("decorators.user.LoggerUtil.create_error_log")
    async def test_require_authentication_no_auth_header(self, mock_logger_error):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = None

        @require_authentication
        async def test_func(request: Request):
            return "success"

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await test_func(request=mock_request)

        assert "Authorization header required" in exc_info.value.detail
        mock_logger_error.assert_called_once_with("No Authorization header found")

    @pytest.mark.asyncio
    @patch("decorators.user.LoggerUtil.create_error_log")
    async def test_require_authentication_no_request_object(self, mock_logger_error):
        # Arrange
        @require_authentication
        async def test_func():
            return "success"

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await test_func()

        assert "Authentication required" in exc_info.value.detail
        mock_logger_error.assert_called_once_with("No request object found in function arguments")

    @pytest.mark.asyncio
    @patch("decorators.user.Auth0Service")
    @patch("decorators.user.LoggerUtil.create_error_log")
    async def test_require_authentication_invalid_token(self, mock_logger_error, mock_auth0_service):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer invalid-token"

        mock_auth0_instance = MagicMock()
        mock_auth0_instance.validate_token.side_effect = CustomUnauthorized(detail="Token has expired")
        mock_auth0_service.return_value = mock_auth0_instance

        @require_authentication
        async def test_func(request: Request):
            return "success"

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await test_func(request=mock_request)

        assert "Token has expired" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("decorators.user.Auth0Service")
    @patch("decorators.user.LoggerUtil.create_error_log")
    async def test_require_authentication_unexpected_error(self, mock_logger_error, mock_auth0_service):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer token"

        mock_auth0_instance = MagicMock()
        mock_auth0_instance.validate_token.side_effect = Exception("Unexpected error")
        mock_auth0_service.return_value = mock_auth0_instance

        @require_authentication
        async def test_func(request: Request):
            return "success"

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await test_func(request=mock_request)

        assert "Authentication failed" in exc_info.value.detail
        mock_logger_error.assert_called_once()

    @pytest.mark.asyncio
    @patch("decorators.user.Auth0Service")
    @patch("decorators.user.User.get_by_auth0_user_id")
    @patch("decorators.user.set_context_user")
    @patch("decorators.user.LoggerUtil.create_info_log")
    async def test_require_authentication_request_in_args(
        self,
        mock_logger_info,
        mock_set_context_user,
        mock_get_user,
        mock_auth0_service,
    ):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer valid-token"
        mock_request.state = Mock()

        mock_auth0_instance = MagicMock()
        mock_auth0_instance.validate_token.return_value = {
            "sub": "auth0|user123",
        }
        mock_auth0_service.return_value = mock_auth0_instance

        mock_user = Mock()
        mock_get_user.return_value = mock_user

        @require_authentication
        async def test_func(request):
            return "success"

        # Act
        result = await test_func(mock_request)

        # Assert
        assert result == "success"

    @pytest.mark.asyncio
    @patch("decorators.user.Auth0Service")
    @patch("decorators.user.User.get_by_auth0_user_id")
    @patch("decorators.user.set_context_user")
    @patch("decorators.user.LoggerUtil.create_info_log")
    async def test_require_authentication_with_additional_args(
        self,
        mock_logger_info,
        mock_set_context_user,
        mock_get_user,
        mock_auth0_service,
    ):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer valid-token"
        mock_request.state = Mock()

        mock_auth0_instance = MagicMock()
        mock_auth0_instance.validate_token.return_value = {
            "sub": "auth0|user123",
        }
        mock_auth0_service.return_value = mock_auth0_instance

        mock_user = Mock()
        mock_get_user.return_value = mock_user

        @require_authentication
        async def test_func(request: Request, param1: str, param2: int):
            return f"{param1}-{param2}"

        # Act
        result = await test_func(request=mock_request, param1="test", param2=42)

        # Assert
        assert result == "test-42"

    @pytest.mark.asyncio
    @patch("decorators.user.Auth0Service")
    @patch("decorators.user.User.get_by_auth0_user_id")
    @patch("decorators.user.set_context_user")
    @patch("decorators.user.LoggerUtil.create_info_log")
    async def test_require_authentication_sets_user_state(
        self,
        mock_logger_info,
        mock_set_context_user,
        mock_get_user,
        mock_auth0_service,
    ):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer valid-token"
        mock_request.state = Mock()

        token_payload = {
            "sub": "auth0|user123",
            "email": "test@example.com",
            "name": "Test User",
        }
        mock_auth0_instance = MagicMock()
        mock_auth0_instance.validate_token.return_value = token_payload
        mock_auth0_service.return_value = mock_auth0_instance

        mock_user = Mock()
        mock_get_user.return_value = mock_user

        @require_authentication
        async def test_func(request: Request):
            return request.state.user

        # Act
        result = await test_func(request=mock_request)

        # Assert
        assert result == token_payload
        mock_set_context_user.assert_called_once_with(mock_user)
        mock_get_user.assert_called_once_with("auth0|user123")

    @pytest.mark.asyncio
    @patch("decorators.user.Auth0Service")
    @patch("decorators.user.User.get_by_auth0_user_id")
    @patch("decorators.user.set_context_user")
    @patch("decorators.user.LoggerUtil.create_info_log")
    async def test_require_authentication_logs_user_id(
        self,
        mock_logger_info,
        mock_set_context_user,
        mock_get_user,
        mock_auth0_service,
    ):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer valid-token"
        mock_request.state = Mock()

        token_payload = {"sub": "auth0|specificuser", "email": "user@test.com"}
        mock_auth0_instance = MagicMock()
        mock_auth0_instance.validate_token.return_value = token_payload
        mock_auth0_service.return_value = mock_auth0_instance

        mock_user = Mock()
        mock_get_user.return_value = mock_user

        @require_authentication
        async def test_func(request: Request):
            return "success"

        # Act
        await test_func(request=mock_request)

        # Assert
        assert mock_logger_info.call_count == 1
        call_args = mock_logger_info.call_args[0][0]
        assert "auth0|specificuser" in call_args
