import logging
from typing import Generator, Optional

import httpx
from pydantic import AnyHttpUrl

LOG = logging.getLogger(__name__)


class NEFAuth(httpx.Auth):
    requires_response_body = True

    def __init__(
        self, nef_url: AnyHttpUrl, nef_username: str, nef_password: str
    ) -> None:
        self.nef_url = str(nef_url).rstrip("/")
        self.nef_username = nef_username
        self.nef_password = nef_password

        self.current_token: Optional[str] = None

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        token = self.current_token
        if token is None:
            res = yield self.build_login_request()
            token = self.update_token(res)

        request.headers["Authorization"] = token
        res = yield request

        if res.status_code == 401:
            res = yield self.build_login_request()
            token = self.update_token(res)

            request.headers["Authorization"] = token
            yield request

    def build_login_request(self) -> httpx.Request:
        LOG.debug("Building login request")
        return httpx.Request(
            method="POST",
            url=f"{self.nef_url}/api/v1/login/access-token",
            data={
                "username": self.nef_username,
                "password": self.nef_password,
            },
        )

    def update_token(self, res: httpx.Response) -> str:
        LOG.debug("Updating token from login response")

        if not res.is_success:
            LOG.error(
                "Login response is not successfull ({}): {}",
                res.status_code,
                res.content,
            )
            raise RuntimeError("Failed to login to NEF")

        token = f"Bearer {res.json()['access_token']}"
        self.current_token = token
        return token
