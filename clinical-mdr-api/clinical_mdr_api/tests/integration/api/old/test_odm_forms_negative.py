# pylint: disable=unused-argument, redefined-outer-name, too-many-arguments, line-too-long, too-many-statements

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.tests.integration.utils.api import drop_db, inject_and_clear_db
from clinical_mdr_api.tests.integration.utils.data_library import (
    STARTUP_CT_TERM,
    STARTUP_ODM_ALIASES,
    STARTUP_ODM_DESCRIPTIONS,
    STARTUP_ODM_ITEM_GROUPS,
    STARTUP_ODM_VENDOR_ATTRIBUTES,
    STARTUP_ODM_VENDOR_ELEMENTS,
    STARTUP_ODM_VENDOR_NAMESPACES,
)
from clinical_mdr_api.tests.utils.checks import assert_response_status_code


@pytest.fixture(scope="module")
def api_client(test_data):
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    inject_and_clear_db("old.json.test.odm.forms.negative")
    db.cypher_query(STARTUP_ODM_DESCRIPTIONS)
    db.cypher_query(STARTUP_CT_TERM)
    db.cypher_query(STARTUP_ODM_ALIASES)
    db.cypher_query(STARTUP_ODM_ITEM_GROUPS)
    db.cypher_query(STARTUP_ODM_VENDOR_NAMESPACES)
    db.cypher_query(STARTUP_ODM_VENDOR_ELEMENTS)
    db.cypher_query(STARTUP_ODM_VENDOR_ATTRIBUTES)

    yield

    drop_db("old.json.test.odm.forms.negative")


def test_create_a_new_odm_form(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name1",
        "oid": "oid1",
        "sdtm_version": "0.1",
        "repeating": "No",
        "scope_uid": "term1",
        "descriptions": ["odm_description2", "odm_description3"],
        "alias_uids": ["odm_alias1"],
    }
    response = api_client.post("concepts/odms/forms", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmForm_000001"
    assert res["name"] == "name1"
    assert res["library_name"] == "Sponsor"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["sdtm_version"] == "0.1"
    assert res["scope"] == {
        "uid": "term1",
        "code_submission_value": "code_submission_value1",
        "preferred_term": "preferred_term1",
    }
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
    assert res["activity_groups"] == []
    assert res["item_groups"] == []
    assert res["vendor_elements"] == []
    assert res["vendor_attributes"] == []
    assert res["vendor_element_attributes"] == []
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_cannot_add_odm_vendor_attribute_with_an_invalid_value_to_an_odm_form(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute3", "value": "3423"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Provided values for following attributes don't match their regex pattern:

{'odm_vendor_attribute3': '^[a-zA-Z]+$'}"""
    )


def test_cannot_add_odm_vendor_element_attribute_with_an_invalid_value_to_an_odm_form(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute1", "value": "3423"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-element-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Provided values for following attributes don't match their regex pattern:

{'odm_vendor_attribute1': '^[a-zA-Z]+$'}"""
    )


def test_add_odm_vendor_element_to_an_odm_form(api_client):
    data = [{"uid": "odm_vendor_element1", "value": "value1"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-elements", json=data
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmForm_000001"
    assert res["name"] == "name1"
    assert res["library_name"] == "Sponsor"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["sdtm_version"] == "0.1"
    assert res["scope"] == {
        "code_submission_value": "code_submission_value1",
        "preferred_term": "preferred_term1",
        "uid": "term1",
    }
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
    assert res["activity_groups"] == []
    assert res["item_groups"] == []
    assert res["vendor_elements"] == [
        {"uid": "odm_vendor_element1", "name": "nameOne", "value": "value1"}
    ]
    assert res["vendor_attributes"] == []
    assert res["vendor_element_attributes"] == []
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_add_odm_vendor_element_attribute_to_an_odm_form(api_client):
    data = [{"uid": "odm_vendor_attribute1", "value": "valueOne"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-element-attributes", json=data
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmForm_000001"
    assert res["name"] == "name1"
    assert res["library_name"] == "Sponsor"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["sdtm_version"] == "0.1"
    assert res["scope"] == {
        "code_submission_value": "code_submission_value1",
        "preferred_term": "preferred_term1",
        "uid": "term1",
    }
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
    assert res["activity_groups"] == []
    assert res["item_groups"] == []
    assert res["vendor_elements"] == [
        {"uid": "odm_vendor_element1", "name": "nameOne", "value": "value1"}
    ]
    assert res["vendor_attributes"] == []
    assert res["vendor_element_attributes"] == [
        {
            "uid": "odm_vendor_attribute1",
            "name": "nameOne",
            "data_type": "string",
            "value_regex": "^[a-zA-Z]+$",
            "value": "valueOne",
            "vendor_element_uid": "odm_vendor_element1",
        }
    ]
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_cannot_create_a_new_odm_form_with_same_properties(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name1",
        "oid": "oid1",
        "sdtm_version": "0.1",
        "repeating": "No",
        "scope_uid": "term1",
        "descriptions": ["odm_description2", "odm_description3"],
        "alias_uids": ["odm_alias1"],
    }
    response = api_client.post("concepts/odms/forms", json=data)

    assert_response_status_code(response, 409)

    res = response.json()

    assert res["type"] == "AlreadyExistsException"
    assert (
        res["message"]
        == "ODM Form already exists with UID (OdmForm_000001) and data {'description_uids': ['odm_description2', 'odm_description3'], 'alias_uids': ['odm_alias1'], 'scope_uid': 'term1', 'name': 'name1', 'oid': 'oid1', 'sdtm_version': '0.1', 'repeating': False}"
    )


def test_cannot_create_an_odm_form_connected_to_non_existent_scope(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "new name",
        "oid": "new oid",
        "sdtm_version": "0.1",
        "repeating": "No",
        "scope_uid": "wrong_uid",
        "descriptions": [],
        "alias_uids": [],
    }
    response = api_client.post("concepts/odms/forms", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "ODM Form tried to connect to non-existent Scope with UID 'wrong_uid'."
    )


def test_cannot_create_an_odm_form_connected_to_non_existent_concepts(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "new name",
        "oid": "new oid",
        "sdtm_version": "0.1",
        "repeating": "No",
        "descriptions": ["wrong_uid"],
        "alias_uids": ["wrong_uid"],
    }
    response = api_client.post("concepts/odms/forms", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """ODM Form tried to connect to non-existent concepts [('Concept Name: ODM Description', "uids: {'wrong_uid'}"), ('Concept Name: ODM Alias', "uids: {'wrong_uid'}")]."""
    )


def test_getting_error_for_retrieving_non_existent_odm_form(api_client):
    response = api_client.get("concepts/odms/forms/OdmForm_000002")

    assert_response_status_code(response, 404)

    res = response.json()

    assert res["type"] == "NotFoundException"
    assert (
        res["message"]
        == "OdmFormAR with UID 'OdmForm_000002' doesn't exist or there's no version with requested status or version number."
    )


def test_cannot_inactivate_an_odm_form_that_is_in_draft_status(api_client):
    response = api_client.delete("concepts/odms/forms/OdmForm_000001/activations")

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Cannot retire draft version."


def test_cannot_reactivate_an_odm_form_that_is_not_retired(api_client):
    response = api_client.post("concepts/odms/forms/OdmForm_000001/activations")

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Only RETIRED version can be reactivated."


def test_cannot_override_odm_vendor_element_that_has_attributes_connected_this_odm_form(
    api_client,
):
    data = [{"uid": "odm_vendor_element2", "value": "value"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-elements?override=true", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "Cannot remove an ODM Vendor Element whose attributes are connected to this ODM element."
    )


def test_cannot_add_odm_vendor_element_attribute_to_an_odm_form_as_an_odm_vendor_attribute(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute1", "value": "value"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "ODM Vendor Attribute with UID 'odm_vendor_attribute1' cannot not be added as an Vendor Attribute."
    )


def test_cannot_add_odm_vendor_attribute_to_an_odm_form_as_an_odm_vendor_element_attribute(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute3", "value": "value"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-element-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "ODM Vendor Attribute with UID 'odm_vendor_attribute3' cannot not be added as an Vendor Element Attribute."
    )


def test_approve_odm_form(api_client):
    response = api_client.post("concepts/odms/forms/OdmForm_000001/approvals")

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmForm_000001"
    assert res["name"] == "name1"
    assert res["library_name"] == "Sponsor"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Approved version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["sdtm_version"] == "0.1"
    assert res["scope"] == {
        "code_submission_value": "code_submission_value1",
        "preferred_term": "preferred_term1",
        "uid": "term1",
    }
    assert res["descriptions"] == [
        {
            "uid": "odm_description2",
            "name": "name2",
            "language": "language2",
            "description": "description2",
            "instruction": "instruction2",
            "sponsor_instruction": "sponsor_instruction2",
            "version": "1.0",
        },
        {
            "uid": "odm_description3",
            "name": "name3",
            "language": "ENG",
            "description": "description3",
            "instruction": "instruction3",
            "sponsor_instruction": "sponsor_instruction3",
            "version": "1.0",
        },
    ]
    assert res["aliases"] == [
        {"uid": "odm_alias1", "context": "context1", "name": "name1", "version": "0.1"}
    ]
    assert res["activity_groups"] == []
    assert res["item_groups"] == []
    assert res["vendor_elements"] == [
        {"uid": "odm_vendor_element1", "name": "nameOne", "value": "value1"}
    ]
    assert res["vendor_attributes"] == []
    assert res["vendor_element_attributes"] == [
        {
            "uid": "odm_vendor_attribute1",
            "name": "nameOne",
            "data_type": "string",
            "value_regex": "^[a-zA-Z]+$",
            "value": "valueOne",
            "vendor_element_uid": "odm_vendor_element1",
        }
    ]
    assert res["possible_actions"] == ["inactivate", "new_version"]


def test_cannot_add_odm_item_groups_with_an_invalid_value_to_an_odm_form(api_client):
    data = [
        {
            "uid": "odm_item_group1",
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "Yes",
            "collection_exception_condition_oid": "collection_exception_condition_oid1",
            "vendor": {
                "attributes": [{"uid": "odm_vendor_attribute3", "value": "3423"}]
            },
        }
    ]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/item-groups", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Provided values for following attributes don't match their regex pattern:

{'odm_vendor_attribute3': '^[a-zA-Z]+$'}"""
    )


def test_cannot_add_a_non_compatible_odm_vendor_attribute_to_an_odm_form(api_client):
    data = [{"uid": "odm_vendor_attribute5", "value": "value"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Trying to add non-compatible ODM Vendor:

{'odm_vendor_attribute5': ['NonCompatibleVendor']}"""
    )


def test_cannot_add_a_non_compatible_odm_vendor_element_to_an_odm_form(api_client):
    data = [{"uid": "odm_vendor_element4", "value": "value"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-elements", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Trying to add non-compatible ODM Vendor:

{'odm_vendor_element4': ['NonCompatibleVendor']}"""
    )


def test_cannot_add_odm_item_groups_with_non_compatible_odm_vendor_attribute_to_a_specific_odm_form(
    api_client,
):
    data = [
        {
            "uid": "odm_item_group1",
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "No",
            "collection_exception_condition_oid": "collection_exception_condition_oid1",
            "vendor": {"attributes": [{"uid": "odm_vendor_attribute5", "value": "No"}]},
        }
    ]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/item-groups", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Trying to add non-compatible ODM Vendor:

{'odm_vendor_attribute5': ['NonCompatibleVendor']}"""
    )


def test_inactivate_odm_form(api_client):
    response = api_client.delete("concepts/odms/forms/OdmForm_000001/activations")

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["uid"] == "OdmForm_000001"
    assert res["name"] == "name1"
    assert res["library_name"] == "Sponsor"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["end_date"] is None
    assert res["status"] == "Retired"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Inactivated version"
    assert res["author_username"] == "unknown-user@example.com"
    assert res["sdtm_version"] == "0.1"
    assert res["scope"] == {
        "code_submission_value": "code_submission_value1",
        "preferred_term": "preferred_term1",
        "uid": "term1",
    }
    assert res["descriptions"] == [
        {
            "uid": "odm_description2",
            "name": "name2",
            "language": "language2",
            "description": "description2",
            "instruction": "instruction2",
            "sponsor_instruction": "sponsor_instruction2",
            "version": "1.0",
        },
        {
            "uid": "odm_description3",
            "name": "name3",
            "language": "ENG",
            "description": "description3",
            "instruction": "instruction3",
            "sponsor_instruction": "sponsor_instruction3",
            "version": "1.0",
        },
    ]
    assert res["aliases"] == [
        {"uid": "odm_alias1", "context": "context1", "name": "name1", "version": "0.1"}
    ]
    assert res["activity_groups"] == []
    assert res["item_groups"] == []
    assert res["vendor_elements"] == [
        {"uid": "odm_vendor_element1", "name": "nameOne", "value": "value1"}
    ]
    assert res["vendor_attributes"] == []
    assert res["vendor_element_attributes"] == [
        {
            "uid": "odm_vendor_attribute1",
            "name": "nameOne",
            "data_type": "string",
            "value_regex": "^[a-zA-Z]+$",
            "value": "valueOne",
            "vendor_element_uid": "odm_vendor_element1",
        }
    ]
    assert res["possible_actions"] == ["delete", "reactivate"]


def test_cannot_add_odm_item_groups_to_an_odm_form_that_is_in_retired_status(
    api_client,
):
    data = [
        {
            "uid": "odm_item_group1",
            "order_number": 1,
            "mandatory": "Yes",
            "locked": "Yes",
            "collection_exception_condition_oid": "collection_exception_condition_oid1",
            "vendor": {"attributes": []},
        }
    ]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/item-groups", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"


def test_cannot_add_odm_activity_groups_to_an_odm_form_that_is_in_retired_status(
    api_client,
):
    data = [{"uid": "activity_group_root1"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/activity-groups", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"


def test_cannot_add_odm_vendor_element_to_an_odm_form_that_is_in_retired_status(
    api_client,
):
    data = [{"uid": "odm_vendor_element1", "value": "value"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-elements", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"


def test_cannot_add_odm_vendor_attribute_to_an_odm_form_that_is_in_retired_status(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute1", "value": "value"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"


def test_cannot_add_odm_vendor_element_attribute_to_an_odm_form_that_is_in_retired_status(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute1", "value": "value"}]
    response = api_client.post(
        "concepts/odms/forms/OdmForm_000001/vendor-element-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"
