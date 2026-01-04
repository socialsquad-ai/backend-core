from typing import Tuple, Optional, Dict, Any
from data_adapter.user import User
from usecases.persona_management import PersonaManagement
from data_adapter.db import ssq_db
from logger.logging import LoggerUtil


class OnboardingManagement:
    @staticmethod
    @ssq_db.atomic()
    def onboard_user(
        user: User,
        persona_name: str,
        tone: str,
        style: str,
        instructions: str,
        role: str,
        content_categories: list,
        personal_details: str | None = None,
    ) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
        """
        Create a new persona for the current user and update user fields atomically.
        Both operations happen within a single transaction - if either fails, both are rolled back.

        Returns:
            Tuple of (error_message, data, errors):
            - error_message: Empty string if successful, error message otherwise
            - data: Persona details dict if successful, None otherwise
            - errors: Error details if any, None otherwise
        """
        try:
            # Create persona first
            error_message, persona_data, errors = PersonaManagement.create_persona(
                user=user,
                name=persona_name,
                tone=tone,
                style=style,
                instructions=instructions,
                personal_details=personal_details,
            )

            # Check if persona creation failed
            if error_message:
                LoggerUtil.create_error_log(
                    f"Persona creation failed during onboarding: {error_message}"
                )
                # Rollback transaction manually since we're returning error tuple instead of raising
                ssq_db.rollback()
                return error_message, None, errors

            # Update user fields (role, content_categories, status)
            # This happens in the same transaction as persona creation
            try:
                user.update_values(
                    role=role, content_categories=content_categories, status="active"
                )
            except Exception as e:
                error_msg = f"Failed to update user fields: {str(e)}"
                LoggerUtil.create_error_log(error_msg)
                # Rollback transaction manually since we need to return error tuple
                ssq_db.rollback()
                return error_msg, None, str(e)

            return "", persona_data, None

        except Exception as e:
            error_msg = f"Unexpected error during onboarding: {str(e)}"
            LoggerUtil.create_error_log(error_msg)
            # Rollback transaction manually since we need to return error tuple
            ssq_db.rollback()
            return error_msg, None, str(e)
