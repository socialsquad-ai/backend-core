import contextvars
from fastapi import Request

# Create a ContextVar for the request context with a default empty dictionary.
request_metadata = contextvars.ContextVar("request_metadata", default={})
context_api_id = contextvars.ContextVar("context_api_id", default="")
context_thread_id = contextvars.ContextVar("context_thread_id", default="")
context_json_post_payload = contextvars.ContextVar(
    "context_json_post_payload", default={}
)


def get_request_metadata():
    return request_metadata.get()


def set_request_metadata(metadata: dict):
    context_api_id.set(metadata["api_id"])
    context_thread_id.set(
        metadata["thread_id"]
    )  # TODO ::  We need to edit this thread id if we are creating threads from the main context, And revert to the older thread id when the child thread is closed.

    request_metadata.set(metadata)


def get_context_api_id():
    return context_api_id.get()


def get_context_json_post_payload():
    return context_json_post_payload.get()


async def set_context_json_post_payload(request: Request):
    # Doing this cause we can serialize the request object to json once and use it across the function execution.
    try:
        context_json_post_payload.set(await request.json())
    except Exception as e:
        from logger.logging import LoggerUtil

        LoggerUtil.create_error_log(
            "Bad request json payload: {}".format(e),
        )
        context_json_post_payload.set({})


def clear_request_metadata():
    request_metadata.set({})
    context_api_id.set("")
    context_thread_id.set("")
    context_json_post_payload.set({})
