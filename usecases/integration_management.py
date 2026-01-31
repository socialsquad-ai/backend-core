from datetime import datetime, timedelta, timezone

import requests
import json

from config.env import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    META_CLIENT_ID,
    META_CLIENT_SECRET,
    SSQ_BASE_URL,
    SSQ_CLIENT_WEB_URL,
    SSQ_CLIENT_MOBILE_URL,
)
from config.non_env import Platform
from data_adapter.integration import Integration
from data_adapter.user import User
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
            "auth_url": "https://www.instagram.com/oauth/authorize?force_reauth=true&client_id={client_id}&redirect_uri={redirect_uri}&scope=instagram_business_basic,instagram_business_manage_messages,instagram_business_manage_comments,instagram_business_content_publish,instagram_business_manage_insights&response_type=code&state={state}",
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
        auth0_user_id = get_context_user().auth0_user_id
        state = {"user_id": auth0_user_id, "interface_type": interface_type}

        redirect_uri = f"{SSQ_BASE_URL}/v1/integrations/{platform}/oauth/callback"

        return (
            "",
            config["auth_url"].format(client_id=config["client_id"], redirect_uri=redirect_uri, state=json.dumps(state)),
            None,
        )

    @staticmethod
    def handle_oauth_callback(platform, code, state):
        config = IntegrationManagement.PLATFORMS.get(platform)
        if not config:
            return UNSUPPORTED_PLATFORM, None, [UNSUPPORTED_PLATFORM]

        try:
            # 1. Exchange authorization code for access token
            success, response_data, error = IntegrationManagement._exchange_code_for_token(platform, code, config)
            if not success:
                LoggerUtil.create_error_log(f"Error fetching access token: {response_data}")
                return "Error fetching access token", None, [error]

            # 2. Parse state and get user
            state_data = json.loads(state)
            user = User.get_by_auth0_user_id(state_data.get("user_id"))
            if not user:
                return USER_NOT_FOUND, None, [USER_NOT_FOUND]

            # 3. Enrich data based on platform
            if platform == Platform.INSTAGRAM.value:
                response_data = IntegrationManagement._enrich_instagram_data(config, response_data)
            elif platform == Platform.YOUTUBE.value:
                response_data = IntegrationManagement._enrich_youtube_data(config, response_data)

            # 4. Prepare and save integration
            token_data = IntegrationManagement._prepare_token_data(platform, user, response_data)
            Integration.create_or_update_integration(**token_data)

            LoggerUtil.create_info_log(f"Integration for {platform} created/updated successfully")

            redirect_url = SSQ_CLIENT_WEB_URL if state_data.get("interface_type") == "web" else SSQ_CLIENT_MOBILE_URL
            return "", redirect_url, None

        except Exception as e:
            LoggerUtil.create_error_log(f"Error in handle_oauth_callback: {e}")
            return "Error in handle_oauth_callback", None, [str(e)]

    @staticmethod
    def _exchange_code_for_token(platform, code, config):
        """Exchange the authorization code for an initial access token."""
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{SSQ_BASE_URL}/v1/integrations/{platform}/oauth/callback",
        }
        response = requests.post(config["token_url"], data=data)
        response_data = response.json()

        if "access_token" not in response_data:
            return False, response_data, response_data.get("error_message", "Unknown error")
        return True, response_data, None

    @staticmethod
    def _enrich_instagram_data(config, response_data):
        """Perform Instagram-specific token exchange and metadata fetching."""
        # Exchange for a long-lived token
        exchange_url = "https://graph.instagram.com/access_token"
        exchange_params = {
            "grant_type": "ig_exchange_token",
            "client_secret": config["client_secret"],
            "access_token": response_data["access_token"]
        }
        exchange_response = requests.get(exchange_url, params=exchange_params).json()

        if "access_token" in exchange_response:
            response_data.update(exchange_response)

        # Fetch username
        try:
            user_info = requests.get("https://graph.instagram.com/me", params={
                "fields": "id,username",
                "access_token": response_data["access_token"]
            }).json()
            response_data["platform_username"] = user_info.get("username")
        except Exception as e:
            LoggerUtil.create_error_log(f"Failed to fetch Instagram username: {e}")

        response_data["scopes"] = response_data.get("permissions", [])
        return response_data

    @staticmethod
    def _enrich_youtube_data(config, response_data):
        """Perform YouTube-specific metadata preparation."""
        response_data["scopes"] = response_data.get("scope", "").split(",")
        return response_data

    @staticmethod
    def _prepare_token_data(platform, user, response_data):
        """Normalize token data for the Integration model."""
        now = datetime.now(timezone.utc)
        expires_in = int(response_data.get("expires_in", 3600))
        refresh_expires_in = int(response_data.get("refresh_token_expires_in", 604800))

        return {
            "user": user,
            "platform": platform,
            "platform_user_id": response_data.get("user_id"),
            "platform_username": response_data.get("platform_username"),
            "access_token": response_data["access_token"],
            "token_type": response_data.get("token_type", "Bearer"),
            "expires_at": now + timedelta(seconds=expires_in),
            "refresh_token": response_data.get("refresh_token"),
            "refresh_token_expires_at": now + timedelta(seconds=refresh_expires_in) if response_data.get("refresh_token") else None,
            "scopes": response_data.get("scopes", []),
        }

    @staticmethod
    def delete_integration(integration_uuid):
        user = get_context_user()
        integration = Integration.delete_by_uuid_for_user(integration_uuid, user)
        if not integration:
            return "Integration not found", None, ["Integration not found"]
        return "", None, None
