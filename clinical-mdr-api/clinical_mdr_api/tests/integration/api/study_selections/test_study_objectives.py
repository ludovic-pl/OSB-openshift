"""
Tests for /studies/{study_uid}/study-objectives endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import logging
from datetime import datetime, timezone
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.domain_repositories.models.syntax import (
    ObjectiveRoot,
    ObjectiveTemplateRoot,
)
from clinical_mdr_api.main import app
from clinical_mdr_api.models.controlled_terminologies import ct_term
from clinical_mdr_api.models.study_selections.study import Study
from clinical_mdr_api.tests.integration.api.study_selections.utils import (
    ct_term_retrieval_at_date_test_common,
)
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_TERM_NAME_CYPHER,
    STARTUP_STUDY_OBJECTIVE_CYPHER,
)
from clinical_mdr_api.tests.integration.utils.factory_controlled_terminology import (
    create_codelist,
    get_catalogue_name_library_name,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from clinical_mdr_api.tests.utils.checks import assert_response_status_code
from common import config as settings

log = logging.getLogger(__name__)

study: Study
study_objective_uid: str
initial_ct_term_study_standard_test: ct_term.CTTerm


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "studyobjectiveapi"
    inject_and_clear_db(db_name)

    global study
    study = inject_base_data()

    db.cypher_query(STARTUP_CT_TERM_NAME_CYPHER)
    db.cypher_query(STARTUP_STUDY_OBJECTIVE_CYPHER)
    ObjectiveTemplateRoot.generate_node_uids_if_not_present()
    ObjectiveRoot.generate_node_uids_if_not_present()

    catalogue_name, library_name = get_catalogue_name_library_name(use_test_utils=True)
    # Create a study selection
    ct_term_codelist_name = settings.STUDY_OBJECTIVE_LEVEL_NAME
    ct_term_name = ct_term_codelist_name + " Name For StudyStandardVersioning test"
    ct_term_codelist = create_codelist(
        ct_term_codelist_name, ct_term_codelist_name, catalogue_name, library_name
    )
    ct_term_start_date = datetime(2020, 3, 25, tzinfo=timezone.utc)

    global initial_ct_term_study_standard_test
    initial_ct_term_study_standard_test = TestUtils.create_ct_term(
        codelist_uid=ct_term_codelist.codelist_uid,
        name_submission_value=ct_term_name,
        sponsor_preferred_name=ct_term_name,
        order=2,
        catalogue_name=catalogue_name,
        library_name=library_name,
        effective_date=ct_term_start_date,
        approve=True,
    )

    cdisc_package_name = "SDTM CT 2020-03-27"
    TestUtils.create_ct_package(
        catalogue=catalogue_name,
        name=cdisc_package_name,
        approve_elements=False,
        effective_date=datetime(2020, 3, 27, tzinfo=timezone.utc),
    )
    # patch the date of the latest HAS_VERSION FINAL relationship so it can be detected by the selected study_standard_Version
    params = {
        "uid": initial_ct_term_study_standard_test.term_uid,
        "date": datetime(2020, 3, 26, tzinfo=timezone.utc),
    }
    db.cypher_query(
        """
                    MATCH (n)-[:HAS_NAME_ROOT]-(ct_name:CTTermNameRoot)-[has_version:HAS_VERSION]-(val) 
                    where 
                        n.uid =$uid AND EXISTS((ct_name)-[:LATEST]-(val)) 
                        AND has_version.status ='Final' 
                    SET has_version.start_date = $date
                """,
        params=params,
    )

    yield


def test_objective_modify_actions_on_locked_study(api_client):
    global study_objective_uid

    response = api_client.post(
        f"/studies/{study.uid}/study-objectives",
        json={
            "objective_uid": "Objective_000001",
            "objective_level_uid": "term_root_final",
        },
    )
    res = response.json()
    assert_response_status_code(response, 201)
    assert res["objective_level"]["term_uid"] == "term_root_final"
    study_objective_uid = res["study_objective_uid"]

    # get all objectives
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/audit-trail/",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    old_res = res

    # update study title to be able to lock it
    response = api_client.patch(
        f"/studies/{study.uid}",
        json={"current_metadata": {"study_description": {"study_title": "new title"}}},
    )
    assert_response_status_code(response, 200)

    # Lock
    response = api_client.post(
        f"/studies/{study.uid}/locks",
        json={"change_description": "Lock 1"},
    )
    assert_response_status_code(response, 201)

    response = api_client.post(
        f"/studies/{study.uid}/study-objectives",
        json={"objective_uid": "Objective_000002"},
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["message"] == f"Study with UID '{study.uid}' is locked."
    # edit objective
    response = api_client.patch(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}",
        json={"new_order": 2},
    )
    assert_response_status_code(response, 400)
    res = response.json()
    assert res["message"] == f"Study with UID '{study.uid}' is locked."

    # get all history when was locked
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/audit-trail/",
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert old_res == res

    # test cannot delete
    response = api_client.delete(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}"
    )
    assert_response_status_code(response, 400)
    assert response.json()["message"] == f"Study with UID '{study.uid}' is locked."


def test_study_objective_with_objective_level_relationship(api_client):
    # get specific study objective
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res["objective_level"]["term_uid"] == "term_root_final"
    before_unlock = res

    # get study objective headers
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/headers?field_name=objective_level.term_uid",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res == ["term_root_final"]

    # Unlock
    response = api_client.delete(f"/studies/{study.uid}/locks")
    assert_response_status_code(response, 200)

    # edit study objective
    response = api_client.patch(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}",
        json={
            "objective_uid": "Objective_000001",
            "objective_level_uid": "term_root_final5",
        },
    )
    res = response.json()
    assert res["objective_level"]["term_uid"] == "term_root_final5"
    assert_response_status_code(response, 200)

    # get all study objectives of a specific study version
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives?study_value_version=1",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    before_unlock["study_version"] = mock.ANY
    assert res["items"][0] == before_unlock

    # get specific study objective of a specific study version
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}?study_value_version=1",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res == before_unlock

    # get study objective headers of specific study version
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/headers?field_name=objective_level.term_uid&study_value_version=1",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res == ["term_root_final"]

    # get all study objectives
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res["items"][0]["objective_level"]["term_uid"] == "term_root_final5"

    # get specific study objective
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res["objective_level"]["term_uid"] == "term_root_final5"

    # get study objective headers
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/headers?field_name=objective_level.term_uid",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res == ["term_root_final5"]


@pytest.mark.parametrize(
    "export_format",
    [
        pytest.param("text/csv"),
        pytest.param("text/xml"),
        pytest.param(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    ],
)
def test_get_study_objectives_csv_xml_excel(api_client, export_format):
    url = f"/studies/{study.uid}/study-objectives"
    exported_data = TestUtils.verify_exported_data_format(
        api_client, export_format, url
    )
    if export_format == "text/csv":
        assert "study_version" in str(exported_data.read())
        assert "LATEST" in str(exported_data.read())


def test_update_library_items_of_relationship_to_value_nodes(api_client):
    """
    Test that the StudyObjective selection remains connected to the specific Value node even if the Value node is not latest anymore.

    StudyObjective is connected to value nodes:
    - ObjectiveValue
    """
    # get specific study objective
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    library_template_objective_uid = res["objective"]["template"]["uid"]
    initial_objective_name = res["objective"]["name"]

    text_value_2_name = "2ndname"
    # change objective name and approve the version
    response = api_client.post(
        f"/objective-templates/{library_template_objective_uid}/versions",
        json={
            "change_description": "test change",
            "name": text_value_2_name,
            "guidance_text": "don't know",
        },
    )
    response = api_client.post(
        f"/objective-templates/{library_template_objective_uid}/approvals?cascade=true"
    )

    # check that the Library item has been changed
    response = api_client.get(f"/objective-templates/{library_template_objective_uid}")
    res = response.json()
    assert_response_status_code(response, 200)
    assert res["name"] == text_value_2_name

    # check that the StudySelection StudyObjective hasn't been updated
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res["objective"]["name"] == initial_objective_name

    # check that the StudySelection can approve the current version
    response = api_client.post(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}/accept-version",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res["accepted_version"] is True
    assert res["objective"]["name"] == initial_objective_name
    assert res["latest_objective"]["name"] == text_value_2_name

    # get all objectives
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/audit-trail/",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    counting_before_sync = len(res)

    # check that the StudySelection's objective can be updated to the LATEST
    response = api_client.post(
        f"/studies/{study.uid}/study-objectives/{study_objective_uid}/sync-latest-version",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert res["objective"]["name"] == text_value_2_name

    # get all objectives
    response = api_client.get(
        f"/studies/{study.uid}/study-objectives/audit-trail/",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert len(res) == counting_before_sync + 1


def test_study_objective_version_selecting_ct_package(api_client):
    """change the name of a CTTerm, and verify that the study selection is still set to the old name of the CTTerm when the Sponsor Standard version is set"""
    study_selection_breadcrumb = "study-objectives"
    study_selection_ctterm_uid_input_key = "objective_level_uid"
    study_selection_ctterm_keys = "objective_level"
    study_selection_ctterm_uid_key = "term_uid"
    study_selection_ctterm_name_key = "sponsor_preferred_name"
    study_for_ctterm_versioning = TestUtils.create_study()
    response = api_client.post(
        f"/studies/{study_for_ctterm_versioning.uid}/{study_selection_breadcrumb}",
        json={
            "objective_uid": "Objective_000001",
            study_selection_ctterm_uid_input_key: "term_root_final",
        },
    )
    res = response.json()
    assert_response_status_code(response, 201)
    study_selection_uid_study_standard_test = res["study_objective_uid"]
    assert res["order"] == 1
    assert (
        res[study_selection_ctterm_keys][study_selection_ctterm_uid_key]
        == "term_root_final"
    )

    # edit ctterm
    new_ctterm_name = "new ctterm name"
    ctterm_uid = initial_ct_term_study_standard_test.term_uid
    # change ctterm name and approve the version
    response = api_client.post(
        f"/ct/terms/{ctterm_uid}/names/versions",
    )
    assert_response_status_code(response, 201)
    response = api_client.patch(
        f"/ct/terms/{ctterm_uid}/names",
        json={
            "sponsor_preferred_name": new_ctterm_name,
            "sponsor_preferred_name_sentence_case": new_ctterm_name,
            "change_description": "string",
        },
    )
    response = api_client.post(f"/ct/terms/{ctterm_uid}/names/approvals")
    assert_response_status_code(response, 201)

    # get study selection with ctterm latest
    response = api_client.patch(
        f"/studies/{study_for_ctterm_versioning.uid}/{study_selection_breadcrumb}/{study_selection_uid_study_standard_test}",
        json={
            study_selection_ctterm_uid_input_key: ctterm_uid,
        },
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert (
        res[study_selection_ctterm_keys][study_selection_ctterm_uid_key] == ctterm_uid
    )
    assert (
        res[study_selection_ctterm_keys][study_selection_ctterm_name_key]
        == new_ctterm_name
    )

    # get ct_packages
    response = api_client.get(
        "/ct/packages",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    ct_package_uid = res[0]["uid"]

    # create study standard version
    response = api_client.post(
        f"/studies/{study_for_ctterm_versioning.uid}/study-standard-versions",
        json={
            "ct_package_uid": ct_package_uid,
        },
    )
    res = response.json()
    assert_response_status_code(response, 201)
    assert res["ct_package"]["uid"] == ct_package_uid

    # get study selection with previous ctterm
    response = api_client.get(
        f"/studies/{study_for_ctterm_versioning.uid}/{study_selection_breadcrumb}/{study_selection_uid_study_standard_test}",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert (
        res[study_selection_ctterm_keys][study_selection_ctterm_uid_key] == ctterm_uid
    )
    assert (
        res[study_selection_ctterm_keys][study_selection_ctterm_name_key]
        == initial_ct_term_study_standard_test.sponsor_preferred_name
    )

    # edit objective
    response = api_client.patch(
        f"/studies/{study_for_ctterm_versioning.uid}/{study_selection_breadcrumb}/{study_selection_uid_study_standard_test}",
        json={
            "name": "New_Objective_Name_1",
        },
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert (
        res[study_selection_ctterm_keys][study_selection_ctterm_name_key]
        == initial_ct_term_study_standard_test.sponsor_preferred_name
    )

    # get versions of objective
    response = api_client.get(
        f"/studies/{study_for_ctterm_versioning.uid}/{study_selection_breadcrumb}/{study_selection_uid_study_standard_test}/audit-trail/",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert (
        res[0][study_selection_ctterm_keys][study_selection_ctterm_name_key]
        == initial_ct_term_study_standard_test.sponsor_preferred_name
    )
    assert (
        res[1][study_selection_ctterm_keys][study_selection_ctterm_name_key]
        == new_ctterm_name
    )

    # get all objectives
    response = api_client.get(
        f"/studies/{study_for_ctterm_versioning.uid}/{study_selection_breadcrumb}/audit-trail/",
    )
    res = response.json()
    assert_response_status_code(response, 200)
    assert (
        res[0][study_selection_ctterm_keys][study_selection_ctterm_name_key]
        == initial_ct_term_study_standard_test.sponsor_preferred_name
    )
    assert (
        res[1][study_selection_ctterm_keys][study_selection_ctterm_name_key]
        == new_ctterm_name
    )


def test_study_objective_ct_term_retrieval_at_date(api_client):
    """
    Test that any CT Term name fetched in the context of a study selection either:
    * Matches the date of the Study Standard version when available
    * Or the latest final version is returned
    The study selection return model includes a queried_effective_data property to verify this
    """

    study_for_queried_effective_date = TestUtils.create_study()
    study_selection_breadcrumb = "study-objectives"
    study_selection_ctterm_keys = "objective_level"
    study_selection_ctterm_uid_input_key = "objective_level_uid"

    # Create selection
    response = api_client.post(
        f"/studies/{study_for_queried_effective_date.uid}/{study_selection_breadcrumb}",
        json={
            "objective_uid": "Objective_000001",
            study_selection_ctterm_uid_input_key: "term_root_final",
        },
    )
    res = response.json()
    assert_response_status_code(response, 201)
    assert res[study_selection_ctterm_keys]["queried_effective_date"] is None
    assert res[study_selection_ctterm_keys]["date_conflict"] is False
    study_selection_uid_study_standard_test = res["study_objective_uid"]

    ct_term_retrieval_at_date_test_common(
        api_client,
        study_selection_breadcrumb=study_selection_breadcrumb,
        study_selection_ctterm_uid_input_key=study_selection_ctterm_uid_input_key,
        study_selection_ctterm_keys=study_selection_ctterm_keys,
        study_for_queried_effective_date=study_for_queried_effective_date,
        initial_ct_term_study_standard_test=initial_ct_term_study_standard_test,
        study_selection_uid_study_standard_test=study_selection_uid_study_standard_test,
    )
