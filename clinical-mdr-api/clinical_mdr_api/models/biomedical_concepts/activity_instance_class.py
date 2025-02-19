from typing import Annotated, Callable, Self

from pydantic import Field, validator

from clinical_mdr_api.domains.biomedical_concepts.activity_instance_class import (
    ActivityInstanceClassAR,
)
from clinical_mdr_api.domains.versioned_object_aggregate import (
    LibraryItemStatus,
    ObjectAction,
)
from clinical_mdr_api.models.concepts.concept import VersionProperties
from clinical_mdr_api.models.libraries.library import Library
from clinical_mdr_api.models.utils import BaseModel, InputModel, PatchInputModel


class CompactActivityInstanceClass(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[str | None, Field(source="parent_class.uid", nullable=True)] = None
    name: Annotated[
        str | None, Field(source="parent_class.has_latest_value.name", nullable=True)
    ] = None


class SimpleDatasetClass(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str,
        Field(
            source="maps_dataset_class.uid",
        ),
    ]


class ActivityInstanceClass(VersionProperties):
    class Config:
        orm_mode = True

    uid: Annotated[str | None, Field(source="uid", nullable=True)] = None
    name: Annotated[
        str | None, Field(source="has_latest_value.name", nullable=True)
    ] = None
    order: Annotated[
        int | None, Field(source="has_latest_value.order", nullable=True)
    ] = None
    definition: Annotated[
        str | None, Field(source="has_latest_value.definition", nullable=True)
    ] = None
    is_domain_specific: Annotated[
        bool | None, Field(source="has_latest_value.is_domain_specific", nullable=True)
    ] = None
    parent_class: Annotated[
        CompactActivityInstanceClass | None, Field(nullable=True)
    ] = None
    dataset_classes: Annotated[
        list[SimpleDatasetClass] | None, Field(nullable=True)
    ] = None
    library_name: Annotated[
        str | None, Field(source="has_library.name", nullable=True)
    ] = None
    possible_actions: Annotated[
        list[str],
        Field(
            description=(
                "Holds those actions that can be performed on the ActivityInstances. "
                "Actions are: 'approve', 'edit', 'new_version'."
            ),
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
    def from_activity_instance_class_ar(
        cls,
        activity_instance_class_ar: ActivityInstanceClassAR,
        find_activity_instance_class_by_uid: Callable[
            [str], ActivityInstanceClassAR | None
        ],
    ) -> Self:
        parent_class = find_activity_instance_class_by_uid(
            activity_instance_class_ar.activity_instance_class_vo.parent_uid
        )
        return cls(
            uid=activity_instance_class_ar.uid,
            name=activity_instance_class_ar.name,
            order=activity_instance_class_ar.activity_instance_class_vo.order,
            definition=activity_instance_class_ar.activity_instance_class_vo.definition,
            is_domain_specific=activity_instance_class_ar.activity_instance_class_vo.is_domain_specific,
            parent_class=(
                CompactActivityInstanceClass(
                    uid=parent_class.uid, name=parent_class.name
                )
                if parent_class
                else None
            ),
            dataset_classes=(
                [
                    SimpleDatasetClass(uid=dataset_class.uid)
                    for dataset_class in activity_instance_class_ar.activity_instance_class_vo.dataset_class_uids
                ]
                if activity_instance_class_ar.activity_instance_class_vo.dataset_class_uids
                else []
            ),
            library_name=Library.from_library_vo(
                activity_instance_class_ar.library
            ).name,
            start_date=activity_instance_class_ar.item_metadata.start_date,
            end_date=activity_instance_class_ar.item_metadata.end_date,
            status=activity_instance_class_ar.item_metadata.status.value,
            version=activity_instance_class_ar.item_metadata.version,
            change_description=activity_instance_class_ar.item_metadata.change_description,
            author_username=activity_instance_class_ar.item_metadata.author_username,
            possible_actions=sorted(
                [_.value for _ in activity_instance_class_ar.get_possible_actions()]
            ),
        )


class ActivityInstanceClassInput(InputModel):
    name: Annotated[str | None, Field(min_length=1)] = None
    order: int | None = None
    definition: Annotated[str | None, Field(min_length=1)] = None
    is_domain_specific: bool | None = None
    parent_uid: Annotated[str | None, Field(min_length=1)] = None
    library_name: Annotated[str | None, Field(min_length=1)] = None
    change_description: Annotated[str | None, Field(min_length=1)] = None


class ActivityInstanceClassMappingInput(PatchInputModel):
    dataset_class_uids: list[str] = []


class ActivityInstanceClassVersion(ActivityInstanceClass):
    """
    Class for storing ActivityInstanceClass and calculation of differences
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
