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
    inject_and_clear_db("old.json.test.odm.formal.expressions")
    db.cypher_query(STARTUP_ODM_DESCRIPTIONS)

    yield

    drop_db("old.json.test.odm.formal.expressions")


def test_getting_empty_list_of_odm_formal_expressions(api_client):
    response = api_client.get("concepts/odms/formal-expressions")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res == {"items": [], "page": 1, "size": 10, "total": 0}


def test_creating_a_new_odm_formal_expression(api_client):
    data = {
        "library_name": "Sponsor",
        "context": "context1",
        "expression": "expression1",
    }
    response = api_client.post("concepts/odms/formal-expressions", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmFormalExpression_000001"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["expression"] == "expression1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_getting_non_empty_list_of_odm_formal_expressions(api_client):
    response = api_client.get("concepts/odms/formal-expressions")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["uid"] == "OdmFormalExpression_000001"
    assert res["items"][0]["library_name"] == "Sponsor"
    assert res["items"][0]["context"] == "context1"
    assert res["items"][0]["expression"] == "expression1"
    assert res["items"][0]["end_date"] is None
    assert res["items"][0]["status"] == "Draft"
    assert res["items"][0]["version"] == "0.1"
    assert res["items"][0]["change_description"] == "Initial version"
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["possible_actions"] == ["approve", "delete", "edit"]


def test_getting_possible_header_values_of_odm_formal_expressions(api_client):
    response = api_client.get(
        "concepts/odms/formal-expressions/headers?field_name=context"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res == ["context1"]


def test_getting_a_specific_odm_formal_expression(api_client):
    response = api_client.get(
        "concepts/odms/formal-expressions/OdmFormalExpression_000001"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["uid"] == "OdmFormalExpression_000001"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["expression"] == "expression1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_getting_versions_of_a_specific_odm_formal_expression(api_client):
    response = api_client.get(
        "concepts/odms/formal-expressions/OdmFormalExpression_000001/versions"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res[0]["uid"] == "OdmFormalExpression_000001"
    assert res[0]["library_name"] == "Sponsor"
    assert res[0]["context"] == "context1"
    assert res[0]["expression"] == "expression1"
    assert res[0]["end_date"] is None
    assert res[0]["status"] == "Draft"
    assert res[0]["version"] == "0.1"
    assert res[0]["change_description"] == "Initial version"
    assert res[0]["author_username"] == "unknown-user@example.com"
    assert res[0]["possible_actions"] == ["approve", "delete", "edit"]


def test_updating_an_existing_odm_formal_expression(api_client):
    data = {
        "library_name": "Sponsor",
        "context": "context1",
        "expression": "expression1 updated",
        "change_description": "updated expression",
    }
    response = api_client.patch(
        "concepts/odms/formal-expressions/OdmFormalExpression_000001", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["uid"] == "OdmFormalExpression_000001"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["expression"] == "expression1 updated"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["change_description"] == "updated expression"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_approving_an_odm_formal_expression(api_client):
    response = api_client.post(
        "concepts/odms/formal-expressions/OdmFormalExpression_000001/approvals"
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmFormalExpression_000001"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["expression"] == "expression1 updated"
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Approved version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["inactivate", "new_version"]


def test_inactivating_a_specific_odm_formal_expression(api_client):
    response = api_client.delete(
        "concepts/odms/formal-expressions/OdmFormalExpression_000001/activations"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["uid"] == "OdmFormalExpression_000001"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["expression"] == "expression1 updated"
    assert res["end_date"] is None
    assert res["status"] == "Retired"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Inactivated version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["delete", "reactivate"]


def test_reactivating_a_specific_odm_formal_expression(api_client):
    response = api_client.post(
        "concepts/odms/formal-expressions/OdmFormalExpression_000001/activations"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["uid"] == "OdmFormalExpression_000001"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["expression"] == "expression1 updated"
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Reactivated version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["inactivate", "new_version"]


def test_creating_a_new_odm_formal_expression_version(api_client):
    response = api_client.post(
        "concepts/odms/formal-expressions/OdmFormalExpression_000001/versions"
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmFormalExpression_000001"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context1"
    assert res["expression"] == "expression1 updated"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"
    assert res["change_description"] == "New draft created"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "edit"]


def test_create_a_new_odm_formal_expression_for_deleting_it(api_client):
    data = {
        "library_name": "Sponsor",
        "context": "context - delete",
        "expression": "expression2",
    }
    response = api_client.post("concepts/odms/formal-expressions", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmFormalExpression_000002"
    assert res["library_name"] == "Sponsor"
    assert res["context"] == "context - delete"
    assert res["expression"] == "expression2"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_deleting_a_specific_odm_formal_expression(api_client):
    response = api_client.delete(
        "concepts/odms/formal-expressions/OdmFormalExpression_000002"
    )

    assert_response_status_code(response, 204)


def test_create_a_new_odm_condition_with_relation_to_odm_formal_expression(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name1",
        "oid": "oid1",
        "formal_expressions": ["OdmFormalExpression_000001"],
        "descriptions": ["odm_description3"],
        "alias_uids": [],
    }
    response = api_client.post("concepts/odms/conditions", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmCondition_000001"
    assert res["name"] == "name1"
    assert res["library_name"] == "Sponsor"
    assert res["oid"] == "oid1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["formal_expressions"] == [
        {
            "uid": "OdmFormalExpression_000001",
            "context": "context1",
            "expression": "expression1 updated",
            "version": "1.1",
        }
    ]
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
    assert res["aliases"] == []
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_getting_uids_of_a_specific_odm_formal_expressions_active_relationships(
    api_client,
):
    response = api_client.get(
        "concepts/odms/formal-expressions/OdmFormalExpression_000001/relationships"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["OdmCondition"] == ["OdmCondition_000001"]
