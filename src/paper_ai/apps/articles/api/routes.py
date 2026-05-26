from uuid import UUID

from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from ..exceptions.status_ex import InvalidStatusChangeException
from ..services import (
    create_project,
    delete_project,
    get_project,
    start_generation,
)
from ..tasks import run_generation_step
from .schemas import (
    CreateProjectResponseSchema,
    CreateProjectSchema,
    ProjectResponseSchema,
    project_to_response,
)

projects_router = Router(tags=["projects"])


@projects_router.post("", response=CreateProjectResponseSchema)
def create_project_route(request: HttpRequest, body: CreateProjectSchema):
    project_id = create_project(
        marker=body.marker,
        depth=[(item.keyword, item.count) for item in body.depth],
        width=body.width,
        n_gramms=body.n_gramms,
        count_chapters=body.count_chapters,
        about_author=body.about_author,
    )
    return CreateProjectResponseSchema(id=project_id)


@projects_router.delete("/{project_id}", response={204: None})
def delete_project_route(request: HttpRequest, project_id: UUID):
    try:
        delete_project(str(project_id))
    except LookupError as exc:
        raise HttpError(404, str(exc)) from exc
    return 204, None


@projects_router.get("/{project_id}", response=ProjectResponseSchema)
def get_project_route(request: HttpRequest, project_id: UUID):
    try:
        project = get_project(str(project_id))
    except LookupError as exc:
        raise HttpError(404, str(exc)) from exc
    return project_to_response(project)


@projects_router.post("/{project_id}/start", response={204: None})
def start_generation_route(request: HttpRequest, project_id: UUID):
    try:
        start_generation(str(project_id))
        run_generation_step.delay(str(project_id))
    except LookupError as exc:
        raise HttpError(404, str(exc)) from exc
    except InvalidStatusChangeException as exc:
        raise HttpError(400, str(exc)) from exc
    return 204, None
