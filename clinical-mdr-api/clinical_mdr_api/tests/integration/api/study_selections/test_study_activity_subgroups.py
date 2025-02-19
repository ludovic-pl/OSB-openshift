"""
Tests for /studies/{uid}/study-activity-subgroups endpoints
"""

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

# pytest fixture functions have other fixture functions as arguments,
# which pylint interprets as unused arguments

import logging
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from neomodel import db

from clinical_mdr_api.main import app
from clinical_mdr_api.models.concepts.activities.activity import Activity
from clinical_mdr_api.models.concepts.activities.activity_group import ActivityGroup
from clinical_mdr_api.models.concepts.activities.activity_sub_group import (
    ActivitySubGroup,
)
from clinical_mdr_api.models.controlled_terminologies import ct_term
from clinical_mdr_api.models.study_selections.study import Study
from clinical_mdr_api.tests.integration.utils.api import (
    inject_and_clear_db,
    inject_base_data,
)
from clinical_mdr_api.tests.integration.utils.data_library import (
    get_codelist_with_term_cypher,
)
from clinical_mdr_api.tests.integration.utils.factory_controlled_terminology import (
    create_codelist,
    get_catalogue_name_library_name,
)
from clinical_mdr_api.tests.integration.utils.utils import TestUtils
from clinical_mdr_api.tests.utils.checks import assert_response_status_code

log = logging.getLogger(__name__)

study: Study
general_activity_group: ActivityGroup
randomisation_activity_subgroup: ActivitySubGroup
randomized_activity: Activity
initial_ct_term_study_standard_test: ct_term.CTTerm


@pytest.fixture(scope="module")
def api_client(test_data):
    """Create FastAPI test client
    using the database name set in the `test_data` fixture"""
    yield TestClient(app)


@pytest.fixture(scope="module")
def test_data():
    """Initialize test data"""
    db_name = "study-activity-subgroup.api"
    inject_and_clear_db(db_name)
    global study
    study = inject_base_data()

    db.cypher_query(
        get_codelist_with_term_cypher(
            "EFFICACY", "Flowchart Group", term_uid="term_efficacy_uid"
        )
    )

    global general_activity_group
    global randomisation_activity_subgroup
    global randomized_activity

    general_activity_group = TestUtils.create_activity_group(name="General")
    randomisation_activity_subgroup = TestUtils.create_activity_subgroup(
        name="Randomisation", activity_groups=[general_activity_group.uid]
    )
    randomized_activity = TestUtils.create_activity(
        name="Randomized",
        activity_subgroups=[randomisation_activity_subgroup.uid],
        activity_groups=[general_activity_group.uid],
        library_name="Sponsor",
    )

    catalogue_name, library_name = get_catalogue_name_library_name(use_test_utils=True)
    # Create a study selection
    ct_term_codelist = create_codelist(
        "Flowchart Group", "CTCodelist_Name", catalogue_name, library_name
    )

    global initial_ct_term_study_standard_test
    ct_term_name = "Flowchart Group Name"
    ct_term_start_date = datetime(2020, 3, 25, tzinfo=timezone.utc)
    initial_ct_term_study_standard_test = TestUtils.create_ct_term(
        codelist_uid=ct_term_codelist.codelist_uid,
        name_submission_value=ct_term_name,
        sponsor_preferred_name=ct_term_name,
        order=1,
        catalogue_name=catalogue_name,
        library_name=library_name,
        effective_date=ct_term_start_date,
        approve=True,
    )

    cdisc_package_name = "SDTM CT 2020-03-27"

    TestUtils.create_ct_package(
        catalogue=catalogue_name,
        name=cdisc_package_name,
        approve_elements=False,
        effective_date=datetime(2020, 3, 27, tzinfo=timezone.utc),
    )

    # patch the date of the latest HAS_VERSION FINAL relationship so it can be detected by the selected study_standard_Version
    params = {
        "uid": initial_ct_term_study_standard_test.term_uid,
        "date": datetime(2020, 3, 26, tzinfo=timezone.utc),
    }
    db.cypher_query(
        """
                    MATCH (n)-[:HAS_NAME_ROOT]-(ct_name:CTTermNameRoot)-[has_version:HAS_VERSION]-(val) 
                    where 
                        n.uid =$uid AND EXISTS((ct_name)-[:LATEST]-(val)) 
                        AND has_version.status ='Final' 
                    SET has_version.start_date = $date
                """,
        params=params,
    )

    yield


def test_post_and_get_all_study_activity_subgroups(api_client):
    study_activity_subgroup_into_study_study_activity_group_mapping: dict[str, str] = {}
    study_activity_subgroup_into_activity_subgroup_mapping: dict[str, str] = {}
    for i in range(20):
        randomisation_activity_subgroup = TestUtils.create_activity_subgroup(
            name=f"Randomisation {i}", activity_groups=[general_activity_group.uid]
        )
        randomized_activity = TestUtils.create_activity(
            name=f"Randomized {i}",
            activity_subgroups=[randomisation_activity_subgroup.uid],
            activity_groups=[general_activity_group.uid],
            library_name="Sponsor",
        )
        response = api_client.post(
            f"/studies/{study.uid}/study-activities",
            json={
                "activity_uid": randomized_activity.uid,
                "activity_subgroup_uid": randomisation_activity_subgroup.uid,
                "activity_group_uid": general_activity_group.uid,
                "soa_group_term_uid": "term_efficacy_uid",
            },
        )
        assert_response_status_code(response, 201)
        res = response.json()
        assert res["activity"]["uid"] == randomized_activity.uid
        assert (
            res["study_activity_subgroup"]["activity_subgroup_uid"]
            == randomisation_activity_subgroup.uid
        )
        assert (
            res["study_activity_group"]["activity_group_uid"]
            == general_activity_group.uid
        )
        study_activity_group_uid = res["study_activity_group"][
            "study_activity_group_uid"
        ]
        study_activity_subgroup_uid = res["study_activity_subgroup"][
            "study_activity_subgroup_uid"
        ]

        # Save ActivitySubGroup for specific StudyActivitySubGroup
        study_activity_subgroup_into_activity_subgroup_mapping[
            study_activity_subgroup_uid
        ] = randomisation_activity_subgroup.uid
        # Find parent StudyActivityGroup for given StudyActivitySubGroup
        study_activity_subgroup_into_study_study_activity_group_mapping[
            study_activity_subgroup_uid
        ] = study_activity_group_uid

    response = api_client.get(
        f"/studies/{study.uid}/study-activity-subgroups", params={"page_size": 0}
    )
    assert_response_status_code(response, 200)
    study_activity_subgroups = response.json()["items"]
    assert len(study_activity_subgroups) == 20
    for study_activity_subgroup in study_activity_subgroups:
        assert (
            study_activity_subgroup["activity_subgroup_uid"]
            == study_activity_subgroup_into_activity_subgroup_mapping[
                study_activity_subgroup["study_activity_subgroup_uid"]
            ]
        )
        # Check if StudyActivitySubGroup returns correct StudyActivityGroup
        assert (
            study_activity_subgroup["study_activity_group_uid"]
            == study_activity_subgroup_into_study_study_activity_group_mapping[
                study_activity_subgroup["study_activity_subgroup_uid"]
            ]
        )


def test_modify_visibility_flag_in_protocol_flowchart(
    api_client,
):
    activity_group = TestUtils.create_activity_group(name="AG")
    activity_subgroup = TestUtils.create_activity_subgroup(
        name="AS", activity_groups=[activity_group.uid]
    )
    activity = TestUtils.create_activity(
        name="Act",
        library_name="Sponsor",
        activity_groups=[activity_group.uid],
        activity_subgroups=[activity_subgroup.uid],
    )
    response = api_client.post(
        f"/studies/{study.uid}/study-activities",
        json={
            "activity_uid": activity.uid,
            "activity_subgroup_uid": activity_subgroup.uid,
            "activity_group_uid": activity_group.uid,
            "soa_group_term_uid": "term_efficacy_uid",
        },
    )
    assert_response_status_code(response, 201)
    res = response.json()
    study_activity_uid = res["study_activity_uid"]
    study_activity_subgroup_uid = res["study_activity_subgroup"][
        "study_activity_subgroup_uid"
    ]
    assert res["show_activity_in_protocol_flowchart"] is False
    assert res["show_activity_subgroup_in_protocol_flowchart"] is True
    assert res["show_activity_group_in_protocol_flowchart"] is True
    assert res["show_soa_group_in_protocol_flowchart"] is False

    response = api_client.patch(
        f"/studies/{study.uid}/study-activities/{study_activity_uid}",
        json={
            "show_activity_in_protocol_flowchart": True,
        },
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["show_activity_in_protocol_flowchart"] is True

    response = api_client.patch(
        f"/studies/{study.uid}/study-activity-subgroups/{study_activity_subgroup_uid}",
        json={
            "show_activity_subgroup_in_protocol_flowchart": False,
        },
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["show_activity_subgroup_in_protocol_flowchart"] is False

    response = api_client.get(
        f"/studies/{study.uid}/study-activities/{study_activity_uid}",
    )
    assert_response_status_code(response, 200)
    res = response.json()
    assert res["show_activity_in_protocol_flowchart"] is True
    assert res["show_activity_subgroup_in_protocol_flowchart"] is False
    assert res["show_activity_group_in_protocol_flowchart"] is True
    assert res["show_soa_group_in_protocol_flowchart"] is False
