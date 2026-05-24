from uuid import UUID

from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from ....domain.exceptions.generation_ex import GenerationException
from ....domain.exceptions.status_ex import InvalidStatusChangeException
from ....infrastructure.exceptions.article_project_ex import ArticleProjectNotFoundException
from ..dependencies import (
    get_article_project_repository,
    get_create_project_use_case,
    get_run_step_generation_use_case,
    get_start_generation_use_case,
    get_delete_project_use_case,
)
from ..schemas.create_project import CreateProjectResponseSchema, CreateProjectSchema
from ..schemas.project import ProjectResponseSchema, project_to_response

projects_router = Router(tags=["projects"])


@projects_router.post("", response=CreateProjectResponseSchema)
def create_project(request: HttpRequest, body: CreateProjectSchema):
    project_id = get_create_project_use_case().execute(body.to_dto())
    return CreateProjectResponseSchema(id=project_id)

@projects_router.delete("/{project_id}", response={204: None})
def delete_project(request: HttpRequest, project_id: UUID):
    try:
        get_delete_project_use_case().execute(str(project_id))
    except ArticleProjectNotFoundException as exc:
        raise HttpError(404, str(exc)) from exc
    return 204, None

@projects_router.get("/{project_id}", response=ProjectResponseSchema)
def get_project(request: HttpRequest, project_id: UUID):
    try:
        project = get_article_project_repository().get_by_id(str(project_id))
    except Exception as exc:
        raise HttpError(404, "Проект не найден") from exc
    return project_to_response(project)


@projects_router.post("/{project_id}/start", response={204: None})
def start_generation(request: HttpRequest, project_id: UUID):
    try:
        get_start_generation_use_case().execute(str(project_id))
    except ArticleProjectNotFoundException as exc:
        raise HttpError(404, str(exc)) from exc
    except InvalidStatusChangeException as exc:
        raise HttpError(400, str(exc)) from exc
    return 204, None

