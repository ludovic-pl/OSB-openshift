from typing import Annotated

from pydantic import Field

from clinical_mdr_api.models.syntax_templates.template_parameter_term import (
    IndexedTemplateParameterTerm,
)
from clinical_mdr_api.models.utils import InputModel


class TemplateParameterMultiSelectInput(InputModel):
    terms: Annotated[
        list[IndexedTemplateParameterTerm] | None,
        Field(
            description="A list of indexed template parameter terms that are used at this position in the template.",
        ),
    ]
    value: Annotated[
        float | None,
        Field(
            description="A numeric value used at this position in the template.",
        ),
    ] = None
    conjunction: Annotated[
        str | None,
        Field(
            description="If the selected template parameter term has multiple values, "
            "the conjunction string to connect them. Available values are ['and', 'or', ','].",
        ),
    ] = None
    labels: list[str] | None = None
