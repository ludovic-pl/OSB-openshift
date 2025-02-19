from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import Field, validator

from clinical_mdr_api.models.utils import BaseModel, PatchInputModel, PostInputModel
from clinical_mdr_api.models.validators import transform_to_utc


class NotificationType(Enum):
    INFORMATION = "information"
    WARNING = "warning"
    ERROR = "error"


class Notification(BaseModel):
    sn: int
    title: str
    notification_type: str
    description: Annotated[str | None, Field(nullable=True)] = None
    started_at: Annotated[datetime | None, Field(nullable=True)] = None
    ended_at: Annotated[datetime | None, Field(nullable=True)] = None
    published_at: Annotated[datetime | None, Field(nullable=True)] = None


class NotificationPostInput(PostInputModel):
    title: Annotated[str, Field(min_length=1)]
    notification_type: NotificationType = NotificationType.INFORMATION
    description: Annotated[str | None, Field(min_length=1)] = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    published: bool = False

    _date_validator = validator("started_at", "ended_at", allow_reuse=True)(
        transform_to_utc
    )


class NotificationPatchInput(PatchInputModel):
    title: Annotated[str, Field(min_length=1)]
    notification_type: NotificationType = NotificationType.INFORMATION
    description: Annotated[str | None, Field(min_length=1)] = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    published: bool = False

    _date_validator = validator("started_at", "ended_at", allow_reuse=True)(
        transform_to_utc
    )
