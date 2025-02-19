from clinical_mdr_api.domain_repositories.concepts.activities.activity_sub_group_repository import (
    ActivitySubGroupRepository,
)
from clinical_mdr_api.domains.concepts.activities.activity_sub_group import (
    ActivitySubGroupAR,
    ActivitySubGroupVO,
    SimpleActivityGroupVO,
)
from clinical_mdr_api.models.concepts.activities.activity_sub_group import (
    ActivitySubGroup,
    ActivitySubGroupCreateInput,
    ActivitySubGroupEditInput,
    ActivitySubGroupVersion,
)
from clinical_mdr_api.services.concepts.concept_generic_service import (
    ConceptGenericService,
)


class ActivitySubGroupService(ConceptGenericService[ActivitySubGroupAR]):
    aggregate_class = ActivitySubGroupAR
    repository_interface = ActivitySubGroupRepository
    version_class = ActivitySubGroupVersion

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: ActivitySubGroupAR
    ) -> ActivitySubGroup:
        return ActivitySubGroup.from_activity_ar(
            activity_subgroup_ar=item_ar,
            find_activity_by_uid=self._repos.activity_group_repository.find_by_uid_2,
        )

    def _create_aggregate_root(
        self, concept_input: ActivitySubGroupCreateInput, library
    ) -> ActivitySubGroupAR:
        return ActivitySubGroupAR.from_input_values(
            author_id=self.author_id,
            concept_vo=ActivitySubGroupVO.from_repository_values(
                name=concept_input.name,
                name_sentence_case=concept_input.name_sentence_case,
                definition=concept_input.definition,
                abbreviation=concept_input.abbreviation,
                activity_groups=(
                    [
                        SimpleActivityGroupVO(activity_group_uid=activity_group)
                        for activity_group in concept_input.activity_groups
                    ]
                    if concept_input.activity_groups
                    else []
                ),
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            concept_exists_by_library_and_name_callback=self._repos.activity_subgroup_repository.latest_concept_in_library_exists_by_name,
            activity_group_exists=self._repos.activity_group_repository.final_concept_exists,
        )

    def _edit_aggregate(
        self,
        item: ActivitySubGroupAR,
        concept_edit_input: ActivitySubGroupEditInput,
    ) -> ActivitySubGroupAR:
        item.edit_draft(
            author_id=self.author_id,
            change_description=concept_edit_input.change_description,
            concept_vo=ActivitySubGroupVO.from_repository_values(
                name=concept_edit_input.name,
                name_sentence_case=concept_edit_input.name_sentence_case,
                definition=concept_edit_input.definition,
                abbreviation=concept_edit_input.abbreviation,
                activity_groups=(
                    [
                        SimpleActivityGroupVO(activity_group_uid=activity_group)
                        for activity_group in concept_edit_input.activity_groups
                    ]
                    if concept_edit_input.activity_groups
                    else []
                ),
            ),
            concept_exists_by_library_and_name_callback=self._repos.activity_subgroup_repository.latest_concept_in_library_exists_by_name,
            activity_group_exists=self._repos.activity_group_repository.final_concept_exists,
        )
        return item
