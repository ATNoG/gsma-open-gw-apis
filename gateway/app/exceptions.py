from http import HTTPStatus


class ApiException(Exception):
    def __init__(
        self,
        status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_SERVER_ERROR",
        message: str = "An unknown error has occured.",
    ):
        super().__init__(self, message)

        self.status = status
        self.code = code
        self.message = message
