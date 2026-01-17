import httpx

from config.non_env import INSTAGRAM_GRAPH_API_BASE_URL, Platform
from logger.logging import LoggerUtil


async def _make_instagram_api_request(url: str, access_token: str, params: dict = None):
    """Helper function to make requests to Instagram Graph API."""
    if params is None:
        params = {}
    params["access_token"] = access_token

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            LoggerUtil.create_error_log(f"HTTP error occurred: {e.response.text}")
            # Consider how to propagate this error
            return {"error": f"HTTP error: {e.response.status_code}"}
        except Exception as e:
            LoggerUtil.create_error_log(f"An unexpected error occurred: {str(e)}")
            return {"error": "An unexpected error occurred."}

async def get_instagram_media(access_token: str, fields: str = None):
    """Get all media for the user."""
    url = f"{INSTAGRAM_GRAPH_API_BASE_URL}/me/media"
    params = {"fields": fields} if fields else {}
    return await _make_instagram_api_request(url, access_token, params)

async def get_instagram_media_by_id(media_id: str, access_token: str, fields: str = None):
    """Get a specific media by its ID."""
    url = f"{INSTAGRAM_GRAPH_API_BASE_URL}/{media_id}"
    params = {"fields": fields} if fields else {}
    return await _make_instagram_api_request(url, access_token, params)

async def get_instagram_media_comments(media_id: str, access_token: str, fields: str = None):
    """Get comments for a specific media."""
    url = f"{INSTAGRAM_GRAPH_API_BASE_URL}/{media_id}/comments"
    params = {"fields": fields} if fields else {}
    return await _make_instagram_api_request(url, access_token, params)


class PlatformService:
    @staticmethod
    async def delete_comment(platform: str, comment_id: str, access_token: str) -> bool:
        """
        Delete a comment on the specified platform.
        """
        try:
            if platform == Platform.INSTAGRAM.value:
                url = f"{INSTAGRAM_GRAPH_API_BASE_URL}/{comment_id}"
                async with httpx.AsyncClient() as client:
                    response = await client.delete(url, params={"access_token": access_token})

                if response.status_code == 200:
                    LoggerUtil.create_info_log(f"Successfully deleted comment {comment_id}")
                    return True
                else:
                    LoggerUtil.create_error_log(f"Failed to delete comment {comment_id}: {response.text}")
                    return False

            LoggerUtil.create_error_log(f"Unsupported platform for delete_comment: {platform}")
            return False

        except Exception as e:
            LoggerUtil.create_error_log(f"Exception in delete_comment: {str(e)}")
            return False

    @staticmethod
    async def reply_to_comment(platform: str, comment_id: str, message: str, access_token: str) -> bool:
        """
        Reply to a comment on the specified platform.
        """
        try:
            if platform == Platform.INSTAGRAM.value:
                url = f"{INSTAGRAM_GRAPH_API_BASE_URL}/{comment_id}/replies"
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        params={"access_token": access_token},
                        json={"message": message}
                    )

                if response.status_code == 200:
                    LoggerUtil.create_info_log(f"Successfully replied to comment {comment_id}")
                    return True
                else:
                    LoggerUtil.create_error_log(f"Failed to reply to comment {comment_id}: {response.text}")
                    return False

            LoggerUtil.create_error_log(f"Unsupported platform for reply_to_comment: {platform}")
            return False

        except Exception as e:
            LoggerUtil.create_error_log(f"Exception in reply_to_comment: {str(e)}")
            return False

    @staticmethod
    async def send_direct_message(platform: str, recipient_id: str, message: str, access_token: str) -> bool:
        """
        Send a direct message on the specified platform.
        """
        try:
            if platform == Platform.INSTAGRAM.value:
                url = f"{INSTAGRAM_GRAPH_API_BASE_URL}/me/messages"
                payload = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": message},
                    "messaging_type": "RESPONSE"
                }
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        params={"access_token": access_token},
                        json=payload
                    )

                if response.status_code == 200:
                    LoggerUtil.create_info_log(f"Successfully sent DM to {recipient_id}")
                    return True
                else:
                    LoggerUtil.create_error_log(f"Failed to send DM to {recipient_id}: {response.text}")
                    return False

            LoggerUtil.create_error_log(f"Unsupported platform for send_direct_message: {platform}")
            return False

        except Exception as e:
            LoggerUtil.create_error_log(f"Exception in send_direct_message: {str(e)}")
            return False
