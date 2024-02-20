from enum import Enum


class HttpStatus(Enum):
    NOT_FOUND_404 = 404
    BAD_REQUEST_400 = 400
    UNAUTHORIZED_401 = 401
    FORBIDDEN_403 = 403
    UNPROCESSABLE_ENTITY_422 = 422
    INTERNAL_SERVER_ERROR_500 = 500
    OK_200 = 200
    CREATED_201 = 201
    ACCEPTED_202 = 202
    NO_CONTENT_204 = 204
    RESET_CONTENT_205 = 205
    PARTIAL_CONTENT_206 = 206
    MULTI_STATUS_207 = 207
    ALREADY_REPORTED_208 = 208
    IM_USED_226 = 226

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
