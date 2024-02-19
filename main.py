from concurrent.futures import ThreadPoolExecutor
import threading
import functools
import asyncio
import json

from router import Router
from igloo import Parser


class Penguin(Router):
    def __init__(self, host="0.0.0.0", port=3000, logger=True, workers=50) -> None:
        self.host = host
        self.port = port
        self.logger = logger
        self.workers = workers
        self.executor = ThreadPoolExecutor(self.workers)
        self.router = Router

    async def execute(self, request_line):
        method, path = request_line[0], request_line[1]

        defined_routes = self.router.ROUTE_MAP

        matched_route = None

        for route_key, route_function in defined_routes.items():
            (
                defined_method,
                defined_path,
            ) = route_key

            if method == defined_method and Parser.path_matches(defined_path, path):
                matched_route = route_key
                break

        if matched_route:
            route_function = defined_routes[matched_route]
            params = Parser.get_params(route_function, request_line, matched_route)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor, functools.partial(route_function, **params)
            )
        else:
            pass

    async def handler(self, reader, writer):
        while True:
            data = await reader.read(4096)
            if not data:
                break

            decoded_data = data.decode()
            request_lines = decoded_data.split("\r\n")
            request_line = request_lines[0]

            if self.logger:
                print(request_line)

            request = Parser.request_parser(request_line)

            await self.execute(request)

            # TODO Ajustar o response dentro do Router
            response_json = {"message": "Hello, Penguin!"}
            response_data = json.dumps(response_json).encode("utf-8")

            response_headers = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response_data)}\r\n\r\n"

            writer.write(response_headers.encode("utf-8"))
            await writer.drain()

            writer.write(response_data)
            await writer.drain()

        writer.close()

    async def run(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)

        addr = server.sockets[0].getsockname()

        print(f"🐧Penguin listening on -> {addr[0]}:{addr[1]}")

        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    server = Penguin()

    @server.route("GET", "/teste/{name}/{age}")
    def teste_function(name, age):
        print(name)
        print(age)
        current_thread = threading.current_thread().name
        print(f"Thread: {current_thread}")
        import time

        time.sleep(1)
        print(f"Fim: {current_thread}")

    asyncio.run(server.run())
