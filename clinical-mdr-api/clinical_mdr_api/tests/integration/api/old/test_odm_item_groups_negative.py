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
    STARTUP_ODM_ITEMS,
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
    inject_and_clear_db("old.json.test.odm.item.groups.negative")
    db.cypher_query(STARTUP_ODM_DESCRIPTIONS)
    db.cypher_query(STARTUP_ODM_ALIASES)
    db.cypher_query(STARTUP_ODM_ITEMS)
    db.cypher_query(STARTUP_CT_TERM)
    db.cypher_query(STARTUP_ODM_VENDOR_NAMESPACES)
    db.cypher_query(STARTUP_ODM_VENDOR_ELEMENTS)
    db.cypher_query(STARTUP_ODM_VENDOR_ATTRIBUTES)

    yield

    drop_db("old.json.test.odm.item.groups.negative")


def test_create_a_new_odm_item_group(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name1",
        "oid": "oid1",
        "repeating": "No",
        "is_reference_data": "No",
        "sas_dataset_name": "sas_dataset_name1",
        "origin": "origin1",
        "purpose": "purpose1",
        "comment": "comment1",
        "descriptions": ["odm_description2", "odm_description3"],
        "alias_uids": ["odm_alias1"],
        "sdtm_domain_uids": ["term1"],
    }
    response = api_client.post("concepts/odms/item-groups", json=data)

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmItemGroup_000001"
    assert res["library_name"] == "Sponsor"
    assert res["name"] == "name1"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["is_reference_data"] == "No"
    assert res["sas_dataset_name"] == "sas_dataset_name1"
    assert res["origin"] == "origin1"
    assert res["purpose"] == "purpose1"
    assert res["comment"] == "comment1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
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
    assert res["sdtm_domains"] == [
        {
            "uid": "term1",
            "code_submission_value": "code_submission_value1",
            "preferred_term": "preferred_term1",
        }
    ]
    assert res["activity_subgroups"] == []
    assert res["items"] == []
    assert res["vendor_elements"] == []
    assert res["vendor_attributes"] == []
    assert res["vendor_element_attributes"] == []
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_cannot_add_odm_vendor_attribute_with_an_invalid_value_to_an_odm_item_group(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute3", "value": "3423"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Provided values for following attributes don't match their regex pattern:

{'odm_vendor_attribute3': '^[a-zA-Z]+$'}"""
    )


def test_cannot_add_a_non_compatible_odm_vendor_attribute_to_an_odm_item_group(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute5", "value": "value"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Trying to add non-compatible ODM Vendor:

{'odm_vendor_attribute5': ['NonCompatibleVendor']}"""
    )


def test_cannot_add_a_non_compatible_odm_vendor_element_to_an_odm_item_group(
    api_client,
):
    data = [{"uid": "odm_vendor_element4", "value": "value"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-elements", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Trying to add non-compatible ODM Vendor:

{'odm_vendor_element4': ['NonCompatibleVendor']}"""
    )


def test_cannot_add_odm_items_with_non_compatible_odm_vendor_attribute_to_a_specific_odm_item_group(
    api_client,
):
    data = [
        {
            "uid": "odm_item1",
            "order_number": 1,
            "mandatory": "Yes",
            "key_sequence": "key_sequence1",
            "method_oid": "method_oid1",
            "imputation_method_oid": "imputation_method_oid1",
            "role": "role1",
            "role_codelist_oid": "role_codelist_oid1",
            "collection_exception_condition_oid": "collection_exception_condition_oid1",
            "vendor": {"attributes": [{"uid": "odm_vendor_attribute5", "value": "No"}]},
        }
    ]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/items", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Trying to add non-compatible ODM Vendor:

{'odm_vendor_attribute5': ['NonCompatibleVendor']}"""
    )


def test_cannot_add_odm_vendor_element_attribute_with_an_invalid_value_to_an_odm_item_group(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute1", "value": "3423"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-element-attributes",
        json=data,
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Provided values for following attributes don't match their regex pattern:

{'odm_vendor_attribute1': '^[a-zA-Z]+$'}"""
    )


def test_add_odm_vendor_element_to_an_odm_item_group(api_client):
    data = [{"uid": "odm_vendor_element1", "value": "value1"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-elements", json=data
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmItemGroup_000001"
    assert res["library_name"] == "Sponsor"
    assert res["name"] == "name1"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["is_reference_data"] == "No"
    assert res["sas_dataset_name"] == "sas_dataset_name1"
    assert res["origin"] == "origin1"
    assert res["purpose"] == "purpose1"
    assert res["comment"] == "comment1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
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
    assert res["sdtm_domains"] == [
        {
            "uid": "term1",
            "code_submission_value": "code_submission_value1",
            "preferred_term": "preferred_term1",
        }
    ]
    assert res["activity_subgroups"] == []
    assert res["items"] == []
    assert res["vendor_elements"] == [
        {"uid": "odm_vendor_element1", "name": "nameOne", "value": "value1"}
    ]
    assert res["vendor_attributes"] == []
    assert res["vendor_element_attributes"] == []
    assert res["possible_actions"] == ["approve", "delete", "edit"]


def test_add_odm_vendor_element_attribute_to_an_odm_item_group(api_client):
    data = [{"uid": "odm_vendor_attribute1", "value": "valueOne"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-element-attributes",
        json=data,
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmItemGroup_000001"
    assert res["library_name"] == "Sponsor"
    assert res["name"] == "name1"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["is_reference_data"] == "No"
    assert res["sas_dataset_name"] == "sas_dataset_name1"
    assert res["origin"] == "origin1"
    assert res["purpose"] == "purpose1"
    assert res["comment"] == "comment1"
    assert res["end_date"] is None
    assert res["status"] == "Draft"
    assert res["version"] == "0.1"
    assert res["change_description"] == "Initial version"
    assert res["author_username"] == "unknown-user@example.com"
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
    assert res["sdtm_domains"] == [
        {
            "uid": "term1",
            "code_submission_value": "code_submission_value1",
            "preferred_term": "preferred_term1",
        }
    ]
    assert res["activity_subgroups"] == []
    assert res["items"] == []
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


def test_cannot_create_a_new_odm_item_group_with_same_properties(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "name1",
        "oid": "oid1",
        "repeating": "No",
        "is_reference_data": "No",
        "sas_dataset_name": "sas_dataset_name1",
        "origin": "origin1",
        "purpose": "purpose1",
        "comment": "comment1",
        "descriptions": ["odm_description2", "odm_description3"],
        "alias_uids": ["odm_alias1"],
        "sdtm_domain_uids": ["term1"],
    }
    response = api_client.post("concepts/odms/item-groups", json=data)

    assert_response_status_code(response, 409)

    res = response.json()

    assert res["type"] == "AlreadyExistsException"
    assert (
        res["message"]
        == "ODM Item Group already exists with UID (OdmItemGroup_000001) and data {'description_uids': ['odm_description2', 'odm_description3'], 'alias_uids': ['odm_alias1'], 'sdtm_domain_uids': ['term1'], 'name': 'name1', 'oid': 'oid1', 'repeating': False, 'is_reference_data': False, 'sas_dataset_name': 'sas_dataset_name1', 'origin': 'origin1', 'purpose': 'purpose1', 'comment': 'comment1'}"
    )


def test_cannot_create_an_odm_item_group_connected_to_non_existent_concepts(api_client):
    data = {
        "library_name": "Sponsor",
        "name": "new name",
        "oid": "new oid",
        "repeating": "No",
        "is_reference_data": "No",
        "sas_dataset_name": "sas_dataset_name1",
        "origin": "origin1",
        "purpose": "purpose1",
        "comment": "comment1",
        "descriptions": ["wrong_uid"],
        "alias_uids": ["wrong_uid"],
        "sdtm_domain_uids": [],
    }
    response = api_client.post("concepts/odms/item-groups", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """ODM Item Group tried to connect to non-existent concepts [('Concept Name: ODM Description', "uids: {'wrong_uid'}"), ('Concept Name: ODM Alias', "uids: {'wrong_uid'}")]."""
    )


def test_cannot_create_an_odm_item_group_connected_to_non_existent_sdtm_domain(
    api_client,
):
    data = {
        "library_name": "Sponsor",
        "name": "new name",
        "oid": "new oid",
        "repeating": "No",
        "is_reference_data": "No",
        "sas_dataset_name": "sas_dataset_name1",
        "origin": "origin1",
        "purpose": "purpose1",
        "comment": "comment1",
        "descriptions": [],
        "alias_uids": [],
        "sdtm_domain_uids": ["wrong_uid"],
    }
    response = api_client.post("concepts/odms/item-groups", json=data)

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "ODM Item Group tried to connect to non-existent SDTM Domain with UID 'wrong_uid'."
    )


def test_getting_error_for_retrieving_non_existent_odm_item_group(api_client):
    response = api_client.get("concepts/odms/item-groups/OdmItemGroup_000002")

    assert_response_status_code(response, 404)

    res = response.json()

    assert res["type"] == "NotFoundException"
    assert (
        res["message"]
        == "OdmItemGroupAR with UID 'OdmItemGroup_000002' doesn't exist or there's no version with requested status or version number."
    )


def test_cannot_inactivate_an_odm_item_group_that_is_in_draft_status(api_client):
    response = api_client.delete(
        "concepts/odms/item-groups/OdmItemGroup_000001/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Cannot retire draft version."


def test_cannot_reactivate_an_odm_item_group_that_is_not_retired(api_client):
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/activations"
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "Only RETIRED version can be reactivated."


def test_cannot_override_odm_vendor_element_that_has_attributes_connected_this_odm_item_group(
    api_client,
):
    data = [{"uid": "odm_vendor_element2", "value": "value"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-elements?override=true",
        json=data,
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "Cannot remove an ODM Vendor Element whose attributes are connected to this ODM element."
    )


def test_cannot_add_odm_vendor_element_attribute_to_an_odm_item_group_as_an_odm_vendor_attribute(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute1", "value": "value"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "ODM Vendor Attribute with UID 'odm_vendor_attribute1' cannot not be added as an Vendor Attribute."
    )


def test_cannot_add_odm_vendor_attribute_to_an_odm_item_group_as_an_odm_vendor_element_attribute(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute3", "value": "value"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-element-attributes",
        json=data,
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == "ODM Vendor Attribute with UID 'odm_vendor_attribute3' cannot not be added as an Vendor Element Attribute."
    )


def test_approve_odm_item_group(api_client):
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/approvals"
    )

    assert_response_status_code(response, 201)

    res = response.json()

    assert res["uid"] == "OdmItemGroup_000001"
    assert res["library_name"] == "Sponsor"
    assert res["name"] == "name1"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["is_reference_data"] == "No"
    assert res["sas_dataset_name"] == "sas_dataset_name1"
    assert res["origin"] == "origin1"
    assert res["purpose"] == "purpose1"
    assert res["comment"] == "comment1"
    assert res["end_date"] is None
    assert res["status"] == "Final"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Approved version"
    assert res["author_username"] == "unknown-user@example.com"
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
    assert res["sdtm_domains"] == [
        {
            "uid": "term1",
            "code_submission_value": "code_submission_value1",
            "preferred_term": "preferred_term1",
        }
    ]
    assert res["activity_subgroups"] == []
    assert res["items"] == []
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


def test_cannot_add_odm_items_with_an_invalid_value_to_to_an_odm_item_group(api_client):
    data = [
        {
            "uid": "odm_item1",
            "order_number": 1,
            "mandatory": "Yes",
            "data_entry_required": "Yes",
            "sdv": "Yes",
            "locked": "No",
            "key_sequence": "key_sequence1",
            "method_oid": "method_oid1",
            "imputation_method_oid": "imputation_method_oid1",
            "role": "role1",
            "role_codelist_oid": "role_codelist_oid1",
            "collection_exception_condition_oid": "collection_exception_condition_oid1",
            "vendor": {
                "attributes": [{"uid": "odm_vendor_attribute3", "value": "3423"}]
            },
        }
    ]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/items", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert (
        res["message"]
        == """Provided values for following attributes don't match their regex pattern:

{'odm_vendor_attribute3': '^[a-zA-Z]+$'}"""
    )


def test_inactivate_odm_item_group(api_client):
    response = api_client.delete(
        "concepts/odms/item-groups/OdmItemGroup_000001/activations"
    )

    assert_response_status_code(response, 200)

    res = response.json()

    assert res["uid"] == "OdmItemGroup_000001"
    assert res["library_name"] == "Sponsor"
    assert res["name"] == "name1"
    assert res["oid"] == "oid1"
    assert res["repeating"] == "No"
    assert res["is_reference_data"] == "No"
    assert res["sas_dataset_name"] == "sas_dataset_name1"
    assert res["origin"] == "origin1"
    assert res["purpose"] == "purpose1"
    assert res["comment"] == "comment1"
    assert res["end_date"] is None
    assert res["status"] == "Retired"
    assert res["version"] == "1.0"
    assert res["change_description"] == "Inactivated version"
    assert res["author_username"] == "unknown-user@example.com"
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
    assert res["sdtm_domains"] == [
        {
            "uid": "term1",
            "code_submission_value": "code_submission_value1",
            "preferred_term": "preferred_term1",
        }
    ]
    assert res["activity_subgroups"] == []
    assert res["items"] == []
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


def test_cannot_add_odm_items_to_an_odm_item_group_that_is_in_retired_status(
    api_client,
):
    data = [
        {
            "uid": "odm_item1",
            "order_number": 1,
            "mandatory": "Yes",
            "data_entry_required": "Yes",
            "sdv": "Yes",
            "locked": "No",
            "key_sequence": "key_sequence1",
            "method_oid": "method_oid1",
            "imputation_method_oid": "imputation_method_oid1",
            "role": "role1",
            "role_codelist_oid": "role_codelist_oid1",
            "collection_exception_condition_oid": "collection_exception_condition_oid1",
            "vendor": {"attributes": []},
        }
    ]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/items", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"


def test_cannot_add_odm_activity_sub_groups_to_an_odm_item_group_that_is_in_retired_status(
    api_client,
):
    data = [{"uid": "activity_subgroup_root1"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/activity-sub-groups", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"


def test_cannot_add_odm_vendor_element_to_an_odm_item_group_that_is_in_retired_status(
    api_client,
):
    data = [{"uid": "odm_vendor_element1", "value": "value"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-elements", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"


def test_cannot_add_odm_vendor_attribute_to_an_odm_item_group_that_is_in_retired_status(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute1", "value": "value"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-attributes", json=data
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"


def test_cannot_add_odm_vendor_element_attribute_to_an_odm_item_group_that_is_in_retired_status(
    api_client,
):
    data = [{"uid": "odm_vendor_attribute1", "value": "value"}]
    response = api_client.post(
        "concepts/odms/item-groups/OdmItemGroup_000001/vendor-element-attributes",
        json=data,
    )

    assert_response_status_code(response, 400)

    res = response.json()

    assert res["type"] == "BusinessLogicException"
    assert res["message"] == "The object is inactive"
