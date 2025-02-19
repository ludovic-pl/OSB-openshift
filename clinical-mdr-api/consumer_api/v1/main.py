# RESTful API endpoints used by consumers that want to extract data from StudyBuilder
# pylint: disable=invalid-name
# pylint: disable=redefined-builtin
from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from common import config
from common.auth import rbac
from common.models.error import ErrorResponse
from consumer_api.shared.responses import PaginatedResponse
from consumer_api.v1 import db as DB
from consumer_api.v1 import models

router = APIRouter()


# GET endpoint to retrieve a list of studies
@router.get(
    "/studies",
    dependencies=[rbac.STUDY_READ],
    response_model=PaginatedResponse[models.Study],
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request",
        },
    },
)
async def get_studies(
    request: Request,
    sort_by: models.SortByStudies = models.SortByStudies.UID,
    sort_order: models.SortOrder = models.SortOrder.ASC,
    page_size: Annotated[
        int, Query(ge=1, le=config.MAX_PAGE_SIZE)
    ] = config.DEFAULT_PAGE_SIZE,
    page_number: Annotated[int, Query(ge=1)] = 1,
    id: Annotated[
        str, Query(description="Filter by study ID (case-insensitive partial match)")
    ] = None,
):
    """Get a paginated list of studies"""
    studies = DB.get_studies(
        sort_by=sort_by,
        sort_order=sort_order,
        page_size=page_size,
        page_number=page_number,
        id=id,
    )

    return PaginatedResponse.from_input(
        request=request,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        page_size=page_size,
        page_number=page_number,
        items=[models.Study.from_input(study) for study in studies],
        query_param_names=["id"],
    )


# GET endpoint to retrieve a study's visits
@router.get(
    "/studies/{uid}/study-visits",
    dependencies=[rbac.STUDY_READ],
    response_model=PaginatedResponse[models.StudyVisit],
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request",
        },
    },
)
async def get_study_visits(
    request: Request,
    uid: Annotated[str, Path(description="Study UID")],
    sort_by: models.SortByStudyVisits = models.SortByStudyVisits.UID,
    sort_order: models.SortOrder = models.SortOrder.ASC,
    page_size: Annotated[
        int, Query(ge=1, le=config.MAX_PAGE_SIZE)
    ] = config.PAGE_SIZE_100,
    page_number: Annotated[int, Query(ge=1)] = 1,
    study_version_number: Annotated[
        str | None, Query(description="Study Version Number")
    ] = None,
):
    """Get a paginated list of study visits"""
    study_visits = DB.get_study_visits(
        study_uid=uid,
        sort_by=sort_by,
        sort_order=sort_order,
        page_size=page_size,
        page_number=page_number,
        study_version_number=study_version_number,
    )

    return PaginatedResponse.from_input(
        request=request,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        page_size=page_size,
        page_number=page_number,
        items=[
            models.StudyVisit.from_input(study_visit) for study_visit in study_visits
        ],
        query_param_names=["study_version_number"],
    )


# GET endpoint to retrieve a study's activities
@router.get(
    "/studies/{uid}/study-activities",
    dependencies=[rbac.STUDY_READ],
    response_model=PaginatedResponse[models.StudyActivity],
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request",
        },
    },
)
async def get_study_activities(
    request: Request,
    uid: Annotated[str, Path(description="Study UID")],
    sort_by: models.SortByStudyActivities = models.SortByStudyActivities.UID,
    sort_order: models.SortOrder = models.SortOrder.ASC,
    page_size: Annotated[
        int, Query(ge=1, le=config.MAX_PAGE_SIZE)
    ] = config.PAGE_SIZE_100,
    page_number: Annotated[int, Query(ge=1)] = 1,
    study_version_number: Annotated[
        str | None, Query(description="Study Version Number")
    ] = None,
):
    """Get a paginated list of study activities"""
    study_activities = DB.get_study_activities(
        study_uid=uid,
        sort_by=sort_by,
        sort_order=sort_order,
        page_size=page_size,
        page_number=page_number,
        study_version_number=study_version_number,
    )

    return PaginatedResponse.from_input(
        request=request,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        page_size=page_size,
        page_number=page_number,
        items=[
            models.StudyActivity.from_input(study_activity)
            for study_activity in study_activities
        ],
        query_param_names=["study_version_number"],
    )


# GET endpoint to retrieve a study's detailed soa
@router.get(
    "/studies/{uid}/detailed-soa",
    dependencies=[rbac.STUDY_READ],
    response_model=PaginatedResponse[models.StudyDetailedSoA],
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request",
        },
    },
)
async def get_study_detailed_soa(
    request: Request,
    uid: Annotated[str, Path(description="Study UID")],
    sort_by: models.SortByStudyDetailedSoA = models.SortByStudyDetailedSoA.ACTIVITY_NAME,
    sort_order: models.SortOrder = models.SortOrder.ASC,
    page_size: Annotated[
        int, Query(ge=1, le=config.MAX_PAGE_SIZE)
    ] = config.PAGE_SIZE_100,
    page_number: Annotated[int, Query(ge=1)] = 1,
    study_version_number: Annotated[
        str | None, Query(description="Study Version Number")
    ] = None,
):
    """Get a paginated list of detailed SoA items"""
    study_detailed_soas = DB.get_study_detailed_soa(
        study_uid=uid,
        sort_by=sort_by,
        sort_order=sort_order,
        page_size=page_size,
        page_number=page_number,
        study_version_number=study_version_number,
    )

    return PaginatedResponse.from_input(
        request=request,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        page_size=page_size,
        page_number=page_number,
        items=[
            models.StudyDetailedSoA.from_input(study_detailed_soa)
            for study_detailed_soa in study_detailed_soas
        ],
        query_param_names=["study_version_number"],
    )


# GET endpoint to retrieve a study's operational soa
@router.get(
    "/studies/{uid}/operational-soa",
    dependencies=[rbac.STUDY_READ],
    response_model=PaginatedResponse[models.StudyOperationalSoA],
    status_code=200,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid request",
        },
    },
)
async def get_study_operational_soa(
    request: Request,
    uid: Annotated[str, Path(description="Study UID")],
    sort_by: models.SortByStudyOperationalSoA = models.SortByStudyOperationalSoA.ACTIVITY_NAME,
    sort_order: models.SortOrder = models.SortOrder.ASC,
    page_size: Annotated[
        int, Query(ge=1, le=config.MAX_PAGE_SIZE)
    ] = config.PAGE_SIZE_100,
    page_number: Annotated[int, Query(ge=1)] = 1,
    study_version_number: Annotated[
        str | None, Query(description="Study Version Number")
    ] = None,
):
    """Get a paginated list of operational SoA items representing a point in the activities/visits matrix"""
    study_operational_soas = DB.get_study_operational_soa(
        study_uid=uid,
        sort_by=sort_by,
        sort_order=sort_order,
        page_size=page_size,
        page_number=page_number,
        study_version_number=study_version_number,
    )

    return PaginatedResponse.from_input(
        request=request,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        page_size=page_size,
        page_number=page_number,
        items=[
            models.StudyOperationalSoA.from_input(study_operational_soa)
            for study_operational_soa in study_operational_soas
        ],
        query_param_names=["study_version_number"],
    )
