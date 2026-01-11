import httpx

from config.non_env import PLATFORM_INSTAGRAM
from logger.logging import LoggerUtil


class PlatformService:
    @staticmethod
    async def delete_comment(platform: str, comment_id: str, access_token: str) -> bool:
        """
        Delete a comment on the specified platform.
        """
        try:
            if platform == PLATFORM_INSTAGRAM:
                # Instagram Graph API: DELETE /{comment-id}
                url = f"https://graph.facebook.com/v19.0/{comment_id}"
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
            if platform == PLATFORM_INSTAGRAM:
                # Instagram Graph API: POST /{comment-id}/replies
                url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
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
