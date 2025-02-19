import datetime
from typing import Annotated

from fastapi import Request
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    type: Annotated[str, Field(description="Exception class.")]
    message: Annotated[str, Field(description="More information about the error.")]
    time: Annotated[
        datetime.datetime,
        Field(description="The point in time when the error occurred."),
    ]
    path: Annotated[str, Field(description="The url/path of the request.")]
    method: Annotated[str, Field(description="The HTTP method of the request.")]

    def __init__(self, request: Request, exception: Exception, **data) -> None:
        super().__init__(
            type=type(exception).__name__,
            message=str(getattr(exception, "msg", None) or exception),
            time=datetime.datetime.now(datetime.UTC),
            path=str(request.url),
            method=request.method,
            **data,
        )
