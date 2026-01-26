from datetime import datetime, timedelta, timezone

import requests

from config.env import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    META_CLIENT_ID,
    META_CLIENT_SECRET,
    SSQ_BASE_URL,
    SSQ_CLIENT_URL,
)
from data_adapter.integration import Integration
from logger.logging import LoggerUtil
from utils.contextvar import get_context_user
from utils.error_messages import (
    INTEGRATION_NOT_FOUND,
    UNSUPPORTED_PLATFORM,
    USER_NOT_FOUND,
)


class IntegrationManagement:
    # Platform configurations
    PLATFORMS = {
        "instagram": {
            "auth_url": "https://www.instagram.com/oauth/authorize?force_reauth=true&client_id={client_id}&redirect_uri={redirect_uri}&scope=instagram_business_basic,instagram_business_manage_messages,instagram_business_manage_comments,instagram_business_content_publish,instagram_business_manage_insights&response_type=code",
            "token_url": "https://api.instagram.com/oauth/access_token",
            "client_id": META_CLIENT_ID,
            "client_secret": META_CLIENT_SECRET,
            "scope": "instagram_business_basic,instagram_business_manage_messages,instagram_business_manage_comments,instagram_business_content_publish,instagram_business_manage_insights",
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

    REDIRECT_URIS = {
        "web": "https://instagram.socialsquad.ai/oauth/callback/instagram",
        "mobile": "socialsquad://oauth/callback/instagram",
    }

    @staticmethod
    def get_all_integrations():
        user = get_context_user()
        integrations = Integration.get_all_for_user(user)
        return None, [integration.get_details() for integration in integrations], None

    @staticmethod
    def get_integration_by_uuid(integration_uuid):
        user = get_context_user()
        integration = Integration.get_by_uuid_for_user(integration_uuid, user)
        if not integration:
            return INTEGRATION_NOT_FOUND, None, [INTEGRATION_NOT_FOUND]
        return None, integration[0].get_details(), None

    @staticmethod
    def get_oauth_url(platform, request):
        config = IntegrationManagement.PLATFORMS.get(platform)
        if not config:
            return UNSUPPORTED_PLATFORM, None, [UNSUPPORTED_PLATFORM]

        interface_type = request.query_params.get("interface_type", "web")
        redirect_uri = IntegrationManagement.REDIRECT_URIS[interface_type]

        return (
            "",
            config["auth_url"].format(client_id=config["client_id"], redirect_uri=redirect_uri),
            None,
        )

    @staticmethod
    def handle_oauth_callback(platform, code):
        config = IntegrationManagement.PLATFORMS.get(platform)
        if not config:
            return UNSUPPORTED_PLATFORM, None, [UNSUPPORTED_PLATFORM]

        try:
            data = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{SSQ_BASE_URL}/v1/integrations/{platform}/oauth/callback",
            }
            response = requests.post(config["token_url"], data=data)
            response_data = response.json()
            LoggerUtil.create_info_log(f"token response: {response_data}")

            # Save the tokens
            user = get_context_user()
            if not user:
                return USER_NOT_FOUND, None, [USER_NOT_FOUND]
            user = user[0]

            # For handling expired access tokens
            expires_in = response_data.get("expires_in", 3600)
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            # Refresh token is not available for all platforms so adding a check here
            refresh_token = response_data.get("refresh_token")
            if refresh_token:
                refresh_token_expires_in = response_data.get("refresh_token_expires_in", 604800)
                refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=refresh_token_expires_in)

            # Handling scopes for different platforms
            scopes = []
            if platform == "youtube":
                scopes = response_data["scope"].split(",")
            elif platform == "instagram":
                scopes = response_data["permissions"]

            token_data = {
                "platform_user_id": response_data.get("user_id"),
                "user": user,
                "platform": platform,
                "access_token": response_data["access_token"],
                "expires_at": expires_at,
                "refresh_token": refresh_token,
                "refresh_token_expires_at": refresh_token_expires_at,
                "token_type": response_data.get("token_type", "Bearer"),
                "scopes": scopes,
            }

            Integration.create_integration(**token_data)
            LoggerUtil.create_info_log("Integration created successfully")
            return "", SSQ_CLIENT_URL, None
        except Exception as e:
            LoggerUtil.create_error_log(f"Error in handle_oauth_callback: {e}")
            return "Error in handle_oauth_callback", None, [str(e)]

    @staticmethod
    def delete_integration(integration_uuid):
        user = get_context_user()
        integration = Integration.delete_by_uuid_for_user(integration_uuid, user)
        if not integration:
            return "Integration not found", None, ["Integration not found"]
        return "", None, None
