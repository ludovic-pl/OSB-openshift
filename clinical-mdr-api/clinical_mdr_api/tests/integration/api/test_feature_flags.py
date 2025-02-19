"""
Tests for /feature-flags* endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments
# import json
import logging

import pytest
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app
from clinical_mdr_api.models.feature_flag import FeatureFlag
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from clinical_mdr_api.tests.utils.checks import assert_response_status_code

log = logging.getLogger(__name__)

# Global variables shared between fixtures and tests
feature_flags: list[FeatureFlag]


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "featureflags.api"
    inject_and_clear_db(db_name)
    inject_base_data()

    global feature_flags

    feature_flags = []

    for index in range(10):
        feature_flags.append(
            TestUtils.create_feature_flag(
                name=f"Feature Flag {index}",
                enabled=index % 2 == 0,
                description=f"Description {index}",
            )
        )

    yield


FEATURE_FLAG_ALL = [
    "sn",
    "name",
    "enabled",
    "description",
]
FEATURE_FLAG_NOT_NULL = [
    "sn",
    "name",
    "enabled",
]


def test_get_all_feature_flags(api_client):
    response = api_client.get("system/feature-flags")
    res = response.json()

    assert_response_status_code(response, 200)
    assert len(res) == 10

    for item in res:
        for x in FEATURE_FLAG_NOT_NULL:
            assert item[x] is not None


def test_get_feature_flag(api_client):
    response = api_client.get(f"/feature-flags/{feature_flags[0].sn}")

    assert_response_status_code(response, 200)


def test_create_feature_flag(api_client):
    data = {"name": "Name", "enabled": False, "description": "Description"}
    response = api_client.post("/feature-flags", json=data)

    assert_response_status_code(response, 201)
    res = response.json()
    assert res["sn"]
    assert res["name"] == data["name"]
    assert res["enabled"] == data["enabled"]
    assert res["description"] == data["description"]


def test_update_feature_flag(api_client):
    data = {"enabled": True}
    response = api_client.patch("/feature-flags/11", json=data)

    assert_response_status_code(response, 200)
    res = response.json()
    assert res["sn"] == 11
    assert res["enabled"] == data["enabled"]


def test_delete_feature_flag(api_client):
    response = api_client.delete(f"/feature-flags/{feature_flags[0].sn}")
    assert_response_status_code(response, 204)

    response = api_client.get(f"/feature-flags/{feature_flags[0].sn}")
    assert_response_status_code(response, 404)
    res = response.json()

    assert (
        res["message"]
        == f"Feature Flag with Serial Number '{feature_flags[0].sn}' doesn't exist."
    )


def test_cannot_create_feature_flag_with_existing_name(api_client):
    response = api_client.post(
        "/feature-flags",
        json={"name": "Name", "enabled": False, "description": "Description"},
    )

    assert_response_status_code(response, 409)
    res = response.json()
    assert res["message"] == "Feature Flag with Name 'Name' already exists."


def validate_serial_number_against_neo4j_max_and_min_int(api_client):
    serial_number = 9223372036854775808
    max_int = 9223372036854775807
    min_int = -9223372036854775807

    # Test positive integer
    response = api_client.get(f"/feature-flags/{serial_number}")
    assert_response_status_code(response, 400)
    assert (
        response.json()["message"]
        == f"Serial Number must not be greater than '{max_int}' and less than '{min_int}'."
    )

    response = api_client.patch(
        f"/feature-flags/{serial_number}",
        json={"name": "Name", "enabled": True, "description": "Description"},
    )
    assert_response_status_code(response, 400)
    assert (
        response.json()["message"]
        == f"Serial Number must not be greater than '{max_int}' and less than '{min_int}'."
    )

    response = api_client.delete(f"/feature-flags/{serial_number}")
    assert_response_status_code(response, 400)
    assert (
        response.json()["message"]
        == f"Serial Number must not be greater than '{max_int}' and less than '{min_int}'."
    )

    # Test negative integer
    response = api_client.get(f"/feature-flags/-{serial_number}")
    assert_response_status_code(response, 400)
    assert (
        response.json()["message"]
        == f"Serial Number must not be greater than '{max_int}' and less than '{min_int}'."
    )

    response = api_client.patch(
        f"/feature-flags/-{serial_number}",
        json={"name": "Name", "enabled": True, "description": "Description"},
    )
    assert_response_status_code(response, 400)
    assert (
        response.json()["message"]
        == f"Serial Number must not be greater than '{max_int}' and less than '{min_int}'."
    )

    response = api_client.delete(f"/feature-flags/-{serial_number}")
    assert_response_status_code(response, 400)
    assert (
        response.json()["message"]
        == f"Serial Number must not be greater than '{max_int}' and less than '{min_int}'."
    )
