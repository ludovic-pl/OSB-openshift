from neomodel import db

from clinical_mdr_api.domain_repositories.controlled_terminologies.ct_term_attributes_repository import (
    CTTermAttributesRepository,
)
from clinical_mdr_api.domains.controlled_terminologies.ct_term_attributes import (
    CTTermAttributesAR,
    CTTermAttributesVO,
)
from clinical_mdr_api.models.controlled_terminologies.ct_term_attributes import (
    CTTermAttributes,
    CTTermAttributesVersion,
)
from clinical_mdr_api.models.utils import BaseModel
from clinical_mdr_api.services.controlled_terminologies.ct_term_generic_service import (
    CTTermGenericService,
)


class CTTermAttributesService(CTTermGenericService[CTTermAttributesAR]):
    aggregate_class = CTTermAttributesAR
    repository_interface = CTTermAttributesRepository
    version_class = CTTermAttributesVersion

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: CTTermAttributesAR
    ) -> CTTermAttributes:
        return CTTermAttributes.from_ct_term_ar(item_ar)

    @db.transaction
    def edit_draft(self, term_uid: str, term_input: BaseModel) -> BaseModel:
        item = self._find_by_uid_or_raise_not_found(term_uid, for_update=True)

        item.edit_draft(
            author_id=self.author_id,
            change_description=term_input.change_description,
            ct_term_vo=CTTermAttributesVO.from_input_values(
                codelists=item.ct_term_vo.codelists,
                catalogue_name=item.ct_term_vo.catalogue_name,
                code_submission_value=self.get_input_or_previous_property(
                    term_input.code_submission_value,
                    item.ct_term_vo.code_submission_value,
                ),
                name_submission_value=self.get_input_or_previous_property(
                    term_input.name_submission_value,
                    item.ct_term_vo.name_submission_value,
                ),
                preferred_term=self.get_input_or_previous_property(
                    term_input.nci_preferred_name, item.ct_term_vo.preferred_term
                ),
                definition=self.get_input_or_previous_property(
                    term_input.definition, item.ct_term_vo.definition
                ),
                # passing always True callbacks, as we can't change catalogue
                # in scope of CTTermName or CTTermAttributes, it can be only changed via CTTermRoot
                codelist_exists_callback=lambda _: True,
                catalogue_exists_callback=lambda _: True,
            ),
            term_exists_by_name_callback=self.repository.term_specific_exists_by_name,
            term_exists_by_code_submission_value_callback=self.repository.term_attributes_exists_by_code_submission_value,
        )
        self.repository.save(item)
        return self._transform_aggregate_root_to_pydantic_model(item)
