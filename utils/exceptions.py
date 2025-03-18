class CustomUnauthorized(Exception):
    def __init__(self, detail: str = "Unauthorized access"):
        self.detail = detail


class CustomBadRequest(Exception):
    def __init__(self, detail: str = "Bad Request", errors: dict = None):
        self.detail = detail
        self.errors = errors
