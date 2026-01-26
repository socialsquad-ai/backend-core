from unittest.mock import Mock, patch, AsyncMock
import jwt
import pytest
import httpx

from utils.auth0_service import Auth0Service
from utils.exceptions import CustomUnauthorized


class TestAuth0ServiceInit:
    """Test cases for Auth0Service initialization"""

    @patch("utils.auth0_service.env")
    def test_auth0_service_initialization(self, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        # Act
        service = Auth0Service()

        # Assert
        assert service.domain == "test.auth0.com"
        assert service.audience == "test-audience"
        assert service.issuer == "https://test.auth0.com/"
        assert service._jwks is None
        assert service._jwks_url == "https://test.auth0.com/.well-known/jwks.json"


@pytest.mark.asyncio
class TestGetJwks:
    """Test cases for _get_jwks method"""

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.httpx.AsyncClient")
    async def test_get_jwks_fetches_and_caches(self, mock_client_cls, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        # Mock the context manager and the get method
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        mock_response = Mock()
        mock_response.json.return_value = {"keys": [{"kid": "test-key-id"}]}
        mock_response.raise_for_status = Mock()
        mock_client.get.return_value = mock_response

        service = Auth0Service()

        # Act
        result1 = await service._get_jwks()
        result2 = await service._get_jwks()

        # Assert
        assert result1 == {"keys": [{"kid": "test-key-id"}]}
        assert result2 == result1  # Should return cached value
        assert mock_client.get.call_count == 1  # Should only call API once

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.httpx.AsyncClient")
    @patch("utils.auth0_service.LoggerUtil.create_error_log")
    async def test_get_jwks_handles_request_exception(self, mock_logger, mock_client_cls, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.RequestError("Network error")

        service = Auth0Service()

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await service._get_jwks()

        assert exc_info.value.detail == "Authentication service unavailable"
        mock_logger.assert_called_once()

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.httpx.AsyncClient")
    async def test_get_jwks_with_timeout(self, mock_client_cls, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        mock_response = Mock()
        mock_response.json.return_value = {"keys": []}
        mock_response.raise_for_status = Mock()
        mock_client.get.return_value = mock_response

        service = Auth0Service()

        # Act
        await service._get_jwks()

        # Assert
        mock_client.get.assert_called_once_with("https://test.auth0.com/.well-known/jwks.json", timeout=10)


@pytest.mark.asyncio
class TestGetSigningKey:
    """Test cases for _get_signing_key method"""

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.jwt.get_unverified_header")
    async def test_get_signing_key_no_kid_in_header(self, mock_get_header, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_get_header.return_value = {}

        service = Auth0Service()

        # Act
        result = await service._get_signing_key("test-token")

        # Assert
        assert result is None

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.jwt.get_unverified_header")
    async def test_get_signing_key_with_invalid_token(self, mock_get_header, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_get_header.side_effect = Exception("Invalid token")

        service = Auth0Service()

        # Act
        result = await service._get_signing_key("invalid-token")

        # Assert
        assert result is None

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.jwt.get_unverified_header")
    async def test_get_signing_key_key_not_found_in_jwks(self, mock_get_header, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_get_header.return_value = {"kid": "missing-key-id"}

        service = Auth0Service()
        # Mock _get_jwks directly instead of mocking http requests
        service._get_jwks = AsyncMock(return_value={"keys": [{"kid": "different-key-id"}]})

        # Act
        result = await service._get_signing_key("test-token")

        # Assert
        assert result is None

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.jwt.get_unverified_header")
    @patch("utils.auth0_service.jwt.utils.base64url_decode")
    async def test_get_signing_key_with_rsa_key(self, mock_base64_decode, mock_get_header, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_get_header.return_value = {"kid": "test-key-id"}

        # Simulate RSA key components
        n_bytes = b"\x00\xc0" + b"\xff" * 254
        e_bytes = b"\x01\x00\x01"
        mock_base64_decode.side_effect = [n_bytes, e_bytes]

        service = Auth0Service()
        service._get_jwks = AsyncMock(return_value={
            "keys": [{"kid": "test-key-id", "kty": "RSA", "n": "AQAB", "e": "AQAB"}]
        })

        # Act
        result = await service._get_signing_key("test-token")

        # Assert
        assert result is not None
        assert isinstance(result, str)
        assert "BEGIN PUBLIC KEY" in result


@pytest.mark.asyncio
class TestValidateToken:
    """Test cases for validate_token method"""

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_info_log")
    @patch("utils.auth0_service.jwt.decode")
    async def test_validate_token_removes_bearer_prefix(self, mock_jwt_decode, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_jwt_decode.return_value = {"sub": "user123", "aud": "test-audience"}

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value="test-key")

        # Act
        result = await service.validate_token("Bearer test-token")

        # Assert
        assert result == {"sub": "user123", "aud": "test-audience"}
        mock_logger.assert_called_once()

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_error_log")
    async def test_validate_token_raises_on_invalid_signature_key(self, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await service.validate_token("test-token")

        assert exc_info.value.detail == "Invalid token signature"

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_error_log")
    @patch("utils.auth0_service.jwt.decode")
    async def test_validate_token_handles_expired_signature_error(self, mock_jwt_decode, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError("Token expired")

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value="test-key")

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await service.validate_token("test-token")

        assert exc_info.value.detail == "Token has expired"
        mock_logger.assert_called_once_with("Token has expired")

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_error_log")
    @patch("utils.auth0_service.jwt.decode")
    async def test_validate_token_handles_invalid_audience_error(self, mock_jwt_decode, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_jwt_decode.side_effect = jwt.InvalidAudienceError("Invalid audience")

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value="test-key")

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await service.validate_token("test-token")

        assert exc_info.value.detail == "Invalid token audience"
        mock_logger.assert_called_once_with("Invalid audience in token")

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_error_log")
    @patch("utils.auth0_service.jwt.decode")
    async def test_validate_token_handles_invalid_issuer_error(self, mock_jwt_decode, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_jwt_decode.side_effect = jwt.InvalidIssuerError("Invalid issuer")

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value="test-key")

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await service.validate_token("test-token")

        assert exc_info.value.detail == "Invalid token issuer"
        mock_logger.assert_called_once_with("Invalid issuer in token")

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_error_log")
    @patch("utils.auth0_service.jwt.decode")
    async def test_validate_token_handles_invalid_signature_error(self, mock_jwt_decode, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_jwt_decode.side_effect = jwt.InvalidSignatureError("Invalid signature")

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value="test-key")

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await service.validate_token("test-token")

        assert exc_info.value.detail == "Invalid token signature"
        mock_logger.assert_called_once_with("Invalid token signature")

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_error_log")
    @patch("utils.auth0_service.jwt.decode")
    async def test_validate_token_handles_invalid_token_error(self, mock_jwt_decode, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_jwt_decode.side_effect = jwt.InvalidTokenError("Invalid token")

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value="test-key")

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await service.validate_token("test-token")

        assert exc_info.value.detail == "Invalid token"

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_error_log")
    @patch("utils.auth0_service.jwt.decode")
    async def test_validate_token_handles_generic_exception(self, mock_jwt_decode, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_jwt_decode.side_effect = Exception("Unexpected error")

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value="test-key")

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await service.validate_token("test-token")

        assert exc_info.value.detail == "Token validation failed"

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_info_log")
    @patch("utils.auth0_service.jwt.decode")
    async def test_validate_token_success_with_complete_payload(self, mock_jwt_decode, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        payload = {
            "sub": "auth0|user123",
            "aud": "test-audience",
            "iss": "https://test.auth0.com/",
            "exp": 1234567890,
            "iat": 1234567800,
        }
        mock_jwt_decode.return_value = payload

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value="test-key")

        # Act
        result = await service.validate_token("test-token")

        # Assert
        assert result == payload
        mock_jwt_decode.assert_called_once_with(
            "test-token",
            "test-key",
            algorithms=["RS256"],
            audience="test-audience",
            issuer="https://test.auth0.com/",
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
                "verify_iat": True,
            },
        )

    @patch("utils.auth0_service.env")
    @patch("utils.auth0_service.LoggerUtil.create_info_log")
    @patch("utils.auth0_service.jwt.decode")
    async def test_validate_token_without_bearer_prefix(self, mock_jwt_decode, mock_logger, mock_env):
        # Arrange
        mock_env.AUTH0_DOMAIN = "test.auth0.com"
        mock_env.AUTH0_AUDIENCE = "test-audience"
        mock_env.AUTH0_ISSUER = "https://test.auth0.com/"

        mock_jwt_decode.return_value = {"sub": "user123"}

        service = Auth0Service()
        service._get_signing_key = AsyncMock(return_value="test-key")

        # Act
        result = await service.validate_token("just-token-without-bearer")

        # Assert
        assert result == {"sub": "user123"}
