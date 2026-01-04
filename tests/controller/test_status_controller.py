"""
Unit tests for controller/status_controller.py

Tests cover all endpoint handlers including:
- get_status
- get_deep_status
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock the decorators before importing the controller
sys.modules["decorators.user"] = MagicMock()
sys.modules["decorators.user"].require_authentication = lambda f: f

sys.modules["decorators.common"] = MagicMock()
sys.modules["decorators.common"].validate_json_payload = lambda schema: lambda f: f

from controller.status_controller import get_deep_status, get_status  # noqa: E402


class TestGetStatus:
    """Test cases for get_status endpoint"""

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_status_success(self, mock_response_format, mock_get_status):
        """Test successful status check"""
        # Arrange
        mock_request = Mock()
        mock_get_status.return_value = ("", {"status": "ok"}, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": {"status": "ok"}}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_status(mock_request)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": {"status": "ok"}}
        mock_get_status.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_status_returns_200(self, mock_response_format, mock_get_status):
        """Test that status endpoint always returns 200"""
        # Arrange
        mock_request = Mock()
        mock_get_status.return_value = ("", {"status": "ok"}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_status(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_status_passes_request_to_management(self, mock_response_format, mock_get_status):
        """Test that request is passed to StatusManagement"""
        # Arrange
        mock_request = Mock()
        mock_request.headers = {"test-header": "value"}
        mock_get_status.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_status(mock_request)

        # Assert
        mock_get_status.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_status_with_error_message(self, mock_response_format, mock_get_status):
        """Test status check with error message"""
        # Arrange
        mock_request = Mock()
        mock_get_status.return_value = ("Error occurred", {"status": "error"}, ["error1"])

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {}
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_status(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["message"] == "Error occurred"
        assert call_kwargs["data"] == {"status": "error"}
        assert call_kwargs["errors"] == ["error1"]


class TestGetDeepStatus:
    """Test cases for get_deep_status endpoint"""

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_deep_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_deep_status_success(self, mock_response_format, mock_get_deep_status):
        """Test successful deep status check"""
        # Arrange
        mock_request = Mock()
        mock_request.state.json_data = {"example_key": "value"}
        mock_get_deep_status.return_value = ("", {"db": "ok"}, None)

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {"status_code": 200, "message": "", "data": {"db": "ok"}}
        mock_response_format.return_value = mock_response_instance

        # Act
        result = await get_deep_status(mock_request)

        # Assert
        assert result == {"status_code": 200, "message": "", "data": {"db": "ok"}}

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_deep_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_deep_status_returns_200_on_success(self, mock_response_format, mock_get_deep_status):
        """Test that deep status returns 200 when no error"""
        # Arrange
        mock_request = Mock()
        mock_request.state.json_data = {"example_key": "value"}
        mock_get_deep_status.return_value = ("", {"db": "ok"}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_deep_status(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 200

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_deep_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_deep_status_returns_500_on_error(self, mock_response_format, mock_get_deep_status):
        """Test that deep status returns 500 when error occurs"""
        # Arrange
        mock_request = Mock()
        mock_request.state.json_data = {"example_key": "value"}
        mock_get_deep_status.return_value = ("DB connection failed", {"db": "error"}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_deep_status(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_deep_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_deep_status_passes_request(self, mock_response_format, mock_get_deep_status):
        """Test that request is passed to StatusManagement"""
        # Arrange
        mock_request = Mock()
        mock_request.state.json_data = {"example_key": "test_value"}
        mock_get_deep_status.return_value = ("", {}, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_deep_status(mock_request)

        # Assert
        mock_get_deep_status.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_deep_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_deep_status_with_errors(self, mock_response_format, mock_get_deep_status):
        """Test deep status check with errors"""
        # Arrange
        mock_request = Mock()
        mock_request.state.json_data = {"example_key": "value"}
        mock_get_deep_status.return_value = ("System check failed", {"db": "error", "redis": "error"}, ["DB connection failed", "Redis connection failed"])

        mock_response_instance = Mock()
        mock_response_instance.get_json.return_value = {}
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_deep_status(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["status_code"] == 500
        assert call_kwargs["message"] == "System check failed"
        assert call_kwargs["errors"] == ["DB connection failed", "Redis connection failed"]

    @pytest.mark.asyncio
    @patch("controller.status_controller.StatusManagement.get_deep_status")
    @patch("controller.status_controller.APIResponseFormat")
    async def test_get_deep_status_returns_data(self, mock_response_format, mock_get_deep_status):
        """Test that deep status returns correct data"""
        # Arrange
        mock_request = Mock()
        mock_request.state.json_data = {"example_key": "value"}
        data = {"ssq_db": {"response": "ok", "error": False}, "redis": {"response": "ok", "error": False}}
        mock_get_deep_status.return_value = ("", data, None)

        mock_response_instance = Mock()
        mock_response_format.return_value = mock_response_instance

        # Act
        await get_deep_status(mock_request)

        # Assert
        call_kwargs = mock_response_format.call_args[1]
        assert call_kwargs["data"] == data
