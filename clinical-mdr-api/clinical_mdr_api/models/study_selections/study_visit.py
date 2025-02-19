from datetime import datetime
from typing import Annotated, Callable

from pydantic import Field, conlist, validator

from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import (
    StudyStatus,
)
from clinical_mdr_api.domains.study_selections.study_epoch import StudyEpochEpoch
from clinical_mdr_api.domains.study_selections.study_visit import (
    StudyVisitContactMode,
    StudyVisitEpochAllocation,
    StudyVisitRepeatingFrequency,
    StudyVisitTimeReference,
    StudyVisitType,
    StudyVisitVO,
    VisitClass,
    VisitContactModeNamedTuple,
    VisitEpochAllocationNamedTuple,
    VisitRepeatingFrequencyNamedTuple,
    VisitSubclass,
    VisitTimeReferenceNamedTuple,
    VisitTypeNamedTuple,
)
from clinical_mdr_api.models.controlled_terminologies.ct_term_name import CTTermName
from clinical_mdr_api.models.utils import BaseModel, PatchInputModel, PostInputModel
from common import config


class StudyVisitCreateInput(PostInputModel):
    study_epoch_uid: Annotated[str, Field(alias="study_epoch_uid")]
    visit_type_uid: Annotated[str, Field(source="has_visit_type.uid")]
    time_reference_uid: str | None
    time_value: Annotated[
        int | None,
        Field(nullable=True, gt=-config.MAX_INT_NEO4J, lt=config.MAX_INT_NEO4J),
    ]
    time_unit_uid: str | None
    visit_sublabel_codelist_uid: str | None = None
    visit_sublabel_reference: str | None = None
    consecutive_visit_group: str | None = None
    show_visit: Annotated[bool, Field(alias="show_visit")]
    min_visit_window_value: Annotated[
        int | None,
        Field(nullable=True, gt=-config.MAX_INT_NEO4J, lt=config.MAX_INT_NEO4J),
    ] = -9999
    max_visit_window_value: Annotated[
        int | None,
        Field(nullable=True, gt=-config.MAX_INT_NEO4J, lt=config.MAX_INT_NEO4J),
    ] = 9999
    visit_window_unit_uid: str | None = None
    description: str | None = None
    start_rule: str | None = None
    end_rule: str | None = None
    visit_contact_mode_uid: str
    epoch_allocation_uid: str | None = None
    visit_class: str
    visit_subclass: str | None = None
    is_global_anchor_visit: bool
    is_soa_milestone: bool = False
    visit_name: str | None = None
    visit_short_name: str | None = None
    visit_number: float | None = None
    unique_visit_number: Annotated[
        int | None,
        Field(nullable=True, gt=-config.MAX_INT_NEO4J, lt=config.MAX_INT_NEO4J),
    ] = None
    repeating_frequency_uid: Annotated[
        str | None, Field(source="has_repeating_frequency.uid")
    ] = None


class StudyVisitEditInput(PatchInputModel):
    uid: Annotated[str, Field(description="Uid of the Visit")]
    study_epoch_uid: Annotated[str, Field(alias="study_epoch_uid")]
    visit_type_uid: Annotated[str, Field(source="has_visit_type.uid")]
    time_reference_uid: str | None
    time_value: Annotated[
        int | None,
        Field(nullable=True, gt=-config.MAX_INT_NEO4J, lt=config.MAX_INT_NEO4J),
    ]
    time_unit_uid: str | None
    visit_sublabel_codelist_uid: str | None = None
    visit_sublabel_reference: str | None = None
    consecutive_visit_group: str | None = None
    show_visit: Annotated[bool, Field(alias="show_visit")]
    min_visit_window_value: Annotated[
        int | None,
        Field(nullable=True, gt=-config.MAX_INT_NEO4J, lt=config.MAX_INT_NEO4J),
    ] = -9999
    max_visit_window_value: Annotated[
        int | None,
        Field(nullable=True, gt=-config.MAX_INT_NEO4J, lt=config.MAX_INT_NEO4J),
    ] = 9999
    visit_window_unit_uid: str | None = None
    description: str | None = None
    start_rule: str | None = None
    end_rule: str | None = None
    visit_contact_mode_uid: str
    epoch_allocation_uid: str | None = None
    visit_class: str
    visit_subclass: str | None = None
    is_global_anchor_visit: bool
    is_soa_milestone: bool = False
    visit_name: str | None = None
    visit_short_name: str | None = None
    visit_number: float | None = None
    unique_visit_number: Annotated[
        int | None,
        Field(nullable=True, gt=-config.MAX_INT_NEO4J, lt=config.MAX_INT_NEO4J),
    ] = None
    repeating_frequency_uid: Annotated[
        str | None, Field(source="has_repeating_frequency.uid")
    ] = None


class TimeUnit(BaseModel):
    class Config:
        orm_mode = True

    name: Annotated[
        str | None,
        Field(
            description="Uid of visit unit",
            source="has_timepoint.has_latest_value.has_unit_definition.has_latest_value.name",
            nullable=True,
        ),
    ] = None
    conversion_factor_to_master: Annotated[
        float | None,
        Field(
            description="Uid of visit unit",
            source="has_timepoint.has_latest_value.has_unit_definition.has_latest_value.conversion_factor_to_master",
            nullable=True,
        ),
    ] = None
    from_timedelta: Annotated[
        Callable | None, Field(exclude_from_orm=True, nullable=True)
    ] = None

    @validator("from_timedelta", always=True)
    # pylint: disable=no-self-argument,unused-argument
    def validate_time_unit_obj(cls, value, values):
        if values.get("conversion_factor_to_master") is not None:
            return lambda u, x: u.conversion_factor_to_master * x
        return None


class WindowTimeUnit(BaseModel):
    class Config:
        orm_mode = True

    name: Annotated[
        str | None,
        Field(
            description="Uid of visit unit",
            source="has_window_unit.has_latest_value.name",
            nullable=True,
        ),
    ] = None
    conversion_factor_to_master: Annotated[
        float | None,
        Field(
            description="Uid of visit unit",
            source="has_window_unit.has_latest_value.conversion_factor_to_master",
            nullable=True,
        ),
    ] = None
    from_timedelta: Annotated[
        Callable | None, Field(exclude_from_orm=True, nullable=True)
    ] = None

    @validator("from_timedelta", always=True)
    # pylint: disable=no-self-argument,unused-argument
    def validate_time_unit_obj(cls, value, values):
        if values.get("conversion_factor_to_master"):
            return lambda u, x: u.conversion_factor_to_master * x
        return None


class TimePoint(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str | None,
        Field(
            description="Uid of timepoint", source="has_timepoint.uid", nullable=True
        ),
    ] = None

    time_unit_uid: Annotated[
        str | None,
        Field(
            description="Uid of time unit",
            source="has_timepoint.has_latest_value.has_unit_definition.uid",
            nullable=True,
        ),
    ] = None
    visit_timereference: Annotated[
        VisitTimeReferenceNamedTuple | None,
        Field(
            source="has_timepoint.has_latest_value.has_time_reference.uid",
            nullable=True,
        ),
    ] = None

    @validator("visit_timereference", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def instantiate_visit_timereference(
        cls, value, values
    ) -> VisitTimeReferenceNamedTuple | None:
        if value:
            return StudyVisitTimeReference[value]
        return None

    visit_value: Annotated[
        int | None,
        Field(
            description="Value of timepoint",
            source="has_timepoint.has_latest_value.has_value.has_latest_value.value",
            nullable=True,
        ),
    ] = None


class StudyDay(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str | None,
        Field(
            description="The uid of study day",
            source="has_study_day.uid",
            nullable=True,
        ),
    ] = None
    value: Annotated[
        int | None,
        Field(
            description="The value of the study day",
            source="has_study_day.has_latest_value.value",
            nullable=True,
        ),
    ] = None


class StudyDurationDays(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str | None,
        Field(
            description="The uid of study duration days",
            source="has_study_duration_days.uid",
            nullable=True,
        ),
    ] = None
    value: Annotated[
        int | None,
        Field(
            description="The value of the study duration days",
            source="has_study_duration_days.has_latest_value.value",
            nullable=True,
        ),
    ] = None


class StudyWeek(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str | None,
        Field(
            description="The uid of study week",
            source="has_study_week.uid",
            nullable=True,
        ),
    ] = None
    value: Annotated[
        int | None,
        Field(
            description="The value of the study week",
            source="has_study_week.has_latest_value.value",
            nullable=True,
        ),
    ] = None


class StudyDurationWeeks(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str | None,
        Field(
            description="The uid of study duration weeks",
            source="has_study_duration_weeks.uid",
            nullable=True,
        ),
    ] = None
    value: Annotated[
        int | None,
        Field(
            description="The value of the study duration weeks",
            source="has_study_duration_weeks.has_latest_value.value",
            nullable=True,
        ),
    ] = None


class WeekInStudy(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str | None,
        Field(
            description="The uid of week in study",
            source="has_week_in_study.uid",
            nullable=True,
        ),
    ] = None
    value: Annotated[
        int | None,
        Field(
            description="The value of the week in study",
            source="has_week_in_study.has_latest_value.value",
            nullable=True,
        ),
    ] = None


class VisitName(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str | None,
        Field(
            description="The uid of the visit name",
            source="has_visit_name.uid",
            nullable=True,
        ),
    ] = None
    name: Annotated[
        str | None,
        Field(
            description="The name of the visit",
            source="has_visit_name.has_latest_value.name",
            nullable=True,
        ),
    ] = None


class StudyEpochSimpleOGM(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str,
        Field(
            description="The uid of the visit name",
            source="study_epoch_has_study_visit.uid",
        ),
    ]
    study_uid: Annotated[
        str,
        Field(
            description="The uid of the study",
            source="has_after.audit_trail.uid",
        ),
    ]
    epoch: Annotated[
        CTTermName,
        Field(
            description="The name of the visit",
            source="study_epoch_has_study_visit.has_epoch.uid",
        ),
    ]

    @validator("epoch", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def instantiate_epoch(cls, value, values) -> CTTermName:
        return StudyEpochEpoch[value]

    order: Annotated[
        int,
        Field(
            description="The order of epoch",
            source="study_epoch_has_study_visit.order",
        ),
    ]


class StudyVisitOGM(BaseModel, StudyVisitVO):
    class Config:
        orm_mode = True

    uid: Annotated[str, Field(description="Uid of the Visit", source="uid")]

    study_id_prefix: Annotated[
        str | None,
        Field(
            description="study id like 'CDISC DEV'",
            source="has_study_visit.study_id_prefix",
            nullable=True,
        ),
    ] = None
    study_number: Annotated[
        str | None,
        Field(
            description="study number like 0",
            source="has_study_visit.study_number",
            nullable=True,
        ),
    ] = None

    consecutive_visit_group: Annotated[
        str | None,
        Field(
            description="Consecutive visit group",
            source="consecutive_visit_group",
            nullable=True,
        ),
    ] = None
    visit_window_min: Annotated[
        int | None,
        Field(
            description="Min value of visit window",
            source="visit_window_min",
            nullable=True,
        ),
    ] = None
    visit_window_max: Annotated[
        int | None,
        Field(
            description="Max value of visit window",
            source="visit_window_max",
            nullable=True,
        ),
    ] = None
    window_unit_uid: Annotated[
        str | None,
        Field(
            description="Uid of window unit",
            source="has_window_unit.uid",
            nullable=True,
        ),
    ] = None
    description: Annotated[
        str | None,
        Field(description="Description", source="description", nullable=True),
    ] = None
    start_rule: Annotated[
        str | None,
        Field(
            description="The start rule of visit", source="start_rule", nullable=True
        ),
    ] = None
    end_rule: Annotated[
        str | None,
        Field(description="The end rule of visit", source="end_rule", nullable=True),
    ] = None
    visit_contact_mode: Annotated[
        VisitContactModeNamedTuple,
        Field(
            description="The contact mode of study visit",
            source="has_visit_contact_mode.uid",
        ),
    ]

    @validator("visit_contact_mode", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def instantiate_visit_contact_mode(
        cls, value, values
    ) -> VisitContactModeNamedTuple:
        return StudyVisitContactMode[value]

    epoch_allocation: Annotated[
        VisitEpochAllocationNamedTuple | None,
        Field(
            description="Epoch allocation rule",
            source="has_epoch_allocation.uid",
            nullable=True,
        ),
    ] = None

    @validator("epoch_allocation", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def instantiate_epoch_allocation(
        cls, value, values
    ) -> VisitEpochAllocationNamedTuple | None:
        if value:
            return StudyVisitEpochAllocation[value]
        return None

    visit_type: Annotated[
        VisitTypeNamedTuple,
        Field(
            description="Uid of visit unit",
            source="has_visit_type.uid",
        ),
    ]

    @validator("visit_type", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def instantiate_visit_type(cls, value, values) -> VisitTypeNamedTuple:
        return StudyVisitType[value]

    author_id: Annotated[
        str | None,
        Field(
            description="ID of user that created last modification",
            source="has_after.author_id",
            nullable=True,
        ),
    ]
    start_date: Annotated[
        datetime | None,
        Field(
            description="The most recent point in time when the study visit was edited."
            "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
            source="has_after.date",
            nullable=True,
        ),
    ]
    status: Annotated[
        StudyStatus,
        Field(description="Study visit status", source="status"),
    ]

    @validator("status", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def instantiate_study_status(cls, value, values):
        return StudyStatus[value]

    visit_class: Annotated[VisitClass, Field(source="visit_class")]

    @validator("visit_class", pre=True)
    # pylint: disable=no-self-argument
    def instantiate_visit_class(cls, value):
        return VisitClass[value]

    visit_subclass: Annotated[
        VisitSubclass | None, Field(source="visit_subclass", nullable=True)
    ]

    @validator("visit_subclass", pre=True)
    # pylint: disable=no-self-argument
    def instantiate_visit_subclass(cls, value):
        if value:
            return VisitSubclass[value]
        return None

    is_global_anchor_visit: Annotated[
        bool,
        Field(
            description="Is global anchor visit",
            source="is_global_anchor_visit",
        ),
    ]
    is_soa_milestone: Annotated[bool, Field(source="is_soa_milestone")]

    repeating_frequency: Annotated[
        VisitRepeatingFrequencyNamedTuple | None,
        Field(source="has_repeating_frequency.uid", nullable=True),
    ] = None

    @validator("repeating_frequency", pre=True)
    # pylint: disable=no-self-argument,unused-argument
    def instantiate_repeating_frequency(
        cls, value, values
    ) -> VisitRepeatingFrequencyNamedTuple:
        if value:
            return StudyVisitRepeatingFrequency[value]
        return None

    timepoint: Annotated[TimePoint | None, Field(nullable=True)] = None
    study_day: Annotated[StudyDay | None, Field(nullable=True)] = None
    study_week: Annotated[StudyWeek | None, Field(nullable=True)] = None
    study_duration_days: Annotated[StudyDurationDays | None, Field(nullable=True)] = (
        None
    )
    study_duration_weeks: Annotated[StudyDurationWeeks | None, Field(nullable=True)] = (
        None
    )
    week_in_study: Annotated[WeekInStudy | None, Field(nullable=True)] = None
    visit_name_sc: Annotated[VisitName, Field()]

    visit_number: Annotated[
        float | None,
        Field(
            description="The number of the study visit",
            source="visit_number",
            nullable=True,
        ),
    ] = None
    visit_order: Annotated[
        int | None, Field(description="The order of the study visit", nullable=True)
    ] = None
    subvisit_number: Annotated[int | None, Field(nullable=True)] = None
    subvisit_anchor: "StudyVisitOGM | None"
    show_visit: Annotated[
        bool | None,
        Field(
            description="Whether to show visit or not",
            source="show_visit",
            nullable=True,
        ),
    ] = None
    time_unit_object: Annotated[TimeUnit | None, Field(nullable=True)]
    window_unit_object: Annotated[WindowTimeUnit | None, Field(nullable=True)]
    epoch_connector: Annotated[StudyEpochSimpleOGM, Field()]
    day_unit_object: Annotated[TimeUnit, Field()]

    @validator("day_unit_object", pre=True, always=True)
    # pylint: disable=no-self-argument,unused-argument
    def validate_day_unit_obj(cls, value, values):
        return TimeUnit(
            name=config.DAY_UNIT_NAME,
            conversion_factor_to_master=config.DAY_UNIT_CONVERSION_FACTOR_TO_MASTER,
            from_timedelta=lambda u, x: u.conversion_factor_to_master * x,
        )

    week_unit_object: Annotated[TimeUnit, Field()]

    @validator("week_unit_object", pre=True, always=True)
    # pylint: disable=no-self-argument,unused-argument
    def validate_week_unit_obj(cls, value, values):
        return TimeUnit(
            name=config.WEEK_UNIT_NAME,
            conversion_factor_to_master=config.WEEK_UNIT_CONVERSION_FACTOR_TO_MASTER,
            from_timedelta=lambda u, x: u.conversion_factor_to_master * x,
        )

    anchor_visit: "StudyVisitOGM | None"

    visit_sublabel: Annotated[
        str | None,
        Field(description="Study visit status", source="visit_sublabel", nullable=True),
    ] = None
    visit_sublabel_reference: Annotated[
        str | None,
        Field(
            description="Study visit status",
            source="visit_sublabel_reference",
            nullable=True,
        ),
    ] = None
    visit_sublabel_uid: Annotated[
        str | None,
        Field(
            description="Study visit status", source="visit_sublabel_uid", nullable=True
        ),
    ] = None
    vis_unique_number: Annotated[
        int | None, Field(source="unique_visit_number", nullable=True)
    ] = None
    vis_short_name: Annotated[
        str | None, Field(source="short_visit_label", nullable=True)
    ] = None


class StudyVisitOGMVer(StudyVisitOGM):
    change_type: Annotated[
        str,
        Field(
            description="type of action",
            source="has_after.__label__",
        ),
    ]
    end_date: Annotated[
        datetime | None,
        Field(
            description="The last point in time when the study visit was edited."
            "The format is ISO 8601 in UTC±0, e.g.: '2020-10-31T16:00:00+00:00' for October 31, 2020 at 6pm in UTC+2 timezone.",
            source="has_before.date",
            nullable=True,
        ),
    ] = None


class SimpleStudyVisit(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[str, Field(description="Uid of the visit", source="uid")]
    visit_name: Annotated[
        str,
        Field(
            description="Name of the visit",
            source="has_visit_name.has_latest_value.name",
        ),
    ]
    visit_type_name: Annotated[
        str,
        Field(
            description="Name of the visit type",
            source="has_visit_type.has_name_root.has_latest_value.name",
        ),
    ]


class StudyVisit(BaseModel):
    class Config:
        allow_population_by_field_name = True
        orm_mode = True

    uid: Annotated[str, Field(description="Uid of the Visit")]
    study_epoch_uid: Annotated[str, Field(alias="study_epoch_uid")]
    visit_type_uid: Annotated[str, Field(source="has_visit_type.uid")]
    visit_sublabel_codelist_uid: Annotated[str | None, Field(nullable=True)] = None
    visit_sublabel_reference: Annotated[str | None, Field(nullable=True)] = None
    consecutive_visit_group: Annotated[str | None, Field(nullable=True)] = None
    show_visit: Annotated[bool, Field(alias="show_visit")]
    min_visit_window_value: Annotated[int | None, Field(nullable=True)] = -9999
    max_visit_window_value: Annotated[int | None, Field(nullable=True)] = 9999
    visit_window_unit_uid: Annotated[str | None, Field(nullable=True)] = None
    description: Annotated[str | None, Field(nullable=True)] = None
    start_rule: Annotated[str | None, Field(nullable=True)] = None
    end_rule: Annotated[str | None, Field(nullable=True)] = None
    study_uid: str
    study_id: Annotated[
        str | None, Field(description="The study ID like 'CDISC DEV-0'", nullable=True)
    ] = None
    study_version: Annotated[
        str | None,
        Field(
            title="study version or date information",
            description="Study version number, if specified, otherwise None.",
            nullable=True,
        ),
    ] = None
    study_epoch: CTTermName
    # study_epoch_name can be calculated from uid
    epoch_uid: Annotated[str, Field(description="The uid of the study epoch")]

    order: int
    visit_type: CTTermName
    visit_type_name: str

    time_reference_uid: Annotated[str | None, Field(nullable=True)] = None
    time_reference_name: Annotated[str | None, Field(nullable=True)] = None
    time_reference: Annotated[CTTermName | None, Field(nullable=True)] = None
    time_value: Annotated[int | None, Field(nullable=True)] = None
    time_unit_uid: Annotated[str | None, Field(nullable=True)] = None
    time_unit_name: Annotated[str | None, Field(nullable=True)] = None
    time_unit: Annotated[CTTermName | None, Field(nullable=True)] = None
    visit_contact_mode_uid: str
    visit_contact_mode: CTTermName
    epoch_allocation_uid: Annotated[str | None, Field(nullable=True)] = None
    epoch_allocation: Annotated[CTTermName | None, Field(nullable=True)] = None

    repeating_frequency_uid: Annotated[str | None, Field(nullable=True)] = None
    repeating_frequency: Annotated[CTTermName | None, Field(nullable=True)] = None

    duration_time: Annotated[float | None, Field(nullable=True)] = None
    duration_time_unit: Annotated[str | None, Field(nullable=True)] = None

    study_day_number: Annotated[int | None, Field(nullable=True)] = None
    study_duration_days: Annotated[int | None, Field(nullable=True)] = None
    study_duration_days_label: Annotated[str | None, Field(nullable=True)] = None
    study_day_label: Annotated[str | None, Field(nullable=True)] = None
    study_week_number: Annotated[int | None, Field(nullable=True)] = None
    study_duration_weeks: Annotated[int | None, Field(nullable=True)] = None
    study_duration_weeks_label: Annotated[str | None, Field(nullable=True)] = None
    study_week_label: Annotated[str | None, Field(nullable=True)] = None
    week_in_study_label: Annotated[str | None, Field(nullable=True)] = None

    visit_number: Annotated[float, Field(alias="visit_number")]
    visit_subnumber: int

    unique_visit_number: Annotated[int, Field(alias="unique_visit_number")]
    visit_subname: str
    visit_sublabel: Annotated[str | None, Field(alias="visit_sublabel", nullable=True)]

    visit_name: str
    visit_short_name: str

    visit_window_unit_name: Annotated[str | None, Field(nullable=True)] = None
    visit_class: str
    visit_subclass: Annotated[str | None, Field(nullable=True)] = None
    is_global_anchor_visit: bool
    is_soa_milestone: bool
    status: Annotated[str, Field(description="Study Visit status")]
    start_date: Annotated[datetime, Field(description="Study Visit creation date")]
    end_date: Annotated[
        datetime | None,
        Field(description="Study Visit last date of version", nullable=True),
    ] = None
    author_username: Annotated[str | None, Field(nullable=True)] = None
    possible_actions: Annotated[
        list[str],
        Field(description="List of actions to perform on item"),
    ]
    study_activity_count: Annotated[
        int | None,
        Field(
            description="Count of Study Activities assigned to Study Visit",
            nullable=True,
        ),
    ] = None
    change_type: Annotated[
        str | None, Field(description="Type of Action", nullable=True)
    ] = None


class StudyVisitVersion(StudyVisit):
    changes: dict


class AllowedTimeReferences(BaseModel):
    time_reference_uid: str
    time_reference_name: str


class VisitConsecutiveGroupInput(PostInputModel):
    visits_to_assign: Annotated[
        conlist(str, min_items=2),
        Field(
            description="List of visits to be assigned to the consecutive_visit_group",
        ),
    ]
    overwrite_visit_from_template: Annotated[
        str | None,
        Field(
            description="The uid of the visit from which get properties to overwrite"
        ),
    ] = None
