import re
from uuid import UUID

from django.http import HttpRequest, HttpResponse
from ninja import Router
from ninja.errors import HttpError

from ..exceptions.generation_ex import InvalidGenerationStepException
from ..exceptions.status_ex import InvalidStatusChangeException
from ..services.excel_import import RowError, parse_workbook
from ..services.generation import save_generation_estimate, start_generation
from ..exceptions.article_project_ex import ArticleProjectAlredyInProgressException
from ..services.project import (
    create_project,
    delete_project,
    get_project,
    list_llm_models,
    list_projects,
    update_project,
)
from ..tasks import run_generation_step
from .schemas import (
    BulkOperationResponseSchema,
    BulkProjectIdsSchema,
    CreateProjectResponseSchema,
    CreateProjectSchema,
    ImportProjectsResponseSchema,
    LlmModelSchema,
    ProjectListResponseSchema,
    ProjectResponseSchema,
    UpdateProjectSchema,
    project_to_list_item,
    project_to_response,
)

projects_router = Router(tags=["projects"])


def _slugify_filename(value: str) -> str:
    slug = re.sub(r"[^\w\-]+", "-", value, flags=re.UNICODE).strip("-")
    return slug[:80] or "article"


@projects_router.get("", response=ProjectListResponseSchema)
def list_projects_route(
    request: HttpRequest,
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
):
    items, total = list_projects(limit=limit, offset=offset, status=status)
    return ProjectListResponseSchema(
        items=[project_to_list_item(project) for project in items],
        total=total,
    )


@projects_router.get("/llm-models", response=list[LlmModelSchema])
def list_llm_models_route(request: HttpRequest):
    return [
        LlmModelSchema(id=model.id, model_name=model.model_name)
        for model in list_llm_models()
    ]


@projects_router.post("", response=CreateProjectResponseSchema)
def create_project_route(request: HttpRequest, body: CreateProjectSchema):
    try:
        project_id = create_project(
            marker=body.marker,
            depth=[(item.keyword, item.count) for item in body.depth],
            width=body.width,
            n_gramms=body.n_gramms,
            count_chapters=body.count_chapters,
            about_author=body.about_author,
            llm_model_id=body.llm_model_id,
        )
    except LookupError as exc:
        raise HttpError(404, str(exc)) from exc
    except Exception as exc:
        raise HttpError(400, str(exc)) from exc
    return CreateProjectResponseSchema(id=project_id)


@projects_router.post("/import", response=ImportProjectsResponseSchema)
def import_projects_route(request: HttpRequest):
    upload = request.FILES.get("file")
    if not upload:
        raise HttpError(400, "Файл не передан")
    if not upload.name or not upload.name.lower().endswith(".xlsx"):
        raise HttpError(400, "Ожидается файл .xlsx")

    llm_model_id_raw = request.POST.get("llm_model_id")
    llm_model_id = int(llm_model_id_raw) if llm_model_id_raw else None

    parsed_rows, import_errors = parse_workbook(upload.file)
    created = []
    for row_number, row in parsed_rows:
        try:
            project_id = create_project(
                marker=row.marker,
                depth=row.depth,
                width=row.width,
                n_gramms=row.n_gramms,
                count_chapters=row.count_chapters,
                about_author=row.about_author,
                llm_model_id=llm_model_id,
            )
            created.append({"id": project_id, "marker": row.marker})
        except Exception as exc:
            import_errors.append(RowError(row=row_number, message=str(exc)))

    return ImportProjectsResponseSchema(
        created=created,
        errors=[{"row": err.row, "message": err.message} for err in import_errors],
    )


@projects_router.post("/bulk/estimate", response=BulkOperationResponseSchema)
def bulk_estimate_route(request: HttpRequest, body: BulkProjectIdsSchema):
    ok: list[str] = []
    failed: list[dict[str, str]] = []
    for project_id in body.project_ids:
        try:
            save_generation_estimate(project_id)
            ok.append(project_id)
        except Exception as exc:
            failed.append({"id": project_id, "error": str(exc)})
    return BulkOperationResponseSchema(ok=ok, failed=failed)


@projects_router.post("/bulk/start", response=BulkOperationResponseSchema)
def bulk_start_route(request: HttpRequest, body: BulkProjectIdsSchema):
    ok: list[str] = []
    failed: list[dict[str, str]] = []
    for project_id in body.project_ids:
        try:
            start_generation(project_id)
            run_generation_step.delay(project_id)
            ok.append(project_id)
        except Exception as exc:
            failed.append({"id": project_id, "error": str(exc)})
    return BulkOperationResponseSchema(ok=ok, failed=failed)


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


@projects_router.put("/{project_id}", response=ProjectResponseSchema)
def update_project_route(request: HttpRequest, project_id: UUID, body: UpdateProjectSchema):
    try:
        project = update_project(
            str(project_id),
            marker=body.marker,
            depth=[(item.keyword, item.count) for item in body.depth],
            width=body.width,
            n_gramms=body.n_gramms,
            count_chapters=body.count_chapters,
            about_author=body.about_author,
            llm_model_id=body.llm_model_id,
        )
    except LookupError as exc:
        raise HttpError(404, str(exc)) from exc
    except ArticleProjectAlredyInProgressException as exc:
        raise HttpError(400, str(exc)) from exc
    except Exception as exc:
        raise HttpError(400, str(exc)) from exc
    return project_to_response(project)


@projects_router.get("/{project_id}/article.html")
def export_article_html_route(request: HttpRequest, project_id: UUID):
    try:
        project = get_project(str(project_id))
    except LookupError as exc:
        raise HttpError(404, str(exc)) from exc

    paper = project.article_paper
    if not paper or not paper.final_article:
        raise HttpError(404, "Статья ещё не сгенерирована")

    filename = f"{_slugify_filename(project.marker)}.html"
    response = HttpResponse(paper.final_article, content_type="text/html; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@projects_router.post("/{project_id}/estimate", response=ProjectResponseSchema)
def estimate_project_cost_route(request: HttpRequest, project_id: UUID):
    try:
        project = save_generation_estimate(str(project_id))
    except LookupError as exc:
        raise HttpError(404, str(exc)) from exc
    except InvalidGenerationStepException as exc:
        raise HttpError(400, str(exc)) from exc
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
    except InvalidGenerationStepException as exc:
        raise HttpError(400, str(exc)) from exc
    return 204, None
