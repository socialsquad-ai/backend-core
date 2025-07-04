import contextvars
from dataclasses import dataclass, asdict
from typing import Any
from fastapi import Request


@dataclass(frozen=True)
class RequestMetadata:
    api_id: str
    thread_id: str

    @classmethod
    def empty(cls) -> "RequestMetadata":
        return cls(api_id="", thread_id="")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class JsonPayload:
    data: dict[str, Any]

    @classmethod
    def empty(cls) -> "JsonPayload":
        return cls(data={})

    def to_dict(self) -> dict[str, Any]:
        return self.data


# Initialize context vars with empty frozen dataclasses
request_metadata = contextvars.ContextVar(
    "request_metadata", default=RequestMetadata.empty()
)
context_json_post_payload = contextvars.ContextVar(
    "context_json_post_payload", default=JsonPayload.empty()
)


def get_request_metadata() -> dict[str, Any]:
    # Return as dictionary to maintain backward compatibility
    return request_metadata.get().to_dict()


def set_request_metadata(metadata: dict) -> None:
    # Store as immutable dataclass
    request_metadata.set(
        RequestMetadata(api_id=metadata["api_id"], thread_id=metadata["thread_id"])
    )


def get_context_api_id() -> str:
    return request_metadata.get().api_id


def get_request_json_post_payload() -> dict[str, Any]:
    # Return as dictionary to maintain backward compatibility
    try:
        return context_json_post_payload.get().to_dict()
    except Exception:
        return {}


async def set_context_json_post_payload(request: Request) -> None:
    try:
        payload = await request.json()
        # Store as immutable dataclass
        context_json_post_payload.set(JsonPayload(data=payload))
    except Exception as e:
        from logger.logging import LoggerUtil

        LoggerUtil.create_error_log(
            "Bad request json payload: {}".format(e),
        )
        context_json_post_payload.set(JsonPayload.empty())


def clear_request_metadata() -> None:
    request_metadata.set(RequestMetadata.empty())
    context_json_post_payload.set(JsonPayload.empty())
