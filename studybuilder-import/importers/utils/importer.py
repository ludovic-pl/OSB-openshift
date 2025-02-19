import copy
import json
import logging
import time
from collections.abc import Callable
from functools import lru_cache, wraps
from typing import Dict

import aiohttp
import requests

from ..functions.caselessdict import CaselessDict
from ..functions.utils import create_logger, load_env
from ..utils import import_templates
from .api_bindings import (
    CODELIST_NAME_MAP,
    CODELIST_SDTM_DOMAIN_ABBREVIATION,
    UNIT_SUBSET_AGE,
    ApiBinding,
)
from .metrics import Metrics

logger = logging.getLogger("legacy_mdr_migrations - utils")

metrics = Metrics()

API_HEADERS = {"Accept": "application/json", "User-Agent": "test"}

# ---------------------------------------------------------------
# Env loading
# ---------------------------------------------------------------
#
API_BASE_URL = load_env("API_BASE_URL")


class TermCache:
    def __init__(self, api):
        self.api = api
        self.all_terms_attributes = self.api.get_all_from_api_paged("/ct/terms/attributes")
        self.all_terms_name_submission_values = CaselessDict(
            self.api.get_all_identifiers(
                self.all_terms_attributes,
                identifier="name_submission_value",
                value="term_uid",
            )
        )
        self.all_terms_code_submission_values = CaselessDict(
            self.api.get_all_identifiers(
                self.all_terms_attributes,
                identifier="code_submission_value",
                value="term_uid",
            )
        )
        self.all_term_names = self.api.get_all_from_api_paged("/ct/terms/names")
        self.all_term_name_values = CaselessDict(
            self.api.get_all_identifiers_multiple(
                self.all_term_names,
                identifier="sponsor_preferred_name",
                values=["term_uid", "catalogue_name"],
            )
        )
        self.added_terms = CaselessDict()


# Decorator to avoid starting every function with the open() context manager
def open_file():
    def open_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            filename = args[1]
            if filename:
                self.log.info(f"Opening file: {filename}")
                try:
                    with open(filename, encoding="utf-8", errors="ignore") as textfile:
                        return func(self, textfile, *args[2:], **kwargs)
                except FileNotFoundError:
                    self.log.error(f"File {filename} not found, skipping")
            else:
                self.log.info("Empty filename, skipping")

        return wrapper

    return open_decorator


# Decorator to avoid starting every function with the open() context manager
def open_file_async():
    def open_decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            self = args[0]
            filename = args[1]
            if filename:
                self.log.info(f"Opening file: {filename}")
                try:
                    with open(filename, encoding="utf-8", errors="ignore") as textfile:
                        await func(self, textfile, *args[2:], **kwargs)
                except FileNotFoundError:
                    self.log.error(f"File {filename} not found, skipping")
            else:
                self.log.info("Empty filename, skipping")

        return wrapper

    return open_decorator


class BaseImporter:
    logging_name = "legacy_mdr_migrations"

    def __init__(self, api=None, metrics_inst=None, cache=None):
        self.log = create_logger(self.logging_name)
        if metrics_inst is None:
            self.metrics = Metrics()
        else:
            self.metrics = metrics_inst
        if api is None:
            headers = self._authenticate(API_HEADERS)
            self.api = ApiBinding(API_BASE_URL, headers, self.metrics, logger=self.log)
        else:
            self.api = api

        self.cache = cache

        self.visit_type_codelist_name = "VisitType"
        self.element_subtype_codelist_name = "Element Sub Type"

    def refresh_auth(self):
        headers = self._authenticate(API_HEADERS)
        self.api.update_headers(headers)

    @staticmethod
    def _authenticate(headers: Dict) -> Dict:
        """Authenticates with client secret flow and appends Authorization header the dict of API request headers"""

        headers = headers.copy()

        client_id = load_env("CLIENT_ID", "")

        api_token = load_env("STUDYBUILDER_API_TOKEN", "")

        if api_token:
            headers["Authorization"] = f"Bearer {api_token}"

        elif client_id:
            client_secret = load_env("CLIENT_SECRET")
            token_endpoint = load_env("TOKEN_ENDPOINT")
            scope = load_env("SCOPE")

            response = requests.post(
                token_endpoint,
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials",
                    "scope": scope,
                },
            )

            response.raise_for_status()
            payload = response.json()

            access_token = payload.get("access_token")
            if not access_token:
                msg = "missing access token from token payload"
                logger.error(msg)
                raise RuntimeError(msg)

            token_type = payload.get("token_type")
            if not access_token:
                msg = "missing token type from token payload"
                logger.error(msg)
                raise RuntimeError(msg)

            headers["Authorization"] = f"{token_type} {access_token}"

        return headers

    def run(self):
        pass

    def prepare(self):
        pass

    def ensure_cache(self):
        if self.cache is None:
            self.log.info("Creating term cache")
            self.cache = TermCache(self.api)

    def get_cache(self):
        self.ensure_cache()
        return self.cache

    ############ helper functions ###########

    # Check if a codelist contains a term with sponsor preferred name equal to the given name.
    def search_codelist(self, codelist, name):
        for item in codelist:
            if (
                item.get("name", {}).get("sponsor_preferred_name", "").lower()
                == name.lower()
            ):
                return True
        return False

    # Search a codelist for a term with the given sponsor preferred name.
    # For use with codelists fetched like:
    # terms = self.api.get_terms_for_codelist_name("Objective Category")
    def get_uid_for_sponsor_preferred_name(self, terms, name):
        for item in terms:
            try:
                if item["name"]["sponsor_preferred_name"] == name:
                    return item["term_uid"]
            except KeyError:
                pass

    # Helper to return the first term that has a matching catalogue name.
    def _find_term_with_catalogue(self, terms, catalogue):
        for term in terms:
            if term["catalogue_name"] == catalogue:
                return term

    async def process_simple_term_migration(
        self, data: dict, session: aiohttp.ClientSession
    ):
        self.ensure_cache()
        result = None
        term_name = data["body"]["sponsor_preferred_name"]
        concept_id = data.get("term_concept_id")
        if concept_id and concept_id.lower() != "none":
            post_status = None
        else:
            post_status, post_result = await self.api.post_to_api_async(
                url="/ct/terms", body=data["body"], session=session
            )
        term_uid = None
        if post_status == 201:
            self.cache.added_terms[term_name] = post_result
            term_uid = post_result["term_uid"]
            self.log.info(f"Added term name '{term_name}' with uid '{term_uid}'")
            time.sleep(0.01)
            status, result = await self.api.approve_async(
                "/ct/terms/" + term_uid + "/names/approvals", session=session
            )
            if status != 201:
                self.log.error(
                    f"Failed to approve term name '{term_name}' with uid '{term_uid}'"
                )
                metrics.icrement("/ct/terms--NamesApproveError")
            else:
                self.log.info(f"Approved term name '{term_name}' with uid '{term_uid}'")
                metrics.icrement("/ct/terms--NamesApprove")
            status, result = await self.api.approve_async(
                "/ct/terms/" + term_uid + "/attributes/approvals", session=session
            )
            if status != 201:
                self.log.error(
                    f"Failed to approve term attributes '{term_name}' with uid '{term_uid}'"
                )
                metrics.icrement("/ct/terms--AttributesApproveError")
            else:
                self.log.info(
                    f"Approved term attributes '{term_name}' with uid '{term_uid}'"
                )
                metrics.icrement("/ct/terms--AttributesApprove")
        else:
            self.log.info(
                f"Failed to create new term name '{term_name}' with uid '{term_uid}', trying to link to already existing"
            )
            if concept_id and concept_id.lower() == "none":
                self.log.error(f"Term '{term_name}' should not be linked, skipping")
                return
            elif concept_id:
                catalogue = data["body"]["catalogue_name"]
                submval = data["body"]["code_submission_value"]
                self.log.info(
                    f"Looking up term with concept id '{concept_id}' with submission value '{submval}' in catalogue '{catalogue}'"
                )
                matching_terms = self.api.lookup_terms_from_concept_id(
                    concept_id, catalogue_name=catalogue, code_submission_value=submval
                )
                if len(matching_terms) == 0:
                    self.log.warning(
                        f"Could not find term with concept id '{concept_id}' with submission value '{submval}' in catalogue '{catalogue}'"
                    )
                    matching_terms = self.api.lookup_terms_from_concept_id(
                        concept_id, code_submission_value=submval
                    )
                    if len(matching_terms) == 0:
                        self.log.warning(
                            f"Could not find term with concept id '{concept_id}' with submission value '{submval}' in any catalogue'"
                        )
                        matching_terms = self.api.lookup_terms_from_concept_id(
                            concept_id, catalogue_name=catalogue
                        )
                        if len(matching_terms) == 0:
                            self.log.warning(
                                f"Could not find term with concept id '{concept_id}' with any submission value in catalogue '{catalogue}'"
                            )
                            matching_terms = self.api.lookup_terms_from_concept_id(
                                concept_id
                            )
                            if len(matching_terms) == 0:
                                self.log.error(
                                    f"Could not find term with concept id '{concept_id}' with any submission value in any catalogue, skipping"
                                )
                                return
                term_uid = matching_terms[0]["term_uid"]

                self.log.info(
                    f"Found term(s) with uid(s) {[t['term_uid'] for t in matching_terms]} for concept id '{concept_id}'"
                )
                codelist_uid = data["body"]["codelist_uid"]
                if any(
                    [
                        codelist_uid in [x["codelist_uid"] for x in t["codelists"]]
                        for t in matching_terms
                    ]
                ):
                    self.log.info(
                        f"Term name '{term_name}' already exits in the codelist with uid {codelist_uid}, not adding again"
                    )
                    return
            elif term_name in self.cache.added_terms:
                term_uid = self.cache.added_terms[term_name]["term_uid"]
                self.log.info(
                    f"Term name '{term_name}' with uid '{term_uid}' found in cache of newly added terms"
                )
            elif term_name in self.cache.all_term_name_values:
                found_terms = self.cache.all_term_name_values[term_name]
                term_in_catalogue = self._find_term_with_catalogue(
                    found_terms, data["body"]["catalogue_name"]
                )
                self.log.info(
                    f"Term name '{term_name}' found as '{[str(t['catalogue_name']) + ':' + t['term_uid'] for t in found_terms]}' among existing term names"
                )
                if term_in_catalogue is None:
                    self.log.error(
                        f"Term '{term_name}' not found in catalogue: '{data['body']['catalogue_name']}', using first match from catalogue '{found_terms[0]['catalogue_name']}'"
                    )
                    term_uid = found_terms[0]["term_uid"]
                else:
                    term_uid = term_in_catalogue["term_uid"]
                codelist_uid = data["body"]["codelist_uid"]
                codelist = self.retry_function(
                    self.api.get_terms_for_codelist_uid,
                    [codelist_uid],
                    nbr_retries=3,
                    retry_delay=0.5,
                )
                if self.search_codelist(codelist, term_name):
                    self.log.info(
                        f"Term name '{term_name}' already exits in the codelist with uid {codelist_uid}, not adding again"
                    )
                    return
            elif (
                data["body"].get("code_submission_value")
                in self.cache.all_terms_code_submission_values
            ):
                term_uid = self.cache.all_terms_code_submission_values[
                    data["body"].get("code_submission_value")
                ]
                self.log.info(
                    f"Term name '{term_name}' found with uid '{term_uid}' among existing term code submission values"
                )
            elif (
                data["body"].get("name_submission_value")
                in self.cache.all_terms_name_submission_values
            ):
                term_uid = self.cache.all_terms_name_submission_values[
                    data["body"].get("name_submission_value")
                ]
                self.log.info(
                    f"Term name '{term_name}' found with uid '{term_uid}' among existing term name submission values"
                )
            if term_uid:
                codelist_uid = data["body"]["codelist_uid"]
                self.log.info(
                    f"Add term name '{term_name}' with uid '{term_uid}' to codelist '{codelist_uid}'"
                )
                result = await self.api.post_to_api_async(
                    url="/ct/codelists/" + codelist_uid + "/terms",
                    body={"term_uid": term_uid, "order": data["body"]["order"]},
                    session=session,
                )
                post_status, post_result = result
                if post_status != 201:
                    self.log.error(
                        f"Failed to add term name '{term_name}' with uid '{term_uid}' to codelist '{codelist_uid}'"
                    )
        if data.get("element_type_uid"):
            self.api.post_to_api(
                {
                    "path": f"/ct/terms/{term_uid}/parents?parent_uid={data.get('element_type_uid')}&relationship_type=type",
                    "body": {},
                }
            )
        return result

    # Retry a function that sporadically fails.
    # After the first failure it will sleep for retry_delay seconds,
    # then double the delay for each subsequent failure.
    def retry_function(
        self,
        function: Callable,
        args: list,
        nbr_retries: int = 3,
        retry_delay: float = 0.5,
    ):
        for n in range(nbr_retries + 1):
            try:
                return function(*args)
            except Exception:
                self.log.warning(
                    f"Function failed, retry {n+1} of {nbr_retries} in {retry_delay} seconds"
                )
                time.sleep(retry_delay)
                retry_delay = 2 * retry_delay

    @lru_cache(maxsize=10000)
    def lookup_concept_uid(self, name, endpoint, subset=None, library=None, only_final=False):
        self.log.info(f"Looking up concept {endpoint} with name '{name}'")
        filt = {"name": {"v": [name], "op": "eq"}}
        if library is not None:
            if isinstance(library, tuple):
                filt["library_name"] = {"v": list(library), "op": "eq"}
            else:
                filt["library_name"] = {"v": [library], "op": "eq"}
        if only_final:
            filt["status"] = {"v": ["Final"], "op": "eq"}
        path = f"/concepts/{endpoint}"
        params = {"filters": json.dumps(filt)}
        if subset:
            params["subset"] = subset
        items = self.api.get_all_from_api(path, params={"filters": json.dumps(filt)})
        if items is not None and len(items) > 0:
            uid = items[0].get("uid", None)
            self.log.info(
                f"Found concept {endpoint} with name '{name}' and uid '{uid}'"
            )
            return uid
        self.log.warning(f"Could not find concept {endpoint} with name '{name}'")

    @lru_cache(maxsize=10000)
    def lookup_ct_term_uid(
        self, codelist_name, value, key="sponsor_preferred_name", uid_key="term_uid"
    ):
        filt = {key: {"v": [value], "op": "eq"}}
        if codelist_name in CODELIST_NAME_MAP:
            self.log.info(
                f"Looking up term with '{key}' == '{value}' in codelist '{codelist_name}': {CODELIST_NAME_MAP[codelist_name]}, returning uid from '{uid_key}'"
            )
            params = {
                "codelist_uid": CODELIST_NAME_MAP[codelist_name],
                "page_size": 1,
                "filters": json.dumps(filt),
            }
        else:
            self.log.info(
                f"Looking up term with '{key}' == '{value}' in codelist '{codelist_name}', returning uid from '{uid_key}'"
            )
            params = {
                "codelist_name": codelist_name,
                "page_size": 1,
                "filters": json.dumps(filt),
            }
        data = self.api.get_all_identifiers(
            self.api.get_all_from_api("/ct/terms/names", params=params),
            identifier=key,
            value=uid_key,
        )
        uid = data.get(value, None)
        if uid:
            self.log.debug(
                f"Found term with '{key}' == '{value}' in codelist '{codelist_name}', uid '{uid}'"
            )
            return uid
        self.log.warning(
            f"Could not find term with '{key}' == '{value}' in codelist '{codelist_name}'"
        )

    def lookup_unit_uid(self, name, subset=None):
        uid = self.lookup_concept_uid(name, "unit-definitions", subset=subset)
        if uid is None:
            self.log.info(
                f"Unit name '{name}' not found, trying again with lowercase '{name.lower()}'"
            )
            uid = self.lookup_concept_uid(
                name.lower(), "unit-definitions", subset=subset
            )
        if uid is None:
            self.log.info(
                f"Unit name '{name}' not found, trying again with uppercase '{name.upper()}'"
            )
            uid = self.lookup_concept_uid(
                name.upper(), "unit-definitions", subset=subset
            )
        self.log.info(f"Looked up unit name '{name}', found uid '{uid}'")
        return uid

    @lru_cache(maxsize=10000)
    def lookup_codelist_term_uid(self, codelist_name, sponsor_preferred_name):
        self.log.info(
            f"Looking up term with name '{sponsor_preferred_name}' from codelist '{codelist_name}'"
        )
        terms = self.fetch_codelist_terms(codelist_name)
        if terms is not None:
            for term in terms:
                if term["name"]["sponsor_preferred_name"] == sponsor_preferred_name:
                    uid = term["term_uid"]
                    self.log.debug(
                        f"Found term with sponsor preferred name '{sponsor_preferred_name}' and uid '{uid}'"
                    )
                    return uid
        self.log.warning(
            f"Could not find term with sponsor preferred name '{sponsor_preferred_name}'"
        )

    @lru_cache(maxsize=10000)
    def fetch_codelist_terms(self, name):
        if name in CODELIST_NAME_MAP:
            self.log.info(
                f"Fetching terms for codelist with name '{name}', id {CODELIST_NAME_MAP[name]}"
            )
            params = {"codelist_uid": CODELIST_NAME_MAP[name]}
        else:
            self.log.info(f"Fetching terms for codelist with name '{name}'")
            params = {"codelist_name": name}
        items = self.api.get_all_from_api("/ct/terms", params=params)
        if items is None:
            items = []
        self.log.debug(f"Got {len(items)} terms from codelist with name '{name}'")
        return items

    def create_or_get_numeric_value(self, value, subset):
        if value is None:
            return None
        data = copy.deepcopy(import_templates.numeric_value_with_unit)
        for key in data.keys():
            if not key.lower().endswith("uid"):
                data[key] = value.get(key, data[key])
        data["unit_definition_uid"] = self.lookup_unit_uid(
            value["unit_label"], subset=subset
        )
        data["library_name"] = "Sponsor"
        for key, val in data.items():
            if val == "string":
                data[key] = None
        val = self.api.simple_post_to_api("/concepts/numeric-values-with-unit", data)
        if val is not None:
            return val.get("uid", None)

    def create_or_get_lag_time(self, value):
        data = copy.deepcopy(import_templates.lag_time)
        for key in data.keys():
            if not key.lower().endswith("uid"):
                data[key] = value.get(key, data[key])
        data["unit_definition_uid"] = self.lookup_unit_uid(
            value["unit_label"], subset=UNIT_SUBSET_AGE
        )
        data["sdtm_domain_uid"] = self.lookup_ct_term_uid(
            CODELIST_SDTM_DOMAIN_ABBREVIATION, value["sdtm_domain_label"]
        )
        data["library_name"] = "Sponsor"
        for key, val in data.items():
            if val == "string":
                data[key] = None
        # print(json.dumps(data, indent=2))
        val = self.api.simple_post_to_api("/concepts/lag-times", data)
        if val is not None:
            return val.get("uid", None)

    @lru_cache(maxsize=10000)
    def lookup_dictionary_uid(self, name):
        self.log.info(f"Looking up dictionary with name '{name}'")
        items = self.api.get_all_from_api(
            f"/dictionaries/codelists", params={"library_name": name}
        )
        if items is not None and len(items) > 0:
            uid = items[0].get("codelist_uid", None)
            self.log.debug(f"Found dictionary with name '{name}' and uid '{uid}'")
            return uid
        self.log.warning(f"Could not find dictionary with name '{name}'")

    @lru_cache(maxsize=10000)
    def lookup_ct_codelist_uid(self, name):
        self.log.info(f"Looking up ct codelist with name '{name}'")
        filt = {"name": {"v": [name], "op": "eq"}}
        items = self.api.get_all_from_api(
            "/ct/codelists/names", params={"filters": json.dumps(filt)}
        )
        if items is not None and len(items) > 0:
            uid = items[0].get("codelist_uid", None)
            self.log.debug(f"Found ct codelist with name '{name}' and uid '{uid}'")
            return uid
        self.log.warning(f"Could not find ct codelist with name '{name}'")

    @lru_cache(maxsize=10000)
    def fetch_dictionary_terms(self, name):
        uid = self.lookup_dictionary_uid(name)
        self.log.info(f"Fetching terms for dictionary with name '{name}'")
        items = self.api.get_all_from_api(
            "/dictionaries/terms", params={"codelist_uid": uid}
        )
        if items is None:
            items = []
        self.log.debug(f"Got {len(items)} terms from dictionary with name '{name}'")
        return items

    @lru_cache(maxsize=10000)
    def lookup_dictionary_term_uid(self, dictionary_name, term_name):
        self.log.info(
            f"Looking up term with name '{term_name}' from dictionary '{dictionary_name}'"
        )
        snomed_uid = self.lookup_dictionary_uid(dictionary_name)
        filt = {"name": {"v": [term_name], "op": "eq"}}
        items = self.api.get_all_from_api(
            "/dictionaries/terms",
            params={"codelist_uid": snomed_uid, "filters": json.dumps(filt)},
        )
        if items is not None and len(items) > 0:
            uid = items[0].get("term_uid", None)
            self.log.debug(f"Found term with name '{term_name}' and uid '{uid}'")
            return uid
        self.log.warning(f"Could not find term with name '{term_name}'")

    @lru_cache(maxsize=10000)
    def lookup_codelist_term_name_from_concept_id(self, codelist_name, concept_id):
        self.log.info(
            f"Looking up term with concept id '{concept_id}' from codelist '{codelist_name}'"
        )
        terms = self.fetch_codelist_terms(codelist_name)
        if terms is not None:
            for term in terms:
                if term["attributes"]["concept_id"] == concept_id:
                    name = term["name"]["sponsor_preferred_name"]
                    self.log.debug(
                        f"Found term with concept id '{concept_id}' and name '{name}'"
                    )
                    return name
        self.log.warning(
            f"Could not find term with concept id '{concept_id}' in codelist '{codelist_name}'"
        )
