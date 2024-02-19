class Router:
    ROUTE_MAP = {}

    @classmethod
    def route(cls, method: str, path: str):
        def wrapper(handler):
            cls.ROUTE_MAP[(method, path)] = handler
            return handler

        return wrapper

    def not_found():
        return "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
