import datetime
import json
import re
from copy import copy
from typing import Any, Callable, Generic, Iterable, Self, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import conint, root_validator
from pydantic.fields import Undefined
from pydantic.generics import GenericModel
from starlette.responses import Response

from clinical_mdr_api.domains.concepts.unit_definitions.unit_definition import (
    UnitDefinitionAR,
)
from clinical_mdr_api.services.user_info import UserInfoService
from common.config import STUDY_TIME_UNIT_SUBSET

EXCLUDE_PROPERTY_ATTRIBUTES_FROM_SCHEMA = {
    "remove_from_wildcard",
    "source",
    "exclude_from_orm",
    "is_json",
}


def from_duration_object_to_value_and_unit(
    duration: str,
    find_all_study_time_units: Callable[[str], Iterable[UnitDefinitionAR]],
):
    duration_code = duration[-1].lower()
    # cut off the first 'P' and last unit letter
    duration_value = int(duration[1:-1])

    all_study_time_units, _ = find_all_study_time_units(subset=STUDY_TIME_UNIT_SUBSET)
    # We are using a callback here and this function returns objects as an item list, hence we need to unwrap i
    found_unit = None
    # find unit extracted from iso duration string (duration_code) and find it in the set of all age units
    for unit in all_study_time_units:
        unit_first_letter = unit.name[0].lower()
        unit_last_letter = unit.name[-1].lower()
        # if duration value which is passed is great than 1 we should find a corresponding unit in the plural version
        if (
            duration_value > 1
            and unit_first_letter == duration_code
            and unit_last_letter == "s"
        ):
            found_unit = unit
            break
        if duration_value <= 1 and unit_first_letter == duration_code:
            found_unit = unit
            break
    return duration_value, found_unit


def get_latest_on_datetime_str():
    return f"LATEST on {datetime.datetime.now(datetime.UTC).isoformat()}"


class BaseModel(PydanticBaseModel):
    @classmethod
    def from_orm(cls, obj):
        """
        We override this method to allow flattening on nested models.

        It is now possible to declare a source property on a Field()
        call to specify the location where this method should get a
        field's value from.
        """

        def _extract_part_from_node(node_to_extract, path, extract_from_relationship):
            """
            Traverse specified path in the node_to_extract.
            The possible paths for the traversal are stored in the node _relations dictionary.
            """
            if extract_from_relationship:
                path += "_relationship"
            if not hasattr(node_to_extract, "_relations"):
                return None
            if path not in node_to_extract._relations.keys():
                # it means that the field is Optional and None was set to be a default value
                if field.field_info.default is None:
                    return None
                raise RuntimeError(
                    f"{path} is not present in node relations (did you forget to fetch it?)"
                )
            return node_to_extract._relations[path]

        def _get_value_from_source_field(model_field, db_node, db_field):
            value = getattr(db_node, db_field)

            # In case of author_username model field, we need to lookup the User node using the `source` field value as `User.user_id`
            if model_field == "author_username":
                value = UserInfoService.get_author_username_from_id(value)

            return value

        ret = []
        for name, field in cls.__fields__.items():
            source = field.field_info.extra.get("source")
            if field.field_info.extra.get("exclude_from_orm"):
                continue
            if not source:
                if issubclass(field.type_, BaseModel):
                    # get out of recursion
                    if field.type_ is cls:
                        continue
                    # added copy to not override properties in main obj
                    value = field.type_.from_orm(copy(obj))
                    # if some value of nested model is initialized then set the whole nested object
                    if isinstance(value, list):
                        if value:
                            setattr(obj, name, value)
                        else:
                            setattr(obj, name, [])
                    else:
                        if any(value.dict().values()):
                            setattr(obj, name, value)
                        # if all values of nested model are None set the whole object to None
                        else:
                            setattr(obj, name, None)
                # Quick fix to provide default None value to fields that allow it
                # Not the best place to do this...
                elif field.field_info.default == Undefined and not hasattr(obj, name):
                    setattr(obj, name, None)
                continue
            if "." in source or "|" in source:
                orig_source = source
                # split by . that implicates property on node or | that indicates property on the relationship
                parts = re.split(r"[.|]", source)
                source = parts[-1]
                last_traversal = parts[-2]
                node = obj
                parts = parts[:-1]
                for _, part in enumerate(parts):
                    extract_from_relationship = False
                    if part == last_traversal and "|" in orig_source:
                        extract_from_relationship = True
                    # if node is a list of nodes we want to extract property/relationship
                    # from all nodes in list of nodes
                    if isinstance(node, list):
                        return_node = []
                        for item in node:
                            extracted = _extract_part_from_node(
                                node_to_extract=item,
                                path=part,
                                extract_from_relationship=extract_from_relationship,
                            )
                            return_node.extend(extracted)
                        node = return_node
                    else:
                        node = _extract_part_from_node(
                            node_to_extract=node,
                            path=part,
                            extract_from_relationship=extract_from_relationship,
                        )
                    if node is None:
                        break
            else:
                node = obj
            if node is not None:
                # if node is a list we want to
                # extract property from each element of list and return list of property values
                if isinstance(node, list):
                    value = [
                        _get_value_from_source_field(name, n, source) for n in node
                    ]
                else:
                    value = _get_value_from_source_field(name, node, source)

            else:
                value = None
            # if obtained value is a list and field type is not List
            # it means that we are building some list[BaseModel] but its fields are not of list type

            if isinstance(value, list) and not field.sub_fields:
                # if ret array is not instantiated
                # it means that the first property out of the whole list [BaseModel] is being instantiated
                if not ret:
                    for val in value:
                        temp_obj = copy(obj)
                        setattr(temp_obj, name, val)
                        ret.append(temp_obj)
                # if ret exists it means that some properties out of whole list [BaseModel] are already instantiated
                else:
                    for val, item in zip(value, ret):
                        setattr(item, name, val)
            else:
                setattr(obj, name, value)
        # Nothing to return and the value returned by the query
        # is an empty list => return an empty list
        if not ret and isinstance(value, list):
            return []
        # Returning single BaseModel
        if not ret and not isinstance(value, list):
            return super().from_orm(obj)
        # if ret exists it means that the list of BaseModels is being returned
        objs_to_return = []
        for item in ret:
            objs_to_return.append(super().from_orm(item))
        return objs_to_return

    class Config:
        # Configuration applies to all our models #

        @staticmethod
        def schema_extra(schema: dict[str, Any], _: Type) -> None:
            """Exclude some custom internal attributes of Fields (properties) from the schema definitions"""
            for prop in schema.get("properties", {}).values():
                for attr in EXCLUDE_PROPERTY_ATTRIBUTES_FROM_SCHEMA:
                    prop.pop(attr, None)


class InputModel(BaseModel):
    @root_validator(pre=True)
    # pylint: disable=no-self-argument
    def strip_whitespace(cls, values: dict):
        for key, value in values.items():
            if isinstance(value, str):
                values[key] = value.strip()
            elif isinstance(value, list):
                values[key] = [
                    elm.strip() if isinstance(elm, str) else elm for elm in value
                ]
        return values


class PostInputModel(InputModel): ...


class PatchInputModel(InputModel): ...


class BatchInputModel(InputModel): ...


T = TypeVar("T")


class CustomPage(GenericModel, Generic[T]):
    """
    A generic class used as a return type for paginated queries.

    Attributes:
        items (list[T]): The items returned by the query.
        total (int): The total number of items that match the query.
        page (int): The number of the current page.
        size (int): The maximum number of items per page.
    """

    items: list[T]
    total: conint(ge=0)
    page: conint(ge=0)
    size: conint(ge=0)

    @classmethod
    def create(cls, items: list[T], total: int, page: int, size: int) -> Self:
        return cls(total=total, items=items, page=page, size=size)


class GenericFilteringReturn(GenericModel, Generic[T]):
    """
    A generic class used as a return type for filtered queries.

    Attributes:
        items (list[T]): The items returned by the query.
        total (int): The total number of items that match the query.
    """

    items: list[T]
    total: conint(ge=0)

    @classmethod
    def create(cls, items: list[T], total: int) -> Self:
        return cls(items=items, total=total)


class PrettyJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=4,
            separators=(", ", ": "),
        ).encode("utf-8")
