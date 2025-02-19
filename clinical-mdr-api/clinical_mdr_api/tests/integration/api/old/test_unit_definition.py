# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

import clinical_mdr_api.services.libraries.libraries as library_service
from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_CATALOGUE_CYPHER,
    STARTUP_PARAMETERS_CYPHER,
    library_data,
)
from clinical_mdr_api.tests.integration.utils.method_library import (
    create_codelist,
    create_ct_term,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.unit.definition")
    db.cypher_query(STARTUP_PARAMETERS_CYPHER)
    db.cypher_query(STARTUP_CT_CATALOGUE_CYPHER)

    library_service.create(**library_data)
    catalogue_name = "catalogue"
    library_name = "Test library"
    ct_unit_cod = create_codelist(
        "CT Unit", "CTCodelist_000001", catalogue_name, library_name
    )
    create_ct_term(
        ct_unit_cod.codelist_uid,
        "CT Unit term 1",
        "unit1-ct-uid",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        ct_unit_cod.codelist_uid,
        "CT Unit term 2",
        "unit1-ct-uid-patched",
        2,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        ct_unit_cod.codelist_uid,
        "CT Unit term 3",
        "unit1-ct-uid-2",
        3,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        ct_unit_cod.codelist_uid,
        "CT Unit term 4",
        "unit1-ct-uid-3",
        4,
        catalogue_name,
        library_name,
    )
    ct_unit_dim_cod = create_codelist(
        "CT Unit Dimension", "CTCodelist_000002", catalogue_name, library_name
    )
    create_ct_term(
        ct_unit_dim_cod.codelist_uid,
        "CT Unit Dim term 1",
        "unit1-dimension",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        ct_unit_dim_cod.codelist_uid,
        "CT Unit Dim term 2",
        "unit1-dimension-2",
        2,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        ct_unit_dim_cod.codelist_uid,
        "CT Unit Dim term 3",
        "unit1-dimension-patched",
        3,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        ct_unit_dim_cod.codelist_uid,
        "CT Unit Dim term 4",
        "unit1-dimension-patched-2",
        4,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        ct_unit_dim_cod.codelist_uid,
        "CT Unit Dim term 5",
        "other-dimension",
        5,
        catalogue_name,
        library_name,
    )
    ct_unit_subset = create_codelist(
        "CT Unit Subset", "CTCodelist_000003", catalogue_name, library_name
    )
    create_ct_term(
        ct_unit_subset.codelist_uid,
        "CT Unit Subset term 1",
        "unit-subset-uid-1",
        1,
        catalogue_name,
        library_name,
    )
    create_ct_term(
        ct_unit_subset.codelist_uid,
        "CT Unit Subset term 2",
        "unit-subset-uid-2",
        2,
        catalogue_name,
        library_name,
    )

    yield

    drop_db("old.json.test.unit.definition")


def test_empty_list_11(api_client):
    response = api_client.get("/concepts/unit-definitions")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res == {"items": [], "page": 1, "size": 10, "total": 0}


def test_adding2(api_client):
    data = {
        "name": "unit1",
        "library_name": "Test library",
        "ct_units": ["unit1-ct-uid"],
        "convertible_unit": True,
        "display_unit": True,
        "master_unit": True,
        "si_unit": True,
        "us_conventional_unit": True,
        "unit_dimension": "unit1-dimension",
        "legacy_code": "unit1-legacy-code",
        "use_molecular_weight": False,
        "conversion_factor_to_master": 1.0,
        "order": 1,
    }
    response = api_client.post("/concepts/unit-definitions", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Initial version"
    assert res["uid"] == "UnitDefinition_000001"
    assert res["name"] == "unit1"
    assert res["library_name"] == "Test library"
    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_adding_non_unique_name(api_client):
    data = {
        "name": "unit1",
        "library_name": "Test library",
        "ct_units": ["unit1-ct-uid-2"],
        "convertible_unit": True,
        "display_unit": True,
        "master_unit": True,
        "si_unit": True,
        "us_conventional_unit": True,
        "unit_dimension": "unit1-dimension-2",
        "legacy_code": "unit1-legacy-code-2",
        "use_molecular_weight": False,
        "conversion_factor_to_master": 1.0,
        "order": 2,
    }
    response = api_client.post("/concepts/unit-definitions", json=data)

    assert_response_status_code(response, 409)

    res = response.json()

    assert res["type"] == "AlreadyExistsException"
    assert res["message"] == "Unit Definition with ['name: unit1'] already exists."


def test_get_all_11(api_client):
    response = api_client.get("/concepts/unit-definitions")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res["items"][0]["unit_subsets"] == []
    assert res["items"][0]["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res["items"][0]["end_date"] is None
    assert res["items"][0]["status"] == "Draft"
    assert res["items"][0]["version"] == "0.1"
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["change_description"] == "Initial version"
    assert res["items"][0]["uid"] == "UnitDefinition_000001"
    assert res["items"][0]["name"] == "unit1"
    assert res["items"][0]["library_name"] == "Test library"
    assert res["items"][0]["convertible_unit"] is True
    assert res["items"][0]["display_unit"] is True
    assert res["items"][0]["master_unit"] is True
    assert res["items"][0]["si_unit"] is True
    assert res["items"][0]["us_conventional_unit"] is True
    assert res["items"][0]["legacy_code"] == "unit1-legacy-code"
    assert res["items"][0]["use_molecular_weight"] is False
    assert res["items"][0]["conversion_factor_to_master"] == 1.0
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["ucum"] is None
    assert res["items"][0]["comment"] is None
    assert res["items"][0]["definition"] is None
    assert res["items"][0]["template_parameter"] is False


def test_delete_success1(api_client):
    response = api_client.delete("/concepts/unit-definitions/UnitDefinition_000001")

    assert_response_status_code(response, 204)


def test_empty_list5(api_client):
    response = api_client.get("/concepts/unit-definitions")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res == {"items": [], "page": 1, "size": 10, "total": 0}


def test_adding3(api_client):
    data = {
        "name": "unit1",
        "library_name": "Test library",
        "ct_units": ["unit1-ct-uid"],
        "convertible_unit": True,
        "display_unit": True,
        "master_unit": True,
        "si_unit": True,
        "us_conventional_unit": True,
        "unit_dimension": "unit1-dimension",
        "legacy_code": "unit1-legacy-code",
        "use_molecular_weight": False,
        "conversion_factor_to_master": 1.0,
        "order": 1,
    }
    response = api_client.post("/concepts/unit-definitions", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Initial version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_retire_draft_fail2(api_client):
    response = api_client.delete(
        "/concepts/unit-definitions/UnitDefinition_000002/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Cannot retire draft version."


def test_reactivate_draft_fail2(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Only RETIRED version can be reactivated."


def test_post_versions_draft_fail2(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/versions"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "New draft version can be created only for FINAL versions."


def test_get_all3(api_client):
    response = api_client.get("/concepts/unit-definitions")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res["items"][0]["unit_subsets"] == []
    assert res["items"][0]["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res["items"][0]["end_date"] is None
    assert res["items"][0]["status"] == "Draft"
    assert res["items"][0]["version"] == "0.1"
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["change_description"] == "Initial version"
    assert res["items"][0]["uid"] == "UnitDefinition_000002"
    assert res["items"][0]["name"] == "unit1"
    assert res["items"][0]["library_name"] == "Test library"
    assert res["items"][0]["convertible_unit"] is True
    assert res["items"][0]["display_unit"] is True
    assert res["items"][0]["master_unit"] is True
    assert res["items"][0]["si_unit"] is True
    assert res["items"][0]["us_conventional_unit"] is True
    assert res["items"][0]["legacy_code"] == "unit1-legacy-code"
    assert res["items"][0]["use_molecular_weight"] is False
    assert res["items"][0]["conversion_factor_to_master"] == 1.0
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["ucum"] is None
    assert res["items"][0]["comment"] is None
    assert res["items"][0]["definition"] is None
    assert res["items"][0]["template_parameter"] is False


def test_get_specific_latest3(api_client):
    response = api_client.get("/concepts/unit-definitions/UnitDefinition_000002")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Initial version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_status_draft2(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?status=Draft"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Initial version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_version_0_12(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?version=0.1"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Initial version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_at_specified_date_start_date_ofv0_1_11(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?at_specified_date={start_date_ofV0_1}"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Initial version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_status_final3(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?status=Final"
    )

    assert_response_status_code(response, 404)

    res = response.json()

    assert res["type"] == "NotFoundException"
    assert (
        res["message"]
        == "Unit Definition with UID 'UnitDefinition_000002' doesn't exist."
    )


def test_get_specific_version_0_2_11(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?version=0.2"
    )

    assert_response_status_code(response, 404)

    res = response.json()

    assert res["type"] == "NotFoundException"
    assert (
        res["message"]
        == "Unit Definition with UID 'UnitDefinition_000002' doesn't exist."
    )


def test_get_specific_status_retired2(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?status=Retired"
    )

    assert_response_status_code(response, 404)

    res = response.json()

    assert res["type"] == "NotFoundException"
    assert (
        res["message"]
        == "Unit Definition with UID 'UnitDefinition_000002' doesn't exist."
    )


def test_patch1(api_client):
    data = {
        "change_description": "Patched version",
        "name": "unit1-patched",
        "unit_dimension": "unit1-dimension-patched",
        "legacy_code": "unit1-legacy-code-patched",
    }
    response = api_client.patch(
        "/concepts/unit-definitions/UnitDefinition_000002", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Patched version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_all4(api_client):
    response = api_client.get("/concepts/unit-definitions")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res["items"][0]["unit_subsets"] == []
    assert res["items"][0]["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["items"][0]["end_date"] is None
    assert res["items"][0]["status"] == "Draft"
    assert res["items"][0]["version"] == "0.2"
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["change_description"] == "Patched version"
    assert res["items"][0]["uid"] == "UnitDefinition_000002"
    assert res["items"][0]["name"] == "unit1-patched"
    assert res["items"][0]["library_name"] == "Test library"
    assert res["items"][0]["convertible_unit"] is True
    assert res["items"][0]["display_unit"] is True
    assert res["items"][0]["master_unit"] is True
    assert res["items"][0]["si_unit"] is True
    assert res["items"][0]["us_conventional_unit"] is True
    assert res["items"][0]["legacy_code"] == "unit1-legacy-code-patched"
    assert res["items"][0]["use_molecular_weight"] is False
    assert res["items"][0]["conversion_factor_to_master"] == 1.0
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["ucum"] is None
    assert res["items"][0]["comment"] is None
    assert res["items"][0]["definition"] is None
    assert res["items"][0]["template_parameter"] is False


def test_get_specific_latest4(api_client):
    response = api_client.get("/concepts/unit-definitions/UnitDefinition_000002")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Patched version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_status_draft3(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?status=Draft"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Patched version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_version_0_2_21(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?version=0.2"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Patched version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_at_specified_date_start_date_ofv0_21(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?at_specified_date={start_date_ofV0_2}"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Patched version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_version_0_13(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?version=0.1"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res["end_date"]
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Initial version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_status_final4(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?status=Final"
    )

    assert_response_status_code(response, 404)

    res = response.json()

    assert res["type"] == "NotFoundException"
    assert (
        res["message"]
        == "Unit Definition with UID 'UnitDefinition_000002' doesn't exist."
    )


def test_get_specific_status_retired3(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?status=Retired"
    )

    assert_response_status_code(response, 404)

    res = response.json()

    assert res["type"] == "NotFoundException"
    assert (
        res["message"]
        == "Unit Definition with UID 'UnitDefinition_000002' doesn't exist."
    )


def test_approve1(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/approvals"
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Approved version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_all_after_approval1(api_client):
    response = api_client.get("/concepts/unit-definitions")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["items"][0]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res["items"][0]["unit_subsets"] == []
    assert res["items"][0]["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["items"][0]["end_date"] is None
    assert res["items"][0]["status"] == "Final"
    assert res["items"][0]["version"] == "1.0"
    assert res["items"][0]["author_username"] == "unknown-user@example.com"
    assert res["items"][0]["change_description"] == "Approved version"
    assert res["items"][0]["uid"] == "UnitDefinition_000002"
    assert res["items"][0]["name"] == "unit1-patched"
    assert res["items"][0]["library_name"] == "Test library"
    assert res["items"][0]["convertible_unit"] is True
    assert res["items"][0]["display_unit"] is True
    assert res["items"][0]["master_unit"] is True
    assert res["items"][0]["si_unit"] is True
    assert res["items"][0]["us_conventional_unit"] is True
    assert res["items"][0]["legacy_code"] == "unit1-legacy-code-patched"
    assert res["items"][0]["use_molecular_weight"] is False
    assert res["items"][0]["conversion_factor_to_master"] == 1.0
    assert res["items"][0]["order"] == 1
    assert res["items"][0]["ucum"] is None
    assert res["items"][0]["comment"] is None
    assert res["items"][0]["definition"] is None
    assert res["items"][0]["template_parameter"] is False


def test_get_by_uid_after_approval1(api_client):
    response = api_client.get("/concepts/unit-definitions/UnitDefinition_000002")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Approved version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_by_uid_after_approval_status_final1(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?status=Final"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Approved version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_by_uid_after_approval_version_1_1(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?version=1.0"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Approved version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_approve_final_fail2(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/approvals"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object isn't in draft status."


def test_reactivate_final_fail2(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Only RETIRED version can be reactivated."


def test_patch_final_fail2(api_client):
    data = {
        "change_description": "Patched version 2 (failed)",
        "name": "unit1-patched-fail",
        "unit_dimension": "unit1-dimension-patched-fail",
        "legacy_code": "unit1-legacy-code-patched-fail",
    }
    response = api_client.patch(
        "/concepts/unit-definitions/UnitDefinition_000002", json=data
    )

    assert_response_status_code(response, 422)

    res = response.json()

    assert res["type"] == "ValidationException"
    assert res["message"] == "Unknown CT dimension uid: unit1-dimension-patched-fail"


def test_delete_final_fail2(api_client):
    response = api_client.delete("/concepts/unit-definitions/UnitDefinition_000002")

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Object has been accepted"


def test_inactivate1(api_client):
    response = api_client.delete(
        "/concepts/unit-definitions/UnitDefinition_000002/activations"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Retired"
    assert res["version"] == "1.0"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Inactivated version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_retire_retired_fail1(api_client):
    response = api_client.delete(
        "/concepts/unit-definitions/UnitDefinition_000002/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Cannot retire draft version."


def test_post_versions_on_retired_fail1(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/versions"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Cannot create new Draft version"


def test_approve_retired_fail1(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/approvals"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Only DRAFT version can be approved."


def test_patch_retired_fail1(api_client):
    data = {
        "change_description": "Patched version 2 (failed)",
        "name": "unit1-patched-fail",
        "unit_dimension": "unit1-dimension-patched-fail",
        "legacy_code": "unit1-legacy-code-patched-fail",
    }
    response = api_client.patch(
        "/concepts/unit-definitions/UnitDefinition_000002", json=data
    )

    assert_response_status_code(response, 422)

    res = response.json()

    assert res["type"] == "ValidationException"
    assert res["message"] == "Unknown CT dimension uid: unit1-dimension-patched-fail"


def test_delete_retired_fail1(api_client):
    response = api_client.delete("/concepts/unit-definitions/UnitDefinition_000002")

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Object has been accepted"


def test_reactivate1(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/activations"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Reactivated version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_approve_final_fail3(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/approvals"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object isn't in draft status."


def test_reactivate_final_fail3(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Only RETIRED version can be reactivated."


def test_patch_final_fail3(api_client):
    data = {
        "change_description": "Patched version 2 (failed)",
        "name": "unit1-patched-fail",
        "unit_dimension": "unit1-dimension-patched-fail",
        "legacy_code": "unit1-legacy-code-patched-fail",
    }
    response = api_client.patch(
        "/concepts/unit-definitions/UnitDefinition_000002", json=data
    )

    assert_response_status_code(response, 422)

    res = response.json()

    assert res["type"] == "ValidationException"
    assert res["message"] == "Unknown CT dimension uid: unit1-dimension-patched-fail"


def test_delete_final_fail3(api_client):
    response = api_client.delete("/concepts/unit-definitions/UnitDefinition_000002")

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Object has been accepted"


def test_post_versions1(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/versions"
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "1.1"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "New draft created"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_retire_draft_fail3(api_client):
    response = api_client.delete(
        "/concepts/unit-definitions/UnitDefinition_000002/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Cannot retire draft version."


def test_reactivate_draft_fail3(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Only RETIRED version can be reactivated."


def test_post_versions_draft_fail3(api_client):
    response = api_client.post(
        "/concepts/unit-definitions/UnitDefinition_000002/versions"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "New draft version can be created only for FINAL versions."


def test_delete_draft_that_had_been_accepted_fail1(api_client):
    response = api_client.delete("/concepts/unit-definitions/UnitDefinition_000002")

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Object has been accepted"


def test_patch_next_major_version1(api_client):
    data = {
        "change_description": "Patched version 2",
        "name": "unit1-patched-2",
        "unit_dimension": "unit1-dimension-patched-2",
        "legacy_code": "unit1-legacy-code-patched-2",
    }
    response = api_client.patch(
        "/concepts/unit-definitions/UnitDefinition_000002", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched-2",
        "name": "CT Unit Dim term 4",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "1.2"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Patched version 2"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched-2"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched-2"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_latest5(api_client):
    response = api_client.get("/concepts/unit-definitions/UnitDefinition_000002")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched-2",
        "name": "CT Unit Dim term 4",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "1.2"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Patched version 2"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched-2"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched-2"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_specific_status_final5(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002?status=Final"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"]
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Reactivated version"
    assert res["uid"] == "UnitDefinition_000002"
    assert res["name"] == "unit1-patched"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_get_versions2(api_client):
    response = api_client.get(
        "/concepts/unit-definitions/UnitDefinition_000002/versions"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res[0]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res[0]["unit_subsets"] == []
    assert res[0]["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched-2",
        "name": "CT Unit Dim term 4",
    }
    assert res[0]["end_date"] is None
    assert res[0]["status"] == "Draft"
    assert res[0]["version"] == "1.2"
    assert res[0]["author_username"] == "unknown-user@example.com"
    assert res[0]["change_description"] == "Patched version 2"
    assert res[0]["uid"] == "UnitDefinition_000002"
    assert res[0]["name"] == "unit1-patched-2"
    assert res[0]["library_name"] == "Test library"
    assert res[0]["convertible_unit"] is True
    assert res[0]["display_unit"] is True
    assert res[0]["master_unit"] is True
    assert res[0]["si_unit"] is True
    assert res[0]["us_conventional_unit"] is True
    assert res[0]["legacy_code"] == "unit1-legacy-code-patched-2"
    assert res[0]["use_molecular_weight"] is False
    assert res[0]["conversion_factor_to_master"] == 1.0
    assert res[0]["order"] == 1
    assert res[0]["ucum"] is None
    assert res[0]["comment"] is None
    assert res[0]["definition"] is None
    assert res[0]["template_parameter"] is False
    assert res[1]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res[1]["unit_subsets"] == []
    assert res[1]["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res[1]["end_date"]
    assert res[1]["status"] == "Draft"
    assert res[1]["version"] == "1.1"
    assert res[1]["author_username"] == "unknown-user@example.com"
    assert res[1]["change_description"] == "New draft created"
    assert res[1]["uid"] == "UnitDefinition_000002"
    assert res[1]["name"] == "unit1-patched"
    assert res[1]["library_name"] == "Test library"
    assert res[1]["convertible_unit"] is True
    assert res[1]["display_unit"] is True
    assert res[1]["master_unit"] is True
    assert res[1]["si_unit"] is True
    assert res[1]["us_conventional_unit"] is True
    assert res[1]["legacy_code"] == "unit1-legacy-code-patched"
    assert res[1]["use_molecular_weight"] is False
    assert res[1]["conversion_factor_to_master"] == 1.0
    assert res[1]["order"] == 1
    assert res[1]["ucum"] is None
    assert res[1]["comment"] is None
    assert res[1]["definition"] is None
    assert res[1]["template_parameter"] is False
    assert res[2]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res[2]["unit_subsets"] == []
    assert res[2]["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res[2]["end_date"]
    assert res[2]["status"] == "Final"
    assert res[2]["version"] == "1.0"
    assert res[2]["author_username"] == "unknown-user@example.com"
    assert res[2]["change_description"] == "Reactivated version"
    assert res[2]["uid"] == "UnitDefinition_000002"
    assert res[2]["name"] == "unit1-patched"
    assert res[2]["library_name"] == "Test library"
    assert res[2]["convertible_unit"] is True
    assert res[2]["display_unit"] is True
    assert res[2]["master_unit"] is True
    assert res[2]["si_unit"] is True
    assert res[2]["us_conventional_unit"] is True
    assert res[2]["legacy_code"] == "unit1-legacy-code-patched"
    assert res[2]["use_molecular_weight"] is False
    assert res[2]["conversion_factor_to_master"] == 1.0
    assert res[2]["order"] == 1
    assert res[2]["ucum"] is None
    assert res[2]["comment"] is None
    assert res[2]["definition"] is None
    assert res[2]["template_parameter"] is False
    assert res[3]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res[3]["unit_subsets"] == []
    assert res[3]["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res[3]["end_date"]
    assert res[3]["status"] == "Retired"
    assert res[3]["version"] == "1.0"
    assert res[3]["author_username"] == "unknown-user@example.com"
    assert res[3]["change_description"] == "Inactivated version"
    assert res[3]["uid"] == "UnitDefinition_000002"
    assert res[3]["name"] == "unit1-patched"
    assert res[3]["library_name"] == "Test library"
    assert res[3]["convertible_unit"] is True
    assert res[3]["display_unit"] is True
    assert res[3]["master_unit"] is True
    assert res[3]["si_unit"] is True
    assert res[3]["us_conventional_unit"] is True
    assert res[3]["legacy_code"] == "unit1-legacy-code-patched"
    assert res[3]["use_molecular_weight"] is False
    assert res[3]["conversion_factor_to_master"] == 1.0
    assert res[3]["order"] == 1
    assert res[3]["ucum"] is None
    assert res[3]["comment"] is None
    assert res[3]["definition"] is None
    assert res[3]["template_parameter"] is False
    assert res[4]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res[4]["unit_subsets"] == []
    assert res[4]["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res[4]["end_date"]
    assert res[4]["status"] == "Final"
    assert res[4]["version"] == "1.0"
    assert res[4]["author_username"] == "unknown-user@example.com"
    assert res[4]["change_description"] == "Approved version"
    assert res[4]["uid"] == "UnitDefinition_000002"
    assert res[4]["name"] == "unit1-patched"
    assert res[4]["library_name"] == "Test library"
    assert res[4]["convertible_unit"] is True
    assert res[4]["display_unit"] is True
    assert res[4]["master_unit"] is True
    assert res[4]["si_unit"] is True
    assert res[4]["us_conventional_unit"] is True
    assert res[4]["legacy_code"] == "unit1-legacy-code-patched"
    assert res[4]["use_molecular_weight"] is False
    assert res[4]["conversion_factor_to_master"] == 1.0
    assert res[4]["order"] == 1
    assert res[4]["ucum"] is None
    assert res[4]["comment"] is None
    assert res[4]["definition"] is None
    assert res[4]["template_parameter"] is False
    assert res[5]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res[5]["unit_subsets"] == []
    assert res[5]["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res[5]["end_date"]
    assert res[5]["status"] == "Draft"
    assert res[5]["version"] == "0.2"
    assert res[5]["author_username"] == "unknown-user@example.com"
    assert res[5]["change_description"] == "Patched version"
    assert res[5]["uid"] == "UnitDefinition_000002"
    assert res[5]["name"] == "unit1-patched"
    assert res[5]["library_name"] == "Test library"
    assert res[5]["convertible_unit"] is True
    assert res[5]["display_unit"] is True
    assert res[5]["master_unit"] is True
    assert res[5]["si_unit"] is True
    assert res[5]["us_conventional_unit"] is True
    assert res[5]["legacy_code"] == "unit1-legacy-code-patched"
    assert res[5]["use_molecular_weight"] is False
    assert res[5]["conversion_factor_to_master"] == 1.0
    assert res[5]["order"] == 1
    assert res[5]["ucum"] is None
    assert res[5]["comment"] is None
    assert res[5]["definition"] is None
    assert res[5]["template_parameter"] is False
    assert res[6]["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"}
    ]
    assert res[6]["unit_subsets"] == []
    assert res[6]["unit_dimension"] == {
        "term_uid": "unit1-dimension",
        "name": "CT Unit Dim term 1",
    }
    assert res[6]["end_date"]
    assert res[6]["status"] == "Draft"
    assert res[6]["version"] == "0.1"
    assert res[6]["author_username"] == "unknown-user@example.com"
    assert res[6]["change_description"] == "Initial version"
    assert res[6]["uid"] == "UnitDefinition_000002"
    assert res[6]["name"] == "unit1"
    assert res[6]["library_name"] == "Test library"
    assert res[6]["convertible_unit"] is True
    assert res[6]["display_unit"] is True
    assert res[6]["master_unit"] is True
    assert res[6]["si_unit"] is True
    assert res[6]["us_conventional_unit"] is True
    assert res[6]["legacy_code"] == "unit1-legacy-code"
    assert res[6]["use_molecular_weight"] is False
    assert res[6]["conversion_factor_to_master"] == 1.0
    assert res[6]["order"] == 1
    assert res[6]["ucum"] is None
    assert res[6]["comment"] is None
    assert res[6]["definition"] is None
    assert res[6]["template_parameter"] is False


def test_adding_another_master_unit_in_the_same_dimension(api_client):
    data = {
        "name": "unit2",
        "library_name": "Test library",
        "ct_units": ["unit1-ct-uid-2"],
        "unit_subsets": [],
        "convertible_unit": True,
        "display_unit": True,
        "master_unit": True,
        "si_unit": True,
        "us_conventional_unit": True,
        "unit_dimension": "unit1-dimension-patched-2",
        "legacy_code": "unit1-legacy-code",
        "use_molecular_weight": False,
        "conversion_factor_to_master": 1.0,
        "order": 1,
    }
    response = api_client.post("/concepts/unit-definitions", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "Attempt to create another master unit in dimension 'unit1-dimension-patched-2'."
    )


def test_adding_another_master_unit_in_different_dimension(api_client):
    data = {
        "name": "unit3",
        "library_name": "Test library",
        "ct_units": ["unit1-ct-uid-3"],
        "unit_subsets": [],
        "convertible_unit": True,
        "display_unit": True,
        "master_unit": True,
        "si_unit": True,
        "us_conventional_unit": True,
        "unit_dimension": "other-dimension",
        "legacy_code": "unit1-legacy-code",
        "use_molecular_weight": False,
        "conversion_factor_to_master": 1.0,
        "order": 1,
    }
    response = api_client.post("/concepts/unit-definitions", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Initial version"
    assert res["uid"] == "UnitDefinition_000003"
    assert res["name"] == "unit3"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["ct_units"] == [{"term_uid": "unit1-ct-uid-3", "name": "CT Unit term 4"}]
    assert res["unit_subsets"] == []
    assert res["unit_dimension"] == {
        "term_uid": "other-dimension",
        "name": "CT Unit Dim term 5",
    }
    assert res["legacy_code"] == "unit1-legacy-code"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False


def test_patch_into_another_master_unit_in_the_same_dimension(api_client):
    data = {
        "change_description": "Patched version",
        "unit_dimension": "unit1-dimension-patched-2",
    }
    response = api_client.patch(
        "/concepts/unit-definitions/UnitDefinition_000003", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "Attempt to make 'UnitDefinition_000003' another master unit in dimension 'unit1-dimension-patched-2'."
    )


def test_patch2(api_client):
    data = {
        "change_description": "Patched version",
        "ct_units": ["unit1-ct-uid", "unit1-ct-uid-2"],
        "unit_subsets": ["unit-subset-uid-1", "unit-subset-uid-2"],
        "unit_dimension": "unit1-dimension-patched",
        "legacy_code": "unit1-legacy-code-patched",
    }
    response = api_client.patch(
        "/concepts/unit-definitions/UnitDefinition_000003", json=data
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["ct_units"] == [
        {"term_uid": "unit1-ct-uid", "name": "CT Unit term 1"},
        {"term_uid": "unit1-ct-uid-2", "name": "CT Unit term 3"},
    ]
    assert res["unit_subsets"] == [
        {"term_uid": "unit-subset-uid-1", "name": "CT Unit Subset term 1"},
        {"term_uid": "unit-subset-uid-2", "name": "CT Unit Subset term 2"},
    ]
    assert res["unit_dimension"] == {
        "term_uid": "unit1-dimension-patched",
        "name": "CT Unit Dim term 3",
    }
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.2"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["change_description"] == "Patched version"
    assert res["uid"] == "UnitDefinition_000003"
    assert res["name"] == "unit3"
    assert res["library_name"] == "Test library"
    assert res["convertible_unit"] is True
    assert res["display_unit"] is True
    assert res["master_unit"] is True
    assert res["si_unit"] is True
    assert res["us_conventional_unit"] is True
    assert res["legacy_code"] == "unit1-legacy-code-patched"
    assert res["use_molecular_weight"] is False
    assert res["conversion_factor_to_master"] == 1.0
    assert res["order"] == 1
    assert res["ucum"] is None
    assert res["comment"] is None
    assert res["definition"] is None
    assert res["template_parameter"] is False
