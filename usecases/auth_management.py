from data_adapter.user import User
from logger.logging import LoggerUtil
from utils.auth0_service import Auth0ManagementService
from utils.contextvar import get_request_json_post_payload


class AuthManagement:
    @staticmethod
    async def resend_verification_email():
        """
        Resend verification email to a user.

        Returns:
            Tuple of (message, data, errors)
        """
        payload = get_request_json_post_payload()
        email = payload.get("email")

        LoggerUtil.create_info_log(f"Resend verification requested for email: {email}")

        # Check if user exists in our database
        db_users = User.get_by_email(email)
        if not db_users or len(db_users) == 0:
            LoggerUtil.create_info_log(f"Resend verification requested for non-existent email: {email}")
            # Return generic message to prevent email enumeration
            return (
                "If an account exists with this email, a verification link will be sent.",
                {"success": True},
                None,
            )

        db_user = db_users[0]

        # Check if already verified in our database
        if db_user.email_verified:
            LoggerUtil.create_info_log(f"Resend verification requested for already verified email: {email}")
            return (
                "This email is already verified. You can log in directly.",
                {"success": False},
                ["Email already verified"],
            )

        # User exists and is not verified - trigger verification email via Auth0
        auth0_user_id = db_user.auth0_user_id

        try:
            mgmt_service = Auth0ManagementService()
            result = await mgmt_service.send_verification_email(auth0_user_id)

            if result["success"]:
                return (
                    "Verification email sent! Please check your inbox and spam folder.",
                    {"success": True},
                    None,
                )
            else:
                # Handle rate limiting
                if "rate limit" in result["message"].lower():
                    return (
                        "Too many requests. Please wait a few minutes before trying again.",
                        {"success": False},
                        ["Rate limited"],
                    )
                return (
                    result["message"],
                    {"success": False},
                    [result["message"]],
                )

        except Exception as e:
            LoggerUtil.create_error_log(f"Error sending verification email: {e}")
            return (
                "Service temporarily unavailable. Please try again later.",
                {"success": False},
                [str(e)],
            )
