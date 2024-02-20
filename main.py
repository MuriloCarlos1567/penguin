from concurrent.futures import ThreadPoolExecutor
import functools
import asyncio
import json

from router import Router, HttpStatus
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
            return await asyncio.to_thread(functools.partial(route_function, **params))
        else:
            return self.router.http_error(HttpStatus.FORBIDDEN)

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

            response_data, status_code = await self.execute(request)

            response_json = json.dumps(response_data).encode("utf-8")

            response_headers = f"HTTP/1.1 {status_code}\r\nContent-Type: application/json\r\nContent-Length: {len(response_json)}\r\n\r\n"

            writer.write(response_headers.encode("utf-8"))
            await writer.drain()

            writer.write(response_json)
            await writer.drain()

        writer.close()

    async def run(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)

        addr = server.sockets[0].getsockname()

        print(f"🐧Penguin listening on -> {addr[0]}:{addr[1]}")

        async with server:
            await server.serve_forever()

    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())
        loop.run_forever()
