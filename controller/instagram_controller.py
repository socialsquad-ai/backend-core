from fastapi import APIRouter

from config.non_env import API_VERSION_V1
from decorators.user import require_authentication
from usecases.instagram_management import get_instagram_post, get_instagram_post_comments, get_instagram_posts
from utils.contextvar import get_context_user

instagram_router = APIRouter(prefix=f"{API_VERSION_V1}/instagram", tags=["Instagram"])

@instagram_router.get("/posts")
@require_authentication
async def list_posts(fields: str = None):
    user = get_context_user()
    posts = await get_instagram_posts(user.id, fields)
    return posts

@instagram_router.get("/post/{post_id}")
@require_authentication
async def get_post(post_id: str, fields: str = None):
    user = get_context_user()
    post = await get_instagram_post(user.id, post_id, fields)
    return post

@instagram_router.get("/post/{post_id}/comments")
@require_authentication
async def get_comments(post_id: str, fields: str = None):
    user = get_context_user()
    comments = await get_instagram_post_comments(user.id, post_id, fields)
    return comments
