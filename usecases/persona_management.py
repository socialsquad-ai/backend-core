from data_adapter.personas import Persona, PersonaTemplate
from data_adapter.user import User
from utils.error_messages import (
    RESOURCE_NOT_FOUND,
    INVALID_PAGINATION_PARAMETERS,
    PERSONA_ALREADY_EXISTS,
)


class PersonaManagement:
    @staticmethod
    def get_persona_templates():
        """
        Get all persona templates
        """
        templates = PersonaTemplate.get_all_templates()
        return "", [template.get_details() for template in templates], None

    @staticmethod
    def get_user_personas(user: User, page: int = 1, page_size: int = 10):
        """
        Get paginated personas for a user
        """
        if page < 1 or page_size < 1 or page_size > 100:
            return INVALID_PAGINATION_PARAMETERS, None, None

        query = Persona.get_all_for_user(user, page, page_size)
        total = Persona.get_all_for_user_count(user)

        return (
            "",
            {
                "items": [persona.get_details() for persona in query],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
                if page_size > 0
                else 0,
            },
            None,
        )

    @staticmethod
    def create_persona(
        user: User,
        name: str,
        tone: str,
        style: str,
        instructions: str,
        personal_details: str | None = None,
    ):
        persona = Persona.get_by_name_and_user(name, user)
        if persona:
            return PERSONA_ALREADY_EXISTS, None, None
        persona = Persona.create_persona(
            user=user,
            name=name,
            tone=tone,
            style=style,
            instructions=instructions,
            personal_details=personal_details or "",
        )

        return "", persona.get_details(), None

    @staticmethod
    def get_persona(persona_uuid: str):
        return Persona.get_by_uuid(persona_uuid)

    @staticmethod
    def update_persona(
        user: User,
        persona_uuid: str,
        name: str | None = None,
        tone: str | None = None,
        style: str | None = None,
        instructions: str | None = None,
        personal_details: str | None = None,
    ):
        persona = Persona.get_by_uuid(persona_uuid)
        if not persona:
            return RESOURCE_NOT_FOUND, None, None

        persona = persona[0]

        if name:
            persona_check = Persona.get_by_name_and_user(name, persona.user)
            if persona_check and str(persona_check[0].uuid) != persona_uuid:
                return PERSONA_ALREADY_EXISTS, None, None

        # Update fields if provided
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if tone is not None:
            update_data["tone"] = tone
        if style is not None:
            update_data["style"] = style
        if instructions is not None:
            update_data["instructions"] = instructions
        if personal_details is not None:
            update_data["personal_details"] = personal_details

        # Only update if there are changes
        if update_data:
            for key, value in update_data.items():
                setattr(persona, key, value)
            persona.save()

        return "", persona.get_details(), None

    @staticmethod
    def delete_persona(persona_uuid: str, user: User):
        success = Persona.delete_by_uuid(persona_uuid)
        if not success:
            return RESOURCE_NOT_FOUND, None, None
        return "", None, None
