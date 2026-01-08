from unittest.mock import MagicMock, Mock, patch

from data_adapter.personas import Persona, PersonaTemplate


class TestPersonaTemplateGetAllTemplates:
    @patch.object(PersonaTemplate, "select_query")
    def test_get_all_templates_limits_to_100(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.limit.return_value = []

        PersonaTemplate.get_all_templates()

        mock_select_query.assert_called_once()
        mock_query.limit.assert_called_once_with(100)


class TestPersonaTemplateGetDetails:
    def test_get_details_returns_all_fields(self):
        template = PersonaTemplate()
        template.uuid = "template-uuid-123"
        template.name = "Professional"
        template.description = "A professional tone"
        template.tone = "Formal"
        template.style = "Business"
        template.instructions = "Be professional"

        result = template.get_details()

        assert result["uuid"] == "template-uuid-123"
        assert result["name"] == "Professional"
        assert result["description"] == "A professional tone"
        assert result["tone"] == "Formal"
        assert result["style"] == "Business"
        assert result["instructions"] == "Be professional"


class TestPersonaCreatePersona:
    @patch.object(Persona, "refresh")
    @patch.object(Persona, "create")
    def test_create_persona_creates_and_refreshes(self, mock_create, mock_refresh):
        mock_user = Mock()
        mock_persona = Mock()
        mock_create.return_value = mock_persona
        mock_refreshed_persona = Mock()
        mock_persona.refresh.return_value = mock_refreshed_persona

        result = Persona.create_persona(user=mock_user, name="Test Persona", tone="Casual", style="Friendly", instructions="Be friendly", personal_details="Some details")

        mock_create.assert_called_once_with(user=mock_user, name="Test Persona", tone="Casual", style="Friendly", instructions="Be friendly", personal_details="Some details")
        mock_persona.refresh.assert_called_once()
        assert result == mock_refreshed_persona


class TestPersonaGetByName:
    @patch.object(Persona, "select_query")
    def test_get_by_name_queries_correctly(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.limit.return_value = []

        Persona.get_by_name("Test Name")

        mock_select_query.assert_called_once()
        mock_query.where.assert_called_once()
        mock_where.limit.assert_called_once_with(1)


class TestPersonaGetByNameAndUser:
    @patch.object(Persona, "select_query")
    def test_get_by_name_and_user_returns_persona(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_persona = Mock()
        mock_where.get.return_value = mock_persona

        mock_user = Mock()
        result = Persona.get_by_name_and_user("Test", mock_user)

        assert result == mock_persona
        mock_select_query.assert_called_once()
        mock_where.get.assert_called_once()

    @patch.object(Persona, "select_query")
    def test_get_by_name_and_user_returns_none_when_not_found(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.get.side_effect = Persona.DoesNotExist()

        mock_user = Mock()
        result = Persona.get_by_name_and_user("NonExistent", mock_user)

        assert result is None


class TestPersonaGetAll:
    @patch.object(Persona, "select_query")
    def test_get_all_with_default_pagination(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = []

        Persona.get_all()

        mock_query.limit.assert_called_once_with(10)
        mock_query.offset.assert_called_once_with(0)

    @patch.object(Persona, "select_query")
    def test_get_all_with_custom_pagination(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = []

        Persona.get_all(page=3, page_size=20)

        mock_query.limit.assert_called_once_with(20)
        mock_query.offset.assert_called_once_with(40)  # (3 - 1) * 20


class TestPersonaGetAllCount:
    @patch.object(Persona, "select_query")
    def test_get_all_count_returns_count(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.count.return_value = 42

        result = Persona.get_all_count()

        assert result == 42
        mock_query.count.assert_called_once()


class TestPersonaGetByUuid:
    @patch.object(Persona, "select")
    def test_get_by_uuid_returns_persona(self, mock_select):
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_persona = Mock()
        mock_where.get.return_value = mock_persona

        result = Persona.get_by_uuid("test-uuid")

        assert result == mock_persona
        mock_select.assert_called_once()
        mock_where.get.assert_called_once()

    @patch.object(Persona, "select")
    def test_get_by_uuid_returns_none_when_not_found(self, mock_select):
        mock_query = MagicMock()
        mock_select.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.get.side_effect = Persona.DoesNotExist()

        result = Persona.get_by_uuid("nonexistent-uuid")

        assert result is None


class TestPersonaGetAllForUser:
    @patch.object(Persona, "select_query")
    def test_get_all_for_user_with_default_pagination(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = []

        mock_user = Mock()
        Persona.get_all_for_user(mock_user)

        mock_query.limit.assert_called_once_with(10)
        mock_query.offset.assert_called_once_with(0)

    @patch.object(Persona, "select_query")
    def test_get_all_for_user_with_custom_pagination(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = []

        mock_user = Mock()
        Persona.get_all_for_user(mock_user, page=2, page_size=25)

        mock_query.limit.assert_called_once_with(25)
        mock_query.offset.assert_called_once_with(25)  # (2 - 1) * 25


class TestPersonaGetAllForUserCount:
    @patch.object(Persona, "select_query")
    def test_get_all_for_user_count_returns_count(self, mock_select_query):
        mock_query = MagicMock()
        mock_select_query.return_value = mock_query
        mock_where = MagicMock()
        mock_query.where.return_value = mock_where
        mock_where.count.return_value = 15

        mock_user = Mock()
        result = Persona.get_all_for_user_count(mock_user)

        assert result == 15
        mock_where.count.assert_called_once()


class TestPersonaDeleteByUuid:
    @patch.object(Persona, "get_by_uuid")
    def test_delete_by_uuid_soft_deletes_persona(self, mock_get_by_uuid):
        mock_persona = Mock()
        mock_persona.is_deleted = False
        mock_get_by_uuid.return_value = mock_persona

        result = Persona.delete_by_uuid("test-uuid")

        assert result is True
        assert mock_persona.is_deleted is True
        mock_persona.save.assert_called_once()

    @patch.object(Persona, "get_by_uuid")
    def test_delete_by_uuid_returns_false_when_not_found(self, mock_get_by_uuid):
        mock_get_by_uuid.return_value = None

        result = Persona.delete_by_uuid("nonexistent-uuid")

        assert result is False


class TestPersonaGetDetails:
    def test_get_details_returns_all_fields(self):
        persona = Persona()
        persona.uuid = "persona-uuid-456"
        persona.name = "My Persona"
        persona.tone = "Friendly"
        persona.style = "Casual"
        persona.instructions = "Be nice"
        persona.personal_details = "About me"

        result = persona.get_details()

        assert result["uuid"] == "persona-uuid-456"
        assert result["name"] == "My Persona"
        assert result["tone"] == "Friendly"
        assert result["style"] == "Casual"
        assert result["instructions"] == "Be nice"
        assert result["personal_details"] == "About me"

    def test_get_details_includes_all_required_keys(self):
        persona = Persona()
        persona.uuid = "uuid-789"
        persona.name = "Test"
        persona.tone = "Test"
        persona.style = "Test"
        persona.instructions = "Test"
        persona.personal_details = "Test"

        result = persona.get_details()

        assert "uuid" in result
        assert "name" in result
        assert "tone" in result
        assert "style" in result
        assert "instructions" in result
        assert "personal_details" in result
