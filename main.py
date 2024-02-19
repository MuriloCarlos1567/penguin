from concurrent.futures import ThreadPoolExecutor
from inspect import signature
import threading
import functools
import asyncio
import json

from router import Router


class Penguin(Router):
    def __init__(self, host="0.0.0.0", port=3000, logger=True, workers=50) -> None:
        self.host = host
        self.port = port
        self.logger = logger
        self.workers = workers
        self.executor = ThreadPoolExecutor(self.workers)
        self.router = Router()

    async def get_params(self, route_function, request_line):
        func_signature = signature(route_function)
        params = {}

        for param_name, param in func_signature.parameters.items():
            if param_name == "self":
                continue

        return params

    async def execute(self, request_line):
        key = (request_line.method, request_line.path)

        defined_routes = self.router.defined_routes

        if key in defined_routes:
            route_function = defined_routes[key]
            params = await self.get_params(route_function, request_line)
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

            self.is_declared_path(request_line)

            await self.execute(request_line)

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
    asyncio.run(server.run())
