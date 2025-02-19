from dataclasses import dataclass
from typing import Callable, Self

from pydantic import BaseModel

from common.exceptions import BusinessLogicException


class LibraryItem(BaseModel):
    uid: str
    name: str | None


@dataclass(frozen=True)
class ActivityItemVO:
    """
    The ActivityItemVO acts as the value object for a single ActivityItem value object
    """

    activity_item_class_uid: str
    activity_item_class_name: str | None
    ct_terms: list[LibraryItem]
    unit_definitions: list[LibraryItem]

    @classmethod
    def from_repository_values(
        cls,
        activity_item_class_uid: str,
        activity_item_class_name: str | None,
        ct_terms: list[dict[str, str]],
        unit_definitions=list[dict[str, str]],
    ) -> Self:
        activity_item_vo = cls(
            activity_item_class_uid=activity_item_class_uid,
            activity_item_class_name=activity_item_class_name,
            ct_terms=ct_terms,
            unit_definitions=unit_definitions,
        )

        return activity_item_vo

    def validate(
        self,
        activity_item_class_exists: Callable[[str], bool],
        ct_term_exists: Callable[[str], bool],
        unit_definition_exists: Callable[[str], bool],
    ) -> None:
        BusinessLogicException.raise_if_not(
            activity_item_class_exists(self.activity_item_class_uid),
            msg=f"ActivityItemVO tried to connect to non-existent Activity Item Class with UID '{self.activity_item_class_uid}'.",
        )
        for term in self.ct_terms:
            BusinessLogicException.raise_if_not(
                ct_term_exists(term.uid),
                msg=f"ActivityItemVO tried to connect to non-existent or non-final CTTerm with UID {term.uid}'.",
            )
        for unit in self.unit_definitions:
            BusinessLogicException.raise_if_not(
                unit_definition_exists(unit.uid),
                msg=f"ActivityItemVO tried to connect to non-existent Unit Definition with UID {unit.uid}'.",
            )
