# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.domain_repositories.models.syntax import (
    EndpointRoot,
    EndpointTemplateRoot,
    ObjectiveRoot,
    ObjectiveTemplateRoot,
    TimeframeRoot,
    TimeframeTemplateRoot,
)
from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    CREATE_BASE_TEMPLATE_PARAMETER_TREE,
    STARTUP_CT_TERM_NAME_CYPHER,
    STARTUP_STUDY_ENDPOINT_CYPHER,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.study.selection.endpoint")
    db.cypher_query(CREATE_BASE_TEMPLATE_PARAMETER_TREE)
    db.cypher_query(STARTUP_CT_TERM_NAME_CYPHER)
    db.cypher_query(STARTUP_STUDY_ENDPOINT_CYPHER)
    ObjectiveTemplateRoot.generate_node_uids_if_not_present()
    ObjectiveRoot.generate_node_uids_if_not_present()
    EndpointTemplateRoot.generate_node_uids_if_not_present()
    EndpointRoot.generate_node_uids_if_not_present()
    TimeframeTemplateRoot.generate_node_uids_if_not_present()
    TimeframeRoot.generate_node_uids_if_not_present()

    yield

    drop_db("old.json.test.study.selection.endpoint")


def test_getting_empty_list4(api_client):
    response = api_client.get("/studies/study_root/study-endpoints")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"] == []
    assert res["total"] == 0


def test_getting_empty_list_for_all_studies2(api_client):
    response = api_client.get("/study-endpoints")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res == {"items": [], "page": 1, "size": 10, "total": 0}


def test_adding_selection10(api_client):
    data = {
        "endpoint_level_uid": "term_root_final",
        "endpoint_sublevel_uid": "term_root_final_non_edit",
        "endpoint_uid": "Endpoint_000001",
        "endpoint_units": {"separator": "string", "units": ["unit 1", "unit 2"]},
        "study_objective_uid": "StudyObjective_000001",
        "timeframe_uid": "Timeframe_000001",
    }
    response = api_client.post("/studies/study_root/study-endpoints", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["endpoint"]["change_description"] == "Approved version"
    assert res["endpoint"]["end_date"] is None
    assert res["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["endpoint"]["library"]["is_editable"] is True
    assert res["endpoint"]["library"]["name"] == "Sponsor"
    assert res["endpoint"]["name"] == "endpoint_1"
    assert res["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["endpoint"]["parameter_terms"]) == 0
    assert res["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["endpoint"]["start_date"]
    assert res["endpoint"]["status"] == "Final"
    assert res["endpoint"]["study_count"] == 0
    assert res["endpoint"]["uid"] == "Endpoint_000001"
    assert res["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint"]["version"] == "1.0"
    assert res["endpoint_level"]["term_uid"] == "term_root_final"
    assert res["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["endpoint_level"]["codelists"]) == 1
    assert res["endpoint_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res["endpoint_level"]["codelists"][0]["order"] == 1
    assert res["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["endpoint_level"]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["start_date"]
    assert res["endpoint_level"]["end_date"] is None
    assert res["endpoint_level"]["status"] == "Final"
    assert res["endpoint_level"]["version"] == "1.0"
    assert res["endpoint_level"]["change_description"] == "Approved version"
    assert res["endpoint_level"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint_level"]["queried_effective_date"] is None
    assert res["endpoint_level"]["date_conflict"] is False
    assert res["endpoint_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["endpoint_sublevel"]["term_uid"] == "term_root_final_non_edit"
    assert res["endpoint_sublevel"]["catalogue_name"] == "SDTM CT"
    assert len(res["endpoint_sublevel"]["codelists"]) == 1
    assert res["endpoint_sublevel"]["codelists"][0]["codelist_uid"] == "non_editable_cr"
    assert res["endpoint_sublevel"]["codelists"][0]["order"] == 3
    assert res["endpoint_sublevel"]["codelists"][0]["library_name"] == "CDISC"
    assert res["endpoint_sublevel"]["sponsor_preferred_name"] == "term_value_name3"
    assert (
        res["endpoint_sublevel"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["endpoint_sublevel"]["library_name"] == "CDISC"
    assert res["endpoint_sublevel"]["start_date"]
    assert res["endpoint_sublevel"]["end_date"] is None
    assert res["endpoint_sublevel"]["status"] == "Final"
    assert res["endpoint_sublevel"]["version"] == "1.0"
    assert res["endpoint_sublevel"]["change_description"] == "Approved version"
    assert res["endpoint_sublevel"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint_sublevel"]["queried_effective_date"] is None
    assert res["endpoint_sublevel"]["date_conflict"] is False
    assert res["endpoint_sublevel"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["latest_endpoint"] is None
    assert res["latest_timeframe"] is None
    assert res["endpoint_units"] == {
        "separator": "string",
        "units": [{"uid": "unit 1"}, {"uid": "unit 2"}],
    }
    assert res["author_username"] == "unknown-user@example.com"
    assert res["order"] == 1
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_version"]
    assert res["study_endpoint_uid"] == "StudyEndpoint_000001"
    assert res["study_objective"]["endpoint_count"] == 1
    assert res["study_objective"]["start_date"]
    assert res["study_objective"]["author_username"] == "unknown-user@example.com"
    assert (
        res["study_objective"]["objective"]["change_description"] == "Approved version"
    )
    assert res["study_objective"]["objective"]["end_date"] is None
    assert res["study_objective"]["objective"]["library"]["is_editable"] is True
    assert res["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    assert res["study_objective"]["objective"]["name"] == "objective_1"
    assert res["study_objective"]["objective"]["name_plain"] == "objective_1"
    assert res["study_objective"]["objective"]["template"]["name"] == "objective_1"
    assert (
        res["study_objective"]["objective"]["template"]["name_plain"] == "objective_1"
    )
    assert (
        res["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert res["study_objective"]["objective"]["template"]["sequence_id"] == "O1"
    assert res["study_objective"]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["study_objective"]["objective"]["possible_actions"] == ["inactivate"]
    assert res["study_objective"]["objective"]["start_date"]
    assert res["study_objective"]["objective"]["status"] == "Final"
    assert res["study_objective"]["objective"]["study_count"] == 0
    assert res["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["study_objective"]["objective"]["version"] == "1.0"
    assert res["study_objective"]["latest_objective"] is None
    assert res["study_objective"]["objective_level"] is None
    assert res["study_objective"]["order"] == 1
    assert res["study_objective"]["project_number"] == "123"
    assert res["study_objective"]["project_name"] == "Project ABC"
    assert res["study_objective"]["study_version"]
    assert res["study_objective"]["study_objective_uid"] == "StudyObjective_000001"
    assert res["study_objective"]["accepted_version"] is False
    assert res["study_objective"]["study_uid"] == "study_root"
    assert res["study_uid"] == "study_root"
    assert res["accepted_version"] is False
    assert res["timeframe"]["study_count"] == 0
    assert res["timeframe"]["change_description"] == "Approved version"
    assert res["timeframe"]["end_date"] is None
    assert res["timeframe"]["library"]["is_editable"] is True
    assert res["timeframe"]["library"]["name"] == "Sponsor"
    assert res["timeframe"]["name"] == "timeframe_1"
    assert res["timeframe"]["name_plain"] == "timeframe_1"
    assert len(res["timeframe"]["parameter_terms"]) == 0
    assert res["timeframe"]["possible_actions"] == ["inactivate"]
    assert res["timeframe"]["start_date"]
    assert res["timeframe"]["status"] == "Final"
    assert res["timeframe"]["template"]["name"] == "timeframe_1"
    assert res["timeframe"]["template"]["name_plain"] == "timeframe_1"
    assert res["timeframe"]["template"]["uid"] == "TimeframeTemplate_000011"
    assert res["timeframe"]["template"]["sequence_id"] == "T11"
    assert res["timeframe"]["template"]["library_name"] == "Sponsor"
    assert res["timeframe"]["uid"] == "Timeframe_000001"
    assert res["timeframe"]["author_username"] == "unknown-user@example.com"
    assert res["timeframe"]["version"] == "1.0"


def test_get_all_list_not_empty(api_client):
    response = api_client.get("/studies/study_root/study-endpoints")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["latest_endpoint"] is None
    assert res["items"][0]["latest_timeframe"] is None
    assert res["items"][0]["endpoint"]["change_description"] == "Approved version"
    assert res["items"][0]["endpoint"]["end_date"] is None
    assert res["items"][0]["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["items"][0]["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["items"][0]["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["items"][0]["endpoint"]["library"]["is_editable"] is True
    assert res["items"][0]["endpoint"]["library"]["name"] == "Sponsor"
    assert res["items"][0]["endpoint"]["name"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["items"][0]["endpoint"]["parameter_terms"]) == 0
    assert res["items"][0]["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["endpoint"]["start_date"]
    assert res["items"][0]["endpoint"]["status"] == "Final"
    assert res["items"][0]["endpoint"]["study_count"] == 0
    assert res["items"][0]["endpoint"]["uid"] == "Endpoint_000001"
    assert res["items"][0]["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["endpoint"]["version"] == "1.0"
    assert res["items"][0]["endpoint_level"]["term_uid"] == "term_root_final"
    assert res["items"][0]["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["items"][0]["endpoint_level"]["codelists"]) == 1
    assert (
        res["items"][0]["endpoint_level"]["codelists"][0]["codelist_uid"]
        == "editable_cr"
    )
    assert res["items"][0]["endpoint_level"]["codelists"][0]["order"] == 1
    assert (
        res["items"][0]["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    )
    assert (
        res["items"][0]["endpoint_level"]["sponsor_preferred_name"]
        == "term_value_name1"
    )
    assert (
        res["items"][0]["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["items"][0]["endpoint_level"]["library_name"] == "Sponsor"
    assert res["items"][0]["endpoint_level"]["start_date"]
    assert res["items"][0]["endpoint_level"]["end_date"] is None
    assert res["items"][0]["endpoint_level"]["status"] == "Final"
    assert res["items"][0]["endpoint_level"]["version"] == "1.0"
    assert res["items"][0]["endpoint_level"]["change_description"] == "Approved version"
    assert (
        res["items"][0]["endpoint_level"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["endpoint_level"]["queried_effective_date"] is None
    assert res["items"][0]["endpoint_level"]["date_conflict"] is False
    assert res["items"][0]["endpoint_level"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert (
        res["items"][0]["endpoint_sublevel"]["term_uid"] == "term_root_final_non_edit"
    )
    assert res["items"][0]["endpoint_sublevel"]["catalogue_name"] == "SDTM CT"
    assert len(res["items"][0]["endpoint_sublevel"]["codelists"]) == 1
    assert (
        res["items"][0]["endpoint_sublevel"]["codelists"][0]["codelist_uid"]
        == "non_editable_cr"
    )
    assert res["items"][0]["endpoint_sublevel"]["codelists"][0]["order"] == 3
    assert (
        res["items"][0]["endpoint_sublevel"]["codelists"][0]["library_name"] == "CDISC"
    )
    assert (
        res["items"][0]["endpoint_sublevel"]["sponsor_preferred_name"]
        == "term_value_name3"
    )
    assert (
        res["items"][0]["endpoint_sublevel"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["items"][0]["endpoint_sublevel"]["library_name"] == "CDISC"
    assert res["items"][0]["endpoint_sublevel"]["start_date"]
    assert res["items"][0]["endpoint_sublevel"]["end_date"] is None
    assert res["items"][0]["endpoint_sublevel"]["status"] == "Final"
    assert res["items"][0]["endpoint_sublevel"]["version"] == "1.0"
    assert (
        res["items"][0]["endpoint_sublevel"]["change_description"] == "Approved version"
    )
    assert (
        res["items"][0]["endpoint_sublevel"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["endpoint_sublevel"]["queried_effective_date"] is None
    assert res["items"][0]["endpoint_sublevel"]["date_conflict"] is False
    assert res["items"][0]["endpoint_sublevel"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert res["items"][0]["endpoint_units"]["separator"] == "string"
    assert len(res["items"][0]["endpoint_units"]["units"]) == 2
    assert res["items"][0]["endpoint_units"]["units"][0]["uid"] == "unit 1"
    assert res["items"][0]["endpoint_units"]["units"][0]["name"] == "name 1"
    assert res["items"][0]["endpoint_units"]["units"][1]["uid"] == "unit 2"
    assert res["items"][0]["endpoint_units"]["units"][1]["name"] == "name 2"
    assert res["items"][0]["start_date"]
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["project_number"] == "123"
    assert res["items"][0]["project_name"] == "Project ABC"
    assert res["items"][0]["study_version"]
    assert res["items"][0]["study_endpoint_uid"] == "StudyEndpoint_000001"
    assert res["items"][0]["accepted_version"] is False
    assert res["items"][0]["study_objective"]["endpoint_count"] == 1
    assert res["items"][0]["study_objective"]["accepted_version"] is False
    assert res["items"][0]["study_objective"]["start_date"]
    assert (
        res["items"][0]["study_objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["study_objective"]["latest_objective"] is None
    assert (
        res["items"][0]["study_objective"]["objective"]["change_description"]
        == "Approved version"
    )
    assert res["items"][0]["study_objective"]["objective"]["end_date"] is None
    assert (
        res["items"][0]["study_objective"]["objective"]["library"]["is_editable"]
        is True
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    )
    assert res["items"][0]["study_objective"]["objective"]["name"] == "objective_1"
    assert (
        res["items"][0]["study_objective"]["objective"]["name_plain"] == "objective_1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["name"]
        == "objective_1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["name_plain"]
        == "objective_1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["sequence_id"]
        == "O1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["library_name"]
        == "Sponsor"
    )
    assert len(res["items"][0]["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["items"][0]["study_objective"]["objective"]["possible_actions"] == [
        "inactivate"
    ]
    assert res["items"][0]["study_objective"]["objective"]["start_date"]
    assert res["items"][0]["study_objective"]["objective"]["status"] == "Final"
    assert res["items"][0]["study_objective"]["objective"]["study_count"] == 0
    assert res["items"][0]["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["items"][0]["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["study_objective"]["objective"]["version"] == "1.0"
    assert res["items"][0]["study_objective"]["objective_level"] is None
    assert res["items"][0]["study_objective"]["order"] == 1
    assert res["items"][0]["study_objective"]["project_number"] == "123"
    assert res["items"][0]["study_objective"]["project_name"] == "Project ABC"
    assert res["items"][0]["study_objective"]["study_version"]
    assert (
        res["items"][0]["study_objective"]["study_objective_uid"]
        == "StudyObjective_000001"
    )
    assert res["items"][0]["study_objective"]["study_uid"] == "study_root"
    assert res["items"][0]["study_uid"] == "study_root"
    assert res["items"][0]["timeframe"]["study_count"] == 0
    assert res["items"][0]["timeframe"]["change_description"] == "Approved version"
    assert res["items"][0]["timeframe"]["end_date"] is None
    assert res["items"][0]["timeframe"]["library"]["is_editable"] is True
    assert res["items"][0]["timeframe"]["library"]["name"] == "Sponsor"
    assert res["items"][0]["timeframe"]["name"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["name_plain"] == "timeframe_1"
    assert len(res["items"][0]["timeframe"]["parameter_terms"]) == 0
    assert res["items"][0]["timeframe"]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["timeframe"]["start_date"]
    assert res["items"][0]["timeframe"]["status"] == "Final"
    assert res["items"][0]["timeframe"]["template"]["name"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["template"]["name_plain"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["template"]["uid"] == "TimeframeTemplate_000011"
    assert res["items"][0]["timeframe"]["template"]["sequence_id"] == "T11"
    assert res["items"][0]["timeframe"]["template"]["library_name"] == "Sponsor"
    assert res["items"][0]["timeframe"]["uid"] == "Timeframe_000001"
    assert res["items"][0]["timeframe"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["timeframe"]["version"] == "1.0"
    assert res["total"] == 0


def test_get_all_for_all_studies2(api_client):
    response = api_client.get("/study-endpoints")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["study_uid"] == "study_root"
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["project_number"] == "123"
    assert res["items"][0]["project_name"] == "Project ABC"
    assert res["items"][0]["study_version"]
    assert res["items"][0]["study_endpoint_uid"] == "StudyEndpoint_000001"
    assert res["items"][0]["study_objective"]["study_uid"] == "study_root"
    assert res["items"][0]["study_objective"]["order"] == 1
    assert res["items"][0]["study_objective"]["project_number"] == "123"
    assert res["items"][0]["study_objective"]["project_name"] == "Project ABC"
    assert res["items"][0]["study_objective"]["study_version"]
    assert (
        res["items"][0]["study_objective"]["study_objective_uid"]
        == "StudyObjective_000001"
    )
    assert res["items"][0]["study_objective"]["objective_level"] is None
    assert res["items"][0]["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert res["items"][0]["study_objective"]["objective"]["name"] == "objective_1"
    assert (
        res["items"][0]["study_objective"]["objective"]["name_plain"] == "objective_1"
    )
    assert res["items"][0]["study_objective"]["objective"]["start_date"]
    assert res["items"][0]["study_objective"]["objective"]["end_date"] is None
    assert res["items"][0]["study_objective"]["objective"]["status"] == "Final"
    assert res["items"][0]["study_objective"]["objective"]["version"] == "1.0"
    assert (
        res["items"][0]["study_objective"]["objective"]["change_description"]
        == "Approved version"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["study_objective"]["objective"]["possible_actions"] == [
        "inactivate"
    ]
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["name"]
        == "objective_1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["name_plain"]
        == "objective_1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["sequence_id"]
        == "O1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["library_name"]
        == "Sponsor"
    )
    assert len(res["items"][0]["study_objective"]["objective"]["parameter_terms"]) == 0
    assert (
        res["items"][0]["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["library"]["is_editable"]
        is True
    )
    assert res["items"][0]["study_objective"]["objective"]["study_count"] == 0
    assert res["items"][0]["study_objective"]["start_date"]
    assert (
        res["items"][0]["study_objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["study_objective"]["endpoint_count"] == 1
    assert res["items"][0]["study_objective"]["latest_objective"] is None
    assert res["items"][0]["study_objective"]["accepted_version"] is False
    assert res["items"][0]["endpoint_level"]["term_uid"] == "term_root_final"
    assert res["items"][0]["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["items"][0]["endpoint_level"]["codelists"]) == 1
    assert (
        res["items"][0]["endpoint_level"]["codelists"][0]["codelist_uid"]
        == "editable_cr"
    )
    assert res["items"][0]["endpoint_level"]["codelists"][0]["order"] == 1
    assert (
        res["items"][0]["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    )
    assert (
        res["items"][0]["endpoint_level"]["sponsor_preferred_name"]
        == "term_value_name1"
    )
    assert (
        res["items"][0]["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["items"][0]["endpoint_level"]["library_name"] == "Sponsor"
    assert res["items"][0]["endpoint_level"]["start_date"]
    assert res["items"][0]["endpoint_level"]["end_date"] is None
    assert res["items"][0]["endpoint_level"]["status"] == "Final"
    assert res["items"][0]["endpoint_level"]["version"] == "1.0"
    assert res["items"][0]["endpoint_level"]["change_description"] == "Approved version"
    assert (
        res["items"][0]["endpoint_level"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["endpoint_level"]["queried_effective_date"] is None
    assert res["items"][0]["endpoint_level"]["date_conflict"] is False
    assert res["items"][0]["endpoint_level"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert (
        res["items"][0]["endpoint_sublevel"]["term_uid"] == "term_root_final_non_edit"
    )
    assert res["items"][0]["endpoint_sublevel"]["catalogue_name"] == "SDTM CT"
    assert len(res["items"][0]["endpoint_sublevel"]["codelists"]) == 1
    assert (
        res["items"][0]["endpoint_sublevel"]["codelists"][0]["codelist_uid"]
        == "non_editable_cr"
    )
    assert res["items"][0]["endpoint_sublevel"]["codelists"][0]["order"] == 3
    assert (
        res["items"][0]["endpoint_sublevel"]["codelists"][0]["library_name"] == "CDISC"
    )
    assert (
        res["items"][0]["endpoint_sublevel"]["sponsor_preferred_name"]
        == "term_value_name3"
    )
    assert (
        res["items"][0]["endpoint_sublevel"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["items"][0]["endpoint_sublevel"]["library_name"] == "CDISC"
    assert res["items"][0]["endpoint_sublevel"]["start_date"]
    assert res["items"][0]["endpoint_sublevel"]["end_date"] is None
    assert res["items"][0]["endpoint_sublevel"]["status"] == "Final"
    assert res["items"][0]["endpoint_sublevel"]["version"] == "1.0"
    assert (
        res["items"][0]["endpoint_sublevel"]["change_description"] == "Approved version"
    )
    assert (
        res["items"][0]["endpoint_sublevel"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["endpoint_sublevel"]["queried_effective_date"] is None
    assert res["items"][0]["endpoint_sublevel"]["date_conflict"] is False
    assert res["items"][0]["endpoint_sublevel"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert res["items"][0]["endpoint_units"] == {
        "units": [
            {"uid": "unit 1", "name": "name 1"},
            {"uid": "unit 2", "name": "name 2"},
        ],
        "separator": "string",
    }
    assert res["items"][0]["endpoint"]["uid"] == "Endpoint_000001"
    assert res["items"][0]["endpoint"]["name"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["name_plain"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["start_date"]
    assert res["items"][0]["endpoint"]["end_date"] is None
    assert res["items"][0]["endpoint"]["status"] == "Final"
    assert res["items"][0]["endpoint"]["version"] == "1.0"
    assert res["items"][0]["endpoint"]["change_description"] == "Approved version"
    assert res["items"][0]["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["items"][0]["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["items"][0]["endpoint"]["template"]["library_name"] == "Sponsor"
    assert len(res["items"][0]["endpoint"]["parameter_terms"]) == 0
    assert res["items"][0]["endpoint"]["library"]["name"] == "Sponsor"
    assert res["items"][0]["endpoint"]["library"]["is_editable"] is True
    assert res["items"][0]["endpoint"]["study_count"] == 0
    assert res["items"][0]["timeframe"]["uid"] == "Timeframe_000001"
    assert res["items"][0]["timeframe"]["name"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["name_plain"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["start_date"]
    assert res["items"][0]["timeframe"]["end_date"] is None
    assert res["items"][0]["timeframe"]["status"] == "Final"
    assert res["items"][0]["timeframe"]["version"] == "1.0"
    assert res["items"][0]["timeframe"]["study_count"] == 0
    assert res["items"][0]["timeframe"]["change_description"] == "Approved version"
    assert res["items"][0]["timeframe"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["timeframe"]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["timeframe"]["template"]["name"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["template"]["name_plain"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["template"]["uid"] == "TimeframeTemplate_000011"
    assert res["items"][0]["timeframe"]["template"]["sequence_id"] == "T11"
    assert res["items"][0]["timeframe"]["template"]["library_name"] == "Sponsor"
    assert len(res["items"][0]["timeframe"]["parameter_terms"]) == 0
    assert res["items"][0]["timeframe"]["library"]["name"] == "Sponsor"
    assert res["items"][0]["timeframe"]["library"]["is_editable"] is True
    assert res["items"][0]["latest_endpoint"] is None
    assert res["items"][0]["latest_timeframe"] is None
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["accepted_version"] is False


def test_get_history_of_all_selections(api_client):
    response = api_client.get("/studies/study_root/study-endpoints/audit-trail")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res[0]["endpoint"]["change_description"] == "Approved version"
    assert res[0]["endpoint"]["end_date"] is None
    assert res[0]["endpoint"]["template"]["name"] == "endpoint_1"
    assert res[0]["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res[0]["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res[0]["endpoint"]["template"]["sequence_id"] == "E1"
    assert res[0]["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res[0]["endpoint"]["library"]["is_editable"] is True
    assert res[0]["endpoint"]["library"]["name"] == "Sponsor"
    assert res[0]["endpoint"]["name"] == "endpoint_1"
    assert res[0]["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res[0]["endpoint"]["parameter_terms"]) == 0
    assert res[0]["endpoint"]["possible_actions"] == ["inactivate"]
    assert res[0]["endpoint"]["start_date"]
    assert res[0]["endpoint"]["status"] == "Final"
    assert res[0]["endpoint"]["study_count"] == 0
    assert res[0]["endpoint"]["uid"] == "Endpoint_000001"
    assert res[0]["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res[0]["endpoint"]["version"] == "1.0"
    assert res[0]["endpoint_level"]["term_uid"] == "term_root_final"
    assert res[0]["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res[0]["endpoint_level"]["codelists"]) == 1
    assert res[0]["endpoint_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res[0]["endpoint_level"]["codelists"][0]["order"] == 1
    assert res[0]["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res[0]["endpoint_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res[0]["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res[0]["endpoint_level"]["library_name"] == "Sponsor"
    assert res[0]["endpoint_level"]["start_date"]
    assert res[0]["endpoint_level"]["end_date"] is None
    assert res[0]["endpoint_level"]["status"] == "Final"
    assert res[0]["endpoint_level"]["version"] == "1.0"
    assert res[0]["endpoint_level"]["change_description"] == "Approved version"
    assert res[0]["endpoint_level"]["author_username"] == "unknown-user@example.com"
    assert res[0]["endpoint_level"]["queried_effective_date"] is None
    assert res[0]["endpoint_level"]["date_conflict"] is False
    assert res[0]["endpoint_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res[0]["endpoint_sublevel"]["term_uid"] == "term_root_final_non_edit"
    assert res[0]["endpoint_sublevel"]["catalogue_name"] == "SDTM CT"
    assert len(res[0]["endpoint_sublevel"]["codelists"]) == 1
    assert (
        res[0]["endpoint_sublevel"]["codelists"][0]["codelist_uid"] == "non_editable_cr"
    )
    assert res[0]["endpoint_sublevel"]["codelists"][0]["order"] == 3
    assert res[0]["endpoint_sublevel"]["codelists"][0]["library_name"] == "CDISC"
    assert res[0]["endpoint_sublevel"]["sponsor_preferred_name"] == "term_value_name3"
    assert (
        res[0]["endpoint_sublevel"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res[0]["endpoint_sublevel"]["library_name"] == "CDISC"
    assert res[0]["endpoint_sublevel"]["start_date"]
    assert res[0]["endpoint_sublevel"]["end_date"] is None
    assert res[0]["endpoint_sublevel"]["status"] == "Final"
    assert res[0]["endpoint_sublevel"]["version"] == "1.0"
    assert res[0]["endpoint_sublevel"]["change_description"] == "Approved version"
    assert res[0]["endpoint_sublevel"]["author_username"] == "unknown-user@example.com"
    assert res[0]["endpoint_sublevel"]["queried_effective_date"] is None
    assert res[0]["endpoint_sublevel"]["date_conflict"] is False
    assert res[0]["endpoint_sublevel"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert res[0]["endpoint_units"] == {
        "separator": "string",
        "units": [
            {"uid": "unit 1", "name": "name 1"},
            {"uid": "unit 2", "name": "name 2"},
        ],
    }
    assert res[0]["author_username"] == "unknown-user@example.com"
    assert res[0]["end_date"] is None
    assert res[0]["status"] is None
    assert res[0]["change_type"] == "Create"
    assert res[0]["order"] == 1
    assert res[0]["study_endpoint_uid"] == "StudyEndpoint_000001"
    assert res[0]["study_objective"]["endpoint_count"] == 1
    assert res[0]["study_objective"]["accepted_version"] is False
    assert res[0]["study_objective"]["start_date"]
    assert res[0]["study_objective"]["author_username"] == "unknown-user@example.com"
    assert res[0]["study_objective"]["latest_objective"] is None
    assert (
        res[0]["study_objective"]["objective"]["change_description"]
        == "Approved version"
    )
    assert res[0]["study_objective"]["objective"]["end_date"] is None
    assert res[0]["study_objective"]["objective"]["library"]["is_editable"] is True
    assert res[0]["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    assert res[0]["study_objective"]["objective"]["name"] == "objective_1"
    assert res[0]["study_objective"]["objective"]["name_plain"] == "objective_1"
    assert res[0]["study_objective"]["objective"]["template"]["name"] == "objective_1"
    assert (
        res[0]["study_objective"]["objective"]["template"]["name_plain"]
        == "objective_1"
    )
    assert (
        res[0]["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert res[0]["study_objective"]["objective"]["template"]["sequence_id"] == "O1"
    assert (
        res[0]["study_objective"]["objective"]["template"]["library_name"] == "Sponsor"
    )
    assert len(res[0]["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res[0]["study_objective"]["objective"]["possible_actions"] == ["inactivate"]
    assert res[0]["study_objective"]["objective"]["start_date"]
    assert res[0]["study_objective"]["objective"]["status"] == "Final"
    assert res[0]["study_objective"]["objective"]["study_count"] == 0
    assert res[0]["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res[0]["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res[0]["study_objective"]["objective"]["version"] == "1.0"
    assert res[0]["study_objective"]["objective_level"] is None
    assert res[0]["study_objective"]["order"] == 1
    assert res[0]["study_objective"]["project_number"] == "123"
    assert res[0]["study_objective"]["project_name"] == "Project ABC"
    assert res[0]["study_objective"]["study_version"]
    assert res[0]["study_objective"]["study_objective_uid"] == "StudyObjective_000001"
    assert res[0]["study_objective"]["study_uid"] == "study_root"
    assert res[0]["study_uid"] == "study_root"
    assert res[0]["timeframe"]["study_count"] == 0
    assert res[0]["timeframe"]["change_description"] == "Approved version"
    assert res[0]["timeframe"]["end_date"] is None
    assert res[0]["timeframe"]["library"]["is_editable"] is True
    assert res[0]["timeframe"]["library"]["name"] == "Sponsor"
    assert res[0]["timeframe"]["name"] == "timeframe_1"
    assert res[0]["timeframe"]["name_plain"] == "timeframe_1"
    assert len(res[0]["timeframe"]["parameter_terms"]) == 0
    assert res[0]["timeframe"]["possible_actions"] == ["inactivate"]
    assert res[0]["timeframe"]["start_date"]
    assert res[0]["timeframe"]["status"] == "Final"
    assert res[0]["timeframe"]["template"]["name"] == "timeframe_1"
    assert res[0]["timeframe"]["template"]["name_plain"] == "timeframe_1"
    assert res[0]["timeframe"]["template"]["uid"] == "TimeframeTemplate_000011"
    assert res[0]["timeframe"]["template"]["sequence_id"] == "T11"
    assert res[0]["timeframe"]["template"]["library_name"] == "Sponsor"
    assert res[0]["timeframe"]["uid"] == "Timeframe_000001"
    assert res[0]["timeframe"]["author_username"] == "unknown-user@example.com"
    assert res[0]["timeframe"]["version"] == "1.0"


def test_add_selection_2_no_timeframe_set(api_client):
    data = {
        "endpoint_uid": "Endpoint_000001",
        "study_objective_uid": "StudyObjective_000001",
    }
    response = api_client.post("/studies/study_root/study-endpoints", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["latest_endpoint"] is None
    assert res["latest_timeframe"] is None
    assert res["endpoint"]["change_description"] == "Approved version"
    assert res["endpoint"]["end_date"] is None
    assert res["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["endpoint"]["library"]["is_editable"] is True
    assert res["endpoint"]["library"]["name"] == "Sponsor"
    assert res["endpoint"]["name"] == "endpoint_1"
    assert res["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["endpoint"]["parameter_terms"]) == 0
    assert res["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["endpoint"]["start_date"]
    assert res["endpoint"]["status"] == "Final"
    assert res["endpoint"]["study_count"] == 0
    assert res["endpoint"]["uid"] == "Endpoint_000001"
    assert res["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint"]["version"] == "1.0"
    assert res["endpoint_level"] is None
    assert res["endpoint_sublevel"] is None
    assert res["endpoint_units"] == {"separator": None, "units": []}
    assert res["author_username"] == "unknown-user@example.com"
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_version"]
    assert res["study_endpoint_uid"] == "StudyEndpoint_000003"
    assert res["accepted_version"] is False
    assert res["study_objective"]["endpoint_count"] == 2
    assert res["study_objective"]["accepted_version"] is False
    assert res["study_objective"]["start_date"]
    assert res["study_objective"]["author_username"] == "unknown-user@example.com"
    assert (
        res["study_objective"]["objective"]["change_description"] == "Approved version"
    )
    assert res["study_objective"]["objective"]["end_date"] is None
    assert res["study_objective"]["objective"]["library"]["is_editable"] is True
    assert res["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    assert res["study_objective"]["objective"]["name"] == "objective_1"
    assert res["study_objective"]["objective"]["name_plain"] == "objective_1"
    assert res["study_objective"]["objective"]["template"]["name"] == "objective_1"
    assert (
        res["study_objective"]["objective"]["template"]["name_plain"] == "objective_1"
    )
    assert (
        res["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert res["study_objective"]["objective"]["template"]["sequence_id"] == "O1"
    assert res["study_objective"]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["study_objective"]["objective"]["possible_actions"] == ["inactivate"]
    assert res["study_objective"]["objective"]["start_date"]
    assert res["study_objective"]["objective"]["status"] == "Final"
    assert res["study_objective"]["objective"]["study_count"] == 0
    assert res["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["study_objective"]["objective"]["version"] == "1.0"
    assert res["study_objective"]["latest_objective"] is None
    assert res["study_objective"]["objective_level"] is None
    assert res["study_objective"]["order"] == 1
    assert res["study_objective"]["project_number"] == "123"
    assert res["study_objective"]["project_name"] == "Project ABC"
    assert res["study_objective"]["study_version"]
    assert res["study_objective"]["study_objective_uid"] == "StudyObjective_000001"
    assert res["study_objective"]["study_uid"] == "study_root"
    assert res["study_uid"] == "study_root"
    assert res["timeframe"] is None


def test_check_list_has_2(api_client):
    response = api_client.get("/studies/study_root/study-endpoints")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["latest_endpoint"] is None
    assert res["items"][0]["latest_timeframe"] is None
    assert res["items"][0]["accepted_version"] is False
    assert res["items"][0]["endpoint"]["change_description"] == "Approved version"
    assert res["items"][0]["endpoint"]["end_date"] is None
    assert res["items"][0]["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["items"][0]["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["items"][0]["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["items"][0]["endpoint"]["library"]["is_editable"] is True
    assert res["items"][0]["endpoint"]["library"]["name"] == "Sponsor"
    assert res["items"][0]["endpoint"]["name"] == "endpoint_1"
    assert res["items"][0]["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["items"][0]["endpoint"]["parameter_terms"]) == 0
    assert res["items"][0]["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["endpoint"]["start_date"]
    assert res["items"][0]["endpoint"]["status"] == "Final"
    assert res["items"][0]["endpoint"]["study_count"] == 0
    assert res["items"][0]["endpoint"]["uid"] == "Endpoint_000001"
    assert res["items"][0]["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["endpoint"]["version"] == "1.0"
    assert res["items"][0]["endpoint_level"]["term_uid"] == "term_root_final"
    assert res["items"][0]["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["items"][0]["endpoint_level"]["codelists"]) == 1
    assert (
        res["items"][0]["endpoint_level"]["codelists"][0]["codelist_uid"]
        == "editable_cr"
    )
    assert res["items"][0]["endpoint_level"]["codelists"][0]["order"] == 1
    assert (
        res["items"][0]["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    )
    assert (
        res["items"][0]["endpoint_level"]["sponsor_preferred_name"]
        == "term_value_name1"
    )
    assert (
        res["items"][0]["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["items"][0]["endpoint_level"]["library_name"] == "Sponsor"
    assert res["items"][0]["endpoint_level"]["start_date"]
    assert res["items"][0]["endpoint_level"]["end_date"] is None
    assert res["items"][0]["endpoint_level"]["status"] == "Final"
    assert res["items"][0]["endpoint_level"]["version"] == "1.0"
    assert res["items"][0]["endpoint_level"]["change_description"] == "Approved version"
    assert (
        res["items"][0]["endpoint_level"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["endpoint_level"]["queried_effective_date"] is None
    assert res["items"][0]["endpoint_level"]["date_conflict"] is False
    assert res["items"][0]["endpoint_level"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert (
        res["items"][0]["endpoint_sublevel"]["term_uid"] == "term_root_final_non_edit"
    )
    assert res["items"][0]["endpoint_sublevel"]["catalogue_name"] == "SDTM CT"
    assert len(res["items"][0]["endpoint_sublevel"]["codelists"]) == 1
    assert (
        res["items"][0]["endpoint_sublevel"]["codelists"][0]["codelist_uid"]
        == "non_editable_cr"
    )
    assert res["items"][0]["endpoint_sublevel"]["codelists"][0]["order"] == 3
    assert (
        res["items"][0]["endpoint_sublevel"]["codelists"][0]["library_name"] == "CDISC"
    )
    assert (
        res["items"][0]["endpoint_sublevel"]["sponsor_preferred_name"]
        == "term_value_name3"
    )
    assert (
        res["items"][0]["endpoint_sublevel"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["items"][0]["endpoint_sublevel"]["library_name"] == "CDISC"
    assert res["items"][0]["endpoint_sublevel"]["start_date"]
    assert res["items"][0]["endpoint_sublevel"]["end_date"] is None
    assert res["items"][0]["endpoint_sublevel"]["status"] == "Final"
    assert res["items"][0]["endpoint_sublevel"]["version"] == "1.0"
    assert (
        res["items"][0]["endpoint_sublevel"]["change_description"] == "Approved version"
    )
    assert (
        res["items"][0]["endpoint_sublevel"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["endpoint_sublevel"]["queried_effective_date"] is None
    assert res["items"][0]["endpoint_sublevel"]["date_conflict"] is False
    assert res["items"][0]["endpoint_sublevel"]["possible_actions"] == [
        "inactivate",
        "new_version",
    ]
    assert res["items"][0]["endpoint_units"]["separator"] == "string"
    assert len(res["items"][0]["endpoint_units"]["units"]) == 2
    assert res["items"][0]["endpoint_units"]["units"][0]["uid"] == "unit 1"
    assert res["items"][0]["endpoint_units"]["units"][0]["name"] == "name 1"
    assert res["items"][0]["endpoint_units"]["units"][1]["uid"] == "unit 2"
    assert res["items"][0]["endpoint_units"]["units"][1]["name"] == "name 2"
    assert res["items"][0]["start_date"]
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["project_number"] == "123"
    assert res["items"][0]["project_name"] == "Project ABC"
    assert res["items"][0]["study_version"]
    assert res["items"][0]["study_endpoint_uid"] == "StudyEndpoint_000001"
    assert res["items"][0]["study_objective"]["endpoint_count"] == 2
    assert res["items"][0]["study_objective"]["accepted_version"] is False
    assert res["items"][0]["study_objective"]["start_date"]
    assert (
        res["items"][0]["study_objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["change_description"]
        == "Approved version"
    )
    assert res["items"][0]["study_objective"]["objective"]["end_date"] is None
    assert (
        res["items"][0]["study_objective"]["objective"]["library"]["is_editable"]
        is True
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    )
    assert res["items"][0]["study_objective"]["objective"]["name"] == "objective_1"
    assert (
        res["items"][0]["study_objective"]["objective"]["name_plain"] == "objective_1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["name"]
        == "objective_1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["name_plain"]
        == "objective_1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["sequence_id"]
        == "O1"
    )
    assert (
        res["items"][0]["study_objective"]["objective"]["template"]["library_name"]
        == "Sponsor"
    )
    assert len(res["items"][0]["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["items"][0]["study_objective"]["objective"]["possible_actions"] == [
        "inactivate"
    ]
    assert res["items"][0]["study_objective"]["objective"]["start_date"]
    assert res["items"][0]["study_objective"]["objective"]["status"] == "Final"
    assert res["items"][0]["study_objective"]["objective"]["study_count"] == 0
    assert res["items"][0]["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["items"][0]["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][0]["study_objective"]["objective"]["version"] == "1.0"
    assert res["items"][0]["study_objective"]["latest_objective"] is None
    assert res["items"][0]["study_objective"]["objective_level"] is None
    assert res["items"][0]["study_objective"]["order"] == 1
    assert res["items"][0]["study_objective"]["project_number"] == "123"
    assert res["items"][0]["study_objective"]["project_name"] == "Project ABC"
    assert res["items"][0]["study_objective"]["study_version"]
    assert (
        res["items"][0]["study_objective"]["study_objective_uid"]
        == "StudyObjective_000001"
    )
    assert res["items"][0]["study_objective"]["study_uid"] == "study_root"
    assert res["items"][0]["study_uid"] == "study_root"
    assert res["items"][0]["timeframe"]["study_count"] == 0
    assert res["items"][0]["timeframe"]["change_description"] == "Approved version"
    assert res["items"][0]["timeframe"]["end_date"] is None
    assert res["items"][0]["timeframe"]["library"]["is_editable"] is True
    assert res["items"][0]["timeframe"]["library"]["name"] == "Sponsor"
    assert res["items"][0]["timeframe"]["name"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["name_plain"] == "timeframe_1"
    assert len(res["items"][0]["timeframe"]["parameter_terms"]) == 0
    assert res["items"][0]["timeframe"]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["timeframe"]["start_date"]
    assert res["items"][0]["timeframe"]["status"] == "Final"
    assert res["items"][0]["timeframe"]["template"]["name"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["template"]["name_plain"] == "timeframe_1"
    assert res["items"][0]["timeframe"]["template"]["uid"] == "TimeframeTemplate_000011"
    assert res["items"][0]["timeframe"]["template"]["sequence_id"] == "T11"
    assert res["items"][0]["timeframe"]["template"]["library_name"] == "Sponsor"
    assert res["items"][0]["timeframe"]["uid"] == "Timeframe_000001"
    assert res["items"][0]["timeframe"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["timeframe"]["version"] == "1.0"

    assert res["items"][1]["latest_endpoint"] is None
    assert res["items"][1]["latest_timeframe"] is None
    assert res["items"][1]["endpoint"]["change_description"] == "Approved version"
    assert res["items"][1]["endpoint"]["end_date"] is None
    assert res["items"][1]["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["items"][1]["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["items"][1]["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["items"][1]["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["items"][1]["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["items"][1]["endpoint"]["library"]["is_editable"] is True
    assert res["items"][1]["endpoint"]["library"]["name"] == "Sponsor"
    assert res["items"][1]["endpoint"]["name"] == "endpoint_1"
    assert res["items"][1]["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["items"][1]["endpoint"]["parameter_terms"]) == 0
    assert res["items"][1]["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["items"][1]["endpoint"]["start_date"]
    assert res["items"][1]["endpoint"]["status"] == "Final"
    assert res["items"][1]["endpoint"]["study_count"] == 0
    assert res["items"][1]["endpoint"]["uid"] == "Endpoint_000001"
    assert res["items"][1]["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["items"][1]["endpoint"]["version"] == "1.0"
    assert res["items"][1]["endpoint_level"] is None
    assert res["items"][1]["endpoint_sublevel"] is None
    assert res["items"][1]["endpoint_units"] == {"separator": None, "units": []}
    assert res["items"][1]["start_date"]
    assert res["items"][1]["author_username"] == "unknown-user@example.com"
    assert res["items"][1]["order"] == 2
    assert res["items"][1]["project_number"] == "123"
    assert res["items"][1]["project_name"] == "Project ABC"
    assert res["items"][1]["study_version"]
    assert res["items"][1]["study_endpoint_uid"] == "StudyEndpoint_000003"
    assert res["items"][1]["accepted_version"] is False
    assert res["items"][1]["study_objective"]["endpoint_count"] == 2
    assert res["items"][1]["study_objective"]["accepted_version"] is False
    assert res["items"][1]["study_objective"]["start_date"]
    assert (
        res["items"][1]["study_objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert (
        res["items"][1]["study_objective"]["objective"]["change_description"]
        == "Approved version"
    )
    assert res["items"][1]["study_objective"]["objective"]["end_date"] is None
    assert (
        res["items"][1]["study_objective"]["objective"]["library"]["is_editable"]
        is True
    )
    assert (
        res["items"][1]["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    )
    assert res["items"][1]["study_objective"]["objective"]["name"] == "objective_1"
    assert (
        res["items"][1]["study_objective"]["objective"]["name_plain"] == "objective_1"
    )
    assert (
        res["items"][1]["study_objective"]["objective"]["template"]["name"]
        == "objective_1"
    )
    assert (
        res["items"][1]["study_objective"]["objective"]["template"]["name_plain"]
        == "objective_1"
    )
    assert (
        res["items"][1]["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert (
        res["items"][1]["study_objective"]["objective"]["template"]["sequence_id"]
        == "O1"
    )
    assert (
        res["items"][1]["study_objective"]["objective"]["template"]["library_name"]
        == "Sponsor"
    )
    assert len(res["items"][1]["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["items"][1]["study_objective"]["objective"]["possible_actions"] == [
        "inactivate"
    ]
    assert res["items"][1]["study_objective"]["objective"]["start_date"]
    assert res["items"][1]["study_objective"]["objective"]["status"] == "Final"
    assert res["items"][1]["study_objective"]["objective"]["study_count"] == 0
    assert res["items"][1]["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["items"][1]["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["items"][1]["study_objective"]["objective"]["version"] == "1.0"
    assert res["items"][1]["study_objective"]["latest_objective"] is None
    assert res["items"][1]["study_objective"]["objective_level"] is None
    assert res["items"][1]["study_objective"]["order"] == 1
    assert res["items"][1]["study_objective"]["project_number"] == "123"
    assert res["items"][1]["study_objective"]["project_name"] == "Project ABC"
    assert res["items"][1]["study_objective"]["study_version"]
    assert (
        res["items"][1]["study_objective"]["study_objective_uid"]
        == "StudyObjective_000001"
    )
    assert res["items"][1]["study_objective"]["study_uid"] == "study_root"
    assert res["items"][1]["study_uid"] == "study_root"
    assert res["items"][1]["timeframe"] is None
    assert res["total"] == 0


def test_get_specific6(api_client):
    response = api_client.get(
        "/studies/study_root/study-endpoints/StudyEndpoint_000003"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["latest_endpoint"] is None
    assert res["latest_timeframe"] is None
    assert res["endpoint"]["change_description"] == "Approved version"
    assert res["endpoint"]["end_date"] is None
    assert res["endpoint"]["library"]["is_editable"] is True
    assert res["endpoint"]["library"]["name"] == "Sponsor"
    assert res["endpoint"]["name"] == "endpoint_1"
    assert res["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["endpoint"]["parameter_terms"]) == 0
    assert res["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["endpoint"]["start_date"]
    assert res["endpoint"]["status"] == "Final"
    assert res["endpoint"]["study_count"] == 0
    assert res["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["endpoint"]["uid"] == "Endpoint_000001"
    assert res["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint"]["version"] == "1.0"
    assert res["endpoint_level"] is None
    assert res["endpoint_sublevel"] is None
    assert res["endpoint_units"] == {"separator": None, "units": []}
    assert res["author_username"] == "unknown-user@example.com"
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_version"]
    assert res["study_endpoint_uid"] == "StudyEndpoint_000003"
    assert res["accepted_version"] is False
    assert res["study_objective"]["accepted_version"] is False
    assert res["study_objective"]["endpoint_count"] == 2
    assert res["study_objective"]["start_date"]
    assert res["study_objective"]["author_username"] == "unknown-user@example.com"
    assert res["study_objective"]["latest_objective"] is None
    assert (
        res["study_objective"]["objective"]["change_description"] == "Approved version"
    )
    assert res["study_objective"]["objective"]["end_date"] is None
    assert res["study_objective"]["objective"]["library"]["is_editable"] is True
    assert res["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    assert res["study_objective"]["objective"]["name"] == "objective_1"
    assert res["study_objective"]["objective"]["name_plain"] == "objective_1"
    assert res["study_objective"]["objective"]["template"]["name"] == "objective_1"
    assert (
        res["study_objective"]["objective"]["template"]["name_plain"] == "objective_1"
    )
    assert (
        res["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert res["study_objective"]["objective"]["template"]["sequence_id"] == "O1"
    assert res["study_objective"]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["study_objective"]["objective"]["possible_actions"] == ["inactivate"]
    assert res["study_objective"]["objective"]["start_date"]
    assert res["study_objective"]["objective"]["status"] == "Final"
    assert res["study_objective"]["objective"]["study_count"] == 0
    assert res["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["study_objective"]["objective"]["version"] == "1.0"
    assert res["study_objective"]["objective_level"] is None
    assert res["study_objective"]["order"] == 1
    assert res["study_objective"]["project_number"] == "123"
    assert res["study_objective"]["project_name"] == "Project ABC"
    assert res["study_objective"]["study_version"]
    assert res["study_objective"]["study_objective_uid"] == "StudyObjective_000001"
    assert res["study_objective"]["study_uid"] == "study_root"
    assert res["study_uid"] == "study_root"
    assert res["timeframe"] is None


def test_reorder_specific5(api_client):
    data = {"new_order": 5}
    response = api_client.patch(
        "/studies/study_root/study-endpoints/StudyEndpoint_000003/order", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["latest_endpoint"] is None
    assert res["latest_timeframe"] is None
    assert res["endpoint"]["change_description"] == "Approved version"
    assert res["endpoint"]["end_date"] is None
    assert res["endpoint"]["library"]["is_editable"] is True
    assert res["endpoint"]["library"]["name"] == "Sponsor"
    assert res["endpoint"]["name"] == "endpoint_1"
    assert res["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["endpoint"]["parameter_terms"]) == 0
    assert res["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["endpoint"]["start_date"]
    assert res["endpoint"]["status"] == "Final"
    assert res["endpoint"]["study_count"] == 0
    assert res["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["endpoint"]["uid"] == "Endpoint_000001"
    assert res["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint"]["version"] == "1.0"
    assert res["endpoint_level"] is None
    assert res["endpoint_sublevel"] is None
    assert res["endpoint_units"] == {"separator": None, "units": []}
    assert res["author_username"] == "unknown-user@example.com"
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_version"]
    assert res["study_endpoint_uid"] == "StudyEndpoint_000003"
    assert res["accepted_version"] is False
    assert res["study_objective"]["accepted_version"] is False
    assert res["study_objective"]["endpoint_count"] == 2
    assert res["study_objective"]["start_date"]
    assert res["study_objective"]["author_username"] == "unknown-user@example.com"
    assert res["study_objective"]["latest_objective"] is None
    assert (
        res["study_objective"]["objective"]["change_description"] == "Approved version"
    )
    assert res["study_objective"]["objective"]["end_date"] is None
    assert res["study_objective"]["objective"]["library"]["is_editable"] is True
    assert res["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    assert res["study_objective"]["objective"]["name"] == "objective_1"
    assert res["study_objective"]["objective"]["name_plain"] == "objective_1"
    assert res["study_objective"]["objective"]["template"]["name"] == "objective_1"
    assert (
        res["study_objective"]["objective"]["template"]["name_plain"] == "objective_1"
    )
    assert (
        res["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert res["study_objective"]["objective"]["template"]["sequence_id"] == "O1"
    assert res["study_objective"]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["study_objective"]["objective"]["possible_actions"] == ["inactivate"]
    assert res["study_objective"]["objective"]["start_date"]
    assert res["study_objective"]["objective"]["status"] == "Final"
    assert res["study_objective"]["objective"]["study_count"] == 0
    assert res["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["study_objective"]["objective"]["version"] == "1.0"
    assert res["study_objective"]["objective_level"] is None
    assert res["study_objective"]["order"] == 1
    assert res["study_objective"]["project_number"] == "123"
    assert res["study_objective"]["project_name"] == "Project ABC"
    assert res["study_objective"]["study_version"]
    assert res["study_objective"]["study_objective_uid"] == "StudyObjective_000001"
    assert res["study_objective"]["study_uid"] == "study_root"
    assert res["study_uid"] == "study_root"
    assert res["timeframe"] is None


def test_patch_specific_new_endpoint_level(api_client):
    data = {"endpoint_level_uid": "term_root_final"}
    response = api_client.patch(
        "/studies/study_root/study-endpoints/StudyEndpoint_000003", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["latest_endpoint"] is None
    assert res["latest_timeframe"] is None
    assert res["endpoint"]["change_description"] == "Approved version"
    assert res["endpoint"]["end_date"] is None
    assert res["endpoint"]["library"]["is_editable"] is True
    assert res["endpoint"]["library"]["name"] == "Sponsor"
    assert res["endpoint"]["name"] == "endpoint_1"
    assert res["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["endpoint"]["parameter_terms"]) == 0
    assert res["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["endpoint"]["start_date"]
    assert res["endpoint"]["status"] == "Final"
    assert res["endpoint"]["study_count"] == 0
    assert res["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["endpoint"]["uid"] == "Endpoint_000001"
    assert res["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint"]["version"] == "1.0"
    assert res["endpoint_level"]["term_uid"] == "term_root_final"
    assert res["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["endpoint_level"]["codelists"]) == 1
    assert res["endpoint_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res["endpoint_level"]["codelists"][0]["order"] == 1
    assert res["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["endpoint_level"]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["start_date"]
    assert res["endpoint_level"]["end_date"] is None
    assert res["endpoint_level"]["status"] == "Final"
    assert res["endpoint_level"]["version"] == "1.0"
    assert res["endpoint_level"]["change_description"] == "Approved version"
    assert res["endpoint_level"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint_level"]["queried_effective_date"] is None
    assert res["endpoint_level"]["date_conflict"] is False
    assert res["endpoint_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["endpoint_sublevel"] is None
    assert res["endpoint_units"] == {"separator": None, "units": []}
    assert res["author_username"] == "unknown-user@example.com"
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_version"]
    assert res["study_endpoint_uid"] == "StudyEndpoint_000003"
    assert res["accepted_version"] is False
    assert res["study_objective"]["accepted_version"] is False
    assert res["study_objective"]["endpoint_count"] == 2
    assert res["study_objective"]["start_date"]
    assert res["study_objective"]["author_username"] == "unknown-user@example.com"
    assert res["study_objective"]["latest_objective"] is None
    assert (
        res["study_objective"]["objective"]["change_description"] == "Approved version"
    )
    assert res["study_objective"]["objective"]["end_date"] is None
    assert res["study_objective"]["objective"]["library"]["is_editable"] is True
    assert res["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    assert res["study_objective"]["objective"]["name"] == "objective_1"
    assert res["study_objective"]["objective"]["name_plain"] == "objective_1"
    assert res["study_objective"]["objective"]["template"]["name"] == "objective_1"
    assert (
        res["study_objective"]["objective"]["template"]["name_plain"] == "objective_1"
    )
    assert (
        res["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert res["study_objective"]["objective"]["template"]["sequence_id"] == "O1"
    assert res["study_objective"]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["study_objective"]["objective"]["possible_actions"] == ["inactivate"]
    assert res["study_objective"]["objective"]["start_date"]
    assert res["study_objective"]["objective"]["status"] == "Final"
    assert res["study_objective"]["objective"]["study_count"] == 0
    assert res["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["study_objective"]["objective"]["version"] == "1.0"
    assert res["study_objective"]["objective_level"] is None
    assert res["study_objective"]["order"] == 1
    assert res["study_objective"]["project_number"] == "123"
    assert res["study_objective"]["project_name"] == "Project ABC"
    assert res["study_objective"]["study_version"]
    assert res["study_objective"]["study_objective_uid"] == "StudyObjective_000001"
    assert res["study_objective"]["study_uid"] == "study_root"
    assert res["study_uid"] == "study_root"
    assert res["timeframe"] is None


def test_patch_specific_new_study_objective(api_client):
    data = {"study_objective_uid": "StudyObjective_000001"}
    response = api_client.patch(
        "/studies/study_root/study-endpoints/StudyEndpoint_000003", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["latest_endpoint"] is None
    assert res["latest_timeframe"] is None
    assert res["endpoint"]["change_description"] == "Approved version"
    assert res["endpoint"]["end_date"] is None
    assert res["endpoint"]["library"]["is_editable"] is True
    assert res["endpoint"]["library"]["name"] == "Sponsor"
    assert res["endpoint"]["name"] == "endpoint_1"
    assert res["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["endpoint"]["parameter_terms"]) == 0
    assert res["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["endpoint"]["start_date"]
    assert res["endpoint"]["status"] == "Final"
    assert res["endpoint"]["study_count"] == 0
    assert res["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["endpoint"]["uid"] == "Endpoint_000001"
    assert res["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint"]["version"] == "1.0"
    assert res["endpoint_level"]["term_uid"] == "term_root_final"
    assert res["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["endpoint_level"]["codelists"]) == 1
    assert res["endpoint_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res["endpoint_level"]["codelists"][0]["order"] == 1
    assert res["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["endpoint_level"]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["start_date"]
    assert res["endpoint_level"]["end_date"] is None
    assert res["endpoint_level"]["status"] == "Final"
    assert res["endpoint_level"]["version"] == "1.0"
    assert res["endpoint_level"]["change_description"] == "Approved version"
    assert res["endpoint_level"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint_level"]["queried_effective_date"] is None
    assert res["endpoint_level"]["date_conflict"] is False
    assert res["endpoint_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["endpoint_sublevel"] is None
    assert res["endpoint_units"] == {"separator": None, "units": []}
    assert res["author_username"] == "unknown-user@example.com"
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_version"]
    assert res["study_endpoint_uid"] == "StudyEndpoint_000003"
    assert res["accepted_version"] is False
    assert res["study_objective"]["accepted_version"] is False
    assert res["study_objective"]["endpoint_count"] == 2
    assert res["study_objective"]["start_date"]
    assert res["study_objective"]["author_username"] == "unknown-user@example.com"
    assert res["study_objective"]["latest_objective"] is None
    assert (
        res["study_objective"]["objective"]["change_description"] == "Approved version"
    )
    assert res["study_objective"]["objective"]["end_date"] is None
    assert res["study_objective"]["objective"]["library"]["is_editable"] is True
    assert res["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    assert res["study_objective"]["objective"]["name"] == "objective_1"
    assert res["study_objective"]["objective"]["name_plain"] == "objective_1"
    assert res["study_objective"]["objective"]["template"]["name"] == "objective_1"
    assert (
        res["study_objective"]["objective"]["template"]["name_plain"] == "objective_1"
    )
    assert (
        res["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert res["study_objective"]["objective"]["template"]["sequence_id"] == "O1"
    assert res["study_objective"]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["study_objective"]["objective"]["possible_actions"] == ["inactivate"]
    assert res["study_objective"]["objective"]["start_date"]
    assert res["study_objective"]["objective"]["status"] == "Final"
    assert res["study_objective"]["objective"]["study_count"] == 0
    assert res["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["study_objective"]["objective"]["version"] == "1.0"
    assert res["study_objective"]["objective_level"] is None
    assert res["study_objective"]["order"] == 1
    assert res["study_objective"]["project_number"] == "123"
    assert res["study_objective"]["project_name"] == "Project ABC"
    assert res["study_objective"]["study_version"]
    assert res["study_objective"]["study_objective_uid"] == "StudyObjective_000001"
    assert res["study_objective"]["study_uid"] == "study_root"
    assert res["study_uid"] == "study_root"
    assert res["timeframe"] is None


def test_patch_specific_remove_study_objective(api_client):
    data = {"study_objective_uid": None}
    response = api_client.patch(
        "/studies/study_root/study-endpoints/StudyEndpoint_000003", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["latest_endpoint"] is None
    assert res["latest_timeframe"] is None
    assert res["endpoint"]["change_description"] == "Approved version"
    assert res["endpoint"]["end_date"] is None
    assert res["endpoint"]["library"]["is_editable"] is True
    assert res["endpoint"]["library"]["name"] == "Sponsor"
    assert res["endpoint"]["name"] == "endpoint_1"
    assert res["endpoint"]["name_plain"] == "endpoint_1"
    assert len(res["endpoint"]["parameter_terms"]) == 0
    assert res["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["endpoint"]["start_date"]
    assert res["endpoint"]["status"] == "Final"
    assert res["endpoint"]["study_count"] == 0
    assert res["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["endpoint"]["template"]["name"] == "endpoint_1"
    assert res["endpoint"]["template"]["name_plain"] == "endpoint_1"
    assert res["endpoint"]["template"]["sequence_id"] == "E1"
    assert res["endpoint"]["template"]["uid"] == "EndpointTemplate_000001"
    assert res["endpoint"]["uid"] == "Endpoint_000001"
    assert res["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint"]["version"] == "1.0"
    assert res["endpoint_level"]["term_uid"] == "term_root_final"
    assert res["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["endpoint_level"]["codelists"]) == 1
    assert res["endpoint_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res["endpoint_level"]["codelists"][0]["order"] == 1
    assert res["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["endpoint_level"]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["start_date"]
    assert res["endpoint_level"]["end_date"] is None
    assert res["endpoint_level"]["status"] == "Final"
    assert res["endpoint_level"]["version"] == "1.0"
    assert res["endpoint_level"]["change_description"] == "Approved version"
    assert res["endpoint_level"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint_level"]["queried_effective_date"] is None
    assert res["endpoint_level"]["date_conflict"] is False
    assert res["endpoint_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["endpoint_sublevel"] is None
    assert res["endpoint_units"] == {"separator": None, "units": []}
    assert res["author_username"] == "unknown-user@example.com"
    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_version"]
    assert res["study_endpoint_uid"] == "StudyEndpoint_000003"
    assert res["accepted_version"] is False
    assert res["study_objective"] is None
    assert res["study_uid"] == "study_root"
    assert res["timeframe"] is None


def test_get_all_endpoints_with_proper_study_count(api_client):
    response = api_client.get("/endpoints?total_count=True")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["uid"] == "Endpoint_000001"
    assert res["items"][0]["name"] == "endpoint_1"
    assert res["items"][0]["name_plain"] == "endpoint_1"
    assert res["items"][0]["end_date"] is None
    assert res["items"][0]["status"] == "Final"
    assert res["items"][0]["version"] == "1.0"
    assert res["items"][0]["change_description"] == "Approved version"
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["possible_actions"] == ["inactivate"]
    assert res["items"][0]["template"] == {
        "name": "endpoint_1",
        "name_plain": "endpoint_1",
        "guidance_text": None,
        "uid": "EndpointTemplate_000001",
        "sequence_id": "E1",
        "library_name": "Sponsor",
    }
    assert res["items"][0]["parameter_terms"] == []
    assert res["items"][0]["library"] == {"name": "Sponsor", "is_editable": True}
    assert res["items"][0]["study_count"] == 1


def test_previewing_selection_create(api_client):
    data = {
        "endpoint_data": {
            "library_name": "Sponsor",
            "endpoint_template_uid": "EndpointTemplate_000022",
            "parameter_terms": [],
        },
        "endpoint_level_uid": "term_root_final",
        "endpoint_units": {"separator": "string", "units": ["unit 1", "unit 2"]},
        "study_objective_uid": "StudyObjective_000001",
        "timeframe_uid": "Timeframe_000001",
    }
    response = api_client.post("/studies/study_root/study-endpoints/preview", json=data)

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_uid"] == "study_root"
    assert res["study_version"]
    assert res["study_endpoint_uid"] == "preview"
    assert res["study_objective"]["accepted_version"] is False
    assert res["study_objective"]["endpoint_count"] == 1
    assert res["study_objective"]["latest_objective"] is None
    assert (
        res["study_objective"]["objective"]["change_description"] == "Approved version"
    )
    assert res["study_objective"]["objective"]["end_date"] is None
    assert res["study_objective"]["objective"]["library"]["is_editable"] is True
    assert res["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    assert res["study_objective"]["objective"]["name"] == "objective_1"
    assert res["study_objective"]["objective"]["name_plain"] == "objective_1"
    assert len(res["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["study_objective"]["objective"]["possible_actions"] == ["inactivate"]
    assert res["study_objective"]["objective"]["start_date"]
    assert res["study_objective"]["objective"]["status"] == "Final"
    assert res["study_objective"]["objective"]["study_count"] == 0
    assert res["study_objective"]["objective"]["template"]["library_name"] == "Sponsor"
    assert res["study_objective"]["objective"]["template"]["name"] == "objective_1"
    assert (
        res["study_objective"]["objective"]["template"]["name_plain"] == "objective_1"
    )
    assert res["study_objective"]["objective"]["template"]["sequence_id"] == "O1"
    assert (
        res["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert res["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["study_objective"]["objective"]["version"] == "1.0"
    assert res["study_objective"]["objective_level"] is None
    assert res["study_objective"]["order"] == 1
    assert res["study_objective"]["project_name"] == "Project ABC"
    assert res["study_objective"]["project_number"] == "123"
    assert res["study_objective"]["start_date"]
    assert res["study_objective"]["study_objective_uid"] == "StudyObjective_000001"
    assert res["study_objective"]["study_uid"] == "study_root"
    assert res["study_objective"]["study_version"]
    assert res["study_objective"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint_level"]["term_uid"] == "term_root_final"
    assert res["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["endpoint_level"]["codelists"]) == 1
    assert res["endpoint_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res["endpoint_level"]["codelists"][0]["order"] == 1
    assert res["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["endpoint_level"]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["start_date"]
    assert res["endpoint_level"]["end_date"] is None
    assert res["endpoint_level"]["status"] == "Final"
    assert res["endpoint_level"]["version"] == "1.0"
    assert res["endpoint_level"]["change_description"] == "Approved version"
    assert res["endpoint_level"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint_level"]["queried_effective_date"] is None
    assert res["endpoint_level"]["date_conflict"] is False
    assert res["endpoint_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["endpoint_sublevel"] is None
    assert res["endpoint_units"] == {"separator": None, "units": []}
    assert res["endpoint"]["change_description"] == "Approved version"
    assert res["endpoint"]["end_date"] is None
    assert res["endpoint"]["template"]["name"] == "endpoint_template_2"
    assert res["endpoint"]["template"]["name_plain"] == "endpoint_template_2"
    assert res["endpoint"]["template"]["uid"] == "EndpointTemplate_000022"
    assert res["endpoint"]["template"]["sequence_id"] == "E22"
    assert res["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["endpoint"]["library"]["is_editable"] is True
    assert res["endpoint"]["library"]["name"] == "Sponsor"
    assert res["endpoint"]["name"] == "endpoint_template_2"
    assert res["endpoint"]["name_plain"] == "endpoint_template_2"
    assert len(res["endpoint"]["parameter_terms"]) == 0
    assert res["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["endpoint"]["start_date"]
    assert res["endpoint"]["status"] == "Final"
    assert res["endpoint"]["study_count"] == 0
    assert res["endpoint"]["uid"] == "preview"
    assert res["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint"]["version"] == "1.0"
    assert res["timeframe"]["study_count"] == 0
    assert res["timeframe"]["change_description"] == "Approved version"
    assert res["timeframe"]["end_date"] is None
    assert res["timeframe"]["library"]["is_editable"] is True
    assert res["timeframe"]["library"]["name"] == "Sponsor"
    assert res["timeframe"]["name"] == "timeframe_1"
    assert res["timeframe"]["name_plain"] == "timeframe_1"
    assert len(res["timeframe"]["parameter_terms"]) == 0
    assert res["timeframe"]["possible_actions"] == ["inactivate"]
    assert res["timeframe"]["start_date"]
    assert res["timeframe"]["status"] == "Final"
    assert res["timeframe"]["template"]["name"] == "timeframe_1"
    assert res["timeframe"]["template"]["name_plain"] == "timeframe_1"
    assert res["timeframe"]["template"]["uid"] == "TimeframeTemplate_000011"
    assert res["timeframe"]["template"]["sequence_id"] == "T11"
    assert res["timeframe"]["template"]["library_name"] == "Sponsor"
    assert res["timeframe"]["uid"] == "Timeframe_000001"
    assert res["timeframe"]["author_username"] == "unknown-user@example.com"
    assert res["timeframe"]["version"] == "1.0"
    assert res["latest_endpoint"] is None
    assert res["latest_timeframe"] is None
    assert res["author_username"] == "unknown-user@example.com"
    assert res["accepted_version"] is False


def test_adding_selection_create(api_client):
    data = {
        "endpoint_data": {
            "library_name": "Sponsor",
            "endpoint_template_uid": "EndpointTemplate_000022",
            "parameter_terms": [],
        },
        "endpoint_level_uid": "term_root_final",
        "endpoint_units": {"separator": "string", "units": ["unit 1", "unit 2"]},
        "study_objective_uid": "StudyObjective_000001",
        "timeframe_uid": "Timeframe_000001",
    }
    response = api_client.post(
        "/studies/study_root/study-endpoints?create_endpoint=true", json=data
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["order"] == 2
    assert res["project_number"] == "123"
    assert res["project_name"] == "Project ABC"
    assert res["study_uid"] == "study_root"
    assert res["study_version"]
    assert res["study_endpoint_uid"] == "StudyEndpoint_000008"
    assert res["study_objective"]["endpoint_count"] == 2
    assert res["study_objective"]["accepted_version"] is False
    assert res["study_objective"]["start_date"]
    assert res["study_objective"]["author_username"] == "unknown-user@example.com"
    assert (
        res["study_objective"]["objective"]["change_description"] == "Approved version"
    )
    assert res["study_objective"]["objective"]["end_date"] is None
    assert res["study_objective"]["objective"]["library"]["is_editable"] is True
    assert res["study_objective"]["objective"]["library"]["name"] == "Sponsor"
    assert res["study_objective"]["objective"]["name"] == "objective_1"
    assert res["study_objective"]["objective"]["name_plain"] == "objective_1"
    assert res["study_objective"]["objective"]["template"]["name"] == "objective_1"
    assert (
        res["study_objective"]["objective"]["template"]["name_plain"] == "objective_1"
    )
    assert (
        res["study_objective"]["objective"]["template"]["uid"]
        == "ObjectiveTemplate_000001"
    )
    assert res["study_objective"]["objective"]["template"]["sequence_id"] == "O1"
    assert res["study_objective"]["objective"]["template"]["library_name"] == "Sponsor"
    assert len(res["study_objective"]["objective"]["parameter_terms"]) == 0
    assert res["study_objective"]["objective"]["possible_actions"] == ["inactivate"]
    assert res["study_objective"]["objective"]["start_date"]
    assert res["study_objective"]["objective"]["status"] == "Final"
    assert res["study_objective"]["objective"]["study_count"] == 0
    assert res["study_objective"]["objective"]["uid"] == "Objective_000001"
    assert (
        res["study_objective"]["objective"]["author_username"]
        == "unknown-user@example.com"
    )
    assert res["study_objective"]["objective"]["version"] == "1.0"
    assert res["study_objective"]["latest_objective"] is None
    assert res["study_objective"]["objective_level"] is None
    assert res["study_objective"]["order"] == 1
    assert res["study_objective"]["project_number"] == "123"
    assert res["study_objective"]["project_name"] == "Project ABC"
    assert res["study_objective"]["study_version"]
    assert res["study_objective"]["study_objective_uid"] == "StudyObjective_000001"
    assert res["study_objective"]["study_uid"] == "study_root"
    assert res["endpoint_level"]["term_uid"] == "term_root_final"
    assert res["endpoint_level"]["catalogue_name"] == "SDTM CT"
    assert len(res["endpoint_level"]["codelists"]) == 1
    assert res["endpoint_level"]["codelists"][0]["codelist_uid"] == "editable_cr"
    assert res["endpoint_level"]["codelists"][0]["order"] == 1
    assert res["endpoint_level"]["codelists"][0]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["sponsor_preferred_name"] == "term_value_name1"
    assert (
        res["endpoint_level"]["sponsor_preferred_name_sentence_case"]
        == "term_value_name_sentence_case"
    )
    assert res["endpoint_level"]["library_name"] == "Sponsor"
    assert res["endpoint_level"]["start_date"]
    assert res["endpoint_level"]["end_date"] is None
    assert res["endpoint_level"]["status"] == "Final"
    assert res["endpoint_level"]["version"] == "1.0"
    assert res["endpoint_level"]["change_description"] == "Approved version"
    assert res["endpoint_level"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint_level"]["queried_effective_date"] is None
    assert res["endpoint_level"]["date_conflict"] is False
    assert res["endpoint_level"]["possible_actions"] == ["inactivate", "new_version"]
    assert res["endpoint_sublevel"] is None
    assert res["endpoint_units"] == {
        "separator": "string",
        "units": [
            {"uid": "unit 1", "name": "name 1"},
            {"uid": "unit 2", "name": "name 2"},
        ],
    }
    assert res["endpoint"]["change_description"] == "Approved version"
    assert res["endpoint"]["end_date"] is None
    assert res["endpoint"]["template"]["name"] == "endpoint_template_2"
    assert res["endpoint"]["template"]["name_plain"] == "endpoint_template_2"
    assert res["endpoint"]["template"]["uid"] == "EndpointTemplate_000022"
    assert res["endpoint"]["template"]["sequence_id"] == "E22"
    assert res["endpoint"]["template"]["library_name"] == "Sponsor"
    assert res["endpoint"]["library"]["is_editable"] is True
    assert res["endpoint"]["library"]["name"] == "Sponsor"
    assert res["endpoint"]["name"] == "endpoint_template_2"
    assert res["endpoint"]["name_plain"] == "endpoint_template_2"
    assert len(res["endpoint"]["parameter_terms"]) == 0
    assert res["endpoint"]["possible_actions"] == ["inactivate"]
    assert res["endpoint"]["start_date"]
    assert res["endpoint"]["status"] == "Final"
    assert res["endpoint"]["study_count"] == 0
    assert res["endpoint"]["uid"] == "Endpoint_000003"
    assert res["endpoint"]["author_username"] == "unknown-user@example.com"
    assert res["endpoint"]["version"] == "1.0"
    assert res["timeframe"]["study_count"] == 0
    assert res["timeframe"]["change_description"] == "Approved version"
    assert res["timeframe"]["end_date"] is None
    assert res["timeframe"]["library"]["is_editable"] is True
    assert res["timeframe"]["library"]["name"] == "Sponsor"
    assert res["timeframe"]["name"] == "timeframe_1"
    assert res["timeframe"]["name_plain"] == "timeframe_1"
    assert len(res["timeframe"]["parameter_terms"]) == 0
    assert res["timeframe"]["possible_actions"] == ["inactivate"]
    assert res["timeframe"]["start_date"]
    assert res["timeframe"]["status"] == "Final"
    assert res["timeframe"]["template"]["name"] == "timeframe_1"
    assert res["timeframe"]["template"]["name_plain"] == "timeframe_1"
    assert res["timeframe"]["template"]["uid"] == "TimeframeTemplate_000011"
    assert res["timeframe"]["template"]["sequence_id"] == "T11"
    assert res["timeframe"]["template"]["library_name"] == "Sponsor"
    assert res["timeframe"]["uid"] == "Timeframe_000001"
    assert res["timeframe"]["author_username"] == "unknown-user@example.com"
    assert res["timeframe"]["version"] == "1.0"
    assert res["latest_endpoint"] is None
    assert res["latest_timeframe"] is None
    assert res["author_username"] == "unknown-user@example.com"
    assert res["accepted_version"] is False


def test_delete5(api_client):
    response = api_client.delete(
        "/studies/study_root/study-endpoints/StudyEndpoint_000008"
    )
    assert_response_status_code(response, 204)
