from data_adapter.personas import Persona, PersonaTemplate
from data_adapter.account import Account
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
    def get_account_personas(account: Account, page: int = 1, page_size: int = 10):
        """
        Get paginated personas for an account
        """
        if page < 1 or page_size < 1 or page_size > 100:
            return INVALID_PAGINATION_PARAMETERS, None, None

        query = Persona.get_all_for_account(account, page, page_size)
        total = Persona.get_all_for_account_count(account)

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
    def create_account_persona(
        account: Account,
        name: str,
        tone: str,
        style: str,
        instructions: str,
        personal_details: str | None = None,
    ):
        persona = Persona.get_by_name_and_account(name, account)
        if persona:
            return PERSONA_ALREADY_EXISTS, None, None
        persona = Persona.create_persona(
            account=account,
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
    def update_account_persona(
        account: Account,
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
            persona_check = Persona.get_by_name_and_account(name, persona.account)
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
    def delete_account_persona(persona_uuid: str, account: Account):
        success = Persona.delete_by_uuid(persona_uuid)
        if not success:
            return RESOURCE_NOT_FOUND, None, None
        return "", None, None
