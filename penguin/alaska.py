from enum import Enum


class HttpStatus(Enum):
    NOT_FOUND = 404
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTI_STATUS = 207
    ALREADY_REPORTED = 208
    IM_USED = 226

    def __str__(self):
        return str(self.value)


class Router:
    ROUTE_MAP = {}

    @classmethod
    def route(cls, method: str, path: str):
        def wrapper(handler):
            cls.ROUTE_MAP[(method, path)] = handler
            return handler

        return wrapper

    @classmethod
    def get(cls, path: str):
        return cls.route("GET", path)

    @classmethod
    def post(cls, path: str):
        return cls.route("POST", path)

    @classmethod
    def http_error(cls, status: HttpStatus):
        return None, status.value
