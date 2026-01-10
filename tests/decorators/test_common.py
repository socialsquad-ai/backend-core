import asyncio
from unittest.mock import Mock, patch

import pytest
from fastapi import Request

from decorators.common import (
    require_internal_authentication,
    singleton_class,
    validate_json_payload,
    validate_query_params,
)
from utils.exceptions import CustomBadRequest, CustomUnauthorized


class TestValidateJsonPayload:
    """Test cases for validate_json_payload decorator"""

    @pytest.mark.asyncio
    @patch("decorators.common.get_request_json_post_payload")
    async def test_validate_json_payload_with_valid_payload(self, mock_get_payload):
        # Arrange
        schema = {"name": {"type": "string", "required": True}}
        mock_get_payload.return_value = {"name": "test"}

        @validate_json_payload(schema)
        async def test_func():
            return "success"

        # Act
        result = await test_func()

        # Assert
        assert result == "success"

    @pytest.mark.asyncio
    @patch("decorators.common.get_request_json_post_payload")
    @patch("decorators.common.LoggerUtil.create_error_log")
    async def test_validate_json_payload_with_invalid_payload(self, mock_logger, mock_get_payload):
        # Arrange
        schema = {"name": {"type": "string", "required": True}}
        mock_get_payload.return_value = {"age": 25}  # Missing required 'name'

        @validate_json_payload(schema)
        async def test_func():
            return "success"

        # Act & Assert
        with pytest.raises(CustomBadRequest) as exc_info:
            await test_func()

        assert "Invalid payload" in exc_info.value.detail
        mock_logger.assert_called_once()

    @pytest.mark.asyncio
    @patch("decorators.common.get_request_json_post_payload")
    @patch("decorators.common.LoggerUtil.create_error_log")
    async def test_validate_json_payload_with_exception(self, mock_logger, mock_get_payload):
        # Arrange
        schema = {"name": {"type": "string"}}
        mock_get_payload.side_effect = Exception("JSON parse error")

        @validate_json_payload(schema)
        async def test_func():
            return "success"

        # Act & Assert
        with pytest.raises(CustomBadRequest) as exc_info:
            await test_func()

        assert "Invalid json payload" in exc_info.value.detail
        mock_logger.assert_called_once()

    @pytest.mark.asyncio
    @patch("decorators.common.get_request_json_post_payload")
    async def test_validate_json_payload_with_complex_schema(self, mock_get_payload):
        # Arrange
        schema = {
            "name": {"type": "string", "required": True},
            "age": {"type": "integer", "required": True, "min": 0, "max": 150},
            "email": {"type": "string", "required": False},
        }
        mock_get_payload.return_value = {"name": "John", "age": 30}

        @validate_json_payload(schema)
        async def test_func():
            return "success"

        # Act
        result = await test_func()

        # Assert
        assert result == "success"

    @pytest.mark.asyncio
    @patch("decorators.common.get_request_json_post_payload")
    async def test_validate_json_payload_allows_unknown_fields(self, mock_get_payload):
        # Arrange - decorator uses allow_unknown=True
        schema = {"name": {"type": "string", "required": True}}
        mock_get_payload.return_value = {
            "name": "test",
            "extra_field": "value",
        }

        @validate_json_payload(schema)
        async def test_func():
            return "success"

        # Act
        result = await test_func()

        # Assert
        assert result == "success"


class TestValidateQueryParams:
    """Test cases for validate_query_params decorator"""

    @pytest.mark.asyncio
    async def test_validate_query_params_decorator_exists(self):
        # Arrange & Act
        @validate_query_params
        async def test_func():
            return "success"

        result = await test_func()

        # Assert
        assert result == "success"

    @pytest.mark.asyncio
    async def test_validate_query_params_passes_through(self):
        # Arrange
        @validate_query_params
        async def test_func(param1, param2):
            return f"{param1}-{param2}"

        # Act
        result = await test_func("value1", "value2")

        # Assert
        assert result == "value1-value2"


class TestSingletonClass:
    """Test cases for singleton_class decorator"""

    @pytest.mark.asyncio
    async def test_singleton_class_creates_single_instance(self):
        # Arrange
        @singleton_class
        class TestClass:
            def __init__(self):
                self.value = "test"

        # Act
        instance1 = await TestClass()
        instance2 = await TestClass()

        # Assert
        assert instance1 is instance2

    @pytest.mark.asyncio
    async def test_singleton_class_preserves_state(self):
        # Arrange
        @singleton_class
        class TestClass:
            def __init__(self):
                self.counter = 0

            def increment(self):
                self.counter += 1

        # Act
        instance1 = await TestClass()
        instance1.increment()
        instance2 = await TestClass()

        # Assert
        assert instance1.counter == 1
        assert instance2.counter == 1
        assert instance1 is instance2

    @pytest.mark.asyncio
    async def test_singleton_class_with_constructor_args(self):
        # Arrange
        @singleton_class
        class TestClass:
            def __init__(self, name, value):
                self.name = name
                self.value = value

        # Act
        instance1 = await TestClass("test", 42)
        instance2 = await TestClass("different", 99)  # Args ignored after first call

        # Assert
        assert instance1 is instance2
        assert instance1.name == "test"
        assert instance1.value == 42

    @pytest.mark.asyncio
    async def test_singleton_class_concurrent_access(self):
        # Arrange
        @singleton_class
        class TestClass:
            def __init__(self):
                self.initialized = True

        # Act - Multiple concurrent calls
        instances = await asyncio.gather(
            TestClass(),
            TestClass(),
            TestClass(),
        )

        # Assert - All should be same instance
        assert all(inst is instances[0] for inst in instances)


class TestRequireInternalAuthentication:
    """Test cases for require_internal_authentication decorator"""

    @pytest.mark.asyncio
    @patch("decorators.common.env.INTERNAL_AUTH_API_KEY", "correct-api-key")
    @patch("decorators.common.LoggerUtil.create_info_log")
    async def test_require_internal_authentication_with_valid_key(self, mock_logger):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer correct-api-key"

        @require_internal_authentication
        async def test_func(request: Request):
            return "authenticated"

        # Act
        result = await test_func(request=mock_request)

        # Assert
        assert result == "authenticated"
        mock_logger.assert_called_once_with("Internal authentication successful")

    @pytest.mark.asyncio
    @patch("decorators.common.LoggerUtil.create_error_log")
    async def test_require_internal_authentication_no_auth_header(self, mock_logger):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = None

        @require_internal_authentication
        async def test_func(request: Request):
            return "authenticated"

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await test_func(request=mock_request)

        assert "Authorization header required" in exc_info.value.detail
        mock_logger.assert_called_once()

    @pytest.mark.asyncio
    @patch("decorators.common.LoggerUtil.create_error_log")
    async def test_require_internal_authentication_invalid_format(self, mock_logger):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "InvalidFormat api-key"

        @require_internal_authentication
        async def test_func(request: Request):
            return "authenticated"

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await test_func(request=mock_request)

        assert "Invalid authorization format" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("decorators.common.env.INTERNAL_AUTH_API_KEY", "correct-key")
    @patch("decorators.common.LoggerUtil.create_error_log")
    async def test_require_internal_authentication_wrong_key(self, mock_logger):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer wrong-key"

        @require_internal_authentication
        async def test_func(request: Request):
            return "authenticated"

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await test_func(request=mock_request)

        assert "Invalid internal API key" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("decorators.common.LoggerUtil.create_error_log")
    async def test_require_internal_authentication_no_request_in_args(self, mock_logger):
        # Arrange
        @require_internal_authentication
        async def test_func():
            return "authenticated"

        # Act & Assert
        with pytest.raises(CustomUnauthorized) as exc_info:
            await test_func()

        assert "Authentication required" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch("decorators.common.env.INTERNAL_AUTH_API_KEY", "test-key")
    @patch("decorators.common.LoggerUtil.create_info_log")
    async def test_require_internal_authentication_request_in_args(self, mock_logger):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer test-key"

        @require_internal_authentication
        async def test_func(request):
            return "authenticated"

        # Act
        result = await test_func(mock_request)

        # Assert
        assert result == "authenticated"

    @pytest.mark.asyncio
    @patch("decorators.common.env.INTERNAL_AUTH_API_KEY", "test-key")
    @patch("decorators.common.LoggerUtil.create_info_log")
    async def test_require_internal_authentication_with_kwargs(self, mock_logger):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.headers.get.return_value = "Bearer test-key"

        @require_internal_authentication
        async def test_func(request: Request, data: dict):
            return f"authenticated-{data['key']}"

        # Act
        result = await test_func(request=mock_request, data={"key": "value"})

        # Assert
        assert result == "authenticated-value"
