import logging
import os
import urllib.parse
from typing import Any

from neomodel.sync_.core import db

APP_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))


log = logging.getLogger(__name__)


def query(
    cypher_query,
    params: dict = None,
    handle_unique: bool = True,
    retry_on_session_expire: bool = False,
    resolve_objects: bool = False,
    to_dict_list: bool = True,
):
    """
    Wraps `db.cypher_query()`

    Returns:
    list[dict] | tuple: If `to_dict_list` is True, returns a list of dictionaries representing the query results.
                        If `to_dict_list` is False, returns a tuple containing the rows and columns from the query.
    """
    rows, columns = db.cypher_query(
        query=cypher_query,
        params=params,
        handle_unique=handle_unique,
        retry_on_session_expire=retry_on_session_expire,
        resolve_objects=resolve_objects,
    )

    if to_dict_list:
        return [get_db_result_as_dict(row, columns) for row in rows]

    return rows, columns


def urlencode_link(link: str) -> str:
    """URL encodes a link"""

    url = urllib.parse.urlparse(link)
    query_params = urllib.parse.parse_qs(url.query, keep_blank_values=True)

    url = url._replace(query=urllib.parse.urlencode(query_params, True))
    return urllib.parse.urlunparse(url)


def get_db_result_as_dict(row: list[Any], columns: list[str]) -> dict:
    item = {}
    for key, value in zip(columns, row):
        item[key] = value
    return item


def db_pagination_clause(page_size: int, page_number: int) -> str:
    return f"SKIP {page_number - 1} * {page_size} LIMIT {page_size}"


def db_sort_clause(sort_by: str, sort_order: str = "ASC") -> str:
    return f"ORDER BY toLower({sort_by}) {sort_order}"


def get_api_version() -> str:
    version_path = os.path.join("./consumer_api", "apiVersion")
    with open(version_path, "r", encoding="utf-8") as file:
        return file.read().strip()
