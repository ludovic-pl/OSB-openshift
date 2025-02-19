from typing import Annotated, Callable, Self

from pydantic import Field, validator

from clinical_mdr_api.domains.biomedical_concepts.activity_instance_class import (
    ActivityInstanceClassAR,
)
from clinical_mdr_api.domains.biomedical_concepts.activity_item_class import (
    ActivityItemClassAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemStatus,
    ObjectAction,
)
from clinical_mdr_api.models.concepts.concept import VersionProperties
from clinical_mdr_api.models.libraries.library import Library
from clinical_mdr_api.models.utils import BaseModel, PatchInputModel, PostInputModel
from common import config


class CompactActivityInstanceClass(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[str, Field(source="has_activity_instance_class.uid")]
    name: Annotated[
        str, Field(source="has_activity_instance_class.has_latest_value.name")
    ]


class SimpleDataTypeTerm(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[str, Field(source="has_latest_value.has_data_type.uid")]
    name: Annotated[
        str | None,
        Field(
            source="has_latest_value.has_data_type.has_name_root.has_latest_value.name",
            nullable=True,
        ),
    ] = None


class SimpleRoleTerm(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[str, Field(source="has_latest_value.has_role.uid")]
    name: Annotated[
        str | None,
        Field(
            source="has_latest_value.has_role.has_name_root.has_latest_value.name",
            nullable=True,
        ),
    ] = None


class SimpleVariableClass(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str,
        Field(
            source="maps_variable_class.uid",
        ),
    ]


class ActivityItemClass(VersionProperties):
    class Config:
        orm_mode = True

    uid: Annotated[str | None, Field(source="uid", nullable=True)] = None
    name: Annotated[
        str | None, Field(source="has_latest_value.name", nullable=True)
    ] = None
    definition: Annotated[
        str | None, Field(source="has_latest_value.definition", nullable=True)
    ] = None
    order: Annotated[int, Field(source="has_latest_value.order")]
    mandatory: Annotated[
        bool,
        Field(
            source="has_latest_value.mandatory",
        ),
    ]
    data_type: Annotated[SimpleDataTypeTerm, Field()]
    role: Annotated[SimpleRoleTerm, Field()]
    activity_instance_classes: Annotated[list[CompactActivityInstanceClass], Field()]
    variable_classes: Annotated[
        list[SimpleVariableClass] | None, Field(nullable=True)
    ] = None
    library_name: Annotated[str, Field(source="has_library.name")]
    nci_concept_id: Annotated[
        str | None,
        Field(
            nullable=True,
            source="has_latest_value.nci_concept_id",
        ),
    ] = None
    possible_actions: Annotated[
        list[str],
        Field(
            description=(
                "Holds those actions that can be performed on the ActivityItemClasses. "
                "Actions are: 'approve', 'edit', 'new_version'."
            )
        ),
    ]

    @validator("possible_actions", pre=True, always=True)
    # pylint: disable=no-self-argument,unused-argument
    def validate_possible_actions(cls, value, values):
        if values["status"] == LibraryItemStatus.DRAFT.value and values[
            "version"
        ].startswith("0"):
            return [
                ObjectAction.APPROVE.value,
                ObjectAction.DELETE.value,
                ObjectAction.EDIT.value,
            ]
        if values["status"] == LibraryItemStatus.DRAFT.value:
            return [ObjectAction.APPROVE.value, ObjectAction.EDIT.value]
        if values["status"] == LibraryItemStatus.FINAL.value:
            return [
                ObjectAction.INACTIVATE.value,
                ObjectAction.NEWVERSION.value,
            ]
        if values["status"] == LibraryItemStatus.RETIRED.value:
            return [ObjectAction.REACTIVATE.value]
        return []

    @classmethod
    def from_activity_item_class_ar(
        cls,
        activity_item_class_ar: ActivityItemClassAR,
        find_activity_instance_class_by_uid: Callable[
            [str], ActivityInstanceClassAR | None
        ],
    ) -> Self:
        activity_instance_classes = [
            find_activity_instance_class_by_uid(activity_instance_class_uid)
            for activity_instance_class_uid in activity_item_class_ar.activity_item_class_vo.activity_instance_class_uids
        ]
        return cls(
            uid=activity_item_class_ar.uid,
            name=activity_item_class_ar.name,
            definition=activity_item_class_ar.definition,
            nci_concept_id=activity_item_class_ar.nci_concept_id,
            order=activity_item_class_ar.activity_item_class_vo.order,
            mandatory=activity_item_class_ar.activity_item_class_vo.mandatory,
            activity_instance_classes=[
                CompactActivityInstanceClass(
                    uid=activity_instance_class.uid, name=activity_instance_class.name
                )
                for activity_instance_class in activity_instance_classes
            ],
            data_type=SimpleDataTypeTerm(
                uid=activity_item_class_ar.activity_item_class_vo.data_type_uid,
                name=activity_item_class_ar.activity_item_class_vo.data_type_name,
            ),
            role=SimpleRoleTerm(
                uid=activity_item_class_ar.activity_item_class_vo.role_uid,
                name=activity_item_class_ar.activity_item_class_vo.role_name,
            ),
            variable_classes=(
                [
                    SimpleVariableClass(uid=variable_class_uid)
                    for variable_class_uid in activity_item_class_ar.activity_item_class_vo.variable_class_uids
                ]
                if activity_item_class_ar.activity_item_class_vo.variable_class_uids
                else []
            ),
            library_name=Library.from_library_vo(activity_item_class_ar.library).name,
            start_date=activity_item_class_ar.item_metadata.start_date,
            end_date=activity_item_class_ar.item_metadata.end_date,
            status=activity_item_class_ar.item_metadata.status.value,
            version=activity_item_class_ar.item_metadata.version,
            change_description=activity_item_class_ar.item_metadata.change_description,
            author_username=activity_item_class_ar.item_metadata.author_username,
            possible_actions=sorted(
                [_.value for _ in activity_item_class_ar.get_possible_actions()]
            ),
        )


class ActivityItemClassCreateInput(PostInputModel):
    name: str
    definition: Annotated[str | None, Field(min_length=1)]
    nci_concept_id: Annotated[str | None, Field(min_length=1)]
    order: Annotated[int, Field(gt=0, lt=config.MAX_INT_NEO4J)]
    mandatory: bool
    activity_instance_class_uids: list[str]
    role_uid: str
    data_type_uid: str
    library_name: str


class ActivityItemClassEditInput(PatchInputModel):
    name: Annotated[str | None, Field(min_length=1)] = None
    definition: Annotated[str | None, Field(min_length=1)] = None
    nci_concept_id: Annotated[str | None, Field(min_length=1)] = None
    order: Annotated[int | None, Field(gt=0, lt=config.MAX_INT_NEO4J)] = None
    mandatory: bool | None = None
    activity_instance_class_uids: list[str] = []
    library_name: Annotated[str | None, Field(min_length=1)] = None
    change_description: Annotated[str | None, Field(min_length=1)] = None
    role_uid: Annotated[str | None, Field(min_length=1)] = None
    data_type_uid: Annotated[str | None, Field(min_length=1)] = None


class ActivityItemClassMappingInput(PatchInputModel):
    variable_class_uids: list[str] = []


class ActivityItemClassVersion(ActivityItemClass):
    """
    Class for storing ActivityItemClass and calculation of differences
    """

    changes: Annotated[
        dict[str, bool] | None,
        Field(
            description=(
                "Denotes whether or not there was a change in a specific field/property compared to the previous version. "
                "The field names in this object here refer to the field names of the objective (e.g. name, start_date, ..)."
            ),
            nullable=True,
        ),
    ] = None
