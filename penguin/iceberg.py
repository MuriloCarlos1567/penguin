class HTTPException(Exception):
    def __init__(self, message: str | dict, status_code: int):
        self.status_code = status_code
        self.message = message
