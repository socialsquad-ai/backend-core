from typing import Any, Dict, Optional, Tuple

from data_adapter.personas import Persona, PersonaTemplate
from data_adapter.user import User
from logger.logging import LoggerUtil
from utils.error_messages import (
    INVALID_PAGINATION_PARAMETERS,
    PERSONA_ALREADY_EXISTS,
    RESOURCE_NOT_FOUND,
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
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
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
    ) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
        """
        Create a new persona for a user.

        Returns:
            Tuple of (error_message, data, errors):
            - error_message: Empty string if successful, error message otherwise
            - data: Persona details dict if successful, None otherwise
            - errors: Error details if any, None otherwise
        """
        try:
            # Check if persona with same name already exists for this user
            persona = Persona.get_by_name_and_user(name, user)
            if persona:
                return PERSONA_ALREADY_EXISTS, None, None

            # Create the persona
            persona = Persona.create_persona(
                user=user,
                name=name,
                tone=tone,
                style=style,
                instructions=instructions,
                personal_details=personal_details or "",
            )

            return "", persona.get_details(), None

        except Exception as e:
            error_msg = f"Failed to create persona: {str(e)}"
            LoggerUtil.create_error_log(error_msg)
            return error_msg, None, None

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
        # Verify it belongs to the user
        if persona.user.id != user.id:
            return RESOURCE_NOT_FOUND, None, None

        if name:
            persona_check = Persona.get_by_name_and_user(name, persona.user)
            if persona_check and str(persona_check.uuid) != persona_uuid:
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
        # First verify the persona exists and belongs to the user
        persona = Persona.get_by_uuid(persona_uuid)
        if not persona:
            return RESOURCE_NOT_FOUND, None, None
        # Verify it belongs to the user
        if persona.user.id != user.id:
            return RESOURCE_NOT_FOUND, None, None
        # Soft delete
        success = Persona.delete_by_uuid(persona_uuid)
        if not success:
            return RESOURCE_NOT_FOUND, None, None
        return "", None, None
