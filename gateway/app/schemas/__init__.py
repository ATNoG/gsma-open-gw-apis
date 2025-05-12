from typing import Annotated

from pydantic import BaseModel, Field


class ErrorInfo(BaseModel):
    status: Annotated[int, Field(description="HTTP response status code")]
    code: Annotated[str, Field(description="Code given to this error")]
    message: Annotated[str, Field(description="Detailed error description")]
