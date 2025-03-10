import datetime

import neo4j
from neomodel import (
    BooleanProperty,
    DateTimeProperty,
    IntegerProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    StructuredRel,
    db,
)
from neomodel.properties import Property, validator

from clinical_mdr_api.domain_repositories.models._utils import (
    convert_to_tz_aware_datetime,
)
from clinical_mdr_api.domains.versioned_object_aggregate import LibraryItemStatus
from common.config import NUMBER_OF_UID_DIGITS
from common.exceptions import NotFoundException
from common.utils import convert_to_datetime


class ZonedDateTimeProperty(DateTimeProperty):
    @validator
    def deflate(self, value: datetime.datetime):
        return convert_to_tz_aware_datetime(value)

    @validator
    def inflate(self, value: neo4j.time.DateTime):
        return convert_to_datetime(value)


class ClinicalMdrNode(StructuredNode):
    """
    A `ClinicalMdrNode` is the highest level of abstraction for
    a relationship in the graph.
    It inherits directly from a neomodel `StructuredNode` object.
    All other node models inherit from this class.
    """

    __abstract_node__ = True

    @classmethod
    def category(cls):
        pass

    @classmethod
    def get_definition(cls):
        defined_props = cls.defined_properties()
        return {
            key: value
            for key, value in defined_props.items()
            if isinstance(value, Property)
        }

    def to_dict(self):
        defined_props = self.get_definition()
        props = vars(self)
        return {key: props[key] for key, value in defined_props.items()}


class ClinicalMdrNodeWithUID(ClinicalMdrNode):
    """
    An extension of a ClinicalMdrNode that automatically sets a generated UID when it is saved.
    """

    __abstract_node__ = True
    uid = StringProperty(unique_index=True)

    @classmethod
    def get_next_free_uid_and_increment_counter(cls) -> str:
        """
        Finds the next free available UID for a given object.
        If none of the objects have ever been created, sets up a new incremental counter for this object type.
        """
        object_name = cls.__name__.removesuffix("Root")

        return str(
            db.cypher_query(
                """
        MERGE (m:Counter{{counterId:'{LABEL}Counter'}})
        ON CREATE SET m:{LABEL}Counter, m.count=0
        WITH m
        CALL apoc.atomic.add(m,'count',1,1) yield oldValue, newValue
        WITH newValue(newValue) as uid_number
        RETURN "{LABEL}_"+apoc.text.lpad(""+(uid_number), {number_of_digits}, "0")
        """.format(
                    LABEL=object_name, number_of_digits=NUMBER_OF_UID_DIGITS
                )
            )[0][0][0]
        )

    @classmethod
    def generate_node_uids_if_not_present(cls) -> None:
        """
        Generates UIDs for all nodes of this class that do not yet have a UID.
        Uses the template structure [NODELABEL]_999999 for the generated identifiers.
        """
        node_label = cls.__name__
        object_name = node_label.removesuffix("Root")

        db.cypher_query(
            """
        // the new UIDs will start at the value from the memory node.
        MERGE (m:Counter{{counterId:'{LABEL}Counter'}})
        ON CREATE SET m:{LABEL}Counter, m.count=1
        WITH m
        CALL apoc.lock.nodes([m])

        // Then, get all newly created nodes of a specific label without assigned UID.
        MATCH (n:{NODE_LABEL})
        USING SCAN n:{NODE_LABEL}
        WHERE n.uid is null
        WITH collect(n) as new_nodes, m

        // Increment the counter by the size of the newly created nodes, so we store this for the next transaction.
        SET m.count = m.count + size(new_nodes)

        // Then, we need to assign new UIDs to the created nodes.
        // We start at the old counter value (start_uid_number), and increment the values for each new node.
        WITH new_nodes, range(0,size(new_nodes)-1) as indices, m.count - size(new_nodes) as start_uid_number
        UNWIND indices as index
        WITH new_nodes[index] as node, index + start_uid_number as uid_number
        SET node.uid = "{LABEL}_"+apoc.text.lpad(""+(uid_number), {number_of_digits}, "0")
        """.format(
                LABEL=object_name,
                NODE_LABEL=node_label,
                number_of_digits=NUMBER_OF_UID_DIGITS,
            )
        )

    def save(self):
        """
        Saves the node after create/update of a node.
        This method ensures that there will always be a generated UID assigned.
        """
        if self.uid is None:
            object_name = (
                type(self).__name__[: len(type(self).__name__) - 4]
                if type(self).__name__.endswith("Root")
                else type(self).__name__
            )

            new_uid = db.cypher_query(
                """
            MERGE (m:Counter{{counterId:'{LABEL}Counter'}})
            ON CREATE SET m:{LABEL}Counter, m.count=1
            ON MATCH SET m.count = m.count + 1
            WITH m
            RETURN m.count as number
            """.format(
                    LABEL=object_name
                )
            )[0][0][0]
            self.uid = str(object_name) + "_" + str(new_uid).zfill(NUMBER_OF_UID_DIGITS)
        return super().save()


# pylint: disable=abstract-method
class ClinicalMdrRel(StructuredRel):
    __abstract_node__ = True
    """
    A `ClinicalMdrRel` is the highest level of abstraction for a
    relationship in the graph.
    It inherits directly from a neomodel `StructuredRel` object.
    All other relationship models inherit from this class.
    """

    def to_dict(self):
        defined_props = self.defined_properties()
        props = vars(self)
        return {
            key: props[key]
            for key, value in defined_props.items()
            if isinstance(value, Property)
        }


# pylint: disable=abstract-method
class TemplateUsesParameterRelation(ClinicalMdrRel):
    position = IntegerProperty()


# pylint: disable=abstract-method
class ConjunctionRelation(ClinicalMdrRel):
    position = IntegerProperty()
    set_number = IntegerProperty()


class Library(ClinicalMdrNode):
    name = StringProperty()
    is_editable = BooleanProperty()


# pylint: disable=abstract-method
class VersionRelationship(ClinicalMdrRel):
    """
    A `VersionRelationship` represents a relationship between a `VersionRoot`
    and a `VersionValue` node.
    In the graph, these are persisted as `LATEST`, `HAS_VERSION`,
    `LATEST_DRAFT` or `LATEST_FINAL`.
    """

    start_date = ZonedDateTimeProperty()
    end_date = ZonedDateTimeProperty()
    change_description = StringProperty()
    version = StringProperty()
    status = StringProperty()
    author_id = StringProperty()


class VersionValue(ClinicalMdrNode):
    __abstract_node__ = True
    """
    A `VersionValue` contains at least a name for the object being versioned.
    domain entities (activities, objectives) inherit from this class and add
    other properties if needed.
    """
    name = StringProperty()
    STUDY_SELECTION_REL_LABEL = ""
    STUDY_VALUE_REL_LABEL = ""

    def get_root_uid_by_latest(self):
        cypher_query = f"""
        MATCH (ot)-[:LATEST_FINAL|LATEST_DRAFT]-> (ov:{self.__label__} {{name: "{self.name}"}})
        return ot.uid
        """

        uids, _ = db.cypher_query(cypher_query)

        NotFoundException.raise_if(
            len(uids) < 1, msg=f"Cannot find root for this name {self.name}"
        )

        return uids[0][0]

    def get_study_count(self) -> int:
        cypher_query = f"""
        MATCH (n)<-[:{self.STUDY_SELECTION_REL_LABEL}]-(:StudySelection)<-[:{self.STUDY_VALUE_REL_LABEL}]-(:StudyValue)<--(sr:StudyRoot)
        WHERE elementId(n)=$element_id
        RETURN count(DISTINCT sr)
        """

        count, _ = db.cypher_query(cypher_query, {"element_id": self.element_id})
        return count[0][0]


class VersionRoot(ClinicalMdrNodeWithUID):
    __abstract_node__ = True
    """
    A `VersionRoot` contains the UID of the entity being versioned.
    The object holds references to one or more VersionValues with
    VersionRelationships.
    """
    TEMPLATE_REL_LABEL = ""
    LIBRARY_REL_LABEL = "CONTAINS"
    PARAMETERS_LABEL = "HAS_PARAMETERS"

    has_template = RelationshipTo("VersionRoot", "HAS_TEMPLATE")

    has_version = RelationshipTo(VersionValue, "HAS_VERSION", model=VersionRelationship)
    has_latest_value = RelationshipTo(VersionValue, "LATEST")
    latest_draft = RelationshipTo(VersionValue, "LATEST_DRAFT")
    latest_final = RelationshipTo(VersionValue, "LATEST_FINAL")
    latest_retired = RelationshipTo(VersionValue, "LATEST_RETIRED")

    has_library = RelationshipFrom(Library, LIBRARY_REL_LABEL)
    has_parameters = RelationshipTo(
        ".template_parameter.TemplateParameter",
        PARAMETERS_LABEL,
        model=TemplateUsesParameterRelation,
    )

    def get_final_before(self, date_before: datetime):
        # pylint: disable=no-member
        past_final_versions = self.has_version.match(
            start_date__lte=date_before,
            end_date__gte=date_before,
            status=LibraryItemStatus.FINAL.value,
        )
        # I expect only one or zero elements here
        # otherwise it would mean overreaching entries for the same status
        if len(past_final_versions) > 0:
            return past_final_versions[0]
        return None

    def get_retired_before(self, date_before: datetime):
        # pylint: disable=no-member
        past_retired_versions = self.has_version.match(
            start_date__lte=date_before,
            end_date__gte=date_before,
            status=LibraryItemStatus.RETIRED.value,
        )
        # I expect only one or zero elements here
        # otherwise it would mean overreaching entries for the same status
        if len(past_retired_versions) > 0:
            return past_retired_versions[0]
        return None

    def get_value_for_version(self, version: str):
        # pylint: disable=no-member
        matching_values = self.latest_final.match(version=version)
        if len(matching_values) == 0:
            matching_values = self.latest_draft.match(version=version)
        if len(matching_values) == 0:
            matching_values = self.latest_retired.match(version=version)
        if len(matching_values) == 0:
            matching_values = self.has_version.match(version=version)
        if len(matching_values) > 0:
            return matching_values[0]
        return None

    def get_relation_for_version(self, version: str):
        # pylint: disable=no-member
        value = self.get_value_for_version(version)
        relationships = self.latest_final.all_relationships(value)
        if len(relationships) == 0:
            relationships = self.latest_draft.all_relationships(value)
        if len(relationships) == 0:
            relationships = self.latest_retired.all_relationships(value)
        if len(relationships) == 0:
            relationships = self.has_version.all_relationships(value)

        if len(relationships) > 0:
            return relationships[0]
        return None

    def get_instantiations_count(self):
        cypher_query = """
        MATCH (ot:{template_label} {{uid: "{uid}" }})
        CALL {{WITH ot MATCH (ot)-[:{relation_label}]->(obr)-[:LATEST_FINAL]-> (obv) RETURN count(obv) as finals}}
        CALL {{WITH ot MATCH (ot)-[:{relation_label}]->(obr)-[:LATEST_DRAFT]-> (obv) RETURN count(obv) as drafts}}
        CALL {{WITH ot MATCH (ot)-[:{relation_label}]->(obr)-[:LATEST_RETIRED]-> (obv) RETURN count(obv) as retired}}
        RETURN  finals, drafts, retired
        """.format(
            template_label=self.__label__,
            uid=self.uid,
            relation_label=self.TEMPLATE_REL_LABEL,
        )

        counts, _ = db.cypher_query(cypher_query)
        return counts[0]


class Conjunction(ClinicalMdrNode):
    string = StringProperty()
