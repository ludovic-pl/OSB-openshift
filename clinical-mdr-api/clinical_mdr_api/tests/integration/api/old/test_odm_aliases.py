# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.odm.aliases")
    db.cypher_query("MERGE (library:Library {name:'Sponsor', is_editable:true})")

    yield

    drop_db("old.json.test.odm.aliases")


def test_getting_empty_list_of_odm_aliases(api_client):
    response = api_client.get("concepts/odms/aliases")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res == {"items": [], "page": 1, "size": 10, "total": 0}


def test_creating_a_new_odm_alias(api_client):
    data = {"library_name": "Sponsor", "name": "name1", "context": "context1"}
    response = api_client.post("concepts/odms/aliases", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmAlias_000001"
    assert res["name"] == "name1"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_getting_non_empty_list_of_odm_aliases(api_client):
    response = api_client.get("concepts/odms/aliases")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["uid"] == "OdmAlias_000001"
    assert res["items"][0]["name"] == "name1"
    assert res["items"][0]["library_name"] == "Sponsor"
    assert res["items"][0]["context"] == "context1"
    assert res["items"][0]["end_date"] is None
    assert res["items"][0]["status"] == "Draft"
    assert res["items"][0]["version"] == "0.1"
    assert res["items"][0]["change_description"] == "Initial version"
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["possible_actions"] == ["approve", "delete", "edit"]


def test_getting_possible_header_values_of_odm_aliases(api_client):
    response = api_client.get("concepts/odms/aliases/headers?field_name=name")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res == ["name1"]


def test_getting_versions_of_a_specific_odm_alias(api_client):
    response = api_client.get("concepts/odms/aliases/OdmAlias_000001/versions")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res[0]["uid"] == "OdmAlias_000001"
    assert res[0]["name"] == "name1"
    assert res[0]["library_name"] == "Sponsor"
    assert res[0]["context"] == "context1"
    assert res[0]["end_date"] is None
    assert res[0]["status"] == "Draft"
    assert res[0]["version"] == "0.1"
    assert res[0]["change_description"] == "Initial version"
    assert res[0]["author_username"] == "unknown-user@example.com"
    assert res[0]["possible_actions"] == ["approve", "delete", "edit"]


def test_updating_an_existing_odm_alias(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "new name",
        "context": "context1",
        "change_description": "name changed",
    }
    response = api_client.patch("concepts/odms/aliases/OdmAlias_000001", json=data)

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["uid"] == "OdmAlias_000001"
    assert res["name"] == "new name"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["change_description"] == "name changed"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_approving_an_odm_alias(api_client):
    response = api_client.post("concepts/odms/aliases/OdmAlias_000001/approvals")

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmAlias_000001"
    assert res["name"] == "new name"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Approved version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["inactivate", "new_version"]


def test_inactivating_a_specific_odm_alias(api_client):
    response = api_client.delete("concepts/odms/aliases/OdmAlias_000001/activations")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["uid"] == "OdmAlias_000001"
    assert res["name"] == "new name"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["end_date"] is None
    assert res["status"] == "Retired"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Inactivated version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["delete", "reactivate"]


def test_reactivating_a_specific_odm_alias(api_client):
    response = api_client.post("concepts/odms/aliases/OdmAlias_000001/activations")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["uid"] == "OdmAlias_000001"
    assert res["name"] == "new name"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Reactivated version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["inactivate", "new_version"]


def test_creating_a_new_odm_alias_version(api_client):
    response = api_client.post("concepts/odms/aliases/OdmAlias_000001/versions")

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmAlias_000001"
    assert res["name"] == "new name"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"
    assert res["change_description"] == "New draft created"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "edit"]


def test_create_a_new_odm_alias_for_batch_and_delete(api_client):
    data = {"name": "batch name", "library_name": "Sponsor", "context": "context1"}
    response = api_client.post("concepts/odms/aliases", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmAlias_000002"
    assert res["library_name"] == "Sponsor"
    assert res["name"] == "batch name"
    assert res["context"] == "context1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_batch_operations_for_odm_alias(api_client):
    data = [
        {
            "method": "POST",
            "content": {"name": "new batch name", "context": "new batch context"},
        },
        {
            "method": "PATCH",
            "content": {
                "uid": "OdmAlias_000002",
                "context": "new context",
                "change_description": "context changed",
            },
        },
    ]
    response = api_client.post("concepts/odms/aliases/batch", json=data)

    assert_response_status_code(response, 207)

    res = response.json()

    assert res[0]["response_code"] == 201
    assert res[0]["content"]["start_date"]
    assert res[0]["content"]["end_date"] is None
    assert res[0]["content"]["status"] == "Draft"
    assert res[0]["content"]["version"] == "0.1"
    assert res[0]["content"]["author_username"] == "unknown-user@example.com"
    assert res[0]["content"]["change_description"] == "Initial version"
    assert res[0]["content"]["uid"] == "OdmAlias_000003"
    assert res[0]["content"]["name"] == "new batch name"
    assert res[0]["content"]["context"] == "new batch context"
    assert res[0]["content"]["library_name"] == "Sponsor"
    assert res[0]["content"]["possible_actions"] == ["approve", "delete", "edit"]
    assert res[1]["response_code"] == 200
    assert res[1]["content"]["uid"] == "OdmAlias_000002"
    assert res[1]["content"]["library_name"] == "Sponsor"
    assert res[1]["content"]["name"] == "batch name"
    assert res[1]["content"]["context"] == "new context"
    assert res[1]["content"]["start_date"]
    assert res[1]["content"]["end_date"] is None
    assert res[1]["content"]["status"] == "Draft"
    assert res[1]["content"]["version"] == "0.2"
    assert res[1]["content"]["change_description"] == "context changed"
    assert res[1]["content"]["author_username"] == "unknown-user@example.com"
    assert res[1]["content"]["possible_actions"] == ["approve", "delete", "edit"]


def test_deleting_a_specific_odm_alias(api_client):
    response = api_client.delete("concepts/odms/aliases/OdmAlias_000003")

    assert_response_status_code(response, 204)


def test_create_a_new_odm_form_with_relation_to_odm_alias(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name1",
        "oid": "oid1",
        "sdtm_version": "0.1",
        "repeating": "No",
        "scope_uid": None,
        "descriptions": [],
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
    assert res["descriptions"] == []
    assert res["aliases"] == [
        {
            "uid": "OdmAlias_000001",
            "context": "context1",
            "name": "new name",
            "version": "1.1",
        }
    ]
    assert res["activity_groups"] == []
    assert res["item_groups"] == []
    assert res["vendor_elements"] == []
    assert res["vendor_attributes"] == []
    assert res["vendor_element_attributes"] == []
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_getting_uids_of_a_specific_odm_alias_active_relationships(api_client):
    response = api_client.get("concepts/odms/aliases/OdmAlias_000001/relationships")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["OdmForm"] == ["OdmForm_000001"]
