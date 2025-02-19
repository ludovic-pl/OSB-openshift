"""Study chart router."""

import io
import os
from typing import Annotated

from fastapi import Path, Query, status
from fastapi.responses import HTMLResponse, StreamingResponse
from starlette.requests import Request

from clinical_mdr_api.domain_repositories.study_selections.study_soa_repository import (
    SoALayout,
)
from clinical_mdr_api.models.study_selections.study_selection import DetailedSoAHistory
from clinical_mdr_api.models.utils import CustomPage
from clinical_mdr_api.routers import _generic_descriptions, decorators
from clinical_mdr_api.routers import studies_router as router
from clinical_mdr_api.services.studies.study import StudyService
from clinical_mdr_api.services.studies.study_activity_selection import (
    StudyActivitySelectionService,
)
from clinical_mdr_api.services.studies.study_flowchart import StudyFlowchartService
from clinical_mdr_api.services.utils.table_f import TableWithFootnotes
from common import config
from common.auth import rbac

DETAILED_QUERY_DESCRIPTION = "Return detailed SoA, including all rows that are otherwise hidden from protocol SoA"

DETAILED_QUERY = Query(description=DETAILED_QUERY_DESCRIPTION)

OPERATIONAL_QUERY = Query(
    description="Returns operational SoA if True else Protocol SoA if False (default)"
)

STUDY_UID_PATH = Path(description="The unique id of the study.")

TIME_UNIT_QUERY = Query(
    pattern="^(week|day)$", description="The preferred time unit, either day or week."
)


@router.get(
    "/{study_uid}/flowchart/coordinates",
    dependencies=[rbac.STUDY_READ],
    summary="Returns uid to [row,column] coordinates mapping of items included in SoA Protocol Flowchart table",
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
    response_model=dict[str, tuple[int, int]],
)
def get_study_flowchart_coordinates(
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
) -> dict[str, tuple[int, int]]:
    coordinates = StudyFlowchartService().get_flowchart_item_uid_coordinates(
        study_uid=study_uid, study_value_version=study_value_version
    )
    return coordinates


@router.get(
    "/{study_uid}/flowchart",
    dependencies=[rbac.STUDY_READ],
    summary="Protocol, Detailed or Operational SoA table with footnotes as JSON",
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
    response_model=TableWithFootnotes,
    response_model_exclude_none=True,
)
def get_study_flowchart(
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
    time_unit: Annotated[str | None, TIME_UNIT_QUERY] = None,
    detailed: Annotated[
        bool | None, Query(description=DETAILED_QUERY_DESCRIPTION)
    ] = True,
    operational: Annotated[bool | None, OPERATIONAL_QUERY] = False,
    force_build: Annotated[
        bool | None,
        Query(description="Force building of SoA without using any saved snapshot"),
    ] = False,
) -> TableWithFootnotes:
    table = StudyFlowchartService().get_flowchart_table(
        study_uid=study_uid,
        time_unit=time_unit,
        study_value_version=study_value_version,
        layout=StudyFlowchartService.choose_soa_layout(detailed, operational),
        force_build=force_build,
    )

    return table


@router.get(
    "/{study_uid}/flowchart.html",
    dependencies=[rbac.STUDY_READ],
    summary="Builds and returns an HTML document with Protocol, Detailed or Operational SoA table with footnotes",
    responses={
        200: {"content": {"text/html": {"schema": {"type": "string"}}}},
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_study_flowchart_html(
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
    time_unit: Annotated[str | None, TIME_UNIT_QUERY] = None,
    detailed: Annotated[bool | None, DETAILED_QUERY] = False,
    debug_uids: Annotated[
        bool | None, Query(description="Show uids on column superscript")
    ] = False,
    debug_coordinates: Annotated[
        bool | None, Query(description="Debug coordinates as superscripts")
    ] = False,
    debug_propagation: Annotated[
        bool | None, Query(description="Debug propagations without hiding rows")
    ] = False,
    operational: Annotated[bool | None, OPERATIONAL_QUERY] = False,
) -> HTMLResponse:
    return HTMLResponse(
        StudyFlowchartService().get_study_flowchart_html(
            study_uid=study_uid,
            time_unit=time_unit,
            study_value_version=study_value_version,
            detailed=detailed,
            operational=operational,
            debug_uids=debug_uids,
            debug_coordinates=debug_coordinates,
            debug_propagation=debug_propagation,
        )
    )


@router.get(
    "/{study_uid}/flowchart.docx",
    dependencies=[rbac.STUDY_READ],
    summary="Builds and returns an DOCX document with Protocol, Detailed or Operational SoA table with footnotes",
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}
            }
        },
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_study_flowchart_docx(
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
    time_unit: Annotated[str | None, TIME_UNIT_QUERY] = None,
    detailed: Annotated[bool | None, DETAILED_QUERY] = False,
    operational: Annotated[bool | None, OPERATIONAL_QUERY] = False,
) -> StreamingResponse:
    stream = (
        StudyFlowchartService()
        .get_study_flowchart_docx(
            study_uid=study_uid,
            time_unit=time_unit,
            study_value_version=study_value_version,
            detailed=detailed,
            operational=operational,
        )
        .get_document_stream()
    )

    # determine the size of the binary DOCX document for HTTP header
    size = stream.seek(0, os.SEEK_END)
    stream.seek(0)

    # get study_id for constructing download filename
    study = StudyService().get_by_uid(
        study_uid, study_value_version=study_value_version
    )

    # construct download filename
    filename = []
    if study.current_metadata.identification_metadata.study_id:
        filename.append(study.current_metadata.identification_metadata.study_id)
    if detailed:
        filename.append("detailed")
    filename.append("flowchart.docx")
    filename = " ".join(filename)

    # send response along with document info in HTTP headers
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": f"{size:d}",
        },
    )


@router.get(
    "/{study_uid}/operational-soa.xlsx",
    dependencies=[rbac.STUDY_READ],
    summary="Builds and returns an XLSX document with Operational SoA",
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}
            }
        },
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_operational_soa_xlsx(
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
    time_unit: Annotated[str | None, TIME_UNIT_QUERY] = None,
) -> StreamingResponse:
    xlsx = StudyFlowchartService().get_operational_soa_xlsx(
        study_uid=study_uid,
        time_unit=time_unit,
        study_value_version=study_value_version,
    )

    # render document into a stream
    stream = io.BytesIO()
    xlsx.save(stream)
    size = stream.seek(0, os.SEEK_END)
    stream.seek(0)

    # get Study for constructing download filename
    study = StudyService().get_by_uid(
        study_uid, study_value_version=study_value_version
    )

    # construct download filename
    filename = ["operational", "SoA.xlsx"]
    if study.current_metadata.identification_metadata.study_id:
        filename.insert(0, study.current_metadata.identification_metadata.study_id)
    filename = " ".join(filename)

    # send response along with document info in HTTP header
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": f"{size:d}",
        },
    )


@router.get(
    "/{study_uid}/operational-soa.html",
    dependencies=[rbac.STUDY_READ],
    summary="Builds and returns an HTML document with Operational SoA",
    responses={
        200: {"content": {"text/html": {}}},
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_operational_soa_html(
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
    time_unit: Annotated[str | None, TIME_UNIT_QUERY] = None,
) -> HTMLResponse:
    return HTMLResponse(
        StudyFlowchartService().get_operational_soa_html(
            study_uid=study_uid,
            time_unit=time_unit,
            study_value_version=study_value_version,
        )
    )


@router.get(
    "/{study_uid}/detailed-soa-history",
    dependencies=[rbac.STUDY_READ],
    summary="Returns the history of changes performed to a specific detailed SoA",
    response_model=CustomPage[DetailedSoAHistory],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
def get_detailed_soa_history(
    study_uid: Annotated[str, STUDY_UID_PATH],
    page_number: Annotated[
        int | None, Query(ge=1, description=_generic_descriptions.PAGE_NUMBER)
    ] = config.DEFAULT_PAGE_NUMBER,
    page_size: Annotated[
        int | None,
        Query(
            ge=0,
            le=config.MAX_PAGE_SIZE,
            description=_generic_descriptions.PAGE_SIZE,
        ),
    ] = config.DEFAULT_PAGE_SIZE,
    total_count: Annotated[
        bool | None, Query(description=_generic_descriptions.TOTAL_COUNT)
    ] = False,
) -> list[DetailedSoAHistory]:
    detailed_soa_history = StudyActivitySelectionService().get_detailed_soa_history(
        study_uid=study_uid,
        page_size=page_size,
        page_number=page_number,
        total_count=total_count,
    )
    return CustomPage.create(
        items=detailed_soa_history.items,
        total=detailed_soa_history.total,
        page=page_number,
        size=page_size,
    )


@router.get(
    "/{study_uid}/detailed-soa-exports",
    dependencies=[rbac.STUDY_READ],
    summary="Exports the Detailed SoA content",
    response_model=list[dict],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "study_number",
            "study_version",
            "soa_group",
            "activity_group",
            "activity_subgroup",
            "visit",
            "activity",
            "is_data_collected",
        ],
        "include_if_exists": [
            "epoch",
            "milestone",
        ],
        "formats": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/xml",
            "application/json",
        ],
    }
)
# pylint: disable=unused-argument
def export_detailed_soa_content(
    request: Request,  # request is actually required by the allow_exports decorator
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
) -> list[dict]:
    soa_content = StudyFlowchartService().download_detailed_soa_content(
        study_uid=study_uid,
        study_value_version=study_value_version,
    )
    return soa_content


@router.get(
    "/{study_uid}/operational-soa-exports",
    dependencies=[rbac.STUDY_READ],
    summary="Exports the Operational SoA content",
    response_model=list[dict],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "study_number",
            "study_version",
            "soa_group",
            "activity_group",
            "activity_subgroup",
            "epoch",
            "visit",
            "activity",
            "activity_instance",
            "topic_code",
            "param_code",
        ],
        "formats": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/xml",
            "application/json",
        ],
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
            "Study number=study_number",
            "Study version=study_version",
            "SoA group=soa_group",
            "Activity group=activity_group",
            "Activity subgroup=activity_subgroup",
            "Epoch=epoch",
            "Visit=visit",
            "Activity=activity",
            "Activity instance=activity_instance",
            "Topic code=topic_code",
            "Param code=param_code",
        ],
    }
)
# pylint: disable=unused-argument
def export_operational_soa_content(
    request: Request,  # request is actually required by the allow_exports decorator
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
) -> list[dict]:
    soa_content = StudyFlowchartService().download_operational_soa_content(
        study_uid=study_uid,
        study_value_version=study_value_version,
    )
    return soa_content


@router.get(
    "/{study_uid}/protocol-soa-exports",
    dependencies=[rbac.STUDY_READ],
    summary="Exports the Protocol SoA content",
    response_model=list[dict],
    status_code=200,
    responses={
        404: _generic_descriptions.ERROR_404,
        500: _generic_descriptions.ERROR_500,
    },
)
@decorators.allow_exports(
    {
        "defaults": [
            "study_number",
            "study_version",
            "soa_group",
            "activity_group",
            "activity_subgroup",
            "visit",
            "activity",
        ],
        "include_if_exists": [
            "epoch",
            "milestone",
        ],
        "formats": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/xml",
            "application/json",
        ],
    }
)
# pylint: disable=unused-argument
def export_protocol_soa_content(
    request: Request,  # request is actually required by the allow_exports decorator
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
) -> list[dict]:
    soa_content = StudyFlowchartService().download_detailed_soa_content(
        study_uid=study_uid,
        study_value_version=study_value_version,
        protocol_flowchart=True,
    )
    return soa_content


@router.get(
    "/{study_uid}/flowchart/snapshot",
    dependencies=[rbac.ADMIN_READ],
    summary="Retrieve the saved SoA snapshot for a study version. If no SoA snapshot saved, returns 404.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: _generic_descriptions.ERROR_404,
        status.HTTP_500_INTERNAL_SERVER_ERROR: _generic_descriptions.ERROR_500,
    },
    response_model=TableWithFootnotes,
    response_model_exclude_none=True,
    tags=["Data Migration"],
)
def get_soa_snapshot(
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
    layout: Annotated[
        str, Query(description="SoA layout", pattern=SoALayout.PROTOCOL.value)
    ] = SoALayout.PROTOCOL.value,
) -> TableWithFootnotes:
    return StudyFlowchartService().load_soa_snapshot(
        study_uid=study_uid,
        study_value_version=study_value_version,
        layout=layout,
    )


@router.post(
    "/{study_uid}/flowchart/snapshot",
    dependencies=[rbac.ADMIN_WRITE],
    summary="Update SoA snapshot for a study version based on the recent SoA rules (intended for data migration only)",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: _generic_descriptions.ERROR_404,
        status.HTTP_500_INTERNAL_SERVER_ERROR: _generic_descriptions.ERROR_500,
    },
    response_model=None,
    tags=["Data Migration"],
)
def update_soa_snapshot(
    study_uid: Annotated[str, STUDY_UID_PATH],
    study_value_version: Annotated[
        str | None, _generic_descriptions.STUDY_VALUE_VERSION_QUERY
    ] = None,
    layout: Annotated[
        str, Query(description="SoA layout", pattern=SoALayout.PROTOCOL.value)
    ] = SoALayout.PROTOCOL.value,
) -> None:
    StudyFlowchartService().update_soa_snapshot(
        study_uid=study_uid,
        study_value_version=study_value_version,
        layout=layout,
    )
