from datetime import datetime
from typing import Annotated, Any

from pydantic import Field

from clinical_mdr_api.models.controlled_terminologies.ct_term_name import CTTermName
from clinical_mdr_api.models.utils import BaseModel, PatchInputModel, PostInputModel
from common import config


class StudyEpochCreateInput(PostInputModel):
    study_uid: Annotated[str, Field()]
    start_rule: Annotated[
        str | None, Field(description="Study Epoch Start description", nullable=True)
    ] = None
    end_rule: Annotated[
        str | None, Field(description="Study Epoch end description", nullable=True)
    ] = None
    epoch: Annotated[str | None, Field(nullable=True)] = None
    epoch_subtype: Annotated[str, Field()]
    duration_unit: Annotated[
        str | None,
        Field(description="Study Epoch duration preferred unit", nullable=True),
    ] = None
    order: Annotated[
        int | None,
        Field(
            description="The ordering of the selection",
            nullable=True,
            gt=0,
            lt=config.MAX_INT_NEO4J,
        ),
    ] = None
    description: Annotated[str | None, Field(nullable=True)] = None
    duration: Annotated[
        int | None,
        Field(
            description="Calculated epoch duration",
            nullable=True,
            lt=config.MAX_INT_NEO4J,
        ),
    ] = None
    color_hash: Annotated[
        str | None,
        Field(description="Epoch Color for display", nullable=True),
    ] = "#FFFFFF"


class StudyEpochEditInput(PatchInputModel):
    study_uid: str
    start_rule: Annotated[
        str | None, Field(description="Study Epoch Start description")
    ] = None
    end_rule: Annotated[
        str | None, Field(description="Study Epoch end description")
    ] = None
    epoch: str | None = None
    duration_unit: Annotated[
        str | None, Field(description="Study Epoch duration preferred unit")
    ] = None
    order: Annotated[
        int | None,
        Field(
            description="The ordering of the selection", gt=0, lt=config.MAX_INT_NEO4J
        ),
    ] = None
    description: Annotated[str | None, Field(nullable=True)] = None
    duration: Annotated[
        int | None,
        Field(description="Calculated epoch duration", lt=config.MAX_INT_NEO4J),
    ] = None
    color_hash: Annotated[str | None, Field(description="Epoch Color for display")] = (
        "#FFFFFF"
    )
    # Override epoch from Create Input to make it Optional
    epoch_subtype: str | None = None
    change_description: str


class StudyEpochOGM(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[str, Field(source="uid")]
    study_uid: Annotated[str, Field(source="has_after.audit_trail.uid")]
    study_version: Annotated[
        str | None,
        Field(
            title="study version or date information",
            description="Study version number, if specified, otherwise None.",
            nullable=True,
        ),
    ] = None
    epoch: Annotated[
        str,
        Field(
            title="Epoch name",
            description="Name of the epoch based on CT term",
            source="has_epoch.uid",
        ),
    ]
    epoch_subtype: Annotated[
        str,
        Field(
            title="Epoch sub type name",
            description="Name of the epoch sub type based on CT term",
            source="has_epoch_subtype.uid",
        ),
    ]
    epoch_type: Annotated[
        str,
        Field(source="has_epoch_type.uid"),
    ]
    duration_unit: Annotated[
        str | None,
        Field(
            description="Study Epoch duration preferred unit",
            source="has_duration_unit.uid",
            nullable=True,
        ),
    ] = None

    order: Annotated[
        int | None,
        Field(
            description="The ordering of the selection", source="order", nullable=True
        ),
    ] = None
    description: Annotated[str | None, Field(source="description", nullable=True)] = (
        None
    )

    color_hash: Annotated[
        str | None,
        Field(
            description="Epoch Color for display", source="color_hash", nullable=True
        ),
    ] = None
    start_rule: Annotated[
        str | None,
        Field(
            description="Study Epoch Start description",
            source="start_rule",
            nullable=True,
        ),
    ] = None

    end_rule: Annotated[
        str | None,
        Field(
            description="Study Epoch end description", source="end_rule", nullable=True
        ),
    ] = None
    status: Annotated[str, Field(title="Study Epoch status", source="status")]
    start_date: Annotated[
        datetime,
        Field(
            description="The most recent point in time when the study epoch was edited."
            "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
            source="has_after.date",
        ),
    ]
    author_username: Annotated[
        str | None, Field(source="has_after.author_id", nullable=True)
    ] = None


class StudyEpochOGMVer(StudyEpochOGM):
    study_uid: Annotated[str, Field(source="has_after.audit_trail.uid")]
    study_visits: Annotated[Any, Field(source="has_study_visit")]
    change_type: Annotated[str, Field(source="has_after.__label__")]
    end_date: Annotated[
        datetime | None,
        Field(
            description="The last point in time when the study epoch was edited."
            "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
            source="has_before.date",
            nullable=True,
        ),
    ] = None


class StudyEpoch(BaseModel):
    study_uid: Annotated[str, Field()]
    start_rule: Annotated[
        str | None, Field(description="Study Epoch Start description", nullable=True)
    ] = None
    end_rule: Annotated[
        str | None, Field(description="Study Epoch end description", nullable=True)
    ] = None
    epoch: Annotated[str | None, Field(nullable=True)] = None
    duration_unit: Annotated[
        str | None,
        Field(description="Study Epoch duration preferred unit", nullable=True),
    ] = None
    order: Annotated[
        int | None, Field(description="The ordering of the selection", nullable=True)
    ] = None
    description: Annotated[str | None, Field(nullable=True)] = None
    duration: Annotated[
        int | None, Field(description="Calculated epoch duration", nullable=True)
    ] = None
    color_hash: Annotated[
        str | None,
        Field(description="Epoch Color for display", nullable=True),
    ] = "#FFFFFF"

    epoch_name: Annotated[str, Field(description="Name of the epoch based on CT term")]
    epoch_subtype_name: Annotated[
        str | None,
        Field(description="Name of the epoch sub type based on CT term", nullable=True),
    ] = None
    epoch_type_name: Annotated[str, Field()]
    epoch_subtype: Annotated[str | None, Field(nullable=True)] = None
    uid: Annotated[str, Field()]
    study_version: Annotated[
        str | None,
        Field(
            title="study version or date information",
            description="Study version number, if specified, otherwise None.",
            nullable=True,
        ),
    ] = None
    epoch_ctterm: Annotated[CTTermName, Field(title="Study epoch Term")]
    epoch_subtype_ctterm: Annotated[CTTermName, Field(title="Study Epoch subtype Term")]
    epoch_type_ctterm: Annotated[CTTermName, Field(title="Study Epoch type CTTermName")]
    start_day: Annotated[
        int | None,
        Field(title="Study Epoch start day", nullable=True),
    ] = None
    end_day: Annotated[
        int | None,
        Field(title="Study Epoch end day", nullable=True),
    ] = None
    start_week: Annotated[
        int | None,
        Field(title="Study Epoch start week", nullable=True),
    ] = None
    end_week: Annotated[
        int | None,
        Field(title="Study Epoch end week", nullable=True),
    ] = None
    start_date: Annotated[
        str, Field(description="Study Epoch initial modification date")
    ]
    end_date: Annotated[
        str | None,
        Field(description="Study Epoch last modification date", nullable=True),
    ] = None
    status: Annotated[str, Field(description="Study Epoch status")]
    author_username: Annotated[str | None, Field(nullable=True)] = None
    possible_actions: Annotated[
        list[str],
        Field(description="List of actions to perform on item"),
    ]
    change_description: Annotated[
        str | None,
        Field(description="Description of change reasons", nullable=True),
    ] = ""
    study_visit_count: Annotated[
        int, Field(description="Count of Study Visits assigned to Study Epoch")
    ]
    change_type: Annotated[str | None, Field(nullable=True)] = None


class StudyEpochVersion(StudyEpoch):
    changes: dict


class StudyEpochTypes(BaseModel):
    type: Annotated[str, Field(description="Study Epoch type")]
    type_name: str
    subtype: Annotated[str, Field(description="Study Epoch subtype")]
    subtype_name: str
