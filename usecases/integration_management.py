from data_adapter.integration import Integration
from data_adapter.user import User
from config.env import (
    META_CLIENT_ID,
    META_CLIENT_SECRET,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
)
import requests
from datetime import datetime, timedelta

from logger.logging import LoggerUtil


class IntegrationManagement:
    # Platform configurations
    PLATFORMS = {
        "instagram": {
            "auth_url": "https://api.instagram.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=user_profile,user_media&response_type=code",
            "token_url": "https://api.instagram.com/oauth/access_token",
            "client_id": META_CLIENT_ID,
            "client_secret": META_CLIENT_SECRET,
            "scope": "user_profile,user_media",
        },
        "youtube": {
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&scope=https://www.googleapis.com/auth/youtube&response_type=code&access_type=offline&prompt=consent",
            "token_url": "https://oauth2.googleapis.com/token",
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "scope": "https://www.googleapis.com/auth/youtube",
        },
    }

    PLATFORMS_USING_REFRESH_TOKEN = ["youtube"]

    @staticmethod
    def get_all_integrations(request):
        user = User.get_current_user()
        integrations = Integration.get_all_for_user(user)
        return None, [integration.get_details() for integration in integrations], None

    @staticmethod
    def get_integration_by_uuid(request, integration_uuid):
        user = User.get_current_user()
        try:
            integration = Integration.get_by_uuid_for_user(integration_uuid, user)
            return None, integration.get_details(), None
        except Integration.DoesNotExist:
            return "Integration not found", None, ["Integration not found"]

    @staticmethod
    def get_oauth_url(platform, request):
        config = IntegrationManagement.PLATFORMS.get(platform)
        if not config:
            return "Unsupported platform", None, ["Unsupported platform"]

        redirect_uri = request.app.settings.get(f"{platform.upper()}_REDIRECT_URI")
        return config["auth_url"].format(
            client_id=config["client_id"], redirect_uri=redirect_uri
        )

    @staticmethod
    def handle_oauth_callback(platform, code, request):
        config = IntegrationManagement.PLATFORMS.get(platform)
        if not config:
            return "Unsupported platform", None, ["Unsupported platform"]

        try:
            redirect_uri = request.app.settings.get(f"{platform.upper()}_REDIRECT_URI")
            data = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            }
            response = requests.post(config["token_url"], data=data)
            response_data = response.json()

            # Save the tokens
            user = User.get_current_user()
            expires_in = response_data.get("expires_in", 3600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            token_data = {
                "user_id": user.id,
                "platform": platform,
                "access_token": response_data["access_token"],
                "expires_at": expires_at,
                "token_type": response_data.get("token_type", "Bearer"),
                "scope": response_data.get("scope", ""),
            }

            # For platforms that use refresh tokens, we get a refresh token
            if platform in IntegrationManagement.PLATFORMS_USING_REFRESH_TOKEN:
                token_data["refresh_token"] = response_data.get("refresh_token")

            Integration.create_integration(**token_data)
            LoggerUtil.create_info_log("Integration created successfully")
            return "", response_data, None
        except Exception as e:
            LoggerUtil.create_error_log(f"Error in handle_oauth_callback: {e}")
            return "Error in handle_oauth_callback", None, [str(e)]

    @staticmethod
    def delete_integration(request, integration_uuid):
        user = User.get_current_user()
        try:
            integration = Integration.get_by_uuid_for_user(integration_uuid, user)
            integration.delete_instance()
            return "", None, None
        except Integration.DoesNotExist:
            return "Integration not found", None, ["Integration not found"]
        except Exception as e:
            LoggerUtil.create_error_log(f"Error in delete_integration: {e}")
            return "Error in delete_integration", None, [str(e)]
