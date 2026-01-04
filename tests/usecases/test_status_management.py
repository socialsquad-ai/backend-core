"""
Unit tests for usecases/status_management.py

Tests cover all methods in the StatusManagement class including:
- get_status
- get_deep_status
"""

from unittest.mock import Mock, patch

import pytest

from usecases.status_management import StatusManagement


class TestGetStatus:
    """Test cases for get_status method"""

    def test_get_status_normal_request(self):
        """Test get_status with normal request"""
        # Arrange
        mock_request = Mock()
        mock_request.headers.get.return_value = None

        # Act
        error_message, data, errors = StatusManagement.get_status(mock_request)

        # Assert
        assert error_message == ""
        assert data == {"status": "ok"}
        assert errors is None

    def test_get_status_raises_exception_when_header_present(self):
        """Test get_status raises exception when raise-exception header is present"""
        # Arrange
        mock_request = Mock()
        mock_request.headers.get.return_value = "Test error"

        # Act & Assert
        with pytest.raises(Exception, match="Test error"):
            StatusManagement.get_status(mock_request)

    def test_get_status_checks_raise_exception_header(self):
        """Test get_status checks for raise-exception header"""
        # Arrange
        mock_request = Mock()
        mock_request.headers.get.return_value = None

        # Act
        StatusManagement.get_status(mock_request)

        # Assert
        mock_request.headers.get.assert_called_once_with("raise-exception")

    def test_get_status_with_different_exception_messages(self):
        """Test get_status with different exception messages"""
        # Arrange
        mock_request = Mock()
        mock_request.headers.get.return_value = "Custom exception message"

        # Act & Assert
        with pytest.raises(Exception, match="Custom exception message"):
            StatusManagement.get_status(mock_request)


class TestGetDeepStatus:
    """Test cases for get_deep_status method"""

    @patch("usecases.status_management.LoggerUtil")
    @patch("usecases.status_management.get_db_status")
    def test_get_deep_status_all_systems_healthy(self, mock_get_db_status, mock_logger):
        """Test get_deep_status when all systems are healthy"""
        # Arrange
        mock_request = Mock()
        mock_get_db_status.return_value = ("ok", False)

        # Act
        error_message, data, errors = StatusManagement.get_deep_status(mock_request)

        # Assert
        assert error_message == ""
        assert data["ssq_db"]["response"] == "ok"
        assert data["ssq_db"]["error"] is False
        assert errors is None
        mock_logger.create_info_log.assert_called_once()

    @patch("usecases.status_management.LoggerUtil")
    @patch("usecases.status_management.get_db_status")
    def test_get_deep_status_database_error(self, mock_get_db_status, mock_logger):
        """Test get_deep_status when database has error"""
        # Arrange
        mock_request = Mock()
        mock_get_db_status.return_value = ("Connection failed", True)

        # Act
        error_message, data, errors = StatusManagement.get_deep_status(mock_request)

        # Assert
        assert error_message == "Deep status check failed"
        assert data["ssq_db"]["response"] == "Connection failed"
        assert data["ssq_db"]["error"] is True
        assert errors is None

    @patch("usecases.status_management.LoggerUtil")
    @patch("usecases.status_management.get_db_status")
    def test_get_deep_status_logs_info(self, mock_get_db_status, mock_logger):
        """Test get_deep_status logs info message"""
        # Arrange
        mock_request = Mock()
        mock_get_db_status.return_value = ("ok", False)

        # Act
        StatusManagement.get_deep_status(mock_request)

        # Assert
        mock_logger.create_info_log.assert_called_once_with("Status controller: get_deep_status")

    @patch("usecases.status_management.LoggerUtil")
    @patch("usecases.status_management.get_db_status")
    def test_get_deep_status_returns_correct_data_structure(self, mock_get_db_status, mock_logger):
        """Test get_deep_status returns correct data structure"""
        # Arrange
        mock_request = Mock()
        mock_get_db_status.return_value = ("ok", False)

        # Act
        error_message, data, errors = StatusManagement.get_deep_status(mock_request)

        # Assert
        assert "ssq_db" in data
        assert "response" in data["ssq_db"]
        assert "error" in data["ssq_db"]

    @patch("usecases.status_management.LoggerUtil")
    @patch("usecases.status_management.get_db_status")
    def test_get_deep_status_timeout_error(self, mock_get_db_status, mock_logger):
        """Test get_deep_status with database timeout"""
        # Arrange
        mock_request = Mock()
        mock_get_db_status.return_value = ("Connection timeout", True)

        # Act
        error_message, data, errors = StatusManagement.get_deep_status(mock_request)

        # Assert
        assert error_message == "Deep status check failed"
        assert "timeout" in data["ssq_db"]["response"].lower()
