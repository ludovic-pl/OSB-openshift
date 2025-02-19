# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_CODELISTS_ATTRIBUTES_CYPHER,
    STARTUP_CT_TERM_WITHOUT_CATALOGUE,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.ct.codelist.attributes")
    db.cypher_query(STARTUP_CT_CODELISTS_ATTRIBUTES_CYPHER)
    db.cypher_query(STARTUP_CT_TERM_WITHOUT_CATALOGUE)

    yield

    drop_db("old.json.test.ct.codelist.attributes")


def test_post_create_codelist(api_client):
    data = {
        "catalogue_name": "SDTM CT",
        "name": "name",
        "parent_codelist_uid": None,
        "submission_value": "Submission value",
        "nci_preferred_name": "Nci preferred name",
        "definition": "definition",
        "extensible": True,
        "sponsor_preferred_name": "Sponsor preferred name",
        "template_parameter": True,
        "library_name": "Sponsor",
        "terms": [{"term_uid": "term1", "order": 999999}],
    }
    response = api_client.post("/ct/codelists", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "CTCodelist_000001"
    assert res["parent_codelist_uid"] is None
    assert res["child_codelist_uids"] == []
    assert res["name"] == "name"
    assert res["submission_value"] == "Submission value"
    assert res["nci_preferred_name"] == "Nci preferred name"
    assert res["definition"] == "definition"
    assert res["extensible"] is True
    assert res["sponsor_preferred_name"] == "Sponsor preferred name"
    assert res["template_parameter"] is True
    assert res["library_name"] == "Sponsor"
    assert res["possible_actions"] == ["new_version"]


def test_post_create_codelist_with_parent_codelist(api_client):
    data = {
        "catalogue_name": "SDTM CT",
        "name": "name with parent",
        "parent_codelist_uid": "ct_codelist_root3",
        "submission_value": "Submission value with parent",
        "nci_preferred_name": "Nci preferred name with parent",
        "definition": "definition",
        "extensible": True,
        "sponsor_preferred_name": "Sponsor preferred name with parent",
        "template_parameter": True,
        "library_name": "Sponsor",
        "terms": [],
    }
    response = api_client.post("/ct/codelists", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "CTCodelist_000002"
    assert res["parent_codelist_uid"] == "ct_codelist_root3"
    assert res["child_codelist_uids"] == []
    assert res["name"] == "name with parent"
    assert res["submission_value"] == "Submission value with parent"
    assert res["nci_preferred_name"] == "Nci preferred name with parent"
    assert res["definition"] == "definition"
    assert res["extensible"] is True
    assert res["sponsor_preferred_name"] == "Sponsor preferred name with parent"
    assert res["template_parameter"] is True
    assert res["library_name"] == "Sponsor"
    assert res["possible_actions"] == ["approve", "edit"]


def test_patch_draft_codelist(api_client):
    data = {
        "name": "codelist new name",
        "submission_value": "new codelist submission value",
        "nci_preferred_name": "new codelist preferred term",
        "definition": "new codelist definition",
        "extensible": True,
        "change_description": "changing codelist name",
    }
    response = api_client.patch("/ct/codelists/ct_codelist_root3/attributes", json=data)

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "ct_codelist_root3"
    assert res["parent_codelist_uid"] is None
    assert res["child_codelist_uids"] == ["CTCodelist_000002"]
    assert res["name"] == "codelist new name"
    assert res["submission_value"] == "new codelist submission value"
    assert res["nci_preferred_name"] == "new codelist preferred term"
    assert res["definition"] == "new codelist definition"
    assert res["extensible"] is True
    assert res["library_name"] == "Sponsor"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["change_description"] == "changing codelist name"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "edit"]


def test_patch_draft_codelist_that_is_not_tp(api_client):
    data = {
        "name": "codelist another new name",
        "submission_value": "new codelist submission value",
        "nci_preferred_name": "new codelist preferred term",
        "definition": "new codelist definition",
        "extensible": True,
        "change_description": "changing codelist name",
    }
    response = api_client.patch("/ct/codelists/ct_codelist_root3/attributes", json=data)

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "ct_codelist_root3"
    assert res["parent_codelist_uid"] is None
    assert res["child_codelist_uids"] == ["CTCodelist_000002"]
    assert res["name"] == "codelist another new name"
    assert res["submission_value"] == "new codelist submission value"
    assert res["nci_preferred_name"] == "new codelist preferred term"
    assert res["definition"] == "new codelist definition"
    assert res["extensible"] is True
    assert res["library_name"] == "Sponsor"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.3"
    assert res["change_description"] == "changing codelist name"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "edit"]


def test_post_versions_codelist(api_client):
    response = api_client.post("/ct/codelists/ct_codelist_root1/attributes/versions")

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "ct_codelist_root1"
    assert res["parent_codelist_uid"] is None
    assert res["child_codelist_uids"] == []
    assert res["name"] == "codelist attributes value1"
    assert res["submission_value"] == "codelist submission value1"
    assert res["nci_preferred_name"] == "codelist preferred term"
    assert res["definition"] == "codelist definition"
    assert res["extensible"] is False
    assert res["library_name"] == "Sponsor"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"
    assert res["change_description"] == "New draft created"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "edit"]


def test_post_approve_codelist(api_client):
    response = api_client.post("/ct/codelists/ct_codelist_root3/attributes/approvals")

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "ct_codelist_root3"
    assert res["parent_codelist_uid"] is None
    assert res["child_codelist_uids"] == ["CTCodelist_000002"]
    assert res["name"] == "codelist another new name"
    assert res["submission_value"] == "new codelist submission value"
    assert res["nci_preferred_name"] == "new codelist preferred term"
    assert res["definition"] == "new codelist definition"
    assert res["extensible"] is True
    assert res["library_name"] == "Sponsor"
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Approved version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["new_version"]


def test_get_codelist_with_parent_codelist_uid(api_client):
    response = api_client.get("/ct/codelists/CTCodelist_000002/attributes")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "CTCodelist_000002"
    assert res["parent_codelist_uid"] == "ct_codelist_root3"
    assert res["child_codelist_uids"] == []
    assert res["name"] == "name with parent"
    assert res["submission_value"] == "Submission value with parent"
    assert res["nci_preferred_name"] == "Nci preferred name with parent"
    assert res["definition"] == "definition"
    assert res["extensible"] is True
    assert res["library_name"] == "Sponsor"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "edit"]


def test_post_add_term_to_codelist(api_client):
    data = {"term_uid": "term1"}
    response = api_client.post("/ct/codelists/ct_codelist_root3/terms", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "ct_codelist_root3"
    assert res["parent_codelist_uid"] is None
    assert res["child_codelist_uids"] == ["CTCodelist_000002"]
    assert res["name"] == "codelist another new name"
    assert res["submission_value"] == "new codelist submission value"
    assert res["nci_preferred_name"] == "new codelist preferred term"
    assert res["definition"] == "new codelist definition"
    assert res["extensible"] is True
    assert res["sponsor_preferred_name"] == "codelist_name_value"
    assert res["template_parameter"] is False
    assert res["library_name"] == "Sponsor"
    assert res["possible_actions"] == ["new_version"]


def test_post_approve_child_codelist(api_client):
    response = api_client.post("/ct/codelists/CTCodelist_000002/attributes/approvals")

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "CTCodelist_000002"
    assert res["parent_codelist_uid"] == "ct_codelist_root3"
    assert res["child_codelist_uids"] == []
    assert res["name"] == "name with parent"
    assert res["submission_value"] == "Submission value with parent"
    assert res["nci_preferred_name"] == "Nci preferred name with parent"
    assert res["definition"] == "definition"
    assert res["extensible"] is True
    assert res["library_name"] == "Sponsor"
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Approved version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["new_version"]


def test_post_add_term_to_child_codelist(api_client):
    data = {"term_uid": "term1"}
    response = api_client.post("/ct/codelists/CTCodelist_000002/terms", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["catalogue_name"] == "SDTM CT"
    assert res["codelist_uid"] == "CTCodelist_000002"
    assert res["parent_codelist_uid"] == "ct_codelist_root3"
    assert res["child_codelist_uids"] == []
    assert res["name"] == "name with parent"
    assert res["submission_value"] == "Submission value with parent"
    assert res["nci_preferred_name"] == "Nci preferred name with parent"
    assert res["definition"] == "definition"
    assert res["extensible"] is True
    assert res["sponsor_preferred_name"] == "Sponsor preferred name with parent"
    assert res["template_parameter"] is True
    assert res["library_name"] == "Sponsor"
    assert res["possible_actions"] == ["new_version"]


def test_get_all_sub_codelists_that_have_the_provided_terms(api_client):
    response = api_client.get(
        "/ct/codelists/ct_codelist_root3/sub-codelists?term_uids=term1",
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["catalogue_name"] == "SDTM CT"
    assert res["items"][0]["codelist_uid"] == "CTCodelist_000002"
    assert res["items"][0]["parent_codelist_uid"] == "ct_codelist_root3"
    assert res["items"][0]["child_codelist_uids"] == []
    assert res["items"][0]["library_name"] == "Sponsor"
    assert res["items"][0]["name"]["name"] == "Sponsor preferred name with parent"
    assert res["items"][0]["name"]["template_parameter"] is True
    assert res["items"][0]["name"]["end_date"] is None
    assert res["items"][0]["name"]["status"] == "Draft"
    assert res["items"][0]["name"]["version"] == "0.1"
    assert res["items"][0]["name"]["change_description"] == "Initial version"
    assert res["items"][0]["name"]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["name"]["possible_actions"] == ["approve", "edit"]
    assert res["items"][0]["attributes"]["name"] == "name with parent"
    assert (
        res["items"][0]["attributes"]["submission_value"]
        == "Submission value with parent"
    )
    assert (
        res["items"][0]["attributes"]["nci_preferred_name"]
        == "Nci preferred name with parent"
    )
    assert res["items"][0]["attributes"]["definition"] == "definition"
    assert res["items"][0]["attributes"]["extensible"] is True
    assert res["items"][0]["attributes"]["end_date"] is None
    assert res["items"][0]["attributes"]["status"] == "Final"
    assert res["items"][0]["attributes"]["version"] == "1.0"
    assert res["items"][0]["attributes"]["change_description"] == "Approved version"
    assert (
        res["items"][0]["attributes"]["author_username"] == "unknown-user@example.com"
    )
    assert res["items"][0]["attributes"]["possible_actions"] == ["new_version"]
