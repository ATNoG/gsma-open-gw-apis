from http import HTTPStatus
class ApiException(Exception):
    def __init__(self, status: HTTPStatus, code: str, message: str):
        super().__init__(self, message)
        self.status = status
        self.code = code
        self.message = message