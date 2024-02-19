from concurrent.futures import ThreadPoolExecutor
import threading
import asyncio

class Penguin:
    def __init__(self, host='0.0.0.0', port=3000, logger=True, workers=5) -> None:
        self.host = host
        self.port = port
        self.logger = logger
        self.workers =  workers
        self.executor = ThreadPoolExecutor(self.workers)

    def teste_function(self):
        current_thread = threading.current_thread().name
        print(f'Thread: {current_thread}')
        import time
        time.sleep(5)
        print(f'Fim: {current_thread}')

    async def handler(self, reader, writer):
        while True:
            data = await reader.read(100)
            if not data:
                break
            
            if self.logger:
                decoded_data = data.decode()
                request_lines = decoded_data.split('\r\n')
                request_line = request_lines[0]
                print(request_line)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self.teste_function)

            writer.write(data)
            await writer.drain()

        writer.close()

    async def run(self):
        server = await asyncio.start_server(
            self.handler, self.host, self.port
        )

        addr = server.sockets[0].getsockname()

        print(f'🐧Penguin listening on -> {addr[0]}:{addr[1]}')

        async with server:
            await server.serve_forever()

if __name__ == '__main__':
    server = Penguin()
    asyncio.run(server.run())

