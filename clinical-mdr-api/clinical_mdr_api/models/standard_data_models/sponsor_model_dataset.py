from typing import Annotated, Self

from pydantic import Field

from clinical_mdr_api.domains.standard_data_models.sponsor_model_dataset import (
    SponsorModelDatasetAR,
)
from clinical_mdr_api.models.libraries.library import Library
from clinical_mdr_api.models.standard_data_models.sponsor_model import SponsorModelBase
from clinical_mdr_api.models.utils import InputModel


class SponsorModelDataset(SponsorModelBase):
    class Config:
        orm_mode = True

    uid: Annotated[
        str | None,
        Field(source="uid", nullable=True),
    ] = None
    library_name: Annotated[
        str | None,
        Field(source="has_library.name", nullable=True),
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
    keys: Annotated[
        list[str] | None,
        Field(source="has_sponsor_model_instance.has_key.uid", nullable=True),
    ] = None
    sort_keys: Annotated[
        list[str] | None,
        Field(source="has_sponsor_model_instance.has_sort_key.uid", nullable=True),
    ] = None
    source_ig: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.source_ig", nullable=True),
    ] = None
    comment: Annotated[
        str | None, Field(source="has_sponsor_model_instance.comment", nullable=True)
    ] = None
    ig_comment: Annotated[
        str | None, Field(source="has_sponsor_model_instance.ig_comment", nullable=True)
    ] = None
    map_domain_flag: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.map_domain_flag", nullable=True),
    ] = None
    suppl_qual_flag: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.suppl_qual_flag", nullable=True),
    ] = None
    include_in_raw: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.include_in_raw", nullable=True),
    ] = None
    gen_raw_seqno_flag: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.gen_raw_seqno_flag", nullable=True),
    ] = None
    enrich_build_order: Annotated[
        int | None,
        Field(source="has_sponsor_model_instance.has_dataset|ordinal", nullable=True),
    ] = None
    label: Annotated[
        str | None, Field(source="has_sponsor_model_instance.label", nullable=True)
    ] = None
    state: Annotated[
        str | None, Field(source="has_sponsor_model_instance.state", nullable=True)
    ] = None
    extended_domain: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.extended_domain", nullable=True),
    ] = None

    @classmethod
    def from_sponsor_model_dataset_ar(
        cls,
        sponsor_model_dataset_ar: SponsorModelDatasetAR,
    ) -> Self:
        return cls(
            uid=sponsor_model_dataset_ar.uid,
            is_basic_std=sponsor_model_dataset_ar.sponsor_model_dataset_vo.is_basic_std,
            xml_path=sponsor_model_dataset_ar.sponsor_model_dataset_vo.xml_path,
            xml_title=sponsor_model_dataset_ar.sponsor_model_dataset_vo.xml_title,
            structure=sponsor_model_dataset_ar.sponsor_model_dataset_vo.structure,
            purpose=sponsor_model_dataset_ar.sponsor_model_dataset_vo.purpose,
            keys=sponsor_model_dataset_ar.sponsor_model_dataset_vo.keys,
            sort_keys=sponsor_model_dataset_ar.sponsor_model_dataset_vo.sort_keys,
            source_ig=sponsor_model_dataset_ar.sponsor_model_dataset_vo.source_ig,
            comment=sponsor_model_dataset_ar.sponsor_model_dataset_vo.comment,
            ig_comment=sponsor_model_dataset_ar.sponsor_model_dataset_vo.ig_comment,
            map_domain_flag=sponsor_model_dataset_ar.sponsor_model_dataset_vo.map_domain_flag,
            suppl_qual_flag=sponsor_model_dataset_ar.sponsor_model_dataset_vo.suppl_qual_flag,
            include_in_raw=sponsor_model_dataset_ar.sponsor_model_dataset_vo.include_in_raw,
            gen_raw_seqno_flag=sponsor_model_dataset_ar.sponsor_model_dataset_vo.gen_raw_seqno_flag,
            enrich_build_order=sponsor_model_dataset_ar.sponsor_model_dataset_vo.enrich_build_order,
            label=sponsor_model_dataset_ar.sponsor_model_dataset_vo.label,
            state=sponsor_model_dataset_ar.sponsor_model_dataset_vo.state,
            extended_domain=sponsor_model_dataset_ar.sponsor_model_dataset_vo.extended_domain,
            library_name=Library.from_library_vo(sponsor_model_dataset_ar.library).name,
        )


class SponsorModelDatasetInput(InputModel):
    dataset_uid: Annotated[str, Field(min_length=1)]
    sponsor_model_name: Annotated[
        str,
        Field(
            description="Name of the sponsor model in which to create the dataset. E.g sdtmig_sponsormodel...",
            min_length=1,
        ),
    ]
    sponsor_model_version_number: Annotated[
        str,
        Field(
            description="Version number of the sponsor model in which to create the dataset",
            min_length=1,
        ),
    ]
    is_basic_std: bool | None = None
    xml_path: str | None = None
    xml_title: str | None = None
    structure: str | None = None
    purpose: str | None = None
    keys: list[str] | None = None
    sort_keys: list[str] | None = None
    source_ig: Annotated[
        str | None,
        Field(
            description="Source Implementation Guide, e.g. SDTMIG 3.3 or TAUG-DIABETES 1.0",
        ),
    ] = None
    comment: str | None = None
    ig_comment: str | None = None
    map_domain_flag: bool | None = None
    suppl_qual_flag: bool | None = None
    include_in_raw: bool | None = None
    gen_raw_seqno_flag: bool | None = None
    enrich_build_order: int | None = None
    label: str | None = None
    state: str | None = None
    extended_domain: str | None = None
    library_name: Annotated[
        str | None, Field(description="Defaults to CDISC", min_length=1)
    ] = "CDISC"
