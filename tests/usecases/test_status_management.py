from unittest.mock import Mock, patch

import pytest

from usecases.status_management import StatusManagement


class TestStatusManagementGetStatus:
    def test_get_status_returns_ok_without_exception_header(self):
        mock_request = Mock()
        mock_request.headers.get.return_value = None

        error, data, extra = StatusManagement.get_status(mock_request)

        assert error == ""
        assert data == {"status": "ok"}
        assert extra is None

    def test_get_status_raises_exception_when_header_present(self):
        mock_request = Mock()
        mock_request.headers.get.return_value = "Test exception"

        with pytest.raises(Exception, match="Test exception"):
            StatusManagement.get_status(mock_request)

    def test_get_status_checks_raise_exception_header(self):
        mock_request = Mock()
        mock_request.headers.get.return_value = None

        StatusManagement.get_status(mock_request)

        mock_request.headers.get.assert_called_with("raise-exception")


class TestStatusManagementGetDeepStatus:
    @patch("usecases.status_management.get_db_status")
    @patch("usecases.status_management.LoggerUtil.create_info_log")
    def test_get_deep_status_with_healthy_db(self, mock_log, mock_get_db_status):
        mock_request = Mock()
        mock_get_db_status.return_value = ("ok", False)

        error, data, extra = StatusManagement.get_deep_status(mock_request)

        assert error == ""
        assert data == {"ssq_db": {"response": "ok", "error": False}}
        assert extra is None
        mock_log.assert_called_once_with("Status controller: get_deep_status")

    @patch("usecases.status_management.get_db_status")
    @patch("usecases.status_management.LoggerUtil.create_info_log")
    def test_get_deep_status_with_db_error(self, mock_log, mock_get_db_status):
        mock_request = Mock()
        mock_get_db_status.return_value = ("Connection failed", True)

        error, data, extra = StatusManagement.get_deep_status(mock_request)

        assert error == "Deep status check failed"
        assert data == {"ssq_db": {"response": "Connection failed", "error": True}}
        assert extra is None

    @patch("usecases.status_management.get_db_status")
    @patch("usecases.status_management.LoggerUtil.create_info_log")
    def test_get_deep_status_logs_info(self, mock_log, mock_get_db_status):
        mock_request = Mock()
        mock_get_db_status.return_value = ("ok", False)

        StatusManagement.get_deep_status(mock_request)

        mock_log.assert_called_once()
