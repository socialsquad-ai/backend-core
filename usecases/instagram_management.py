from config.non_env import Platform
from data_adapter.integration import Integration
from utils.platform_service import get_instagram_media, get_instagram_media_by_id, get_instagram_media_comments


async def get_instagram_posts(user_id: str, fields: str = None):
    integration = Integration.get_by_user_id_and_platform(user_id, Platform.INSTAGRAM.value)
    if not integration:
        # Or raise an exception
        return {"error": "Instagram integration not found."}

    access_token = integration.access_token
    return await get_instagram_media(access_token, fields)

async def get_instagram_post(user_id: str, post_id: str, fields: str = None):
    integration = Integration.get_by_user_id_and_platform(user_id, Platform.INSTAGRAM.value)
    if not integration:
        return {"error": "Instagram integration not found."}

    access_token = integration.access_token
    return await get_instagram_media_by_id(post_id, access_token, fields)

async def get_instagram_post_comments(user_id: str, post_id: str, fields: str = None):
    integration = Integration.get_by_user_id_and_platform(user_id, Platform.INSTAGRAM.value)
    if not integration:
        return {"error": "Instagram integration not found."}

    access_token = integration.access_token
    return await get_instagram_media_comments(post_id, access_token, fields)
