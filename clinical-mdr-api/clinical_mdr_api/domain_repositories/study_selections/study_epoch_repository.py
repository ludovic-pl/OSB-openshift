import copy
import datetime
from typing import Callable

from neomodel import db
from neomodel.sync_.match import Optional

from clinical_mdr_api.domain_repositories.generic_repository import (
    manage_previous_connected_study_selection_relationships,
)
from clinical_mdr_api.domain_repositories.models._utils import ListDistinct
from clinical_mdr_api.domain_repositories.models.controlled_terminology import (
    CTTermRoot,
)
from clinical_mdr_api.domain_repositories.models.study import StudyRoot, StudyValue
from clinical_mdr_api.domain_repositories.models.study_audit_trail import (
    Create,
    Delete,
    Edit,
)
from clinical_mdr_api.domain_repositories.models.study_epoch import StudyEpoch
from clinical_mdr_api.domains.study_definition_aggregates.study_metadata import (
    StudyStatus,
)
from clinical_mdr_api.domains.study_selections import study_epoch
from clinical_mdr_api.domains.study_selections.study_epoch import (
    StudyEpochEpoch,
    StudyEpochHistoryVO,
    StudyEpochSubType,
    StudyEpochType,
    StudyEpochVO,
)
from clinical_mdr_api.models.controlled_terminologies.ct_term_name import CTTermName
from clinical_mdr_api.models.study_selections.study_epoch import (
    StudyEpochOGM,
    StudyEpochOGMVer,
)
from common import config as settings
from common.exceptions import ValidationException


def get_ctlist_terms_by_name(
    code_list_name: str, effective_date: datetime.datetime | None = None
):
    if not effective_date:
        ctterm_name_match = "(:CTTermNameRoot)-[:LATEST_FINAL]->(ctnv:CTTermNameValue)"
    else:
        ctterm_name_match = """(ctnr:CTTermNameRoot)-[hv:HAS_VERSION]->(ctnv:CTTermNameValue)
            WHERE (hv.start_date<= datetime($effective_date) < datetime(hv.end_date)) OR (hv.end_date IS NULL AND (hv.start_date <= datetime($effective_date)))
        """
    cypher_query = f"""
        MATCH (:CTCodelistNameValue {{name: $code_list_name}})<-[:LATEST_FINAL]-(:CTCodelistNameRoot)<-[:HAS_NAME_ROOT]-
        (:CTCodelistRoot)-[:HAS_TERM]->
        (tr:CTTermRoot)-[:HAS_NAME_ROOT]->
        {ctterm_name_match}
        return tr.uid, ctnv.name
        """
    items, _ = db.cypher_query(
        cypher_query,
        {
            "code_list_name": code_list_name,
            "effective_date": (
                effective_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                if effective_date
                else None
            ),
        },
    )
    return {a[0]: a[1] for a in items}


class StudyEpochRepository:
    def __init__(self, author_id: str):
        self.author_id = author_id

    def fetch_ctlist(
        self, code_list_name: str, effective_date: datetime.datetime | None = None
    ):
        return get_ctlist_terms_by_name(code_list_name, effective_date=effective_date)

    def get_allowed_configs(self, effective_date: datetime.datetime | None = None):
        if effective_date:
            subtype_name_value_match = """MATCH (term_subtype_name_root)-[hv:HAS_VERSION]->(term_subtype_name_value:CTTermNameValue)
                WHERE (hv.start_date<= datetime($effective_date) < hv.end_date) OR (hv.end_date IS NULL AND (hv.start_date <= datetime($effective_date)))
            """
            type_name_value_match = """MATCH (term_type_name_root)-[hv_type:HAS_VERSION]->(term_type_name_value:CTTermNameValue)
                WHERE (hv_type.start_date<= datetime($effective_date) < hv_type.end_date) OR (hv_type.end_date IS NULL AND (hv_type.start_date <= datetime($effective_date)))
            """
        else:
            subtype_name_value_match = "MATCH (term_subtype_name_root:CTTermNameRoot)-[:LATEST_FINAL]->(term_subtype_name_value:CTTermNameValue)"
            type_name_value_match = "MATCH (term_type_name_root)-[:LATEST_FINAL]->(term_type_name_value:CTTermNameValue)"

        cypher_query = f"""
            MATCH (:CTCodelistNameValue {{name: $code_list_name}})<-[:LATEST_FINAL]-(:CTCodelistNameRoot)<-[:HAS_NAME_ROOT]
            -(:CTCodelistRoot)-[:HAS_TERM]->(term_subtype_root:CTTermRoot)-[:HAS_NAME_ROOT]->(term_subtype_name_root:CTTermNameRoot)
            {subtype_name_value_match}
            MATCH (term_subtype_root)-[:HAS_PARENT_TYPE]->(term_type_root:CTTermRoot)-
            [:HAS_NAME_ROOT]->(term_type_name_root)
            {type_name_value_match}

            return term_subtype_root.uid, term_subtype_name_value.name, term_type_root.uid, term_type_name_value.name
        """
        items, _ = db.cypher_query(
            cypher_query,
            {
                "code_list_name": settings.STUDY_EPOCH_SUBTYPE_NAME,
                "effective_date": (
                    effective_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    if effective_date
                    else None
                ),
            },
        )
        return items

    def get_basic_epoch(self, study_uid: str) -> str | None:
        cypher_query = """
        MATCH (study_root:StudyRoot {uid:$study_uid})-[:LATEST]->(:StudyValue)-[:HAS_STUDY_EPOCH]->(study_epoch:StudyEpoch)-[:HAS_EPOCH_SUB_TYPE]->(:CTTermRoot)-
        [:HAS_NAME_ROOT]->(:CTTermNameRoot)-[:HAS_VERSION]->(:CTTermNameValue {name:$basic_epoch_name})
        WHERE NOT exists((:Delete)-[:BEFORE]->(study_epoch))
        return study_epoch.uid
        """
        basic_visit, _ = db.cypher_query(
            cypher_query,
            {"basic_epoch_name": settings.BASIC_EPOCH_NAME, "study_uid": study_uid},
        )
        return basic_visit[0][0] if len(basic_visit) > 0 else None

    def find_all_epochs_by_study(
        self, study_uid: str, study_value_version: str | None = None
    ) -> list[StudyEpochVO]:
        if study_value_version:
            filters = {
                "study_value__has_version|version": study_value_version,
                "study_value__has_version__uid": study_uid,
            }
        else:
            filters = {"study_value__latest_value__uid": study_uid}

        return [
            self._from_neomodel_to_vo(
                study_epoch_ogm_input=StudyEpochOGM.from_orm(sas_node)
            )
            for sas_node in ListDistinct(
                StudyEpoch.nodes.fetch_relations(
                    "has_epoch",
                    "has_epoch_subtype",
                    "has_epoch_type",
                    "has_after__audit_trail",
                    Optional("has_duration_unit"),
                )
                .filter(**filters)
                .order_by("order")
                .resolve_subgraph()
            ).distinct()
        ]

    def epoch_specific_has_connected_design_cell(
        self, study_uid: str, epoch_uid: str
    ) -> bool:
        """
        Returns True if StudyEpoch with specified uid has connected at least one StudyDesignCell.
        :return:
        """

        sdc_node = (
            StudyEpoch.nodes.fetch_relations(
                "has_design_cell__study_value",
                "has_after",
                "has_after__audit_trail",
            )
            .filter(study_value__latest_value__uid=study_uid, uid=epoch_uid)
            .resolve_subgraph()
        )
        return len(sdc_node) > 0

    def find_by_uid(
        self, uid: str, study_uid: str, study_value_version: str | None = None
    ) -> StudyEpochVO:
        if study_value_version:
            filters = {
                "uid": uid,
                "study_value__has_version__uid": study_uid,
                "study_value__has_version|version": study_value_version,
            }
        else:
            filters = {
                "uid": uid,
                "study_value__latest_value__uid": study_uid,
            }

        epoch_node = ListDistinct(
            StudyEpoch.nodes.fetch_relations(
                "has_epoch",
                "has_epoch_subtype",
                "has_epoch_type",
                "has_after__audit_trail",
                "study_value__has_version",
                Optional("has_duration_unit"),
            )
            .filter(**filters)
            .resolve_subgraph()
        ).distinct()

        ValidationException.raise_if(
            len(epoch_node) > 1,
            msg=f"Found more than one StudyEpoch node with UID '{uid}'.",
        )
        ValidationException.raise_if(
            len(epoch_node) == 0, msg=f"The StudyEpoch with UID '{uid}' doesn't exist."
        )
        return self._from_neomodel_to_vo(
            study_epoch_ogm_input=StudyEpochOGM.from_orm(epoch_node[0])
        )

    def get_all_versions(
        self,
        uid: str,
        study_uid,
        get_ct_terms_for_epoch: Callable[[str], CTTermName],
        extract_multiple_version_study_standards_effective_date: Callable[
            [str], CTTermName
        ],
    ):
        selection_history: list[StudyEpochOGMVer] = [
            StudyEpochOGMVer.from_orm(se_node)
            for se_node in ListDistinct(
                StudyEpoch.nodes.fetch_relations(
                    "has_after__audit_trail",
                    "has_epoch",
                    "has_epoch_subtype",
                    "has_epoch_type",
                    Optional("has_duration_unit"),
                    Optional("has_before"),
                    Optional("has_study_visit"),
                )
                .filter(uid=uid, has_after__audit_trail__uid=study_uid)
                .resolve_subgraph()
            ).distinct()
        ]
        # Extract start dates from the selection history
        start_dates = [history.start_date for history in selection_history]

        # Extract effective dates for each version based on the start dates
        effective_dates = extract_multiple_version_study_standards_effective_date(
            study_uid=study_uid, list_of_start_dates=start_dates
        )
        return sorted(
            [
                self._from_neomodel_to_history_vo(
                    study_epoch_ogm_input=selection_version,
                    get_ct_terms_for_epoch=get_ct_terms_for_epoch,
                    effective_date=effective_date,
                )
                for selection_version, effective_date in zip(
                    selection_history, effective_dates
                )
            ],
            key=lambda item: item.start_date,
            reverse=True,
        )

    def _from_neomodel_to_vo(self, study_epoch_ogm_input: StudyEpochOGM):
        return StudyEpochVO(
            uid=study_epoch_ogm_input.uid,
            study_uid=study_epoch_ogm_input.study_uid,
            start_rule=study_epoch_ogm_input.start_rule,
            end_rule=study_epoch_ogm_input.end_rule,
            description=study_epoch_ogm_input.description,
            epoch=study_epoch.StudyEpochEpoch[study_epoch_ogm_input.epoch],
            subtype=study_epoch.StudyEpochSubType[study_epoch_ogm_input.epoch_subtype],
            epoch_type=study_epoch.StudyEpochType[study_epoch_ogm_input.epoch_type],
            order=study_epoch_ogm_input.order,
            status=StudyStatus(study_epoch_ogm_input.status),
            start_date=study_epoch_ogm_input.start_date,
            author_id=self.author_id,
            color_hash=study_epoch_ogm_input.color_hash,
        )

    def _from_neomodel_to_history_vo(
        self,
        study_epoch_ogm_input: StudyEpochOGMVer,
        get_ct_terms_for_epoch: Callable[[str], CTTermName] = None,
        effective_date: datetime.datetime = None,
    ):
        history_study_epoch_epoch = None
        if get_ct_terms_for_epoch:
            epoch_term: CTTermName = get_ct_terms_for_epoch(
                study_epoch_ogm_input.epoch, at_specific_date=effective_date
            )
            history_study_epoch_epoch = copy.deepcopy(StudyEpochEpoch)
            history_study_epoch_epoch.clear()
            history_study_epoch_epoch.update([(epoch_term.term_uid, epoch_term)])

            epoch_subtype_term: CTTermName = get_ct_terms_for_epoch(
                study_epoch_ogm_input.epoch_subtype, at_specific_date=effective_date
            )
            history_study_epoch_subtype = copy.deepcopy(StudyEpochSubType)
            history_study_epoch_subtype.clear()
            history_study_epoch_subtype.update(
                [(epoch_subtype_term.term_uid, epoch_subtype_term)]
            )

            epoch_type_term: CTTermName = get_ct_terms_for_epoch(
                study_epoch_ogm_input.epoch_type, at_specific_date=effective_date
            )
            history_study_epoch_type = copy.deepcopy(StudyEpochType)
            history_study_epoch_type.clear()
            history_study_epoch_type.update(
                [(epoch_type_term.term_uid, epoch_type_term)]
            )

        return StudyEpochHistoryVO(
            uid=study_epoch_ogm_input.uid,
            study_uid=study_epoch_ogm_input.study_uid,
            start_rule=study_epoch_ogm_input.start_rule,
            end_rule=study_epoch_ogm_input.end_rule,
            description=study_epoch_ogm_input.description,
            epoch=(
                history_study_epoch_epoch[epoch_term.term_uid]
                if history_study_epoch_epoch
                else study_epoch.StudyEpochEpoch[study_epoch_ogm_input.epoch]
            ),
            subtype=(
                history_study_epoch_subtype[epoch_subtype_term.term_uid]
                if history_study_epoch_subtype
                else study_epoch.StudyEpochSubType[study_epoch_ogm_input.epoch_subtype]
            ),
            epoch_type=(
                history_study_epoch_type[epoch_type_term.term_uid]
                if history_study_epoch_type
                else study_epoch.StudyEpochType[study_epoch_ogm_input.epoch_type]
            ),
            order=study_epoch_ogm_input.order,
            status=StudyStatus(study_epoch_ogm_input.status),
            start_date=study_epoch_ogm_input.start_date,
            author_id=self.author_id,
            color_hash=study_epoch_ogm_input.color_hash,
            study_visit_count=len(
                {sv.uid for sv in study_epoch_ogm_input.study_visits.all()}
            ),
            change_type=study_epoch_ogm_input.change_type,
            end_date=study_epoch_ogm_input.end_date,
        )

    def save(self, epoch: StudyEpochVO):
        # if exists
        if epoch.uid is not None:
            return self._update(epoch, create=False)
        # if has to be created
        return self._update(epoch, create=True)

    def _update(self, item: StudyEpochVO, create: bool = False):
        study_root = StudyRoot.nodes.get(uid=item.study_uid)
        study_value: StudyValue = study_root.latest_value.get_or_none()
        ValidationException.raise_if(
            study_value is None, msg="Study doesn't have draft version."
        )
        if not create:
            previous_item = study_value.has_study_epoch.get(uid=item.uid)
        new_study_epoch = StudyEpoch(
            uid=item.uid,
            accepted_version=item.accepted_version,
            order=item.order,
            name=item.name,
            short_name=item.short_name,
            description=item.description,
            start_rule=item.start_rule,
            end_rule=item.end_rule,
            color_hash=item.color_hash,
            status=item.status.value,
        )
        if item.uid is not None:
            new_study_epoch.uid = item.uid
        new_study_epoch.save()
        if item.uid is None:
            item.uid = new_study_epoch.uid
        ct_epoch_subtype = CTTermRoot.nodes.get(uid=item.subtype.term_uid)
        new_study_epoch.has_epoch_subtype.connect(ct_epoch_subtype)
        ct_epoch_type = CTTermRoot.nodes.get(uid=item.epoch_type.term_uid)
        new_study_epoch.has_epoch_type.connect(ct_epoch_type)
        ct_epoch = CTTermRoot.nodes.get(uid=item.epoch.term_uid)
        new_study_epoch.has_epoch.connect(ct_epoch)
        if create:
            new_study_epoch.study_value.connect(study_value)
            self.manage_versioning_create(
                study_root=study_root, item=item, new_item=new_study_epoch
            )
        else:
            if item.is_deleted:
                self.manage_versioning_delete(
                    study_root=study_root,
                    item=item,
                    # pylint: disable=possibly-used-before-assignment
                    previous_item=previous_item,
                    new_item=new_study_epoch,
                )
            else:
                new_study_epoch.study_value.connect(study_value)
                self.manage_versioning_update(
                    study_root=study_root,
                    item=item,
                    previous_item=previous_item,
                    new_item=new_study_epoch,
                )
            manage_previous_connected_study_selection_relationships(
                previous_item=previous_item,
                study_value_node=study_value,
                new_item=new_study_epoch,
                exclude_study_selection_relationships=[],
            )

        return item

    def manage_versioning_create(
        self, study_root: StudyRoot, item: StudyEpochVO, new_item: StudyEpoch
    ):
        action = Create(
            date=datetime.datetime.now(datetime.timezone.utc),
            status=item.status.value,
            author_id=item.author_id,
        )
        action.save()
        action.has_after.connect(new_item)
        study_root.audit_trail.connect(action)

    def manage_versioning_update(
        self,
        study_root: StudyRoot,
        item: StudyEpochVO,
        previous_item: StudyEpoch,
        new_item: StudyEpoch,
    ):
        action = Edit(
            date=datetime.datetime.now(datetime.timezone.utc),
            status=item.status.value,
            author_id=item.author_id,
        )
        action.save()
        action.has_before.connect(previous_item)
        action.has_after.connect(new_item)
        study_root.audit_trail.connect(action)

    def manage_versioning_delete(
        self,
        study_root: StudyRoot,
        item: StudyEpochVO,
        previous_item: StudyEpoch,
        new_item: StudyEpoch,
    ):
        action = Delete(
            date=datetime.datetime.now(datetime.timezone.utc),
            status=item.status.value,
            author_id=item.author_id,
        )
        action.save()
        action.has_before.connect(previous_item)
        action.has_after.connect(new_item)
        study_root.audit_trail.connect(action)
