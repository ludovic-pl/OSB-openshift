# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.domain_repositories.models.syntax import (
    ObjectiveRoot,
    ObjectiveTemplateRoot,
)
from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_TERM_NAME_CYPHER,
    STARTUP_STUDY_OBJECTIVE_CYPHER,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.study.selection.objective")
    db.cypher_query(STARTUP_CT_TERM_NAME_CYPHER)
    db.cypher_query(STARTUP_STUDY_OBJECTIVE_CYPHER)
    ObjectiveTemplateRoot.generate_node_uids_if_not_present()
    ObjectiveRoot.generate_node_uids_if_not_present()

    yield

    drop_db("old.json.test.study.selection.objective")


def test_getting_empty_list5(api_client):
    response = api_client.get("/studies/study_root/study-objectives")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"] == []
    assert res["total"] == 0


def test_getting_empty_list_for_all_studies3(api_client):
    response = api_client.get("/study-objectives")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res == {"items": [], "page": 1, "size": 10, "total": 0}


def test_adding_selection11(api_client):
    data = {
        "objective_uid": "Objective_000001",
        "objective_level_uid": "term_root_final",
    }
    response = api_client.post("/studies/study_root/study-objectives", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["study_version"]
    assert res["study_objective_uid"] == "StudyObjective_000001"
    assert res["order"] == 1
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["accepted_version"] is False
    assert res["study_uid"] == "study_root"
    assert res["objective_level"]["term_uid"] == "term_root_final"
    assert res["objective_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["objective_level"]["codelists"]) == 1
    assert res["objective_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res["objective_level"]["codelists"][0]["order"] == 1
    assert res["objective_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res["objective_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res["objective_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["objective_level"]["library_name"] == "Sponsor"
    assert res["objective_level"]["start_date"]
    assert res["objective_level"]["end_date"] is None
    assert res["objective_level"]["status"] == "Final"
    assert res["objective_level"]["version"] == "1.0"
    assert res["objective_level"]["change_description"] == "Approved version"
    assert res["objective_level"]["author_username"] == "unknown-user@example.com"
    assert res["objective_level"]["queried_effective_date"] is None
    assert res["objective_level"]["date_conflict"] is False
    assert res["objective_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["latest_objective"] is None
    assert res["objective"]["uid"] == "Objective_000001"
    assert res["objective"]["name"] == "objective_1"
    assert res["objective"]["name_plain"] == "objective_1"
    assert res["objective"]["start_date"]
    assert res["objective"]["end_date"] is None
    assert res["objective"]["study_count"] == 0
    assert res["objective"]["status"] == "Final"
    assert res["objective"]["version"] == "1.0"
    assert res["objective"]["change_description"] == "Approved version"
    assert res["objective"]["author_username"] == "unknown-user@example.com"
    assert res["objective"]["possible_actions"] == ["inactivate"]
    assert res["objective"]["template"]["name"] == "objective_1"
    assert res["objective"]["template"]["name_plain"] == "objective_1"
    assert res["objective"]["template"]["uid"] == "ObjectiveTemplate_000001"
    assert res["objective"]["template"]["sequence_id"] == "O1"
    assert res["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["objective"]["parameter_terms"]) == 0
    assert res["objective"]["library"]["name"] == "Sponsor"
    assert res["objective"]["library"]["is_editable"] is True
    assert res["author_username"] == "unknown-user@example.com"
    assert res["endpoint_count"] == 0


def test_get_all_list_non_empty5(api_client):
    response = api_client.get("/studies/study_root/study-objectives")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["study_version"]
    assert res["items"][0]["study_objective_uid"] == "StudyObjective_000001"
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["project_number"] == "123"
    assert res["items"][0]["project_name"] == "Project ABC"
    assert res["items"][0]["accepted_version"] is False
    assert res["items"][0]["study_uid"] == "study_root"
    assert res["items"][0]["objective_level"]["term_uid"] == "term_root_final"
    assert res["items"][0]["objective_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["items"][0]["objective_level"]["codelists"]) == 1
    assert (
        res["items"][0]["objective_level"]["codelists"][0]["codelist_uid"]
        == "editable_cr"
    )
    assert res["items"][0]["objective_level"]["codelists"][0]["order"] == 1
    assert (
        res["items"][0]["objective_level"]["codelists"][0]["library_name"] == "Sponsor"
    )
    assert (
        res["items"][0]["objective_level"]["sponsor_preferred_name"]
        == "term_value_name1"
    )
    assert (
        res["items"][0]["objective_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["items"][0]["objective_level"]["library_name"] == "Sponsor"
    assert res["items"][0]["objective_level"]["start_date"]
    assert res["items"][0]["objective_level"]["end_date"] is None
    assert res["items"][0]["objective_level"]["status"] == "Final"
    assert res["items"][0]["objective_level"]["version"] == "1.0"
    assert (
        res["items"][0]["objective_level"]["change_description"] == "Approved version"
    )
    assert (
        res["items"][0]["objective_level"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["objective_level"]["queried_effective_date"] is None
    assert res["items"][0]["objective_level"]["date_conflict"] is False
    assert res["items"][0]["objective_level"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert res["items"][0]["start_date"]
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["objective"]["uid"] == "Objective_000001"
    assert res["items"][0]["objective"]["name"] == "objective_1"
    assert res["items"][0]["objective"]["name_plain"] == "objective_1"
    assert res["items"][0]["objective"]["start_date"]
    assert res["items"][0]["objective"]["study_count"] == 0
    assert res["items"][0]["objective"]["end_date"] is None
    assert res["items"][0]["objective"]["status"] == "Final"
    assert res["items"][0]["objective"]["version"] == "1.0"
    assert res["items"][0]["objective"]["change_description"] == "Approved version"
    assert res["items"][0]["objective"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["objective"]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["objective"]["template"]["name"] == "objective_1"
    assert res["items"][0]["objective"]["template"]["name_plain"] == "objective_1"
    assert res["items"][0]["objective"]["template"]["uid"] == "ObjectiveTemplate_000001"
    assert res["items"][0]["objective"]["template"]["sequence_id"] == "O1"
    assert res["items"][0]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["items"][0]["objective"]["parameter_terms"]) == 0
    assert res["items"][0]["objective"]["library"]["name"] == "Sponsor"
    assert res["items"][0]["objective"]["library"]["is_editable"] is True
    assert res["items"][0]["latest_objective"] is None
    assert res["items"][0]["endpoint_count"] == 0
    assert res["total"] == 0


def test_get_all_for_all_studies3(api_client):
    response = api_client.get("/study-objectives")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["study_version"]
    assert res["items"][0]["study_objective_uid"] == "StudyObjective_000001"
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["project_number"] == "123"
    assert res["items"][0]["project_name"] == "Project ABC"
    assert res["items"][0]["accepted_version"] is False
    assert res["items"][0]["study_uid"] == "study_root"
    assert res["items"][0]["objective_level"]["term_uid"] == "term_root_final"
    assert res["items"][0]["objective_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["items"][0]["objective_level"]["codelists"]) == 1
    assert (
        res["items"][0]["objective_level"]["codelists"][0]["codelist_uid"]
        == "editable_cr"
    )
    assert res["items"][0]["objective_level"]["codelists"][0]["order"] == 1
    assert (
        res["items"][0]["objective_level"]["codelists"][0]["library_name"] == "Sponsor"
    )
    assert (
        res["items"][0]["objective_level"]["sponsor_preferred_name"]
        == "term_value_name1"
    )
    assert (
        res["items"][0]["objective_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["items"][0]["objective_level"]["library_name"] == "Sponsor"
    assert res["items"][0]["objective_level"]["start_date"]
    assert res["items"][0]["objective_level"]["end_date"] is None
    assert res["items"][0]["objective_level"]["status"] == "Final"
    assert res["items"][0]["objective_level"]["version"] == "1.0"
    assert (
        res["items"][0]["objective_level"]["change_description"] == "Approved version"
    )
    assert (
        res["items"][0]["objective_level"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["objective_level"]["queried_effective_date"] is None
    assert res["items"][0]["objective_level"]["date_conflict"] is False
    assert res["items"][0]["objective_level"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["objective"]["uid"] == "Objective_000001"
    assert res["items"][0]["objective"]["name"] == "objective_1"
    assert res["items"][0]["objective"]["name_plain"] == "objective_1"
    assert res["items"][0]["objective"]["start_date"]
    assert res["items"][0]["objective"]["end_date"] is None
    assert res["items"][0]["objective"]["study_count"] == 0
    assert res["items"][0]["objective"]["status"] == "Final"
    assert res["items"][0]["objective"]["version"] == "1.0"
    assert res["items"][0]["objective"]["change_description"] == "Approved version"
    assert res["items"][0]["objective"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["objective"]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["objective"]["template"]["name"] == "objective_1"
    assert res["items"][0]["objective"]["template"]["name_plain"] == "objective_1"
    assert res["items"][0]["objective"]["template"]["uid"] == "ObjectiveTemplate_000001"
    assert res["items"][0]["objective"]["template"]["sequence_id"] == "O1"
    assert res["items"][0]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["items"][0]["objective"]["parameter_terms"]) == 0
    assert res["items"][0]["objective"]["library"]["name"] == "Sponsor"
    assert res["items"][0]["objective"]["library"]["is_editable"] is True
    assert res["items"][0]["latest_objective"] is None
    assert res["items"][0]["endpoint_count"] == 0


def test_add_selection_2_no_objective_level_set(api_client):
    data = {"objective_uid": "Objective_000002"}
    response = api_client.post("/studies/study_root/study-objectives", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["study_version"]
    assert res["study_objective_uid"] == "StudyObjective_000002"
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["accepted_version"] is False
    assert res["study_uid"] == "study_root"
    assert res["objective_level"] is None
    assert res["latest_objective"] is None
    assert res["objective"]["uid"] == "Objective_000002"
    assert res["objective"]["name"] == "objective_2"
    assert res["objective"]["name_plain"] == "objective_2"
    assert res["objective"]["start_date"]
    assert res["objective"]["end_date"] is None
    assert res["objective"]["study_count"] == 0
    assert res["objective"]["status"] == "Final"
    assert res["objective"]["version"] == "1.0"
    assert res["objective"]["change_description"] == "Approved version"
    assert res["objective"]["author_username"] == "unknown-user@example.com"
    assert res["objective"]["possible_actions"] == ["inactivate"]
    assert res["objective"]["template"]["name"] == "objective_2"
    assert res["objective"]["template"]["name_plain"] == "objective_2"
    assert res["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res["objective"]["template"]["sequence_id"] == "O22"
    assert res["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["objective"]["parameter_terms"]) == 0
    assert res["objective"]["library"]["name"] == "Sponsor"
    assert res["objective"]["library"]["is_editable"] is True
    assert res["author_username"] == "unknown-user@example.com"
    assert res["endpoint_count"] == 0


def test_check_list_has_two(api_client):
    response = api_client.get("/studies/study_root/study-objectives")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["study_version"]
    assert res["items"][0]["study_objective_uid"] == "StudyObjective_000001"
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["project_number"] == "123"
    assert res["items"][0]["project_name"] == "Project ABC"
    assert res["items"][0]["accepted_version"] is False
    assert res["items"][0]["study_uid"] == "study_root"
    assert res["items"][0]["objective_level"]["term_uid"] == "term_root_final"
    assert res["items"][0]["objective_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["items"][0]["objective_level"]["codelists"]) == 1
    assert (
        res["items"][0]["objective_level"]["codelists"][0]["codelist_uid"]
        == "editable_cr"
    )
    assert res["items"][0]["objective_level"]["codelists"][0]["order"] == 1
    assert (
        res["items"][0]["objective_level"]["codelists"][0]["library_name"] == "Sponsor"
    )
    assert (
        res["items"][0]["objective_level"]["sponsor_preferred_name"]
        == "term_value_name1"
    )
    assert (
        res["items"][0]["objective_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["items"][0]["objective_level"]["library_name"] == "Sponsor"
    assert res["items"][0]["objective_level"]["start_date"]
    assert res["items"][0]["objective_level"]["end_date"] is None
    assert res["items"][0]["objective_level"]["status"] == "Final"
    assert res["items"][0]["objective_level"]["version"] == "1.0"
    assert (
        res["items"][0]["objective_level"]["change_description"] == "Approved version"
    )
    assert (
        res["items"][0]["objective_level"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["objective_level"]["queried_effective_date"] is None
    assert res["items"][0]["objective_level"]["date_conflict"] is False
    assert res["items"][0]["objective_level"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert res["items"][0]["objective"]["uid"] == "Objective_000001"
    assert res["items"][0]["objective"]["name"] == "objective_1"
    assert res["items"][0]["objective"]["name_plain"] == "objective_1"
    assert res["items"][0]["objective"]["start_date"]
    assert res["items"][0]["objective"]["end_date"] is None
    assert res["items"][0]["objective"]["status"] == "Final"
    assert res["items"][0]["objective"]["study_count"] == 0
    assert res["items"][0]["objective"]["version"] == "1.0"
    assert res["items"][0]["objective"]["change_description"] == "Approved version"
    assert res["items"][0]["objective"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["objective"]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["objective"]["template"]["name"] == "objective_1"
    assert res["items"][0]["objective"]["template"]["name_plain"] == "objective_1"
    assert res["items"][0]["objective"]["template"]["uid"] == "ObjectiveTemplate_000001"
    assert res["items"][0]["objective"]["template"]["sequence_id"] == "O1"
    assert res["items"][0]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["items"][0]["objective"]["parameter_terms"]) == 0
    assert res["items"][0]["objective"]["library"]["name"] == "Sponsor"
    assert res["items"][0]["objective"]["library"]["is_editable"] is True
    assert res["items"][0]["start_date"]
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["latest_objective"] is None
    assert res["items"][0]["endpoint_count"] == 0
    assert res["items"][1]["study_version"]
    assert res["items"][1]["study_objective_uid"] == "StudyObjective_000002"
    assert res["items"][1]["order"] == 2
    assert res["items"][1]["project_number"] == "123"
    assert res["items"][1]["project_name"] == "Project ABC"
    assert res["items"][1]["accepted_version"] is False
    assert res["items"][1]["study_uid"] == "study_root"
    assert res["items"][1]["objective_level"] is None
    assert res["items"][1]["latest_objective"] is None
    assert res["items"][1]["objective"]["uid"] == "Objective_000002"
    assert res["items"][1]["objective"]["name"] == "objective_2"
    assert res["items"][1]["objective"]["name_plain"] == "objective_2"
    assert res["items"][1]["objective"]["start_date"]
    assert res["items"][1]["objective"]["end_date"] is None
    assert res["items"][1]["objective"]["status"] == "Final"
    assert res["items"][1]["objective"]["study_count"] == 0
    assert res["items"][1]["objective"]["version"] == "1.0"
    assert res["items"][1]["objective"]["change_description"] == "Approved version"
    assert res["items"][1]["objective"]["author_username"] == "unknown-user@example.com"
    assert res["items"][1]["objective"]["possible_actions"] == ["inactivate"]
    assert (
        res["items"][1]["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    )
    assert res["items"][1]["objective"]["template"]["name_plain"] == "objective_2"
    assert res["items"][1]["objective"]["template"]["name"] == "objective_2"
    assert res["items"][1]["objective"]["template"]["sequence_id"] == "O22"
    assert res["items"][1]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["items"][1]["objective"]["parameter_terms"]) == 0
    assert res["items"][1]["objective"]["library"]["name"] == "Sponsor"
    assert res["items"][1]["objective"]["library"]["is_editable"] is True
    assert res["items"][1]["start_date"]
    assert res["items"][1]["author_username"] == "unknown-user@example.com"
    assert res["items"][1]["endpoint_count"] == 0
    assert res["total"] == 0


def test_get_specific7(api_client):
    response = api_client.get(
        "/studies/study_root/study-objectives/StudyObjective_000002"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["study_version"]
    assert res["study_objective_uid"] == "StudyObjective_000002"
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["accepted_version"] is False
    assert res["study_uid"] == "study_root"
    assert res["objective_level"] is None
    assert res["latest_objective"] is None
    assert res["objective"]["uid"] == "Objective_000002"
    assert res["objective"]["name"] == "objective_2"
    assert res["objective"]["name_plain"] == "objective_2"
    assert res["objective"]["start_date"]
    assert res["objective"]["end_date"] is None
    assert res["objective"]["status"] == "Final"
    assert res["objective"]["study_count"] == 0
    assert res["objective"]["version"] == "1.0"
    assert res["objective"]["change_description"] == "Approved version"
    assert res["objective"]["author_username"] == "unknown-user@example.com"
    assert res["objective"]["possible_actions"] == ["inactivate"]
    assert res["objective"]["template"]["name"] == "objective_2"
    assert res["objective"]["template"]["name_plain"] == "objective_2"
    assert res["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res["objective"]["template"]["sequence_id"] == "O22"
    assert res["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["objective"]["parameter_terms"]) == 0
    assert res["objective"]["library"]["name"] == "Sponsor"
    assert res["objective"]["library"]["is_editable"] is True
    assert res["author_username"] == "unknown-user@example.com"
    assert res["endpoint_count"] == 0


def test_reorder_specific6(api_client):
    data = {"new_order": 1}
    response = api_client.patch(
        "/studies/study_root/study-objectives/StudyObjective_000002/order", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["study_version"]
    assert res["study_objective_uid"] == "StudyObjective_000002"
    assert res["order"] == 1
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["accepted_version"] is False
    assert res["study_uid"] == "study_root"
    assert res["objective_level"] is None
    assert res["objective"]["uid"] == "Objective_000002"
    assert res["objective"]["name"] == "objective_2"
    assert res["objective"]["name_plain"] == "objective_2"
    assert res["objective"]["start_date"]
    assert res["objective"]["end_date"] is None
    assert res["objective"]["status"] == "Final"
    assert res["objective"]["study_count"] == 0
    assert res["objective"]["version"] == "1.0"
    assert res["objective"]["change_description"] == "Approved version"
    assert res["objective"]["author_username"] == "unknown-user@example.com"
    assert res["objective"]["possible_actions"] == ["inactivate"]
    assert res["objective"]["template"]["name"] == "objective_2"
    assert res["objective"]["template"]["name_plain"] == "objective_2"
    assert res["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res["objective"]["template"]["sequence_id"] == "O22"
    assert res["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["objective"]["parameter_terms"]) == 0
    assert res["objective"]["library"]["name"] == "Sponsor"
    assert res["objective"]["library"]["is_editable"] is True
    assert res["author_username"] == "unknown-user@example.com"
    assert res["latest_objective"] is None
    assert res["endpoint_count"] == 0


def test_patch_specific1(api_client):
    data = {"objective_level": None}
    response = api_client.patch(
        "/studies/study_root/study-objectives/StudyObjective_000002", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["study_version"]
    assert res["study_objective_uid"] == "StudyObjective_000002"
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["accepted_version"] is False
    assert res["study_uid"] == "study_root"
    assert res["objective_level"] is None
    assert res["latest_objective"] is None
    assert res["objective"]["uid"] == "Objective_000002"
    assert res["objective"]["name"] == "objective_2"
    assert res["objective"]["name_plain"] == "objective_2"
    assert res["objective"]["start_date"]
    assert res["objective"]["end_date"] is None
    assert res["objective"]["status"] == "Final"
    assert res["objective"]["study_count"] == 0
    assert res["objective"]["version"] == "1.0"
    assert res["objective"]["change_description"] == "Approved version"
    assert res["objective"]["author_username"] == "unknown-user@example.com"
    assert res["objective"]["possible_actions"] == ["inactivate"]
    assert res["objective"]["template"]["name"] == "objective_2"
    assert res["objective"]["template"]["name_plain"] == "objective_2"
    assert res["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res["objective"]["template"]["sequence_id"] == "O22"
    assert res["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["objective"]["parameter_terms"]) == 0
    assert res["objective"]["library"]["name"] == "Sponsor"
    assert res["objective"]["library"]["is_editable"] is True
    assert res["author_username"] == "unknown-user@example.com"
    assert res["endpoint_count"] == 0


def test_get_history_of_all_selections1(api_client):
    response = api_client.get("/studies/study_root/study-objectives/audit-trail")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res[0]["order"] == 2
    assert res[0]["study_uid"] == "study_root"
    assert res[0]["study_objective_uid"] == "StudyObjective_000001"
    assert res[0]["objective_level"]["term_uid"] == "term_root_final"
    assert res[0]["objective_level"]["catalogue_name"] == "SDTM CT"
    assert len(res[0]["objective_level"]["codelists"]) == 1
    assert res[0]["objective_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res[0]["objective_level"]["codelists"][0]["order"] == 1
    assert res[0]["objective_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res[0]["objective_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res[0]["objective_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res[0]["objective_level"]["library_name"] == "Sponsor"
    assert res[0]["objective_level"]["start_date"]
    assert res[0]["objective_level"]["end_date"] is None
    assert res[0]["objective_level"]["status"] == "Final"
    assert res[0]["objective_level"]["version"] == "1.0"
    assert res[0]["objective_level"]["change_description"] == "Approved version"
    assert res[0]["objective_level"]["author_username"] == "unknown-user@example.com"
    assert res[0]["objective_level"]["queried_effective_date"] is None
    assert res[0]["objective_level"]["date_conflict"] is False
    assert res[0]["objective_level"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert res[0]["objective"]["uid"] == "Objective_000001"
    assert res[0]["objective"]["name"] == "objective_1"
    assert res[0]["objective"]["name_plain"] == "objective_1"
    assert res[0]["objective"]["start_date"]
    assert res[0]["objective"]["end_date"] is None
    assert res[0]["objective"]["study_count"] == 0
    assert res[0]["objective"]["status"] == "Final"
    assert res[0]["objective"]["version"] == "1.0"
    assert res[0]["objective"]["change_description"] == "Approved version"
    assert res[0]["objective"]["author_username"] == "unknown-user@example.com"
    assert res[0]["objective"]["possible_actions"] == ["inactivate"]
    assert res[0]["objective"]["template"]["name"] == "objective_1"
    assert res[0]["objective"]["template"]["name_plain"] == "objective_1"
    assert res[0]["objective"]["template"]["uid"] == "ObjectiveTemplate_000001"
    assert res[0]["objective"]["template"]["sequence_id"] == "O1"
    assert res[0]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res[0]["objective"]["parameter_terms"]) == 0
    assert res[0]["objective"]["library"]["name"] == "Sponsor"
    assert res[0]["objective"]["library"]["is_editable"] is True
    assert res[0]["author_username"] == "unknown-user@example.com"
    assert res[0]["end_date"] is None
    assert res[0]["status"] is None
    assert res[0]["change_type"] == "Edit"
    assert res[1]["order"] == 1
    assert res[1]["study_uid"] == "study_root"
    assert res[1]["study_objective_uid"] == "StudyObjective_000001"
    assert res[1]["objective_level"]["term_uid"] == "term_root_final"
    assert res[1]["objective_level"]["catalogue_name"] == "SDTM CT"
    assert len(res[1]["objective_level"]["codelists"]) == 1
    assert res[1]["objective_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res[1]["objective_level"]["codelists"][0]["order"] == 1
    assert res[1]["objective_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res[1]["objective_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res[1]["objective_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res[1]["objective_level"]["library_name"] == "Sponsor"
    assert res[1]["objective_level"]["start_date"]
    assert res[1]["objective_level"]["end_date"] is None
    assert res[1]["objective_level"]["status"] == "Final"
    assert res[1]["objective_level"]["version"] == "1.0"
    assert res[1]["objective_level"]["change_description"] == "Approved version"
    assert res[1]["objective_level"]["author_username"] == "unknown-user@example.com"
    assert res[1]["objective_level"]["queried_effective_date"] is None
    assert res[1]["objective_level"]["date_conflict"] is False
    assert res[1]["objective_level"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert res[1]["objective"]["uid"] == "Objective_000001"
    assert res[1]["objective"]["name"] == "objective_1"
    assert res[1]["objective"]["name_plain"] == "objective_1"
    assert res[1]["objective"]["start_date"]
    assert res[1]["objective"]["end_date"] is None
    assert res[1]["objective"]["study_count"] == 0
    assert res[1]["objective"]["status"] == "Final"
    assert res[1]["objective"]["version"] == "1.0"
    assert res[1]["objective"]["change_description"] == "Approved version"
    assert res[1]["objective"]["author_username"] == "unknown-user@example.com"
    assert res[1]["objective"]["possible_actions"] == ["inactivate"]
    assert res[1]["objective"]["template"]["name"] == "objective_1"
    assert res[1]["objective"]["template"]["name_plain"] == "objective_1"
    assert res[1]["objective"]["template"]["uid"] == "ObjectiveTemplate_000001"
    assert res[1]["objective"]["template"]["sequence_id"] == "O1"
    assert res[1]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res[1]["objective"]["parameter_terms"]) == 0
    assert res[1]["objective"]["library"]["name"] == "Sponsor"
    assert res[1]["objective"]["library"]["is_editable"] is True
    assert res[1]["author_username"] == "unknown-user@example.com"
    assert res[1]["end_date"]
    assert res[1]["status"] is None
    assert res[1]["change_type"] == "Create"
    assert res[2]["order"] == 2
    assert res[2]["study_uid"] == "study_root"
    assert res[2]["study_objective_uid"] == "StudyObjective_000002"
    assert res[2]["objective_level"] is None
    assert res[2]["objective"]["uid"] == "Objective_000002"
    assert res[2]["objective"]["name"] == "objective_2"
    assert res[2]["objective"]["name_plain"] == "objective_2"
    assert res[2]["objective"]["start_date"]
    assert res[2]["objective"]["end_date"] is None
    assert res[2]["objective"]["status"] == "Final"
    assert res[2]["objective"]["study_count"] == 0
    assert res[2]["objective"]["version"] == "1.0"
    assert res[2]["objective"]["change_description"] == "Approved version"
    assert res[2]["objective"]["author_username"] == "unknown-user@example.com"
    assert res[2]["objective"]["possible_actions"] == ["inactivate"]
    assert res[2]["objective"]["template"]["name"] == "objective_2"
    assert res[2]["objective"]["template"]["name_plain"] == "objective_2"
    assert res[2]["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res[2]["objective"]["template"]["sequence_id"] == "O22"
    assert res[2]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res[2]["objective"]["parameter_terms"]) == 0
    assert res[2]["objective"]["library"]["name"] == "Sponsor"
    assert res[2]["objective"]["library"]["is_editable"] is True
    assert res[2]["author_username"] == "unknown-user@example.com"
    assert res[2]["end_date"] is None
    assert res[2]["status"] is None
    assert res[2]["change_type"] == "Edit"
    assert res[3]["order"] == 1
    assert res[3]["study_uid"] == "study_root"
    assert res[3]["study_objective_uid"] == "StudyObjective_000002"
    assert res[3]["objective_level"] is None
    assert res[3]["objective"]["uid"] == "Objective_000002"
    assert res[3]["objective"]["name"] == "objective_2"
    assert res[3]["objective"]["name_plain"] == "objective_2"
    assert res[3]["objective"]["start_date"]
    assert res[3]["objective"]["end_date"] is None
    assert res[3]["objective"]["status"] == "Final"
    assert res[3]["objective"]["study_count"] == 0
    assert res[3]["objective"]["version"] == "1.0"
    assert res[3]["objective"]["change_description"] == "Approved version"
    assert res[3]["objective"]["author_username"] == "unknown-user@example.com"
    assert res[3]["objective"]["possible_actions"] == ["inactivate"]
    assert res[3]["objective"]["template"]["name"] == "objective_2"
    assert res[3]["objective"]["template"]["name_plain"] == "objective_2"
    assert res[3]["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res[3]["objective"]["template"]["sequence_id"] == "O22"
    assert res[3]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res[3]["objective"]["parameter_terms"]) == 0
    assert res[3]["objective"]["library"]["name"] == "Sponsor"
    assert res[3]["objective"]["library"]["is_editable"] is True
    assert res[3]["author_username"] == "unknown-user@example.com"
    assert res[3]["end_date"]
    assert res[3]["status"] is None
    assert res[3]["change_type"] == "Edit"
    assert res[4]["order"] == 2
    assert res[4]["study_uid"] == "study_root"
    assert res[4]["study_objective_uid"] == "StudyObjective_000002"
    assert res[4]["objective_level"] is None
    assert res[4]["objective"]["uid"] == "Objective_000002"
    assert res[4]["objective"]["name"] == "objective_2"
    assert res[4]["objective"]["name_plain"] == "objective_2"
    assert res[4]["objective"]["start_date"]
    assert res[4]["objective"]["end_date"] is None
    assert res[4]["objective"]["status"] == "Final"
    assert res[4]["objective"]["study_count"] == 0
    assert res[4]["objective"]["version"] == "1.0"
    assert res[4]["objective"]["change_description"] == "Approved version"
    assert res[4]["objective"]["author_username"] == "unknown-user@example.com"
    assert res[4]["objective"]["possible_actions"] == ["inactivate"]
    assert res[4]["objective"]["template"]["name"] == "objective_2"
    assert res[4]["objective"]["template"]["name_plain"] == "objective_2"
    assert res[4]["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res[4]["objective"]["template"]["sequence_id"] == "O22"
    assert res[4]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res[4]["objective"]["parameter_terms"]) == 0
    assert res[4]["objective"]["library"]["name"] == "Sponsor"
    assert res[4]["objective"]["library"]["is_editable"] is True
    assert res[4]["author_username"] == "unknown-user@example.com"
    assert res[4]["end_date"]
    assert res[4]["status"] is None
    assert res[4]["change_type"] == "Create"


def test_all_history_of_specific_selection8(api_client):
    response = api_client.get(
        "/studies/study_root/study-objectives/StudyObjective_000002/audit-trail"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res[0]["order"] == 2
    assert res[0]["study_uid"] == "study_root"
    assert res[0]["study_objective_uid"] == "StudyObjective_000002"
    assert res[0]["objective_level"] is None
    assert res[0]["objective"]["uid"] == "Objective_000002"
    assert res[0]["objective"]["name"] == "objective_2"
    assert res[0]["objective"]["name_plain"] == "objective_2"
    assert res[0]["objective"]["start_date"]
    assert res[0]["objective"]["end_date"] is None
    assert res[0]["objective"]["status"] == "Final"
    assert res[0]["objective"]["study_count"] == 0
    assert res[0]["objective"]["version"] == "1.0"
    assert res[0]["objective"]["change_description"] == "Approved version"
    assert res[0]["objective"]["author_username"] == "unknown-user@example.com"
    assert res[0]["objective"]["possible_actions"] == ["inactivate"]
    assert res[0]["objective"]["template"]["name"] == "objective_2"
    assert res[0]["objective"]["template"]["name_plain"] == "objective_2"
    assert res[0]["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res[0]["objective"]["template"]["sequence_id"] == "O22"
    assert res[0]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res[0]["objective"]["parameter_terms"]) == 0
    assert res[0]["objective"]["library"]["name"] == "Sponsor"
    assert res[0]["objective"]["library"]["is_editable"] is True
    assert res[0]["author_username"] == "unknown-user@example.com"
    assert res[0]["end_date"] is None
    assert res[0]["status"] is None
    assert res[0]["change_type"] == "Edit"
    assert res[1]["order"] == 1
    assert res[1]["study_uid"] == "study_root"
    assert res[1]["study_objective_uid"] == "StudyObjective_000002"
    assert res[1]["objective_level"] is None
    assert res[1]["objective"]["uid"] == "Objective_000002"
    assert res[1]["objective"]["name"] == "objective_2"
    assert res[1]["objective"]["name_plain"] == "objective_2"
    assert res[1]["objective"]["start_date"]
    assert res[1]["objective"]["end_date"] is None
    assert res[1]["objective"]["status"] == "Final"
    assert res[1]["objective"]["study_count"] == 0
    assert res[1]["objective"]["version"] == "1.0"
    assert res[1]["objective"]["change_description"] == "Approved version"
    assert res[1]["objective"]["author_username"] == "unknown-user@example.com"
    assert res[1]["objective"]["possible_actions"] == ["inactivate"]
    assert res[1]["objective"]["template"]["name"] == "objective_2"
    assert res[1]["objective"]["template"]["name_plain"] == "objective_2"
    assert res[1]["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res[1]["objective"]["template"]["sequence_id"] == "O22"
    assert res[1]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res[1]["objective"]["parameter_terms"]) == 0
    assert res[1]["objective"]["library"]["name"] == "Sponsor"
    assert res[1]["objective"]["library"]["is_editable"] is True
    assert res[1]["author_username"] == "unknown-user@example.com"
    assert res[1]["end_date"]
    assert res[1]["status"] is None
    assert res[1]["change_type"] == "Edit"
    assert res[2]["order"] == 2
    assert res[2]["study_uid"] == "study_root"
    assert res[2]["study_objective_uid"] == "StudyObjective_000002"
    assert res[2]["objective_level"] is None
    assert res[2]["objective"]["uid"] == "Objective_000002"
    assert res[2]["objective"]["name"] == "objective_2"
    assert res[2]["objective"]["name_plain"] == "objective_2"
    assert res[2]["objective"]["start_date"]
    assert res[2]["objective"]["end_date"] is None
    assert res[2]["objective"]["status"] == "Final"
    assert res[2]["objective"]["study_count"] == 0
    assert res[2]["objective"]["version"] == "1.0"
    assert res[2]["objective"]["change_description"] == "Approved version"
    assert res[2]["objective"]["author_username"] == "unknown-user@example.com"
    assert res[2]["objective"]["possible_actions"] == ["inactivate"]
    assert res[2]["objective"]["template"]["name"] == "objective_2"
    assert res[2]["objective"]["template"]["name_plain"] == "objective_2"
    assert res[2]["objective"]["template"]["uid"] == "ObjectiveTemplate_0000022"
    assert res[2]["objective"]["template"]["sequence_id"] == "O22"
    assert res[2]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res[2]["objective"]["parameter_terms"]) == 0
    assert res[2]["objective"]["library"]["name"] == "Sponsor"
    assert res[2]["objective"]["library"]["is_editable"] is True
    assert res[2]["author_username"] == "unknown-user@example.com"
    assert res[2]["end_date"]
    assert res[2]["status"] is None
    assert res[2]["change_type"] == "Create"


def test_patch_specific_replace(api_client):
    data = {"objective_uid": "Objective_000003"}
    response = api_client.patch(
        "/studies/study_root/study-objectives/StudyObjective_000002", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["study_version"]
    assert res["study_objective_uid"] == "StudyObjective_000002"
    assert res["accepted_version"] is False
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_uid"] == "study_root"
    assert res["objective_level"] is None
    assert res["author_username"] == "unknown-user@example.com"
    assert res["latest_objective"] is None
    assert res["objective"]["uid"] == "Objective_000003"
    assert res["objective"]["name"] == "objective_3"
    assert res["objective"]["name_plain"] == "objective_3"
    assert res["objective"]["start_date"]
    assert res["objective"]["end_date"] is None
    assert res["objective"]["status"] == "Final"
    assert res["objective"]["study_count"] == 0
    assert res["objective"]["version"] == "1.0"
    assert res["objective"]["change_description"] == "Approved version"
    assert res["objective"]["author_username"] == "unknown-user@example.com"
    assert res["objective"]["possible_actions"] == ["inactivate"]
    assert res["objective"]["template"]["name"] == "objective_3"
    assert res["objective"]["template"]["name_plain"] == "objective_3"
    assert res["objective"]["template"]["uid"] == "ObjectiveTemplate_000003"
    assert res["objective"]["template"]["sequence_id"] == "O3"
    assert res["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["objective"]["parameter_terms"]) == 0
    assert res["objective"]["library"]["name"] == "Sponsor"
    assert res["objective"]["library"]["is_editable"] is True
    assert res["endpoint_count"] == 0


def test_previewing_selection_create1(api_client):
    data = {
        "objective_data": {
            "library_name": "Sponsor",
            "name": "objective_4",
            "objective_template_uid": "ObjectiveTemplate_000004",
            "parameter_terms": [],
        },
        "objective_level_uid": "term_root_final",
    }
    response = api_client.post(
        "/studies/study_root/study-objectives/preview", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["study_version"]
    assert res["study_objective_uid"] == "preview"
    assert res["accepted_version"] is False
    assert res["order"] == 3
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_uid"] == "study_root"
    assert res["objective_level"]["term_uid"] == "term_root_final"
    assert res["objective_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["objective_level"]["codelists"]) == 1
    assert res["objective_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res["objective_level"]["codelists"][0]["order"] == 1
    assert res["objective_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res["objective_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res["objective_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["objective_level"]["library_name"] == "Sponsor"
    assert res["objective_level"]["start_date"]
    assert res["objective_level"]["end_date"] is None
    assert res["objective_level"]["status"] == "Final"
    assert res["objective_level"]["version"] == "1.0"
    assert res["objective_level"]["change_description"] == "Approved version"
    assert res["objective_level"]["author_username"] == "unknown-user@example.com"
    assert res["objective_level"]["queried_effective_date"] is None
    assert res["objective_level"]["date_conflict"] is False
    assert res["objective_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["author_username"] == "unknown-user@example.com"
    assert res["latest_objective"] is None
    assert res["objective"]["uid"] == "preview"
    assert res["objective"]["name"] == "objective_4"
    assert res["objective"]["name_plain"] == "objective_4"
    assert res["objective"]["start_date"]
    assert res["objective"]["end_date"] is None
    assert res["objective"]["status"] == "Final"
    assert res["objective"]["study_count"] == 0
    assert res["objective"]["version"] == "1.0"
    assert res["objective"]["change_description"] == "Approved version"
    assert res["objective"]["author_username"] == "unknown-user@example.com"
    assert res["objective"]["possible_actions"] == ["inactivate"]
    assert res["objective"]["template"]["name"] == "objective_4"
    assert res["objective"]["template"]["name_plain"] == "objective_4"
    assert res["objective"]["template"]["uid"] == "ObjectiveTemplate_000004"
    assert res["objective"]["template"]["sequence_id"] == "O4"
    assert res["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["objective"]["parameter_terms"]) == 0
    assert res["objective"]["library"]["name"] == "Sponsor"
    assert res["objective"]["library"]["is_editable"] is True
    assert res["endpoint_count"] == 0


def test_adding_selection_create1(api_client):
    data = {
        "objective_data": {
            "library_name": "Sponsor",
            "name": "objective_4",
            "objective_template_uid": "ObjectiveTemplate_000004",
            "parameter_terms": [],
        },
        "objective_level_uid": "term_root_final",
    }
    response = api_client.post(
        "/studies/study_root/study-objectives?create_objective=true", json=data
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["study_version"]
    assert res["study_objective_uid"] == "StudyObjective_000003"
    assert res["accepted_version"] is False
    assert res["order"] == 3
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_uid"] == "study_root"
    assert res["objective_level"]["term_uid"] == "term_root_final"
    assert res["objective_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["objective_level"]["codelists"]) == 1
    assert res["objective_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res["objective_level"]["codelists"][0]["order"] == 1
    assert res["objective_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res["objective_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res["objective_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["objective_level"]["library_name"] == "Sponsor"
    assert res["objective_level"]["start_date"]
    assert res["objective_level"]["end_date"] is None
    assert res["objective_level"]["status"] == "Final"
    assert res["objective_level"]["version"] == "1.0"
    assert res["objective_level"]["change_description"] == "Approved version"
    assert res["objective_level"]["author_username"] == "unknown-user@example.com"
    assert res["objective_level"]["queried_effective_date"] is None
    assert res["objective_level"]["date_conflict"] is False
    assert res["objective_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["author_username"] == "unknown-user@example.com"
    assert res["latest_objective"] is None
    assert res["objective"]["uid"] == "Objective_000006"
    assert res["objective"]["name"] == "objective_4"
    assert res["objective"]["name_plain"] == "objective_4"
    assert res["objective"]["start_date"]
    assert res["objective"]["end_date"] is None
    assert res["objective"]["status"] == "Final"
    assert res["objective"]["study_count"] == 0
    assert res["objective"]["version"] == "1.0"
    assert res["objective"]["change_description"] == "Approved version"
    assert res["objective"]["author_username"] == "unknown-user@example.com"
    assert res["objective"]["possible_actions"] == ["inactivate"]
    assert res["objective"]["template"]["name"] == "objective_4"
    assert res["objective"]["template"]["name_plain"] == "objective_4"
    assert res["objective"]["template"]["uid"] == "ObjectiveTemplate_000004"
    assert res["objective"]["template"]["sequence_id"] == "O4"
    assert res["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["objective"]["parameter_terms"]) == 0
    assert res["objective"]["library"]["name"] == "Sponsor"
    assert res["objective"]["library"]["is_editable"] is True
    assert res["endpoint_count"] == 0


def test_get_all_objectives_with_proper_study_count(api_client):
    response = api_client.get("/objectives?total_count=True")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["uid"] == "Objective_000006"
    assert res["items"][0]["name"] == "objective_4"
    assert res["items"][0]["name_plain"] == "objective_4"
    assert res["items"][0]["end_date"] is None
    assert res["items"][0]["status"] == "Final"
    assert res["items"][0]["version"] == "1.0"
    assert res["items"][0]["change_description"] == "Approved version"
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["template"] == {
        "name": "objective_4",
        "name_plain": "objective_4",
        "guidance_text": None,
        "uid": "ObjectiveTemplate_000004",
        "sequence_id": "O4",
        "library_name": "Sponsor",
    }
    assert res["items"][0]["parameter_terms"] == []
    assert res["items"][0]["library"] == {"name": "Sponsor", "is_editable": True}
    assert res["items"][0]["study_count"] == 1
    assert res["items"][1]["uid"] == "Objective_000003"
    assert res["items"][1]["name"] == "objective_3"
    assert res["items"][1]["name_plain"] == "objective_3"
    assert res["items"][1]["end_date"] is None
    assert res["items"][1]["status"] == "Final"
    assert res["items"][1]["version"] == "1.0"
    assert res["items"][1]["change_description"] == "Approved version"
    assert res["items"][1]["author_username"] == "unknown-user@example.com"
    assert res["items"][1]["possible_actions"] == ["inactivate"]
    assert res["items"][1]["template"] == {
        "name": "objective_3",
        "name_plain": "objective_3",
        "guidance_text": None,
        "uid": "ObjectiveTemplate_000003",
        "sequence_id": "O3",
        "library_name": "Sponsor",
    }
    assert res["items"][1]["parameter_terms"] == []
    assert res["items"][1]["library"] == {"name": "Sponsor", "is_editable": True}
    assert res["items"][1]["study_count"] == 1
    assert res["items"][2]["uid"] == "Objective_000001"
    assert res["items"][2]["name"] == "objective_1"
    assert res["items"][2]["name_plain"] == "objective_1"
    assert res["items"][2]["end_date"] is None
    assert res["items"][2]["status"] == "Final"
    assert res["items"][2]["version"] == "1.0"
    assert res["items"][2]["change_description"] == "Approved version"
    assert res["items"][2]["author_username"] == "unknown-user@example.com"
    assert res["items"][2]["possible_actions"] == ["inactivate"]
    assert res["items"][2]["template"] == {
        "name": "objective_1",
        "name_plain": "objective_1",
        "guidance_text": None,
        "uid": "ObjectiveTemplate_000001",
        "sequence_id": "O1",
        "library_name": "Sponsor",
    }
    assert res["items"][2]["parameter_terms"] == []
    assert res["items"][2]["library"] == {"name": "Sponsor", "is_editable": True}
    assert res["items"][2]["study_count"] == 1


def test_delete6(api_client):
    response = api_client.delete(
        "/studies/study_root/study-objectives/StudyObjective_000003"
    )

    assert_response_status_code(response, 204)
