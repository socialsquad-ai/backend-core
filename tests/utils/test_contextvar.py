from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Request

from utils.contextvar import (
    JsonPayload,
    RequestMetadata,
    clear_request_metadata,
    get_context_api_id,
    get_context_user,
    get_request_json_post_payload,
    get_request_metadata,
    set_context_json_post_payload,
    set_context_user,
    set_request_metadata,
)


class TestRequestMetadata:
    """Test cases for RequestMetadata dataclass"""

    def test_request_metadata_creation(self):
        # Arrange & Act
        metadata = RequestMetadata(api_id="test-api-123", thread_id="thread-456")

        # Assert
        assert metadata.api_id == "test-api-123"
        assert metadata.thread_id == "thread-456"

    def test_request_metadata_is_frozen(self):
        # Arrange
        metadata = RequestMetadata(api_id="test-api-123", thread_id="thread-456")

        # Act & Assert
        with pytest.raises(Exception):  # FrozenInstanceError
            metadata.api_id = "new-api"

    def test_request_metadata_empty(self):
        # Arrange & Act
        metadata = RequestMetadata.empty()

        # Assert
        assert metadata.api_id == ""
        assert metadata.thread_id == ""

    def test_request_metadata_to_dict(self):
        # Arrange
        metadata = RequestMetadata(api_id="test-api-123", thread_id="thread-456")

        # Act
        result = metadata.to_dict()

        # Assert
        assert result == {"api_id": "test-api-123", "thread_id": "thread-456"}


class TestJsonPayload:
    """Test cases for JsonPayload dataclass"""

    def test_json_payload_creation(self):
        # Arrange & Act
        payload = JsonPayload(data={"key": "value"})

        # Assert
        assert payload.data == {"key": "value"}

    def test_json_payload_is_frozen(self):
        # Arrange
        payload = JsonPayload(data={"key": "value"})

        # Act & Assert
        with pytest.raises(Exception):  # FrozenInstanceError
            payload.data = {"new": "data"}

    def test_json_payload_empty(self):
        # Arrange & Act
        payload = JsonPayload.empty()

        # Assert
        assert payload.data == {}

    def test_json_payload_to_dict(self):
        # Arrange
        payload = JsonPayload(data={"key": "value", "nested": {"a": 1}})

        # Act
        result = payload.to_dict()

        # Assert
        assert result == {"key": "value", "nested": {"a": 1}}


class TestGetRequestMetadata:
    """Test cases for get_request_metadata function"""

    def test_get_request_metadata_returns_dict(self):
        # Arrange
        set_request_metadata({"api_id": "test-123", "thread_id": "thread-456"})

        # Act
        result = get_request_metadata()

        # Assert
        assert isinstance(result, dict)
        assert result["api_id"] == "test-123"
        assert result["thread_id"] == "thread-456"

        # Cleanup
        clear_request_metadata()

    def test_get_request_metadata_default_empty(self):
        # Arrange
        clear_request_metadata()

        # Act
        result = get_request_metadata()

        # Assert
        assert result == {"api_id": "", "thread_id": ""}


class TestSetRequestMetadata:
    """Test cases for set_request_metadata function"""

    def test_set_request_metadata_stores_data(self):
        # Arrange
        metadata = {"api_id": "api-789", "thread_id": "thread-012"}

        # Act
        set_request_metadata(metadata)
        result = get_request_metadata()

        # Assert
        assert result["api_id"] == "api-789"
        assert result["thread_id"] == "thread-012"

        # Cleanup
        clear_request_metadata()

    def test_set_request_metadata_overwrites_existing(self):
        # Arrange
        set_request_metadata({"api_id": "old-api", "thread_id": "old-thread"})

        # Act
        set_request_metadata({"api_id": "new-api", "thread_id": "new-thread"})
        result = get_request_metadata()

        # Assert
        assert result["api_id"] == "new-api"
        assert result["thread_id"] == "new-thread"

        # Cleanup
        clear_request_metadata()


class TestGetContextApiId:
    """Test cases for get_context_api_id function"""

    def test_get_context_api_id_returns_api_id(self):
        # Arrange
        set_request_metadata({"api_id": "specific-api-id", "thread_id": "thread-id"})

        # Act
        result = get_context_api_id()

        # Assert
        assert result == "specific-api-id"

        # Cleanup
        clear_request_metadata()

    def test_get_context_api_id_returns_empty_when_not_set(self):
        # Arrange
        clear_request_metadata()

        # Act
        result = get_context_api_id()

        # Assert
        assert result == ""


class TestGetRequestJsonPostPayload:
    """Test cases for get_request_json_post_payload function"""

    def test_get_request_json_post_payload_returns_dict(self):
        # Arrange
        from utils.contextvar import context_json_post_payload

        context_json_post_payload.set(JsonPayload(data={"field": "value"}))

        # Act
        result = get_request_json_post_payload()

        # Assert
        assert result == {"field": "value"}

        # Cleanup
        clear_request_metadata()

    def test_get_request_json_post_payload_returns_empty_dict_on_error(self):
        # Arrange
        clear_request_metadata()

        # Act
        result = get_request_json_post_payload()

        # Assert
        assert result == {}


@pytest.mark.asyncio
class TestSetContextJsonPostPayload:
    """Test cases for set_context_json_post_payload function"""

    async def test_set_context_json_post_payload_with_post_request(self):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.method = "POST"
        mock_request.json = AsyncMock(return_value={"data": "test"})

        # Act
        await set_context_json_post_payload(mock_request)
        result = get_request_json_post_payload()

        # Assert
        assert result == {"data": "test"}

        # Cleanup
        clear_request_metadata()

    async def test_set_context_json_post_payload_skips_get_request(self):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"

        # Act
        await set_context_json_post_payload(mock_request)
        result = get_request_json_post_payload()

        # Assert
        assert result == {}

        # Cleanup
        clear_request_metadata()

    async def test_set_context_json_post_payload_skips_delete_request(self):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.method = "DELETE"

        # Act
        await set_context_json_post_payload(mock_request)
        result = get_request_json_post_payload()

        # Assert
        assert result == {}

        # Cleanup
        clear_request_metadata()

    async def test_set_context_json_post_payload_skips_options_request(self):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.method = "OPTIONS"

        # Act
        await set_context_json_post_payload(mock_request)
        result = get_request_json_post_payload()

        # Assert
        assert result == {}

        # Cleanup
        clear_request_metadata()

    async def test_set_context_json_post_payload_with_put_request(self):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.method = "PUT"
        mock_request.json = AsyncMock(return_value={"update": "data"})

        # Act
        await set_context_json_post_payload(mock_request)
        result = get_request_json_post_payload()

        # Assert
        assert result == {"update": "data"}

        # Cleanup
        clear_request_metadata()

    async def test_set_context_json_post_payload_with_patch_request(self):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.method = "PATCH"
        mock_request.json = AsyncMock(return_value={"patch": "data"})

        # Act
        await set_context_json_post_payload(mock_request)
        result = get_request_json_post_payload()

        # Assert
        assert result == {"patch": "data"}

        # Cleanup
        clear_request_metadata()

    @patch("utils.contextvar.LoggerUtil.create_error_log")
    async def test_set_context_json_post_payload_handles_json_exception(self, mock_logger):
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.method = "POST"
        mock_request.json = AsyncMock(side_effect=Exception("Invalid JSON"))

        # Act
        await set_context_json_post_payload(mock_request)
        result = get_request_json_post_payload()

        # Assert
        assert result == {}
        mock_logger.assert_called_once()

        # Cleanup
        clear_request_metadata()


class TestContextUser:
    """Test cases for context user functions"""

    def test_set_and_get_context_user(self):
        # Arrange
        user_data = {"id": 123, "email": "test@example.com"}

        # Act
        set_context_user(user_data)
        result = get_context_user()

        # Assert
        assert result == user_data

        # Cleanup
        clear_request_metadata()

    def test_get_context_user_returns_none_when_not_set(self):
        # Arrange
        clear_request_metadata()

        # Act
        result = get_context_user()

        # Assert
        assert result is None

    def test_set_context_user_overwrites_existing(self):
        # Arrange
        user1 = {"id": 1, "email": "user1@example.com"}
        user2 = {"id": 2, "email": "user2@example.com"}

        # Act
        set_context_user(user1)
        set_context_user(user2)
        result = get_context_user()

        # Assert
        assert result == user2

        # Cleanup
        clear_request_metadata()


class TestClearRequestMetadata:
    """Test cases for clear_request_metadata function"""

    def test_clear_request_metadata_resets_all_context_vars(self):
        # Arrange
        set_request_metadata({"api_id": "test-api", "thread_id": "test-thread"})
        set_context_user({"id": 123})
        from utils.contextvar import context_json_post_payload

        context_json_post_payload.set(JsonPayload(data={"data": "test"}))

        # Act
        clear_request_metadata()

        # Assert
        assert get_request_metadata() == {"api_id": "", "thread_id": ""}
        assert get_context_user() is None
        assert get_request_json_post_payload() == {}

    def test_clear_request_metadata_idempotent(self):
        # Arrange
        clear_request_metadata()

        # Act
        clear_request_metadata()
        result_metadata = get_request_metadata()
        result_user = get_context_user()

        # Assert
        assert result_metadata == {"api_id": "", "thread_id": ""}
        assert result_user is None
