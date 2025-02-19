# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_ODM_DESCRIPTIONS,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.odm.aliases.negative")
    db.cypher_query(STARTUP_ODM_DESCRIPTIONS)

    yield

    drop_db("old.json.test.odm.aliases.negative")


def test_create_a_new_odm_alias(api_client):
    data = {"library_name": "Sponsor", "name": "Variable", "context": "domain1"}
    response = api_client.post("concepts/odms/aliases", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmAlias_000001"
    assert res["name"] == "Variable"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "domain1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_cannot_create_a_new_odm_alias_with_same_properties(api_client):
    data = {"library_name": "Sponsor", "name": "Variable", "context": "domain1"}
    response = api_client.post("concepts/odms/aliases", json=data)

    assert_response_status_code(response, 409)

    res = response.json()

    assert res["type"] == "AlreadyExistsException"
    assert (
        res["message"]
        == "ODM Alias already exists with UID (OdmAlias_000001) and data {'name': 'Variable', 'context': 'domain1'}"
    )


def test_cannot_inactivate_an_odm_alias_that_is_in_draft_status(api_client):
    response = api_client.delete("concepts/odms/aliases/OdmAlias_000001/activations")

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Cannot retire draft version."


def test_cannot_reactivate_an_odm_alias_that_is_not_retired(api_client):
    response = api_client.post("concepts/odms/aliases/OdmAlias_000001/activations")

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Only RETIRED version can be reactivated."


def test_create_an_odm_form_and_attach_the_odm_alias_to_it(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name1",
        "oid": "oid1",
        "sdtm_version": "0.1",
        "repeating": "No",
        "descriptions": ["odm_description3"],
        "alias_uids": ["OdmAlias_000001"],
    }
    response = api_client.post("concepts/odms/forms", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmForm_000001"
    assert res["name"] == "name1"
    assert res["library_name"] == "Sponsor"
    assert res["oid"] == "oid1"
    assert res["sdtm_version"] == "0.1"
    assert res["repeating"] == "No"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["scope"] is None
    assert res["descriptions"] == [
        {
            "uid": "odm_description3",
            "name": "name3",
            "language": "ENG",
            "description": "description3",
            "instruction": "instruction3",
            "sponsor_instruction": "sponsor_instruction3",
            "version": "0.1",
        }
    ]
    assert res["aliases"] == [
        {
            "uid": "OdmAlias_000001",
            "context": "domain1",
            "name": "Variable",
            "version": "0.1",
        }
    ]
    assert res["activity_groups"] == []
    assert res["item_groups"] == []
    assert res["vendor_elements"] == []
    assert res["vendor_attributes"] == []
    assert res["vendor_element_attributes"] == []
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_cannot_delete_an_odm_alias_that_is_being_used(api_client):
    response = api_client.delete("concepts/odms/aliases/OdmAlias_000001")

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "This ODM Alias is in use."


def test_cannot_delete_non_existent_odm_alias(api_client):
    response = api_client.delete("concepts/odms/aliases/wrong_uid")

    assert_response_status_code(response, 404)

    res = response.json()

    assert res["type"] == "NotFoundException"
    assert res["message"] == "ODM Alias with UID 'wrong_uid' doesn't exist."
