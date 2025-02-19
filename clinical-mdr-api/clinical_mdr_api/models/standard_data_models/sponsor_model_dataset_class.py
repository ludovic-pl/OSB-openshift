from typing import Annotated, Self

from pydantic import Field

from clinical_mdr_api.domains.standard_data_models.sponsor_model_dataset_class import (
    SponsorModelDatasetClassAR,
)
from clinical_mdr_api.models.libraries.library import Library
from clinical_mdr_api.models.standard_data_models.sponsor_model import SponsorModelBase
from clinical_mdr_api.models.utils import InputModel


class SponsorModelDatasetClass(SponsorModelBase):
    class Config:
        orm_mode = True

    uid: Annotated[str | None, Field(source="uid", nullable=True)] = None
    library_name: Annotated[
        str | None, Field(source="has_library.name", nullable=True)
    ] = None
    is_basic_std: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.is_basic_std", nullable=True),
    ] = None
    xml_path: Annotated[
        str | None, Field(source="has_sponsor_model_instance.xml_path", nullable=True)
    ] = None
    xml_title: Annotated[
        str | None, Field(source="has_sponsor_model_instance.xml_title", nullable=True)
    ] = None
    structure: Annotated[
        str | None, Field(source="has_sponsor_model_instance.structure", nullable=True)
    ] = None
    purpose: Annotated[
        str | None, Field(source="has_sponsor_model_instance.purpose", nullable=True)
    ] = None
    comment: Annotated[
        str | None, Field(source="has_sponsor_model_instance.comment", nullable=True)
    ] = None
    label: Annotated[
        str | None, Field(source="has_sponsor_model_instance.label", nullable=True)
    ] = None

    @classmethod
    def from_sponsor_model_dataset_class_ar(
        cls,
        sponsor_model_dataset_class_ar: SponsorModelDatasetClassAR,
    ) -> Self:
        return cls(
            uid=sponsor_model_dataset_class_ar.uid,
            is_basic_std=sponsor_model_dataset_class_ar.sponsor_model_dataset_class_vo.is_basic_std,
            xml_path=sponsor_model_dataset_class_ar.sponsor_model_dataset_class_vo.xml_path,
            xml_title=sponsor_model_dataset_class_ar.sponsor_model_dataset_class_vo.xml_title,
            structure=sponsor_model_dataset_class_ar.sponsor_model_dataset_class_vo.structure,
            purpose=sponsor_model_dataset_class_ar.sponsor_model_dataset_class_vo.purpose,
            comment=sponsor_model_dataset_class_ar.sponsor_model_dataset_class_vo.comment,
            label=sponsor_model_dataset_class_ar.sponsor_model_dataset_class_vo.label,
            library_name=Library.from_library_vo(
                sponsor_model_dataset_class_ar.library
            ).name,
        )


class SponsorModelDatasetClassInput(InputModel):
    dataset_class_uid: Annotated[str, Field(min_length=1)]
    sponsor_model_name: Annotated[
        str,
        Field(
            description="Name of the sponsor model in which to create the dataset class. E.g sdtmig_sponsormodel...",
            min_length=1,
        ),
    ]
    sponsor_model_version_number: Annotated[
        str,
        Field(
            description="Version number of the sponsor model in which to create the dataset class",
            min_length=1,
        ),
    ]
    is_basic_std: bool | None = None
    xml_path: str | None = None
    xml_title: str | None = None
    structure: str | None = None
    purpose: str | None = None
    comment: str | None = None
    label: str | None = None
    library_name: Annotated[
        str | None, Field(description="Defaults to CDISC", min_length=1)
    ] = "CDISC"
