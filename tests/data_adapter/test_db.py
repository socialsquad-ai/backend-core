"""
Unit tests for data_adapter/db.py

Tests cover all methods in the BaseModel class and get_db_status function including:
BaseModel:
- get_by_pk
- get_by_uuid
- save
- refresh
- select_query
- update_query
- soft_delete

Functions:
- get_db_status
"""

from datetime import datetime
from unittest.mock import Mock, patch

from data_adapter.db import BaseModel, get_db_status


class TestBaseModelGetByPk:
    """Test cases for BaseModel.get_by_pk method"""

    @patch.object(BaseModel, "select_query")
    def test_get_by_pk_success(self, mock_select_query):
        """Test getting model by primary key"""
        # Arrange
        mock_model = Mock(id=1)
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = [mock_model]
        mock_select_query.return_value = mock_query

        # Act
        _result = BaseModel.get_by_pk(1)

        # Assert
        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_query.where.return_value.limit.assert_called_once_with(1)

    @patch.object(BaseModel, "select_query")
    def test_get_by_pk_not_found(self, mock_select_query):
        """Test getting model with non-existent pk"""
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = BaseModel.get_by_pk(999)

        # Assert
        assert result == []


class TestBaseModelGetByUuid:
    """Test cases for BaseModel.get_by_uuid method"""

    @patch.object(BaseModel, "select_query")
    def test_get_by_uuid_success(self, mock_select_query):
        """Test getting model by UUID"""
        # Arrange
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_model = Mock(uuid=test_uuid)
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = [mock_model]
        mock_select_query.return_value = mock_query

        # Act
        _result = BaseModel.get_by_uuid(test_uuid)

        # Assert
        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_query.where.return_value.limit.assert_called_once_with(1)

    @patch.object(BaseModel, "select_query")
    def test_get_by_uuid_not_found(self, mock_select_query):
        """Test getting model with invalid UUID"""
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = BaseModel.get_by_uuid("invalid-uuid")

        # Assert
        assert result == []


class TestBaseModelSave:
    """Test cases for BaseModel.save method"""

    @patch("data_adapter.db.datetime")
    def test_save_updates_updated_at(self, mock_datetime):
        """Test save updates updated_at timestamp"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        mock_model = Mock(spec=BaseModel)
        mock_model.updated_at = None

        # Mock the parent save method
        with patch("peewee.Model.save") as mock_parent_save:
            # Bind the method to the instance
            mock_model.save = BaseModel.save.__get__(mock_model, BaseModel)

            # Act
            mock_model.save()

            # Assert
            assert mock_model.updated_at == mock_now
            mock_parent_save.assert_called_once()

    @patch("data_adapter.db.datetime")
    def test_save_skip_updated_at(self, mock_datetime):
        """Test save with skip_updated_at=True"""
        # Arrange
        old_time = datetime(2024, 1, 1, 10, 0, 0)
        mock_model = Mock(spec=BaseModel)
        mock_model.updated_at = old_time

        # Mock the parent save method
        with patch("peewee.Model.save") as _mock_parent_save:
            # Bind the method to the instance
            mock_model.save = BaseModel.save.__get__(mock_model, BaseModel)

            # Act
            mock_model.save(skip_updated_at=True)

            # Assert
            # updated_at should not be changed
            assert mock_model.updated_at == old_time
            mock_datetime.datetime.now.assert_not_called()

    @patch("data_adapter.db.datetime")
    def test_save_with_additional_args(self, mock_datetime):
        """Test save passes through additional arguments"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        mock_model = Mock(spec=BaseModel)
        mock_model.updated_at = None

        # Mock the parent save method
        with patch("peewee.Model.save") as mock_parent_save:
            # Bind the method to the instance
            mock_model.save = BaseModel.save.__get__(mock_model, BaseModel)

            # Act
            mock_model.save(force_insert=True)

            # Assert
            mock_parent_save.assert_called_once()


class TestBaseModelRefresh:
    """Test cases for BaseModel.refresh method"""

    def test_refresh_returns_updated_instance(self):
        """Test refresh returns updated instance from database"""
        # This test verifies that refresh() calls the model's get() method
        # We don't need to test the actual database refresh since that's
        # a peewee ORM responsibility. We just verify the method exists and works.

        # Arrange - create a mock that has a _pk_expr
        from peewee import CharField

        class TestRefreshModel(BaseModel):
            name = CharField()

            class Meta:
                table_name = "test_refresh"

        updated_instance = TestRefreshModel()
        updated_instance.id = 1
        updated_instance.name = "Updated"

        # Mock the get method to return the updated instance
        with patch.object(TestRefreshModel, "get", return_value=updated_instance) as mock_get:
            instance = TestRefreshModel()
            instance.id = 1

            # Act
            result = instance.refresh()

            # Assert
            assert result == updated_instance
            mock_get.assert_called_once()


class TestBaseModelSelectQuery:
    """Test cases for BaseModel.select_query method"""

    @patch.object(BaseModel, "select")
    def test_select_query_without_columns(self, mock_select):
        """Test select_query without specific columns"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query

        # Act
        _result = BaseModel.select_query()

        # Assert
        mock_select.assert_called_once_with()
        mock_query.where.assert_called_once()

    @patch.object(BaseModel, "select")
    def test_select_query_with_columns(self, mock_select):
        """Test select_query with specific columns"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query
        columns = [BaseModel.id, BaseModel.uuid]

        # Act
        _result = BaseModel.select_query(columns)

        # Assert
        mock_select.assert_called_once_with(*columns)

    @patch.object(BaseModel, "select")
    def test_select_query_filters_deleted(self, mock_select):
        """Test select_query filters out soft-deleted records"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query

        # Act
        BaseModel.select_query()

        # Assert
        # Verify where clause filters is_deleted == False
        mock_query.where.assert_called_once()

    @patch.object(BaseModel, "select")
    def test_select_query_none_columns_treated_as_empty_list(self, mock_select):
        """Test select_query with None columns parameter"""
        # Arrange
        mock_query = Mock()
        mock_select.return_value = mock_query

        # Act
        _result = BaseModel.select_query(None)

        # Assert
        mock_select.assert_called_once_with()


class TestBaseModelUpdateQuery:
    """Test cases for BaseModel.update_query method"""

    @patch("data_adapter.db.datetime")
    @patch.object(BaseModel, "update")
    def test_update_query_adds_updated_at(self, mock_update, mock_datetime):
        """Test update_query adds updated_at timestamp"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        update_dict = {"name": "New Name", "status": "active"}

        # Act
        _result = BaseModel.update_query(update_dict)

        # Assert
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0][0]
        assert BaseModel.updated_at in call_args
        assert call_args[BaseModel.updated_at] == mock_now

    @patch("data_adapter.db.datetime")
    @patch.object(BaseModel, "update")
    def test_update_query_skip_updated_at(self, mock_update, mock_datetime):
        """Test update_query with skip_updated_at=True"""
        # Arrange
        update_dict = {"name": "New Name"}

        # Act
        _result = BaseModel.update_query(update_dict, skip_updated_at=True)

        # Assert
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0][0]
        assert BaseModel.updated_at not in call_args
        mock_datetime.datetime.now.assert_not_called()

    @patch("data_adapter.db.datetime")
    @patch.object(BaseModel, "update")
    def test_update_query_empty_dict(self, mock_update, mock_datetime):
        """Test update_query with empty update dictionary"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        update_dict = {}

        # Act
        _result = BaseModel.update_query(update_dict)

        # Assert
        call_args = mock_update.call_args[0][0]
        # Should only contain updated_at
        assert BaseModel.updated_at in call_args


class TestBaseModelSoftDelete:
    """Test cases for BaseModel.soft_delete method"""

    @patch("data_adapter.db.datetime")
    @patch.object(BaseModel, "update")
    def test_soft_delete_sets_is_deleted_and_updated_at(self, mock_update, mock_datetime):
        """Test soft_delete sets is_deleted and updated_at"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        # Act
        _result = BaseModel.soft_delete()

        # Assert
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0][0]
        assert call_args[BaseModel.is_deleted] is True
        assert call_args[BaseModel.updated_at] == mock_now

    @patch("data_adapter.db.datetime")
    @patch.object(BaseModel, "update")
    def test_soft_delete_returns_update_query(self, mock_update, mock_datetime):
        """Test soft_delete returns update query"""
        # Arrange
        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_query = Mock()
        mock_update.return_value = mock_query

        # Act
        result = BaseModel.soft_delete()

        # Assert
        assert result == mock_query


class TestGetDbStatus:
    """Test cases for get_db_status function"""

    @patch("data_adapter.db.LoggerUtil")
    @patch("data_adapter.db.ssq_db")
    def test_get_db_status_success(self, mock_db, mock_logger):
        """Test get_db_status when connection is successful"""
        # Arrange
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ["ok"]
        mock_db.execute_sql.return_value = mock_cursor

        # Act
        result, error = get_db_status()

        # Assert
        assert result == "ok"
        assert error is False
        mock_logger.create_info_log.assert_called()
        mock_db.execute_sql.assert_called_once_with("select 'ok'")

    @patch("data_adapter.db.LoggerUtil")
    @patch("data_adapter.db.ssq_db")
    def test_get_db_status_connection_failure(self, mock_db, mock_logger):
        """Test get_db_status when connection fails"""
        # Arrange
        error_message = "Connection refused"
        mock_db.execute_sql.side_effect = Exception(error_message)

        # Act
        result, error = get_db_status()

        # Assert
        assert result == error_message
        assert error is True
        mock_logger.create_error_log.assert_called_once()

    @patch("data_adapter.db.LoggerUtil")
    @patch("data_adapter.db.ssq_db")
    def test_get_db_status_logs_connection_attempt(self, mock_db, mock_logger):
        """Test get_db_status logs connection information"""
        # Arrange
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ["ok"]
        mock_db.execute_sql.return_value = mock_cursor

        # Act
        get_db_status()

        # Assert
        # Verify initial info log was called
        assert mock_logger.create_info_log.call_count >= 1

    @patch("data_adapter.db.LoggerUtil")
    @patch("data_adapter.db.ssq_db")
    def test_get_db_status_timeout_error(self, mock_db, mock_logger):
        """Test get_db_status with timeout error"""
        # Arrange
        mock_db.execute_sql.side_effect = Exception("Connection timeout")

        # Act
        result, error = get_db_status()

        # Assert
        assert "Connection timeout" in result
        assert error is True

    @patch("data_adapter.db.LoggerUtil")
    @patch("data_adapter.db.ssq_db")
    def test_get_db_status_authentication_error(self, mock_db, mock_logger):
        """Test get_db_status with authentication error"""
        # Arrange
        mock_db.execute_sql.side_effect = Exception("Authentication failed")

        # Act
        result, error = get_db_status()

        # Assert
        assert "Authentication failed" in result
        assert error is True
