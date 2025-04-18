from fastapi import APIRouter
from usecases.question_management import QuestionManager
from decorators.common import validate_json_payload
from fastapi import Request
from controller.util import APIResponseFormat
from config.non_env import API_VERSION_V1

questions_router = APIRouter(
    prefix=f"{API_VERSION_V1}/questions",
    tags=["questions"],
)

manager = QuestionManager()


@questions_router.post("/")
@validate_json_payload(
    {
        "content": {"type": "string", "required": True},
        "title": {"type": "string", "required": True},
        "user_email": {"type": "string", "required": True},
    }
)
async def create_question(request: Request):
    # manager = QuestionManager()

    error_message, data, errors = manager.add_question(request)
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()


@questions_router.get("/")
async def get_questions(request: Request):
    # manager = QuestionManager()

    error_message, data, errors = manager.get_all_questions()
    return APIResponseFormat(
        status_code=200,
        message=error_message,
        data=data,
        errors=errors,
    ).get_json()
