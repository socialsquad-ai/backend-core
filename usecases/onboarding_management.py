from data_adapter.user import User
from usecases.persona_management import PersonaManagement


class OnboardingManagement:
    @staticmethod
    def onboard_user(
        user: User,
        persona_name: str,
        tone: str,
        style: str,
        instructions: str,
        role: str,
        content_categories: list,
        personal_details: str | None = None,
    ):
        """
        Create a new persona for the current user
        """
        persona = PersonaManagement.create_persona(
            user=user,
            name=persona_name,
            tone=tone,
            style=style,
            instructions=instructions,
            personal_details=personal_details,
        )

        if not persona[0]:
            return persona[0], None, persona[2]

        user.update_values(
            role=role, content_categories=content_categories, status="active"
        )

        return "", persona[1], None
