from fastapi import Request

from data_adapter.db import get_db_status
from logger.logging import LoggerUtil


class StatusManagement:
    @staticmethod
    def get_status(request: Request):
        if request.headers.get("raise-exception"):
            raise Exception(f"{request.headers.get('raise-exception')}")
        return "", {"status": "ok"}, None

    @staticmethod
    def get_deep_status(request: Request):
        LoggerUtil.create_info_log("Status controller: get_deep_status")
        # New code to check statuses
        error_message = ""

        db_response, db_error = get_db_status()
        data = {
            "ssq_db": {
                "response": db_response,
                "error": db_error,
            },
        }
        # Redis
        # Elasticsearch here
        if any([db_error]):
            error_message = "Deep status check failed"
        return error_message, data, None
