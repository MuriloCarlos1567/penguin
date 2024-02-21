from concurrent.futures import ThreadPoolExecutor
import functools
import asyncio
import json

from .alaska import Router, HttpStatus
from .iceberg import HTTPException
from .igloo import Parser


class Penguin(Router):
    def __init__(self, host="0.0.0.0", port=3000, logger=True, workers=50) -> None:
        self.host = host
        self.port = port
        self.logger = logger
        self.workers = workers
        self.executor = ThreadPoolExecutor(self.workers)
        self.router = Router

    def include_router(self, router):
        self.router.ROUTE_MAP.update({**router.ROUTE_MAP})

    async def execute(self, request_line, json_body):
        method, path = request_line[0], request_line[1]

        defined_routes = self.router.ROUTE_MAP

        matched_route = None

        loop = asyncio.get_running_loop()

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

            params = Parser.get_params(
                route_function, request_line, matched_route, json_body
            )

            try:
                return await loop.run_in_executor(
                    self.executor, functools.partial(route_function, **params)
                )
            except HTTPException as e:
                self.executor.shutdown(wait=True)
                return e.message, e.status_code
            except Exception as e:
                self.executor.shutdown(wait=True)
                return {
                    "message": "ThreadPoolExecutor error"
                }, HttpStatus.INTERNAL_SERVER_ERROR_500
        else:
            return self.router.http_error(HttpStatus.NOT_FOUND_404)

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

            json_body = json.loads(request_lines[-1]) if request_lines[-1] else {}

            response_data, status_code = await self.execute(request, json_body)

            content_lenght = 0

            response_json = b""

            if response_data:
                response_json = json.dumps(response_data).encode("utf-8")
                content_lenght = len(response_json)

            response_headers = f"HTTP/1.1 {status_code}\r\nContent-Type: application/json\r\nContent-Length: {content_lenght}\r\n\r\n"

            response = response_headers.encode("utf-8") + response_json

            writer.write(response)
            await writer.drain()

        writer.close()

    async def run(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)

        addr = server.sockets[0].getsockname()

        print(
            f"""
        🐧 Summoning the happy penguins ❄️  🧊
        🐧 Warming up the igloo 🏔️  ⛄

        🐧 Penguin listening on -> {addr[0]}:{addr[1]}
        """
        )

        async with server:
            await server.serve_forever()

    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())
        loop.run_forever()
