"""Decorators that can be used on routers"""

import functools

# pylint: disable=unused-import
from clinical_mdr_api.routers.export import allow_exports

# pylint: disable=unused-import
from clinical_mdr_api.services.decorators import validate_if_study_is_not_locked
from common import config
from common.exceptions import ValidationException


def validate_serial_number_against_neo4j_max_and_min_int():
    """Decorator ensures the provided Serial Number is not bigger than MAX_INT_NEO4J, else raises ValidationException."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ValidationException.raise_if(
                kwargs["serial_number"] > config.MAX_INT_NEO4J
                or kwargs["serial_number"] < -config.MAX_INT_NEO4J,
                msg=f"Serial Number must not be greater than '{config.MAX_INT_NEO4J}' and less than '-{config.MAX_INT_NEO4J}'.",
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator
