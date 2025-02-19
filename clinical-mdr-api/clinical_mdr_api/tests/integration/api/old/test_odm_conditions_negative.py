# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_ODM_ALIASES,
    STARTUP_ODM_DESCRIPTIONS,
    STARTUP_ODM_FORMAL_EXPRESSIONS,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.odm.conditions.negative")
    db.cypher_query(STARTUP_ODM_FORMAL_EXPRESSIONS)
    db.cypher_query(STARTUP_ODM_DESCRIPTIONS)
    db.cypher_query(STARTUP_ODM_ALIASES)

    yield

    drop_db("old.json.test.odm.conditions.negative")


def test_create_a_new_odm_condition(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name1",
        "oid": "oid1",
        "formal_expressions": ["odm_formal_expression1"],
        "descriptions": ["odm_description2", "odm_description3"],
        "alias_uids": ["odm_alias1"],
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
            "uid": "odm_formal_expression1",
            "context": "context1",
            "expression": "expression1",
            "version": "0.1",
        }
    ]
    assert res["descriptions"] == [
        {
            "uid": "odm_description2",
            "name": "name2",
            "language": "language2",
            "description": "description2",
            "instruction": "instruction2",
            "sponsor_instruction": "sponsor_instruction2",
            "version": "0.1",
        },
        {
            "uid": "odm_description3",
            "name": "name3",
            "language": "ENG",
            "description": "description3",
            "instruction": "instruction3",
            "sponsor_instruction": "sponsor_instruction3",
            "version": "0.1",
        },
    ]
    assert res["aliases"] == [
        {"uid": "odm_alias1", "context": "context1", "name": "name1", "version": "0.1"}
    ]
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_cannot_create_a_new_odm_condition_with_odm_formal_expressions_with_same_context(
    api_client,
):
    data = {
        "library_name": "Sponsor",
        "name": "a name",
        "oid": "aoid",
        "formal_expressions": ["odm_formal_expression1", "odm_formal_expression3"],
        "descriptions": ["odm_description3"],
        "alias_uids": [],
    }
    response = api_client.post("concepts/odms/conditions", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "ODM Condition tried to connect to ODM Formal Expressions with same Context 'context1'."
    )


def test_cannot_update_an_odm_condition_with_odm_formal_expressions_with_same_context(
    api_client,
):
    data = {
        "change_description": "formal expressions changed",
        "name": "name1",
        "oid": "oid1",
        "formal_expressions": ["odm_formal_expression3"],
        "descriptions": ["odm_description3"],
        "alias_uids": [],
    }
    response = api_client.patch(
        "concepts/odms/conditions/OdmCondition_000001", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "ODM Condition tried to connect to ODM Formal Expressions with same Context 'context1'."
    )


def test_cannot_create_a_new_odm_condition_with_same_properties(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name1",
        "oid": "oid1",
        "formal_expressions": ["odm_formal_expression1"],
        "descriptions": ["odm_description2", "odm_description3"],
        "alias_uids": ["odm_alias1"],
    }
    response = api_client.post("concepts/odms/conditions", json=data)

    assert_response_status_code(response, 409)

    res = response.json()

    assert res["type"] == "AlreadyExistsException"
    assert (
        res["message"]
        == "ODM Condition already exists with UID (OdmCondition_000001) and data {'description_uids': ['odm_description2', 'odm_description3'], 'alias_uids': ['odm_alias1'], 'formal_expression_uids': ['odm_formal_expression1'], 'name': 'name1', 'oid': 'oid1'}"
    )


def test_cannot_create_an_odm_condition_connected_to_non_existent_odm_formal_expression(
    api_client,
):
    data = {
        "library_name": "Sponsor",
        "name": "new name",
        "oid": "new oid",
        "formal_expressions": ["wrong_uid"],
        "descriptions": [],
        "alias_uids": [],
    }
    response = api_client.post("concepts/odms/conditions", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """ODM Condition tried to connect to non-existent concepts [('Concept Name: ODM Formal Expression', "uids: {'wrong_uid'}")]."""
    )


def test_cannot_create_an_odm_condition_connected_to_non_existent_odm_description(
    api_client,
):
    data = {
        "library_name": "Sponsor",
        "name": "new name",
        "oid": "new oid",
        "formal_expressions": [],
        "descriptions": ["wrong_uid"],
        "alias_uids": [],
    }
    response = api_client.post("concepts/odms/conditions", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """ODM Condition tried to connect to non-existent concepts [('Concept Name: ODM Description', "uids: {'wrong_uid'}")]."""
    )


def test_cannot_create_an_odm_condition_connected_to_non_existent_odm_alias(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "new name",
        "oid": "new oid",
        "formal_expressions": [],
        "descriptions": ["odm_description3"],
        "alias_uids": ["wrong_uid"],
    }
    response = api_client.post("concepts/odms/conditions", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """ODM Condition tried to connect to non-existent concepts [('Concept Name: ODM Alias', "uids: {'wrong_uid'}")]."""
    )


def test_cannot_create_a_new_odm_condition_without_an_english_description(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name2",
        "oid": "oid2",
        "formal_expressions": [],
        "descriptions": [
            {
                "name": "name - non-eng",
                "language": "DAN",
                "description": "description - non-eng",
                "instruction": "instruction - non-eng",
                "sponsor_instruction": "sponsor_instruction - non-eng",
            }
        ],
        "alias_uids": [],
    }
    response = api_client.post("concepts/odms/conditions", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "An English ODM Description must be provided."


def test_getting_error_for_retrieving_non_existent_odm_condition(api_client):
    response = api_client.get("concepts/odms/conditions/OdmCondition_000002")

    assert_response_status_code(response, 404)

    res = response.json()

    assert res["type"] == "NotFoundException"
    assert (
        res["message"]
        == "OdmConditionAR with UID 'OdmCondition_000002' doesn't exist or there's no version with requested status or version number."
    )


def test_cannot_inactivate_an_odm_condition_that_is_in_draft_status(api_client):
    response = api_client.delete(
        "concepts/odms/conditions/OdmCondition_000001/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Cannot retire draft version."


def test_cannot_reactivate_an_odm_condition_that_is_not_retired(api_client):
    response = api_client.post(
        "concepts/odms/conditions/OdmCondition_000001/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Only RETIRED version can be reactivated."
