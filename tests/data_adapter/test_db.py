from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

from data_adapter.db import BaseModel, get_db_status, ssq_db


class TestBaseModelGetByPk:
    @patch.object(BaseModel, "select_query")
    def test_get_by_pk_queries_correctly(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = []

        BaseModel.get_by_pk(123)

        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_where.limit.assert_called_once_with(1)


class TestBaseModelGetByUuid:
    @patch.object(BaseModel, "select_query")
    def test_get_by_uuid_queries_correctly(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = []

        test_uuid = "test-uuid-123"
        BaseModel.get_by_uuid(test_uuid)

        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_where.limit.assert_called_once_with(1)


class TestBaseModelSave:
    @patch("data_adapter.db.datetime")
    def test_save_updates_updated_at_by_default(self, mock_datetime):
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = now

        instance = BaseModel()
        with patch.object(BaseModel.__bases__[0], "save", return_value=True) as mock_super_save:
            instance.save()

            assert instance.updated_at == now
            mock_super_save.assert_called_once()

    @patch("data_adapter.db.datetime")
    def test_save_skips_updated_at_when_requested(self, mock_datetime):
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = now

        instance = BaseModel()
        instance.updated_at = None

        with patch.object(BaseModel.__bases__[0], "save", return_value=True) as mock_super_save:
            instance.save(skip_updated_at=True)

            assert instance.updated_at is None
            mock_super_save.assert_called_once()


class TestBaseModelRefresh:
    @patch.object(BaseModel, "get")
    @patch.object(BaseModel, "_pk_expr")
    def test_refresh_gets_instance_by_pk(self, mock_pk_expr, mock_get):
        mock_pk = Mock()
        mock_pk_expr.return_value = mock_pk
        refreshed_instance = Mock()
        mock_get.return_value = refreshed_instance

        instance = BaseModel()
        result = instance.refresh()

        mock_pk_expr.assert_called_once()
        mock_get.assert_called_once_with(mock_pk)
        assert result == refreshed_instance


class TestBaseModelSelectQuery:
    @patch.object(BaseModel, "select")
    def test_select_query_filters_deleted_records(self, mock_select):
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_query.where.return_value = mock_query

        BaseModel.select_query()

        mock_select.assert_called_once()
        mock_query.where.assert_called_once()

    @patch.object(BaseModel, "select")
    def test_select_query_with_columns(self, mock_select):
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_query.where.return_value = mock_query

        columns = ["col1", "col2"]
        BaseModel.select_query(columns=columns)

        mock_select.assert_called_once_with("col1", "col2")

    @patch.object(BaseModel, "select")
    def test_select_query_without_columns(self, mock_select):
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_query.where.return_value = mock_query

        BaseModel.select_query(columns=None)

        mock_select.assert_called_once_with()


class TestBaseModelUpdateQuery:
    @patch("data_adapter.db.datetime")
    @patch.object(BaseModel, "update")
    def test_update_query_adds_updated_at_by_default(self, mock_update, mock_datetime):
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = now

        update_dict = {"name": "test"}
        BaseModel.update_query(update_dict)

        assert BaseModel.updated_at in update_dict
        assert update_dict[BaseModel.updated_at] == now
        mock_update.assert_called_once_with(update_dict)

    @patch("data_adapter.db.datetime")
    @patch.object(BaseModel, "update")
    def test_update_query_skips_updated_at_when_requested(self, mock_update, mock_datetime):
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = now

        update_dict = {"name": "test"}
        BaseModel.update_query(update_dict, skip_updated_at=True)

        assert BaseModel.updated_at not in update_dict
        mock_update.assert_called_once_with(update_dict)


class TestBaseModelSoftDelete:
    @patch("data_adapter.db.datetime")
    @patch.object(BaseModel, "update")
    def test_soft_delete_sets_is_deleted_and_updated_at(self, mock_update, mock_datetime):
        now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = now

        BaseModel.soft_delete()

        call_args = mock_update.call_args[0][0]
        assert call_args[BaseModel.is_deleted] is True
        assert call_args[BaseModel.updated_at] == now
        mock_update.assert_called_once()


class TestGetDbStatus:
    @patch("data_adapter.db.LoggerUtil.create_info_log")
    @patch("data_adapter.db.LoggerUtil.create_error_log")
    @patch.object(ssq_db, "execute_sql")
    def test_get_db_status_success(self, mock_execute_sql, mock_error_log, mock_info_log):
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ["ok"]
        mock_execute_sql.return_value = mock_cursor

        res, error = get_db_status()

        assert res == "ok"
        assert error is False
        assert mock_info_log.called
        mock_execute_sql.assert_called_once_with("select 'ok'")

    @patch("data_adapter.db.LoggerUtil.create_info_log")
    @patch("data_adapter.db.LoggerUtil.create_error_log")
    @patch.object(ssq_db, "execute_sql")
    def test_get_db_status_failure(self, mock_execute_sql, mock_error_log, mock_info_log):
        error_message = "Connection failed"
        mock_execute_sql.side_effect = Exception(error_message)

        res, error = get_db_status()

        assert res == error_message
        assert error is True
        assert mock_info_log.called
        assert mock_error_log.called

    @patch("data_adapter.db.LoggerUtil.create_info_log")
    @patch("data_adapter.db.LoggerUtil.create_error_log")
    @patch.object(ssq_db, "execute_sql")
    def test_get_db_status_logs_connection_info(self, mock_execute_sql, mock_error_log, mock_info_log):
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ["ok"]
        mock_execute_sql.return_value = mock_cursor

        get_db_status()

        # Verify that info log was called with connection details
        info_log_calls = mock_info_log.call_args_list
        assert len(info_log_calls) >= 1
        first_call = str(info_log_calls[0])
        assert "GET_DB_STATUS" in first_call
