from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import ArticleProject
from .services.excel_import import parse_list, parse_workbook
from .services.generation import save_generation_estimate, start_generation
from .services.project import (
    create_project,
    delete_project,
    get_project,
    list_llm_models,
    list_projects,
    update_project,
)
from .tasks import run_generation_step
from .ui_helpers import (
    has_in_progress_projects,
    project_can_edit,
    project_can_start,
    project_is_in_progress,
)


def _parse_text_list(value: str) -> list[str]:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if len(lines) <= 1 and "," in value:
        return parse_list(value)
    return lines


def _projects_context(request: HttpRequest, *, limit: int = 100) -> dict:
    projects, total = list_projects(limit=limit, offset=0)
    return {
        "projects": projects,
        "total": total,
        "has_in_progress": has_in_progress_projects(projects),
        "llm_models": list_llm_models(),
        "project_can_start": project_can_start,
        "project_can_edit": project_can_edit,
    }


@require_GET
def dashboard(request: HttpRequest) -> HttpResponse:
    context = _projects_context(request)
    return render(request, "articles/dashboard.html", context)


@require_GET
def projects_table_partial(request: HttpRequest) -> HttpResponse:
    context = _projects_context(request)
    return render(request, "articles/partials/projects_table.html", context)


def _depth_rows_for_form(depth: list[tuple[str, int]] | None = None) -> list[dict[str, str | int]]:
    if not depth:
        return [{"keyword": "", "count": 1}]
    return [{"keyword": keyword, "count": count} for keyword, count in depth]


def _project_to_form_data(project: ArticleProject) -> dict:
    return {
        "marker": project.marker,
        "about_author": project.about_author,
        "count_chapters": str(project.count_chapters),
        "llm_model_id": str(project.llm_model_id) if project.llm_model_id else "",
        "width": ", ".join(project.width),
        "n_gramms": ", ".join(project.n_gramms),
        "depth": project.get_depth(),
    }


@dataclass
class ParsedProjectForm:
    marker: str
    about_author: str
    count_chapters: int
    llm_model_id: int | None
    width: list[str]
    n_gramms: list[str]
    depth: list[tuple[str, int]]


@dataclass
class ProjectFormParseError:
    form_data: dict
    message: str


def _parse_project_post(request: HttpRequest) -> ParsedProjectForm | ProjectFormParseError:
    marker = request.POST.get("marker", "").strip()
    about_author = request.POST.get("about_author", "").strip()
    count_chapters_raw = request.POST.get("count_chapters", "").strip()
    llm_model_id_raw = request.POST.get("llm_model_id", "").strip()
    width_raw = request.POST.get("width", "")
    n_gramms_raw = request.POST.get("n_gramms", "")

    keywords = request.POST.getlist("depth_keyword")
    counts = request.POST.getlist("depth_count")
    depth: list[tuple[str, int]] = []
    for keyword, count_raw in zip(keywords, counts, strict=False):
        keyword = keyword.strip()
        if not keyword:
            continue
        try:
            depth.append((keyword, int(count_raw)))
        except (TypeError, ValueError):
            form_data = {
                "marker": marker,
                "about_author": about_author,
                "count_chapters": count_chapters_raw,
                "llm_model_id": llm_model_id_raw,
                "width": width_raw,
                "n_gramms": n_gramms_raw,
                "depth": depth,
            }
            return ProjectFormParseError(
                form_data=form_data,
                message=f"Некорректное количество для «{keyword}»",
            )

    form_data = {
        "marker": marker,
        "about_author": about_author,
        "count_chapters": count_chapters_raw,
        "llm_model_id": llm_model_id_raw,
        "width": width_raw,
        "n_gramms": n_gramms_raw,
        "depth": depth,
    }

    try:
        count_chapters = int(count_chapters_raw)
        llm_model_id = int(llm_model_id_raw) if llm_model_id_raw else None
    except ValueError:
        return ProjectFormParseError(
            form_data=form_data,
            message="Укажите корректное количество разделов",
        )

    return ParsedProjectForm(
        marker=marker,
        about_author=about_author,
        count_chapters=count_chapters,
        llm_model_id=llm_model_id,
        width=_parse_text_list(width_raw),
        n_gramms=_parse_text_list(n_gramms_raw),
        depth=depth,
    )


def _render_project_form(
    request: HttpRequest,
    *,
    form_data: dict,
    project: ArticleProject | None = None,
) -> HttpResponse:
    return render(
        request,
        "articles/project_form.html",
        {
            "llm_models": list_llm_models(),
            "form_data": form_data,
            "depth_rows": _depth_rows_for_form(form_data.get("depth")),
            "project": project,
            "is_edit": project is not None,
        },
    )


@require_http_methods(["GET", "POST"])
def project_create(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _render_project_form(request, form_data={})

    parsed = _parse_project_post(request)
    if isinstance(parsed, ProjectFormParseError):
        messages.error(request, parsed.message)
        return _render_project_form(request, form_data=parsed.form_data)

    try:
        project_id = create_project(
            marker=parsed.marker,
            depth=parsed.depth,
            width=parsed.width,
            n_gramms=parsed.n_gramms,
            count_chapters=parsed.count_chapters,
            about_author=parsed.about_author,
            llm_model_id=parsed.llm_model_id,
        )
    except Exception as exc:
        messages.error(request, str(exc))
        return _render_project_form(
            request,
            form_data={
                "marker": parsed.marker,
                "about_author": parsed.about_author,
                "count_chapters": str(parsed.count_chapters),
                "llm_model_id": str(parsed.llm_model_id or ""),
                "width": request.POST.get("width", ""),
                "n_gramms": request.POST.get("n_gramms", ""),
                "depth": parsed.depth,
            },
        )

    messages.success(request, "Проект создан")
    return redirect("articles:project_detail", project_id=project_id)


@require_http_methods(["GET", "POST"])
def project_edit(request: HttpRequest, project_id: UUID) -> HttpResponse:
    try:
        project = get_project(str(project_id))
    except LookupError:
        messages.error(request, "Проект не найден")
        return redirect("articles:dashboard")

    if not project_can_edit(project):
        messages.error(request, "Нельзя редактировать проект во время генерации")
        return redirect("articles:project_detail", project_id=project_id)

    if request.method == "GET":
        return _render_project_form(request, form_data=_project_to_form_data(project), project=project)

    parsed = _parse_project_post(request)
    if isinstance(parsed, ProjectFormParseError):
        messages.error(request, parsed.message)
        return _render_project_form(request, form_data=parsed.form_data, project=project)

    try:
        update_project(
            str(project_id),
            marker=parsed.marker,
            depth=parsed.depth,
            width=parsed.width,
            n_gramms=parsed.n_gramms,
            count_chapters=parsed.count_chapters,
            about_author=parsed.about_author,
            llm_model_id=parsed.llm_model_id,
        )
    except Exception as exc:
        messages.error(request, str(exc))
        return _render_project_form(
            request,
            form_data={
                "marker": parsed.marker,
                "about_author": parsed.about_author,
                "count_chapters": str(parsed.count_chapters),
                "llm_model_id": str(parsed.llm_model_id or ""),
                "width": request.POST.get("width", ""),
                "n_gramms": request.POST.get("n_gramms", ""),
                "depth": parsed.depth,
            },
            project=project,
        )

    messages.success(request, "Проект сохранён")
    return redirect("articles:project_detail", project_id=project_id)


@require_POST
def project_import(request: HttpRequest) -> HttpResponse:
    upload = request.FILES.get("file")
    if not upload:
        messages.error(request, "Выберите файл Excel (.xlsx)")
        return redirect("articles:dashboard")

    llm_model_id_raw = request.POST.get("llm_model_id", "").strip()
    llm_model_id = int(llm_model_id_raw) if llm_model_id_raw else None

    parsed_rows, import_errors = parse_workbook(upload.file)
    created_count = 0
    for row_number, row in parsed_rows:
        try:
            create_project(
                marker=row.marker,
                depth=row.depth,
                width=row.width,
                n_gramms=row.n_gramms,
                count_chapters=row.count_chapters,
                about_author=row.about_author,
                llm_model_id=llm_model_id,
            )
            created_count += 1
        except Exception as exc:
            from .services.excel_import import RowError

            import_errors.append(RowError(row=row_number, message=str(exc)))

    if created_count:
        messages.success(request, f"Импортировано проектов: {created_count}")
    for err in import_errors:
        messages.warning(request, f"Строка {err.row}: {err.message}")
    if not created_count and not import_errors:
        messages.info(request, "В файле нет данных для импорта")
    return redirect("articles:dashboard")


@require_POST
def bulk_estimate(request: HttpRequest) -> HttpResponse:
    project_ids = request.POST.getlist("project_ids")
    ok = 0
    for project_id in project_ids:
        try:
            save_generation_estimate(project_id)
            ok += 1
        except Exception as exc:
            messages.warning(request, f"{project_id}: {exc}")
    if ok:
        messages.success(request, f"Смета рассчитана для {ok} проект(ов)")
    return redirect("articles:dashboard")


@require_POST
def bulk_start(request: HttpRequest) -> HttpResponse:
    project_ids = request.POST.getlist("project_ids")
    ok = 0
    for project_id in project_ids:
        try:
            start_generation(project_id)
            run_generation_step.delay(project_id)
            ok += 1
        except Exception as exc:
            messages.warning(request, f"{project_id}: {exc}")
    if ok:
        messages.success(request, f"Генерация запущена для {ok} проект(ов)")
    return redirect("articles:dashboard")


@require_GET
def project_detail(request: HttpRequest, project_id: UUID) -> HttpResponse:
    try:
        project = get_project(str(project_id))
    except LookupError:
        messages.error(request, "Проект не найден")
        return redirect("articles:dashboard")

    return render(
        request,
        "articles/project_detail.html",
        {
            "project": project,
            "can_start": project_can_start(project),
            "can_edit": project_can_edit(project),
            "is_in_progress": project_is_in_progress(project),
        },
    )


@require_POST
def project_estimate(request: HttpRequest, project_id: UUID) -> HttpResponse:
    try:
        save_generation_estimate(str(project_id))
        messages.success(request, "Смета обновлена")
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect("articles:project_detail", project_id=project_id)


@require_POST
def project_start(request: HttpRequest, project_id: UUID) -> HttpResponse:
    try:
        start_generation(str(project_id))
        run_generation_step.delay(str(project_id))
        messages.success(request, "Генерация запущена")
    except Exception as exc:
        messages.error(request, str(exc))
    return redirect("articles:project_detail", project_id=project_id)


@require_POST
def project_delete(request: HttpRequest, project_id: UUID) -> HttpResponse:
    try:
        delete_project(str(project_id))
        messages.success(request, "Проект удалён")
        return redirect("articles:dashboard")
    except Exception as exc:
        messages.error(request, str(exc))
        return redirect("articles:project_detail", project_id=project_id)
