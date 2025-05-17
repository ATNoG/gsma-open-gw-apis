import logging
from http import HTTPStatus
from collections.abc import Sequence

from fastapi import APIRouter

router = APIRouter(tags=["Management"])


class _ProbesFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        if not isinstance(record.args, Sequence):
            return record

        return record.args[2] not in ["/health"]


logging.getLogger("uvicorn.access").addFilter(_ProbesFilter())


@router.get("/health", status_code=HTTPStatus.NO_CONTENT)
def get_health() -> None:
    return
