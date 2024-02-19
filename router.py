import re


class Router:
    def __init__(self):
        self.defined_routes = {}

    def route(self, method: str, path: str):
        def wrapper(handler):
            self.defined_routes[(method, path)] = handler
            return handler

        return wrapper

    def not_found(self):
        return "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"

    def is_declared_path(self, request: str):
        match = re.match(r"(\w+)\s+(/[\w/]*)\s+(\S+)", request)
        if not match:
            raise Exception("Unexpected router error")
        method, route, _ = match.groups()

        print(self.defined_routes)

        if (method, route) not in self.defined_routes:
            return self.not_found()
