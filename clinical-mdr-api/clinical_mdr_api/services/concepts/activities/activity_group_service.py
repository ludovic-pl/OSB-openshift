from clinical_mdr_api.domain_repositories.concepts.activities.activity_group_repository import (
    ActivityGroupRepository,
)
from clinical_mdr_api.domains.concepts.activities.activity_group import (
    ActivityGroupAR,
    ActivityGroupVO,
)
from clinical_mdr_api.models.concepts.activities.activity_group import (
    ActivityGroup,
    ActivityGroupCreateInput,
    ActivityGroupEditInput,
    ActivityGroupVersion,
)
from clinical_mdr_api.services.concepts.concept_generic_service import (
    ConceptGenericService,
)


class ActivityGroupService(ConceptGenericService[ActivityGroupAR]):
    aggregate_class = ActivityGroupAR
    repository_interface = ActivityGroupRepository
    version_class = ActivityGroupVersion

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivityGroupAR
    ) -> ActivityGroup:
        return ActivityGroup.from_activity_ar(activity_group_ar=item_ar)

    def _create_aggregate_root(
        self, concept_input: ActivityGroupCreateInput, library
    ) -> ActivityGroupAR:
        return ActivityGroupAR.from_input_values(
            author_id=self.author_id,
            concept_vo=ActivityGroupVO.from_repository_values(
                name=concept_input.name,
                name_sentence_case=concept_input.name_sentence_case,
                definition=concept_input.definition,
                abbreviation=concept_input.abbreviation,
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            concept_exists_by_library_and_name_callback=self._repos.activity_group_repository.latest_concept_in_library_exists_by_name,
        )

    def _edit_aggregate(
        self, item: ActivityGroupAR, concept_edit_input: ActivityGroupEditInput
    ) -> ActivityGroupAR:
        item.edit_draft(
            author_id=self.author_id,
            change_description=concept_edit_input.change_description,
            concept_vo=ActivityGroupVO.from_repository_values(
                name=concept_edit_input.name,
                name_sentence_case=concept_edit_input.name_sentence_case,
                definition=concept_edit_input.definition,
                abbreviation=concept_edit_input.abbreviation,
            ),
            concept_exists_by_library_and_name_callback=self._repos.activity_group_repository.latest_concept_in_library_exists_by_name,
        )
        return item
