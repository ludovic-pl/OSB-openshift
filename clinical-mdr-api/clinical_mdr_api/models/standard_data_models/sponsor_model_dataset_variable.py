from typing import Annotated

from pydantic import Field

from clinical_mdr_api.domains.standard_data_models.sponsor_model_dataset_variable import (
    SponsorModelDatasetVariableAR,
)
from clinical_mdr_api.models.libraries.library import Library
from clinical_mdr_api.models.standard_data_models.sponsor_model import SponsorModelBase
from clinical_mdr_api.models.utils import InputModel


class SponsorModelDatasetVariable(SponsorModelBase):
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
        Field(source="has_sponsor_model_instance.has_variable|ordinal", nullable=True),
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
    xml_codelist_multi: Annotated[
        list[str] | None,
        Field(source="has_sponsor_model_instance.xml_codelist_multi", nullable=True),
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
    class_table: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.class_table", nullable=True),
    ] = None
    class_column: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.class_column", nullable=True),
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
    value_lvl_where_cols: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.value_lvl_where_cols", nullable=True),
    ] = None
    value_lvl_label_col: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.value_lvl_label_col", nullable=True),
    ] = None
    value_lvl_collect_ct_val: Annotated[
        str | None,
        Field(
            source="has_sponsor_model_instance.value_lvl_collect_ct_val", nullable=True
        ),
    ] = None
    value_lvl_ct_codelist_id_col: Annotated[
        str | None,
        Field(
            source="has_sponsor_model_instance.value_lvl_ct_codelist_id_col",
            nullable=True,
        ),
    ] = None
    enrich_build_order: Annotated[
        int | None,
        Field(source="has_sponsor_model_instance.enrich_build_order", nullable=True),
    ] = None
    enrich_rule: Annotated[
        str | None,
        Field(source="has_sponsor_model_instance.enrich_rule", nullable=True),
    ] = None
    xml_codelist_values: Annotated[
        bool | None,
        Field(source="has_sponsor_model_instance.xml_codelist_values", nullable=True),
    ] = None

    @classmethod
    def from_sponsor_model_dataset_variable_ar(
        cls,
        sponsor_model_dataset_variable_ar: SponsorModelDatasetVariableAR,
    ) -> "SponsorModelDatasetVariable":
        return cls(
            uid=sponsor_model_dataset_variable_ar.uid,
            is_basic_std=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.is_basic_std,
            label=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.label,
            order=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.order,
            variable_type=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.variable_type,
            length=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.length,
            display_format=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.display_format,
            xml_datatype=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.xml_datatype,
            xml_codelist=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.xml_codelist,
            xml_codelist_multi=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.xml_codelist_multi,
            core=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.core,
            origin=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.origin,
            role=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.role,
            term=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.term,
            algorithm=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.algorithm,
            qualifiers=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.qualifiers,
            comment=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.comment,
            ig_comment=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.ig_comment,
            class_table=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.class_table,
            class_column=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.class_column,
            map_var_flag=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.map_var_flag,
            fixed_mapping=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.fixed_mapping,
            include_in_raw=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.include_in_raw,
            nn_internal=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.nn_internal,
            value_lvl_where_cols=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.value_lvl_where_cols,
            value_lvl_label_col=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.value_lvl_label_col,
            value_lvl_collect_ct_val=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.value_lvl_collect_ct_val,
            value_lvl_ct_codelist_id_col=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.value_lvl_ct_codelist_id_col,
            enrich_build_order=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.enrich_build_order,
            enrich_rule=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.enrich_rule,
            xml_codelist_values=sponsor_model_dataset_variable_ar.sponsor_model_dataset_variable_vo.xml_codelist_values,
            library_name=Library.from_library_vo(
                sponsor_model_dataset_variable_ar.library
            ).name,
        )


class SponsorModelDatasetVariableInput(InputModel):
    dataset_uid: Annotated[
        str,
        Field(
            description="Uid of the dataset in which to create the variable. E.g AE",
            min_length=1,
        ),
    ]
    dataset_variable_uid: Annotated[str, Field(min_length=1)]
    sponsor_model_name: Annotated[
        str,
        Field(
            description="Name of the sponsor model in which to create the variable. E.g sdtmig_sponsormodel...",
            min_length=1,
        ),
    ]
    sponsor_model_version_number: Annotated[
        str,
        Field(
            description="Version number of the sponsor model in which to create the variable",
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
    xml_codelist_multi: list[str] | None = None
    core: str | None = None
    origin: str | None = None
    role: str | None = None
    term: str | None = None
    algorithm: str | None = None
    qualifiers: list[str] | None = None
    comment: str | None = None
    ig_comment: str | None = None
    class_table: str | None = None
    class_column: str | None = None
    map_var_flag: bool | None = None
    fixed_mapping: str | None = None
    include_in_raw: bool | None = None
    nn_internal: bool | None = None
    value_lvl_where_cols: str | None = None
    value_lvl_label_col: str | None = None
    value_lvl_collect_ct_val: str | None = None
    value_lvl_ct_codelist_id_col: str | None = None
    enrich_build_order: int | None = None
    enrich_rule: str | None = None
    xml_codelist_values: bool | None = None
    library_name: Annotated[
        str | None, Field(description="Defaults to CDISC", min_length=1)
    ] = "CDISC"
