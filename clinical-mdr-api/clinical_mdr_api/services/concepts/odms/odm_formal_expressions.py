from neomodel import db

from clinical_mdr_api.domain_repositories.concepts.odms.formal_expression_repository import (
    FormalExpressionRepository,
)
from clinical_mdr_api.domains.concepts.odms.formal_expression import (
    OdmFormalExpressionAR,
    OdmFormalExpressionVO,
)
from clinical_mdr_api.models.concepts.odms.odm_formal_expression import (
    OdmFormalExpression,
    OdmFormalExpressionPatchInput,
    OdmFormalExpressionPostInput,
    OdmFormalExpressionVersion,
)
from clinical_mdr_api.services.concepts.odms.odm_generic_service import (
    OdmGenericService,
)
from common.exceptions import BusinessLogicException, NotFoundException


class OdmFormalExpressionService(OdmGenericService[OdmFormalExpressionAR]):
    aggregate_class = OdmFormalExpressionAR
    version_class = OdmFormalExpressionVersion
    repository_interface = FormalExpressionRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: OdmFormalExpressionAR
    ) -> OdmFormalExpression:
        return OdmFormalExpression.from_odm_formal_expression_ar(
            odm_formal_expression_ar=item_ar
        )

    def _create_aggregate_root(
        self, concept_input: OdmFormalExpressionPostInput, library
    ) -> OdmFormalExpressionAR:
        return OdmFormalExpressionAR.from_input_values(
            author_id=self.author_id,
            concept_vo=OdmFormalExpressionVO.from_repository_values(
                context=concept_input.context,
                expression=concept_input.expression,
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            odm_object_exists_callback=self._repos.odm_formal_expression_repository.odm_object_exists,
        )

    def _edit_aggregate(
        self,
        item: OdmFormalExpressionAR,
        concept_edit_input: OdmFormalExpressionPatchInput,
    ) -> OdmFormalExpressionAR:
        item.edit_draft(
            author_id=self.author_id,
            change_description=concept_edit_input.change_description,
            concept_vo=OdmFormalExpressionVO.from_repository_values(
                context=concept_edit_input.context,
                expression=concept_edit_input.expression,
            ),
            odm_object_exists_callback=self._repos.odm_formal_expression_repository.odm_object_exists,
        )
        return item

    def soft_delete(self, uid: str) -> None:
        NotFoundException.raise_if_not(
            self._repos.odm_formal_expression_repository.exists_by("uid", uid, True),
            "ODM Formal Expression",
            uid,
        )

        BusinessLogicException.raise_if(
            self._repos.odm_formal_expression_repository.has_active_relationships(
                uid, ["has_condition", "has_method"]
            ),
            msg="This ODM Formal Expression is in use.",
        )

        return super().soft_delete(uid)

    @db.transaction
    def get_active_relationships(self, uid: str):
        NotFoundException.raise_if_not(
            self._repos.odm_formal_expression_repository.exists_by("uid", uid, True),
            "ODM Formal Expression",
            uid,
        )

        return self._repos.odm_formal_expression_repository.get_active_relationships(
            uid, ["has_condition", "has_method"]
        )
