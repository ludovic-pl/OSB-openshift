from neomodel import db

from clinical_mdr_api.domain_repositories.concepts.odms.vendor_element_repository import (
    VendorElementRepository,
)
from clinical_mdr_api.domains.concepts.odms.vendor_element import (
    OdmVendorElementAR,
    OdmVendorElementVO,
)
from clinical_mdr_api.models.concepts.odms.odm_vendor_element import (
    OdmVendorElement,
    OdmVendorElementPatchInput,
    OdmVendorElementPostInput,
    OdmVendorElementVersion,
)
from clinical_mdr_api.services.concepts.odms.odm_generic_service import (
    OdmGenericService,
)
from common.exceptions import BusinessLogicException, NotFoundException


class OdmVendorElementService(OdmGenericService[OdmVendorElementAR]):
    aggregate_class = OdmVendorElementAR
    version_class = OdmVendorElementVersion
    repository_interface = VendorElementRepository

    def _transform_aggregate_root_to_pydantic_model(
        self, item_ar: OdmVendorElementAR
    ) -> OdmVendorElement:
        return OdmVendorElement.from_odm_vendor_element_ar(
            odm_vendor_element_ar=item_ar,
            find_odm_vendor_namespace_by_uid=self._repos.odm_vendor_namespace_repository.find_by_uid_2,
            find_odm_vendor_attribute_by_uid=self._repos.odm_vendor_attribute_repository.find_by_uid_2,
        )

    def _create_aggregate_root(
        self, concept_input: OdmVendorElementPostInput, library
    ) -> OdmVendorElementAR:
        return OdmVendorElementAR.from_input_values(
            author_id=self.author_id,
            concept_vo=OdmVendorElementVO.from_repository_values(
                name=concept_input.name,
                compatible_types=[
                    compatible_type.value
                    for compatible_type in concept_input.compatible_types
                ],
                vendor_namespace_uid=concept_input.vendor_namespace_uid,
                vendor_attribute_uids=[],
            ),
            library=library,
            generate_uid_callback=self.repository.generate_uid,
            odm_vendor_namespace_exists_by_callback=self._repos.odm_vendor_namespace_repository.exists_by,
            find_odm_vendor_element_callback=self._repos.odm_vendor_element_repository.find_all,
        )

    def _edit_aggregate(
        self,
        item: OdmVendorElementAR,
        concept_edit_input: OdmVendorElementPatchInput,
    ) -> OdmVendorElementAR:
        item.edit_draft(
            author_id=self.author_id,
            change_description=concept_edit_input.change_description,
            concept_vo=OdmVendorElementVO.from_repository_values(
                name=concept_edit_input.name,
                compatible_types=[
                    compatible_type.value
                    for compatible_type in concept_edit_input.compatible_types
                ],
                vendor_namespace_uid=item.concept_vo.vendor_namespace_uid,
                vendor_attribute_uids=[],
            ),
        )
        return item

    @db.transaction
    def get_active_relationships(self, uid: str):
        NotFoundException.raise_if_not(
            self._repos.odm_vendor_element_repository.exists_by("uid", uid, True),
            "ODM Vendor Element",
            uid,
        )

        return self._repos.odm_vendor_element_repository.get_active_relationships(
            uid, ["belongs_to_vendor_namespace", "has_vendor_attribute"]
        )

    def soft_delete(self, uid: str) -> None:
        NotFoundException.raise_if_not(
            self._repos.odm_vendor_element_repository.exists_by("uid", uid, True),
            "ODM Vendor Element",
            uid,
        )

        BusinessLogicException.raise_if(
            self._repos.odm_vendor_element_repository.has_active_relationships(
                uid, ["belongs_to_form", "belongs_to_item_group", "belongs_to_item"]
            ),
            msg="This ODM Vendor Element is in use.",
        )

        return super().soft_delete(uid)
