"""
Unit tests for data_adapter/personas.py

Tests cover all methods in PersonaTemplate and Persona models including:
PersonaTemplate:
- get_all_templates
- get_details

Persona:
- create_persona
- get_by_name
- get_by_name_and_user
- get_all
- get_all_count
- get_by_uuid
- get_all_for_user
- get_all_for_user_count
- delete_by_uuid
- get_details
"""

from unittest.mock import Mock, patch

from data_adapter.personas import Persona, PersonaTemplate


class TestPersonaTemplateGetAllTemplates:
    """Test cases for PersonaTemplate.get_all_templates method"""

    @patch.object(PersonaTemplate, "select_query")
    def test_get_all_templates_success(self, mock_select_query):
        """Test getting all persona templates"""
        # Arrange
        mock_template1 = Mock(name="Friendly")
        mock_template2 = Mock(name="Professional")
        mock_query = Mock()
        mock_query.limit.return_value = [mock_template1, mock_template2]
        mock_select_query.return_value = mock_query

        # Act
        result = PersonaTemplate.get_all_templates()

        # Assert
        mock_select_query.assert_called_once()
        mock_query.limit.assert_called_once_with(100)
        assert len(result) == 2

    @patch.object(PersonaTemplate, "select_query")
    def test_get_all_templates_empty(self, mock_select_query):
        """Test getting templates when none exist"""
        # Arrange
        mock_query = Mock()
        mock_query.limit.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = PersonaTemplate.get_all_templates()

        # Assert
        assert result == []


class TestPersonaTemplateGetDetails:
    """Test cases for PersonaTemplate.get_details method"""

    def test_get_details_complete_data(self):
        """Test get_details with complete template data"""
        # Arrange
        mock_template = Mock(spec=PersonaTemplate)
        mock_template.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_template.name = "Friendly Assistant"
        mock_template.description = "A friendly and helpful persona"
        mock_template.tone = "warm and welcoming"
        mock_template.style = "conversational"
        mock_template.instructions = "Be friendly and helpful at all times"

        # Bind the method to the instance
        mock_template.get_details = PersonaTemplate.get_details.__get__(mock_template, PersonaTemplate)

        # Act
        result = mock_template.get_details()

        # Assert
        assert result["uuid"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["name"] == "Friendly Assistant"
        assert result["description"] == "A friendly and helpful persona"
        assert result["tone"] == "warm and welcoming"
        assert result["style"] == "conversational"
        assert result["instructions"] == "Be friendly and helpful at all times"


class TestPersonaCreatePersona:
    """Test cases for Persona.create_persona method"""

    @patch.object(Persona, "create")
    def test_create_persona_success(self, mock_create):
        """Test creating a new persona"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona = Mock(id=1)
        mock_persona.refresh.return_value = mock_persona
        mock_create.return_value = mock_persona

        # Act
        result = Persona.create_persona(user=mock_user, name="My Persona", tone="professional", style="formal", instructions="Be professional", personal_details="CEO of Tech Company")

        # Assert
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["user"] == mock_user
        assert call_kwargs["name"] == "My Persona"
        assert call_kwargs["tone"] == "professional"
        mock_persona.refresh.assert_called_once()
        assert result == mock_persona

    @patch.object(Persona, "create")
    def test_create_persona_empty_personal_details(self, mock_create):
        """Test creating persona with empty personal details"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona = Mock()
        mock_persona.refresh.return_value = mock_persona
        mock_create.return_value = mock_persona

        # Act
        _result = Persona.create_persona(user=mock_user, name="Simple Persona", tone="casual", style="friendly", instructions="Be casual", personal_details="")

        # Assert
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["personal_details"] == ""


class TestPersonaGetByName:
    """Test cases for Persona.get_by_name method"""

    @patch.object(Persona, "select_query")
    def test_get_by_name_success(self, mock_select_query):
        """Test getting persona by name"""
        # Arrange
        mock_persona = Mock(name="Test Persona")
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = [mock_persona]
        mock_select_query.return_value = mock_query

        # Act
        _result = Persona.get_by_name("Test Persona")

        # Assert
        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_query.where.return_value.limit.assert_called_once_with(1)

    @patch.object(Persona, "select_query")
    def test_get_by_name_not_found(self, mock_select_query):
        """Test getting persona with invalid name"""
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value.limit.return_value = []
        mock_select_query.return_value = mock_query

        # Act
        result = Persona.get_by_name("NonExistent")

        # Assert
        assert result == []


class TestPersonaGetByNameAndUser:
    """Test cases for Persona.get_by_name_and_user method"""

    @patch.object(Persona, "select_query")
    def test_get_by_name_and_user_success(self, mock_select_query):
        """Test getting persona by name and user"""
        # Arrange
        mock_user = Mock(id=1)
        mock_persona = Mock(name="Test Persona", user=mock_user)
        mock_query = Mock()
        mock_query.where.return_value.get.return_value = mock_persona
        mock_select_query.return_value = mock_query

        # Act
        result = Persona.get_by_name_and_user("Test Persona", mock_user)

        # Assert
        assert result == mock_persona

    @patch.object(Persona, "select_query")
    def test_get_by_name_and_user_not_found(self, mock_select_query):
        """Test getting persona when not found raises DoesNotExist"""
        # Arrange
        mock_user = Mock(id=1)
        mock_query = Mock()
        mock_query.where.return_value.get.side_effect = Persona.DoesNotExist
        mock_select_query.return_value = mock_query

        # Act
        result = Persona.get_by_name_and_user("NonExistent", mock_user)

        # Assert
        assert result is None

    @patch.object(Persona, "select_query")
    def test_get_by_name_and_user_different_user(self, mock_select_query):
        """Test getting persona for different user returns None"""
        # Arrange
        mock_user = Mock(id=999)
        mock_query = Mock()
        mock_query.where.return_value.get.side_effect = Persona.DoesNotExist
        mock_select_query.return_value = mock_query

        # Act
        result = Persona.get_by_name_and_user("Test Persona", mock_user)

        # Assert
        assert result is None


class TestPersonaGetAll:
    """Test cases for Persona.get_all method"""

    @patch.object(Persona, "select_query")
    def test_get_all_default_pagination(self, mock_select_query):
        """Test get_all with default pagination"""
        # Arrange
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        _result = Persona.get_all()

        # Assert
        mock_query.order_by.assert_called_once()
        mock_query.order_by.return_value.limit.assert_called_once_with(10)
        mock_query.order_by.return_value.limit.return_value.offset.assert_called_once_with(0)

    @patch.object(Persona, "select_query")
    def test_get_all_custom_page(self, mock_select_query):
        """Test get_all with custom page"""
        # Arrange
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        _result = Persona.get_all(page=3, page_size=10)

        # Assert
        mock_query.order_by.return_value.limit.return_value.offset.assert_called_once_with(20)

    @patch.object(Persona, "select_query")
    def test_get_all_custom_page_size(self, mock_select_query):
        """Test get_all with custom page size"""
        # Arrange
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        _result = Persona.get_all(page=1, page_size=25)

        # Assert
        mock_query.order_by.return_value.limit.assert_called_once_with(25)

    @patch.object(Persona, "select_query")
    def test_get_all_orders_by_updated_at_desc(self, mock_select_query):
        """Test get_all orders by updated_at descending"""
        # Arrange
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        Persona.get_all()

        # Assert
        mock_query.order_by.assert_called_once()


class TestPersonaGetAllCount:
    """Test cases for Persona.get_all_count method"""

    @patch.object(Persona, "select_query")
    def test_get_all_count_success(self, mock_select_query):
        """Test getting total count of personas"""
        # Arrange
        mock_query = Mock()
        mock_query.count.return_value = 42
        mock_select_query.return_value = mock_query

        # Act
        result = Persona.get_all_count()

        # Assert
        assert result == 42

    @patch.object(Persona, "select_query")
    def test_get_all_count_zero(self, mock_select_query):
        """Test getting count when no personas exist"""
        # Arrange
        mock_query = Mock()
        mock_query.count.return_value = 0
        mock_select_query.return_value = mock_query

        # Act
        result = Persona.get_all_count()

        # Assert
        assert result == 0


class TestPersonaGetByUuid:
    """Test cases for Persona.get_by_uuid method"""

    @patch.object(Persona, "select")
    def test_get_by_uuid_success(self, mock_select):
        """Test getting persona by UUID"""
        # Arrange
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_persona = Mock(uuid=test_uuid)
        mock_query = Mock()
        mock_query.where.return_value.get.return_value = mock_persona
        mock_select.return_value = mock_query

        # Act
        result = Persona.get_by_uuid(test_uuid)

        # Assert
        assert result == mock_persona

    @patch.object(Persona, "select")
    def test_get_by_uuid_not_found(self, mock_select):
        """Test getting persona with invalid UUID"""
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value.get.side_effect = Persona.DoesNotExist
        mock_select.return_value = mock_query

        # Act
        result = Persona.get_by_uuid("invalid-uuid")

        # Assert
        assert result is None


class TestPersonaGetAllForUser:
    """Test cases for Persona.get_all_for_user method"""

    @patch.object(Persona, "select_query")
    def test_get_all_for_user_default_pagination(self, mock_select_query):
        """Test get_all_for_user with default pagination"""
        # Arrange
        mock_user = Mock(id=1)
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        _result = Persona.get_all_for_user(mock_user)

        # Assert
        mock_query.where.assert_called_once()
        mock_query.where.return_value.order_by.return_value.limit.assert_called_once_with(10)
        mock_query.where.return_value.order_by.return_value.limit.return_value.offset.assert_called_once_with(0)

    @patch.object(Persona, "select_query")
    def test_get_all_for_user_custom_page(self, mock_select_query):
        """Test get_all_for_user with custom page"""
        # Arrange
        mock_user = Mock(id=1)
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        _result = Persona.get_all_for_user(mock_user, page=2, page_size=15)

        # Assert
        mock_query.where.return_value.order_by.return_value.limit.assert_called_once_with(15)
        mock_query.where.return_value.order_by.return_value.limit.return_value.offset.assert_called_once_with(15)

    @patch.object(Persona, "select_query")
    def test_get_all_for_user_filters_by_user(self, mock_select_query):
        """Test get_all_for_user filters by user"""
        # Arrange
        mock_user = Mock(id=5)
        mock_query = Mock()
        mock_select_query.return_value = mock_query

        # Act
        Persona.get_all_for_user(mock_user)

        # Assert
        mock_query.where.assert_called_once()


class TestPersonaGetAllForUserCount:
    """Test cases for Persona.get_all_for_user_count method"""

    @patch.object(Persona, "select_query")
    def test_get_all_for_user_count_success(self, mock_select_query):
        """Test getting count of personas for user"""
        # Arrange
        mock_user = Mock(id=1)
        mock_query = Mock()
        mock_query.where.return_value.count.return_value = 15
        mock_select_query.return_value = mock_query

        # Act
        result = Persona.get_all_for_user_count(mock_user)

        # Assert
        assert result == 15

    @patch.object(Persona, "select_query")
    def test_get_all_for_user_count_zero(self, mock_select_query):
        """Test getting count when user has no personas"""
        # Arrange
        mock_user = Mock(id=999)
        mock_query = Mock()
        mock_query.where.return_value.count.return_value = 0
        mock_select_query.return_value = mock_query

        # Act
        result = Persona.get_all_for_user_count(mock_user)

        # Assert
        assert result == 0


class TestPersonaDeleteByUuid:
    """Test cases for Persona.delete_by_uuid method"""

    @patch.object(Persona, "get_by_uuid")
    def test_delete_by_uuid_success(self, mock_get_by_uuid):
        """Test soft deleting persona by UUID"""
        # Arrange
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_persona = Mock(is_deleted=False)
        mock_get_by_uuid.return_value = mock_persona

        # Act
        result = Persona.delete_by_uuid(test_uuid)

        # Assert
        assert result is True
        assert mock_persona.is_deleted is True
        mock_persona.save.assert_called_once()

    @patch.object(Persona, "get_by_uuid")
    def test_delete_by_uuid_not_found(self, mock_get_by_uuid):
        """Test deleting non-existent persona"""
        # Arrange
        mock_get_by_uuid.return_value = None

        # Act
        result = Persona.delete_by_uuid("invalid-uuid")

        # Assert
        assert result is False

    @patch.object(Persona, "get_by_uuid")
    def test_delete_by_uuid_already_deleted(self, mock_get_by_uuid):
        """Test deleting already deleted persona"""
        # Arrange
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_persona = Mock(is_deleted=True)
        mock_get_by_uuid.return_value = mock_persona

        # Act
        result = Persona.delete_by_uuid(test_uuid)

        # Assert
        assert result is True
        assert mock_persona.is_deleted is True


class TestPersonaGetDetails:
    """Test cases for Persona.get_details method"""

    def test_get_details_complete_data(self):
        """Test get_details with complete persona data"""
        # Arrange
        mock_persona = Mock(spec=Persona)
        mock_persona.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_persona.name = "My Business Persona"
        mock_persona.tone = "professional"
        mock_persona.style = "formal"
        mock_persona.instructions = "Always be professional"
        mock_persona.personal_details = "CEO of Tech Company"

        # Bind the method to the instance
        mock_persona.get_details = Persona.get_details.__get__(mock_persona, Persona)

        # Act
        result = mock_persona.get_details()

        # Assert
        assert result["uuid"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["name"] == "My Business Persona"
        assert result["tone"] == "professional"
        assert result["style"] == "formal"
        assert result["instructions"] == "Always be professional"
        assert result["personal_details"] == "CEO of Tech Company"

    def test_get_details_empty_personal_details(self):
        """Test get_details with empty personal details"""
        # Arrange
        mock_persona = Mock(spec=Persona)
        mock_persona.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_persona.name = "Simple Persona"
        mock_persona.tone = "casual"
        mock_persona.style = "friendly"
        mock_persona.instructions = "Be friendly"
        mock_persona.personal_details = ""

        # Bind the method to the instance
        mock_persona.get_details = Persona.get_details.__get__(mock_persona, Persona)

        # Act
        result = mock_persona.get_details()

        # Assert
        assert result["personal_details"] == ""

    def test_get_details_all_fields_present(self):
        """Test that get_details returns all required fields"""
        # Arrange
        mock_persona = Mock(spec=Persona)
        mock_persona.uuid = "550e8400-e29b-41d4-a716-446655440000"
        mock_persona.name = "Test"
        mock_persona.tone = "neutral"
        mock_persona.style = "balanced"
        mock_persona.instructions = "test"
        mock_persona.personal_details = "test"

        # Bind the method to the instance
        mock_persona.get_details = Persona.get_details.__get__(mock_persona, Persona)

        # Act
        result = mock_persona.get_details()

        # Assert
        required_fields = ["uuid", "name", "tone", "style", "instructions", "personal_details"]
        for field in required_fields:
            assert field in result
        assert len(result) == 6
