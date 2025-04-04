# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    CREATE_BASE_TEMPLATE_PARAMETER_TREE,
    STARTUP_UNIT_DEFINITIONS,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.numeric.value.with.unit")
    db.cypher_query(CREATE_BASE_TEMPLATE_PARAMETER_TREE)
    db.cypher_query(STARTUP_UNIT_DEFINITIONS)

    yield

    drop_db("old.json.test.numeric.value.with.unit")


def test_post_numeric_value_with_unit(api_client):
    data = {
        "value": 7.5,
        "unit_definition_uid": "unit_definition_root1",
        "definition": "numeric_value_definition1",
        "abbreviation": "abbv",
        "template_parameter": True,
        "library_name": "Sponsor",
    }
    response = api_client.post("/concepts/numeric-values-with-unit", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "NumericValueWithUnit_000001"
    assert res["name"] == "7.5 [unit_definition_root1]"
    assert res["value"] == 7.5
    assert res["unit_definition_uid"] == "unit_definition_root1"
    assert res["unit_label"] == "name1"
    assert res["name_sentence_case"] == "7.5"
    assert res["definition"] == "numeric_value_definition1"
    assert res["abbreviation"] == "abbv"
    assert res["template_parameter"] is True
    assert res["library_name"] == "Sponsor"
    assert res["status"] is None
    assert res["version"] is None
    assert res["change_description"] is None
    assert res["author_username"] is None
    assert res["end_date"] is None


def test_post_numeric_value_with_unit_existing_numeric_value_with_unit_is_returned(
    api_client,
):
    data = {
        "value": 7.5,
        "unit_definition_uid": "unit_definition_root1",
        "definition": "numeric_value_definition1",
        "abbreviation": "abbv",
        "template_parameter": True,
        "library_name": "Sponsor",
    }
    response = api_client.post("/concepts/numeric-values-with-unit", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "NumericValueWithUnit_000001"
    assert res["name"] == "7.5 [unit_definition_root1]"
    assert res["value"] == 7.5
    assert res["unit_definition_uid"] == "unit_definition_root1"
    assert res["unit_label"] == "name1"
    assert res["name_sentence_case"] == "7.5"
    assert res["definition"] == "numeric_value_definition1"
    assert res["abbreviation"] == "abbv"
    assert res["template_parameter"] is True
    assert res["library_name"] == "Sponsor"
    assert res["status"] is None
    assert res["version"] is None
    assert res["change_description"] is None
    assert res["author_username"] is None
    assert res["end_date"] is None


def test_post_numeric_value_with_unit1(api_client):
    data = {
        "value": 9.12,
        "unit_definition_uid": "unit_definition_root1",
        "definition": "numeric_value_definition2",
        "abbreviation": "abbv",
        "template_parameter": True,
        "library_name": "Sponsor",
    }
    response = api_client.post("/concepts/numeric-values-with-unit", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "NumericValueWithUnit_000002"
    assert res["name"] == "9.12 [unit_definition_root1]"
    assert res["value"] == 9.12
    assert res["unit_definition_uid"] == "unit_definition_root1"
    assert res["unit_label"] == "name1"
    assert res["name_sentence_case"] == "9.12"
    assert res["definition"] == "numeric_value_definition2"
    assert res["abbreviation"] == "abbv"
    assert res["template_parameter"] is True
    assert res["library_name"] == "Sponsor"
    assert res["status"] is None
    assert res["version"] is None
    assert res["change_description"] is None
    assert res["author_username"] is None
    assert res["end_date"] is None


def test_get_all_numeric_value_with_units(api_client):
    response = api_client.get("/concepts/numeric-values-with-unit?total_count=true")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["uid"] == "NumericValueWithUnit_000001"
    assert res["items"][0]["name"] == "7.5"
    assert res["items"][0]["value"] == 7.5
    assert res["items"][0]["unit_definition_uid"] == "unit_definition_root1"
    assert res["items"][0]["unit_label"] == "name1"
    assert res["items"][0]["name_sentence_case"] == "7.5"
    assert res["items"][0]["definition"] == "numeric_value_definition1"
    assert res["items"][0]["abbreviation"] == "abbv"
    assert res["items"][0]["template_parameter"] is True
    assert res["items"][0]["library_name"] == "Sponsor"
    assert res["items"][0]["status"] is None
    assert res["items"][0]["version"] is None
    assert res["items"][0]["change_description"] is None
    assert res["items"][0]["author_username"] is None
    assert res["items"][0]["end_date"] is None
    assert res["items"][1]["uid"] == "NumericValueWithUnit_000002"
    assert res["items"][1]["name"] == "9.12"
    assert res["items"][1]["value"] == 9.12
    assert res["items"][1]["unit_definition_uid"] == "unit_definition_root1"
    assert res["items"][1]["unit_label"] == "name1"
    assert res["items"][1]["name_sentence_case"] == "9.12"
    assert res["items"][1]["definition"] == "numeric_value_definition2"
    assert res["items"][1]["abbreviation"] == "abbv"
    assert res["items"][1]["template_parameter"] is True
    assert res["items"][1]["library_name"] == "Sponsor"
    assert res["items"][1]["status"] is None
    assert res["items"][1]["version"] is None
    assert res["items"][1]["change_description"] is None
    assert res["items"][1]["author_username"] is None
    assert res["items"][1]["end_date"] is None


def test_post_numeric_value_with_unit_specifying_a_non_existent_unit(api_client):
    data = {
        "value": 8.43,
        "unit_definition_uid": "non-existent-uid",
        "definition": "numeric_value_definition2",
        "abbreviation": "abbv",
        "template_parameter": False,
        "library_name": "Sponsor",
    }
    response = api_client.post("/concepts/numeric-values-with-unit", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "NumericValueWithUnitVO tried to connect to non-existent Unit Definition with UID 'non-existent-uid'."
    )
