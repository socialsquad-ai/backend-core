from typing import Dict, List

from fastapi.responses import JSONResponse

from utils.contextvar import get_context_api_id


def api_response_format(api_id: str, message: str, data: dict = None, errors: list = None) -> dict:
    return {"message": message, "data": data, "errors": errors}


class APIResponseFormat:
    def __init__(
        self,
        status_code: int,
        message: str,
        data: Dict = None,
        errors: List = None,
    ):
        self.api_id = get_context_api_id()
        self.status_code = status_code
        self.message = message
        self.data = data
        self.errors = errors

    def get_json(self):
        return JSONResponse(
            status_code=self.status_code,
            headers={"ssq-api-id": self.api_id},
            content={"message": self.message, "data": self.data, "errors": self.errors},
        )
