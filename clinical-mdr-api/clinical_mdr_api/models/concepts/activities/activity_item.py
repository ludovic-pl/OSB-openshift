from typing import Annotated

from pydantic import Field

from clinical_mdr_api.models.concepts.concept import ExtendedConceptPostInput
from clinical_mdr_api.models.utils import BaseModel


class CompactActivityItemClass(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[str, Field(source="has_activity_item_class.uid")]
    name: Annotated[
        str | None,
        Field(source="has_activity_item_class.has_latest_value.name", nullable=True),
    ] = None


class CompactCTTerm(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[str | None, Field(source="has_ct_term.uid", nullable=True)] = None
    name: Annotated[
        str | None,
        Field(source="has_ct_term.has_name_root.has_latest_value.name", nullable=True),
    ] = None


class CompactUnitDefinition(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[
        str | None, Field(source="has_unit_definition.uid", nullable=True)
    ] = None
    name: Annotated[
        str | None,
        Field(source="has_unit_definition.has_latest_value.name", nullable=True),
    ] = None
    dimension_name: Annotated[
        str | None,
        Field(
            source="has_unit_definition.has_latest_value.has_ct_dimension.has_name_root.has_latest_value.name",
            nullable=True,
        ),
    ] = None


class ActivityItem(BaseModel):
    class Config:
        orm_mode = True

    activity_item_class: Annotated[CompactActivityItemClass, Field()]
    ct_terms: Annotated[list[CompactCTTerm], Field()] = []
    unit_definitions: Annotated[list[CompactUnitDefinition], Field()] = []


class ActivityItemCreateInput(ExtendedConceptPostInput):
    activity_item_class_uid: Annotated[str, Field(min_length=1)]
    ct_term_uids: list[str]
    unit_definition_uids: list[str]
