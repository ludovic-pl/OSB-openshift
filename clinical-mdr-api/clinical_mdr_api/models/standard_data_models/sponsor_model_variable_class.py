from typing import Annotated

from pydantic import Field

from clinical_mdr_api.domains.standard_data_models.sponsor_model_variable_class import (
    SponsorModelVariableClassAR,
)
from clinical_mdr_api.models.libraries.library import Library
from clinical_mdr_api.models.standard_data_models.sponsor_model import SponsorModelBase
from clinical_mdr_api.models.utils import InputModel


class SponsorModelVariableClass(SponsorModelBase):
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
    label: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.label", nullable=True),
    ] = None
    order: Annotated[
        int | None,
        Field(
            source="has_sponsor_model_instance.has_variable_class|ordinal",
            nullable=True,
        ),
    ] = None
    variable_type: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.variable_type", nullable=True),
    ] = None
    length: Annotated[
        int | None,
        Field(source="has_sponsor_model_instance.length", nullable=True),
    ] = None
    display_format: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.display_format", nullable=True),
    ] = None
    xml_datatype: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.xml_datatype", nullable=True),
    ] = None
    xml_codelist: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.xml_codelist", nullable=True),
    ] = None
    core: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.core", nullable=True),
    ] = None
    origin: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.origin", nullable=True),
    ] = None
    role: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.role", nullable=True),
    ] = None
    term: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.term", nullable=True),
    ] = None
    algorithm: Annotated[
        str | None, Field(source="has_sponsor_model_instance.algorithm", nullable=True)
    ] = None
    qualifiers: Annotated[
        list[str] | None,
        Field(source="has_sponsor_model_instance.qualifiers", nullable=True),
    ] = None
    comment: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.comment", nullable=True),
    ] = None
    ig_comment: Annotated[
        str | None, Field(source="has_sponsor_model_instance.ig_comment", nullable=True)
    ] = None
    map_var_flag: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.map_var_flag", nullable=True),
    ] = None
    fixed_mapping: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.fixed_mapping", nullable=True),
    ] = None
    include_in_raw: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.include_in_raw", nullable=True),
    ] = None
    nn_internal: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.nn_internal", nullable=True),
    ] = None
    incl_cre_domain: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.incl_cre_domain", nullable=True),
    ] = None
    xml_codelist_values: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.xml_codelist_values", nullable=True),
    ] = None

    @classmethod
    def from_sponsor_model_variable_class_ar(
        cls,
        sponsor_model_variable_class_ar: SponsorModelVariableClassAR,
    ) -> "SponsorModelVariableClass":
        return cls(
            uid=sponsor_model_variable_class_ar.uid,
            is_basic_std=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.is_basic_std,
            label=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.label,
            order=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.order,
            variable_type=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.variable_type,
            length=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.length,
            display_format=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.display_format,
            xml_datatype=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.xml_datatype,
            xml_codelist=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.xml_codelist,
            core=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.core,
            origin=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.origin,
            role=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.role,
            term=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.term,
            algorithm=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.algorithm,
            qualifiers=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.qualifiers,
            comment=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.comment,
            ig_comment=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.ig_comment,
            map_var_flag=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.map_var_flag,
            fixed_mapping=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.fixed_mapping,
            include_in_raw=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.include_in_raw,
            nn_internal=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.nn_internal,
            incl_cre_domain=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.incl_cre_domain,
            xml_codelist_values=sponsor_model_variable_class_ar.sponsor_model_variable_class_vo.xml_codelist_values,
            library_name=Library.from_library_vo(
                sponsor_model_variable_class_ar.library
            ).name,
        )


class SponsorModelVariableClassInput(InputModel):
    dataset_class_uid: Annotated[
        str,
        Field(
            description="Uid of the dataset class in which to create the variable. E.g Findings",
            min_length=1,
        ),
    ]
    variable_class_uid: Annotated[str, Field(min_length=1)]
    sponsor_model_name: Annotated[
        str,
        Field(
            description="Name of the sponsor model in which to create the variable class. E.g sdtmig_sponsormodel...",
            min_length=1,
        ),
    ]
    sponsor_model_version_number: Annotated[
        str,
        Field(
            description="Version number of the sponsor model in which to create the variable class",
            min_length=1,
        ),
    ]
    is_basic_std: bool | None = None
    label: str | None = None
    order: int | None = None
    variable_type: str | None = None
    length: int | None = None
    display_format: str | None = None
    xml_datatype: str | None = None
    xml_codelist: str | None = None
    core: str | None = None
    origin: str | None = None
    role: str | None = None
    term: str | None = None
    algorithm: str | None = None
    qualifiers: list[str] | None = None
    comment: str | None = None
    ig_comment: str | None = None
    map_var_flag: bool | None = None
    fixed_mapping: str | None = None
    include_in_raw: bool | None = None
    nn_internal: bool | None = None
    incl_cre_domain: bool | None = None
    xml_codelist_values: bool | None = None
    library_name: Annotated[
        str | None, Field(description="Defaults to CDISC", min_length=1)
    ] = "CDISC"
