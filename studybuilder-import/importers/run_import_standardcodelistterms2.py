import asyncio
import csv
import sys

import aiohttp

from .functions.utils import create_logger, load_env
from .utils.api_bindings import CODELIST_ELEMENT_TYPE, CODELIST_EPOCH_TYPE
from .utils.importer import BaseImporter, open_file_async
from .utils.metrics import Metrics

logger = create_logger("legacy_mdr_migrations")

metrics = Metrics()

API_HEADERS = {"Accept": "application/json"}

# ---------------------------------------------------------------
# Env loading
# ---------------------------------------------------------------
#
SAMPLE = load_env("MDR_MIGRATION_SAMPLE", default="False") == "True"
API_BASE_URL = load_env("API_BASE_URL")

# SPONSOR DEFINED CODELISTS
MDR_MIGRATION_ARM_TYPE = load_env("MDR_MIGRATION_ARM_TYPE")
MDR_MIGRATION_CRITERIA_CATEGORY = load_env("MDR_MIGRATION_CRITERIA_CATEGORY")
MDR_MIGRATION_CRITERIA_SUB_CATEGORY = load_env("MDR_MIGRATION_CRITERIA_SUB_CATEGORY")
MDR_MIGRATION_CRITERIA_TYPE = load_env("MDR_MIGRATION_CRITERIA_TYPE")
MDR_MIGRATION_COMPOUND_DISPENSED_IN = load_env("MDR_MIGRATION_COMPOUND_DISPENSED_IN")
MDR_MIGRATION_DEVICE = load_env("MDR_MIGRATION_DEVICE")
MDR_MIGRATION_ELEMENT_TYPE = load_env("MDR_MIGRATION_ELEMENT_TYPE")
MDR_MIGRATION_ELEMENT_SUBTYPE = load_env("MDR_MIGRATION_ELEMENT_SUBTYPE")
MDR_MIGRATION_ENDPOINT_CATEGORY = load_env("MDR_MIGRATION_ENDPOINT_CATEGORY")
MDR_MIGRATION_ENDPOINT_SUB_CATEGORY = load_env("MDR_MIGRATION_ENDPOINT_SUB_CATEGORY")
MDR_MIGRATION_ENDPOINT_SUB_LEVEL = load_env("MDR_MIGRATION_ENDPOINT_SUB_LEVEL")
MDR_MIGRATION_FLOWCHART_GROUP = load_env("MDR_MIGRATION_FLOWCHART_GROUP")
MDR_MIGRATION_NULL_FLAVOR = load_env("MDR_MIGRATION_NULL_FLAVOR")
MDR_MIGRATION_OBJECTIVE_CATEGORY = load_env("MDR_MIGRATION_OBJECTIVE_CATEGORY")
MDR_MIGRATION_OPERATOR = load_env("MDR_MIGRATION_OPERATOR")
MDR_MIGRATION_THERAPY_AREA = load_env("MDR_MIGRATION_THERAPY_AREA")
MDR_MIGRATION_TIME_REFERENCE = load_env("MDR_MIGRATION_TIME_REFERENCE")
MDR_MIGRATION_TYPE_OF_TREATMENT = load_env("MDR_MIGRATION_TYPE_OF_TREATMENT")
MDR_MIGRATION_UNIT_DIF = load_env("MDR_MIGRATION_UNIT_DIF")
MDR_MIGRATION_UNIT_DIMENSION = load_env("MDR_MIGRATION_UNIT_DIMENSION")
MDR_MIGRATION_UNIT_SUBSETS = load_env("MDR_MIGRATION_UNIT_SUBSETS")
MDR_MIGRATION_VISIT_CONTACT_MODE = load_env("MDR_MIGRATION_VISIT_CONTACT_MODE")
MDR_MIGRATION_VISIT_SUB_LABEL = load_env("MDR_MIGRATION_VISIT_SUB_LABEL")
MDR_MIGRATION_VISIT_TYPE = load_env("MDR_MIGRATION_VISIT_TYPE")
MDR_MIGRATION_DATATYPE = load_env("MDR_MIGRATION_DATATYPE")
MDR_MIGRATION_LANGUAGE = load_env("MDR_MIGRATION_LANGUAGE")
MDR_MIGRATION_EPOCH_ALLOCATION = load_env("MDR_MIGRATION_EPOCH_ALLOCATION")
MDR_MIGRATION_FREQUENCY = load_env("MDR_MIGRATION_FREQUENCY")
MDR_MIGRATION_TRIAL_TYPE = load_env("MDR_MIGRATION_TRIAL_TYPE")
MDR_MIGRATION_DATA_COLLECTION_MODE = load_env("MDR_MIGRATION_DATA_COLLECTION_MODE")
MDR_MIGRATION_CONFIRMATORY_PURPOSE = load_env("MDR_MIGRATION_CONFIRMATORY_PURPOSE")
MDR_MIGRATION_NONCONFIRMATORY_PURPOSE = load_env(
    "MDR_MIGRATION_NONCONFIRMATORY_PURPOSE"
)
MDR_MIGRATION_TRIAL_BLINDING_SCHEMA = load_env("MDR_MIGRATION_TRIAL_BLINDING_SCHEMA")
MDR_MIGRATION_ROLE = load_env("MDR_MIGRATION_ROLE")
MDR_MIGRATION_DISEASE_MILESTONE = load_env("MDR_MIGRATION_DISEASE_MILESTONE")
MDR_MIGRATION_REGISTID = load_env("MDR_MIGRATION_REGISTID")
MDR_MIGRATION_FINDING_CATEGORIES = load_env("MDR_MIGRATION_FINDING_CATEGORIES")
MDR_MIGRATION_EVENT_CATEGORIES = load_env("MDR_MIGRATION_EVENT_CATEGORIES")
MDR_MIGRATION_INTERVENTION_CATEGORIES = load_env(
    "MDR_MIGRATION_INTERVENTION_CATEGORIES"
)
MDR_MIGRATION_FINDING_SUBCATEGORIES = load_env("MDR_MIGRATION_FINDING_SUBCATEGORIES")
MDR_MIGRATION_EVENT_SUBCATEGORIES = load_env("MDR_MIGRATION_EVENT_SUBCATEGORIES")
MDR_MIGRATION_INTERVENTION_SUBCATEGORIES = load_env(
    "MDR_MIGRATION_INTERVENTION_SUBCATEGORIES"
)
MDR_MIGRATION_FOOTNOTE_TYPE = load_env("MDR_MIGRATION_FOOTNOTE_TYPE")
MDR_MIGRATION_REPEATING_VISIT_FREQUENCY = load_env(
    "MDR_MIGRATION_REPEATING_VISIT_FREQUENCY"
)


# Import terms to standard codelists in sponsor library
class StandardCodelistTerms2(BaseImporter):
    logging_name = "standard_codelistterms2"

    def __init__(self, api=None, metrics_inst=None, cache=None):
        super().__init__(api=api, metrics_inst=metrics_inst, cache=cache)
        self.limit_to_codelists = None

    def limit_codelists(self, codelists):
        self.limit_to_codelists = codelists

    @open_file_async()
    async def migrate_term(self, csvfile, codelist_name, code_lists_uids, session):
        self.ensure_cache()
        readCSV = csv.DictReader(csvfile, delimiter=",")
        api_tasks = []

        if codelist_name == self.element_subtype_codelist_name:
            all_element_type_code_subm_values = self.api.get_all_identifiers(
                self.api.get_all_from_api(
                    f"/ct/terms/attributes?codelist_name={CODELIST_ELEMENT_TYPE}"
                ),
                identifier="code_submission_value",
                value="term_uid",
            )
        for row in readCSV:
            # Fix for files that don't have a NAME_SENTENCE_CASE column
            name_sentence_case = row.get("NAME_SENTENSE_CASE", row["CT_NAME"].lower())
            name_submval = row.get("NAME_SUBMVAL", row["CT_SUBMVAL"])
            if name_submval == "":
                name_submval = None
            data = {
                "path": "/ct/terms",
                "codelist": row["CT_CD_LIST_SUBMVAL"],
                "body": {
                    "catalogue_name": "SDTM CT",
                    "code_submission_value": row["CT_SUBMVAL"],
                    "name_submission_value": name_submval,
                    "nci_preferred_name": row.get("NCI_PREFERRED_NAME", "UNK"),
                    "definition": row["DEFINITION"] or "TBD",
                    "sponsor_preferred_name": row["CT_NAME"],
                    "sponsor_preferred_name_sentence_case": name_sentence_case,
                    "library_name": "Sponsor",
                    "order": row["ORDER"] if row["ORDER"] != "" else None,
                },
            }
            if "CT_CD" in row and row["CT_CD"] != "":
                data["term_concept_id"] = row["CT_CD"]
            if codelist_name == self.element_subtype_codelist_name:
                element_type_subm_value = row["GEN_ELEM_TYPE"]
                if element_type_subm_value in all_element_type_code_subm_values:
                    data["element_type_uid"] = all_element_type_code_subm_values[
                        element_type_subm_value
                    ]

            if codelist_name in code_lists_uids:
                data["body"]["codelist_uid"] = code_lists_uids[codelist_name]
            else:
                metrics.icrement(
                    data["path"]
                    + f"-Names {codelist_name} - SkippedASMissingcodelist_uid"
                )
                continue
            # if not existing_rows.get(data["body"]["sponsor_preferred_name"]):
            api_tasks.append(
                self.process_simple_term_migration(data=data, session=session)
            )
        await asyncio.gather(*api_tasks)

    async def async_run(self):
        # we have to get all codelists when sponsor one will be migrated
        # otherwise sponsor defined terms won't know to which codelist they should connect
        code_lists_uids = self.api.get_code_lists_uids()
        codelists_to_import = [
            (MDR_MIGRATION_VISIT_SUB_LABEL, "Visit Sub Label"),
            (MDR_MIGRATION_CRITERIA_TYPE, "Criteria Type"),
            (MDR_MIGRATION_CRITERIA_CATEGORY, "Criteria Category"),
            (MDR_MIGRATION_CRITERIA_SUB_CATEGORY, "Criteria Sub Category"),
            (MDR_MIGRATION_ENDPOINT_CATEGORY, "Endpoint Category"),
            (MDR_MIGRATION_ENDPOINT_SUB_CATEGORY, "Endpoint Sub Category"),
            (MDR_MIGRATION_ENDPOINT_SUB_LEVEL, "Endpoint Sub Level"),
            (MDR_MIGRATION_OBJECTIVE_CATEGORY, "Objective Category"),
            (MDR_MIGRATION_OPERATOR, "Operator"),
            (MDR_MIGRATION_FLOWCHART_GROUP, "Flowchart Group"),
            (MDR_MIGRATION_VISIT_CONTACT_MODE, "Visit Contact Mode"),
            (MDR_MIGRATION_ARM_TYPE, "Arm Type"),
            (MDR_MIGRATION_UNIT_SUBSETS, "Unit Subset"),
            (MDR_MIGRATION_NULL_FLAVOR, "Null Flavor"),
            (MDR_MIGRATION_THERAPY_AREA, "Therapeutic area"),
            (MDR_MIGRATION_TIME_REFERENCE, "Time Point Reference"),
            (MDR_MIGRATION_TYPE_OF_TREATMENT, "Type of Treatment"),
            (MDR_MIGRATION_COMPOUND_DISPENSED_IN, "Compound Dispensed In"),
            (MDR_MIGRATION_DEVICE, "Delivery Device"),
            (MDR_MIGRATION_ELEMENT_TYPE, "Element Type"),
            (MDR_MIGRATION_ELEMENT_SUBTYPE, "Element Sub Type"),
            (MDR_MIGRATION_LANGUAGE, "Language"),
            (MDR_MIGRATION_DATATYPE, "Data type"),
            # Migration of Visit Types have to go after epoch type as we link the Visit Type term to the specific
            # Epoch to allow using Visit Types only valid for specific Epoch Type context
            (MDR_MIGRATION_VISIT_TYPE, self.visit_type_codelist_name),
            (MDR_MIGRATION_EPOCH_ALLOCATION, "Epoch Allocation"),
            (MDR_MIGRATION_FREQUENCY, "Frequency"),
            (MDR_MIGRATION_TRIAL_TYPE, "Trial Type"),
            (MDR_MIGRATION_DATA_COLLECTION_MODE, "Data Collection Mode"),
            (MDR_MIGRATION_CONFIRMATORY_PURPOSE, "Confirmatory Purpose"),
            (MDR_MIGRATION_NONCONFIRMATORY_PURPOSE, "Non-confirmatory Purpose"),
            (MDR_MIGRATION_TRIAL_BLINDING_SCHEMA, "Trial Blinding Schema"),
            (MDR_MIGRATION_ROLE, "Role"),
            (MDR_MIGRATION_DISEASE_MILESTONE, "Disease Milestone Type"),
            (MDR_MIGRATION_REGISTID, "Registry Identifier"),
            (MDR_MIGRATION_EVENT_CATEGORIES, "Event Category Definition"),
            (MDR_MIGRATION_EVENT_SUBCATEGORIES, "Event Subcategory Definition"),
            (MDR_MIGRATION_FINDING_CATEGORIES, "Finding Category Definition"),
            (MDR_MIGRATION_FINDING_SUBCATEGORIES, "Finding Subcategory Definition"),
            (MDR_MIGRATION_INTERVENTION_CATEGORIES, "Intervention Category Definition"),
            (
                MDR_MIGRATION_INTERVENTION_SUBCATEGORIES,
                "Intervention Subcategory Definition",
            ),
            (MDR_MIGRATION_FOOTNOTE_TYPE, "Footnote Type"),
            (MDR_MIGRATION_REPEATING_VISIT_FREQUENCY, "Repeating Visit Frequency"),
        ]

        timeout = aiohttp.ClientTimeout(None)
        for file_path, codelist_name in codelists_to_import:
            if self.limit_to_codelists and codelist_name not in self.limit_to_codelists:
                self.log.info(f"Skipping codelist '{codelist_name}'")
                continue
            conn = aiohttp.TCPConnector(limit=4, force_close=True)
            async with aiohttp.ClientSession(
                timeout=timeout, connector=conn
            ) as session:
                await self.migrate_term(
                    file_path,
                    codelist_name=codelist_name,
                    code_lists_uids=code_lists_uids,
                    session=session,
                )

    def run(self):
        self.log.info("Migrating sponsor terms")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_run())
        self.log.info("Done migrating sponsor terms")


def main(codelists=[]):
    metr = Metrics()
    migrator = StandardCodelistTerms2(metrics_inst=metr)
    if codelists:
        migrator.limit_codelists(codelists)
    migrator.run()
    metr.print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        codelist_arg = sys.argv[1]
        codelists = codelist_arg.split(",")
    else:
        codelists = []
    main(codelists=codelists)
