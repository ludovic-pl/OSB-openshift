"""
This modules verifies that database nodes/relations and API endpoints look and behave as expected.

It utilizes tests written for verifying a specific migration,
without inserting any test data and without running any migration script on the target database.
"""

import os

from data_corrections.utils.utils import get_db_driver, run_cypher_query
from migrations.utils.utils import get_logger

LOGGER = get_logger(os.path.basename(__file__))
DB_DRIVER = get_db_driver()


def test_remove_user_initials_field_from_all_nodes():
    LOGGER.info("Check for unwanted nodes having user_initials field set")

    records, _summary = run_cypher_query(
        DB_DRIVER,
        """
        MATCH (n)
        WHERE n.user_initials IS NOT NULL
        AND n.author_id IS NOT NULL
        RETURN COUNT(n) as count
        """,
    )
    assert (
        records[0]["count"] == 0
    ), f"Found {len(records)} unwanted nodes having user_initials field set."


def test_remove_user_initials_field_from_all_relations():
    LOGGER.info("Check for unwanted relationships having user_initials field set")

    records, _summary = run_cypher_query(
        DB_DRIVER,
        """
        MATCH ()-[rel]-()
        WHERE rel.user_initials IS NOT NULL
        AND rel.author_id IS NOT NULL
        RETURN COUNT(rel) as count
        """,
    )
    assert (
        records[0]["count"] == 0
    ), f"Found {len(records)} unwanted relationships having user_initials field set."


def test_remove_relationship_between_intervention_and_activity_instance_template_parameters():
    LOGGER.info("Check if relationship between Intervention and ActivityInstance :TemplateParameter nodes exists")

    records, _summary = run_cypher_query(
        DB_DRIVER,
        """
        MATCH (:TemplateParameter {name:"Intervention"})-[rel]->(:TemplateParameter {name:"ActivityInstance"})
        RETURN rel
        """,
    )
    print(records)
    assert (
        len(records) == 0
    ), "The :HAS_PARENT_PARAMETER between Intervention and ActivityInstance :TemplateParameter nodes still exists"
