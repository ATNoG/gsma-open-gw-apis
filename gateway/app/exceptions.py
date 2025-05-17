from http import HTTPStatus


class ApiException(Exception):
    def __init__(
        self,
        status: HTTPStatus | int = HTTPStatus.INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_SERVER_ERROR",
        message: str = "An unknown error has occured.",
    ) -> None:
        super().__init__(self, message)

        self.status = status
        self.code = code
        self.message = message


class MissingDevice(ApiException):
    def __init__(self) -> None:
        super().__init__(
            status=422,
            code="MISSING_IDENTIFIER",
            message="The device cannot be identified.",
        )


class ResourceNotFound(ApiException):
    def __init__(self) -> None:
        super().__init__(
            status=404,
            code="NOT_FOUND",
            message="The specified resource is not found.",
        )


class BadRequest(ApiException):
    def __init__(self) -> None:
        super().__init__(
            status=400,
            code="INVALID_ARGUMENT",
            message="Client specified an invalid argument, request body or query param.",
        )


class InternalServerError(ApiException):
    def __init__(self) -> None:
        super().__init__()


class UnsupportedIdentifier(ApiException):
    def __init__(self) -> None:
        super().__init__(
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
            code="UNSUPPORTED_IDENTIFIER",
            message="The identifier provided is not supported.",
        )
