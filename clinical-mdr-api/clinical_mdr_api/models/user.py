from datetime import datetime
from typing import Annotated

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class UserInfo(PydanticBaseModel):
    user_id: Annotated[str | None, Field(nullable=True)]
    username: Annotated[str | None, Field(nullable=True)]
    name: Annotated[str | None, Field(nullable=True)]
    email: Annotated[str | None, Field(nullable=True)]
    azp: Annotated[str | None, Field(nullable=True)]
    oid: Annotated[str | None, Field(nullable=True)]
    roles: Annotated[list[str], Field()] = []
    created: Annotated[datetime, Field(nullable=True)]
    updated: Annotated[datetime | None, Field(nullable=True)]


class UserInfoPatchInput(PydanticBaseModel):
    username: Annotated[str | None, Field(nullable=True)] = None
    email: Annotated[str | None, Field(nullable=True)] = None
    name: Annotated[str | None, Field(nullable=True)] = None
