from neomodel import StringProperty

from clinical_mdr_api.domain_repositories.models.generic import (
    ClinicalMdrNode,
    ZonedDateTimeProperty,
)


class User(ClinicalMdrNode):
    user_id = StringProperty(unique_index=True)
    username = StringProperty()
    name = StringProperty()
    email = StringProperty()
    azp = StringProperty()
    oid = StringProperty()
    roles = StringProperty()
    created = ZonedDateTimeProperty()
    updated = ZonedDateTimeProperty()
