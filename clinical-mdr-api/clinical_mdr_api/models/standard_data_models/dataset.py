from typing import Annotated

from pydantic import Field

from clinical_mdr_api.models.standard_data_models.variable_class import (
    SimpleDatasetClass,
)
from clinical_mdr_api.models.utils import BaseModel


class SimpleDataModelIG(BaseModel):
    ordinal: Annotated[str | None, Field(nullable=True)] = None
    data_model_ig_name: Annotated[str, Field(title="The name of the data model ig")]


class Dataset(BaseModel):
    class Config:
        orm_mode = True

    uid: Annotated[str, Field()]
    label: Annotated[str, Field()]
    title: Annotated[str, Field()]
    description: Annotated[str | None, Field(nullable=True)] = None
    catalogue_name: Annotated[str, Field()]
    implemented_dataset_class: Annotated[
        SimpleDatasetClass | None, Field(nullable=True)
    ] = None
    data_model_ig: Annotated[SimpleDataModelIG, Field()]

    @classmethod
    def from_repository_output(cls, input_dict: dict):
        return cls(
            uid=input_dict.get("uid"),
            label=input_dict.get("standard_value").get("label"),
            title=input_dict.get("standard_value").get("title"),
            description=input_dict.get("standard_value").get("description"),
            catalogue_name=input_dict.get("catalogue_name"),
            parent_class=input_dict.get("parent_class_name"),
            implemented_dataset_class=(
                SimpleDatasetClass(
                    ordinal=input_dict.get("implemented_dataset_class").get("ordinal"),
                    dataset_class_name=input_dict.get("implemented_dataset_class").get(
                        "dataset_class_name"
                    ),
                )
                if input_dict.get("implemented_dataset_class")
                else None
            ),
            data_model_ig=SimpleDataModelIG(
                ordinal=input_dict.get("data_model_ig").get("ordinal"),
                data_model_ig_name=input_dict.get("data_model_ig").get(
                    "data_model_ig_name"
                ),
            ),
        )
