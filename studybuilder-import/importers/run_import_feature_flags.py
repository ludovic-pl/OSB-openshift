# pylint: disable=logging-fstring-interpolation
import csv

import requests

from .functions.utils import load_env
from .functions.parsers import map_boolean
from .utils.importer import BaseImporter, open_file
from .utils.metrics import Metrics
from .utils.path_join import path_join

# ---------------------------------------------------------------
# Env loading
# ---------------------------------------------------------------
#
API_BASE_URL = load_env("API_BASE_URL")


class FeatureFlags(BaseImporter):
    logging_name = "feature_flags"

    def __init__(self, api=None, metrics_inst=None, cache=None):
        super().__init__(api=api, metrics_inst=metrics_inst, cache=cache)

    @open_file()
    def handle_feature_flags(self, csvfile):
        feature_flags_in_db = requests.get(
            path_join(self.api.api_base_url, "/system/feature-flags"),
            headers=self.api.api_headers,
        ).json()

        feature_flags_in_db = {item["name"]: item for item in feature_flags_in_db}

        csv_data = csv.DictReader(csvfile)

        for row in csv_data:
            body = {
                "name": row["name"],
                "enabled": map_boolean(row["enabled"]),
                "description": row["description"] or None,
            }

            if row["name"] in feature_flags_in_db:
                _old = feature_flags_in_db[row["name"]]
                _sn = str(_old["sn"])
                del _old["sn"]

                if _old == body:
                    self.log.info(
                        f"Feature flag '{row['name']}' already exists with provided values {body}"
                    )
                    continue

                self.log.info(
                    f"Update feature flag '{row['name']}' from {_old} to {body}"
                )

                body["uid"] = _sn
                self.api.patch_to_api(body=body, path="feature-flags")
            else:
                data = {
                    "path": "feature-flags",
                    "body": body,
                }

                self.log.info(f"Add feature flag '{data['body']['name']}'")

                self.api.post_to_api(data)

    def run(self):
        feature_flags = load_env("FEATURE_FLAGS")
        self.log.info("Importing feature flags")

        self.handle_feature_flags(feature_flags)

        self.log.info("Done importing feature flags")


def main():
    metr = Metrics()
    migrator = FeatureFlags(metrics_inst=metr)
    migrator.run()
    metr.print()


if __name__ == "__main__":
    main()
