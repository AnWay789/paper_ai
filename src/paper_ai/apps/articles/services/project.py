from django.core.exceptions import ObjectDoesNotExist

from ..exceptions.article_project_ex import ArticleProjectAlredyInProgressException
from ..models import ArticleProject, LLMModels
from ..validation import validate_project_fields


def list_projects(
    *,
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
) -> tuple[list[ArticleProject], int]:
    queryset = ArticleProject.objects.select_related("article_paper", "llm_model").order_by(
        "-created_at"
    )
    if status:
        queryset = queryset.filter(status=status)
    total = queryset.count()
    items = list(queryset[offset : offset + limit])
    return items, total


def list_llm_models() -> list[LLMModels]:
    return list(LLMModels.objects.order_by("model_name"))


def build_llm_model_lookup() -> dict[str, int]:
    """Ключ — model_name или model_system_name в нижнем регистре, значение — id."""
    lookup: dict[str, int] = {}
    for model in LLMModels.objects.all():
        lookup[model.model_name.strip().lower()] = model.id
        lookup[model.model_system_name.strip().lower()] = model.id
    return lookup


def parse_llm_model_id_from_request(raw: str | None) -> int | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    return int(text)


def resolve_llm_model_id(raw: str, lookup: dict[str, int] | None = None) -> int | None:
    text = raw.strip()
    if not text:
        return None
    if lookup is None:
        lookup = build_llm_model_lookup()
    if text.isdigit():
        model_id = int(text)
        if LLMModels.objects.filter(pk=model_id).exists():
            return model_id
        raise LookupError(f"LLM-модель с id {model_id} не найдена")
    key = text.lower()
    if key in lookup:
        return lookup[key]
    raise LookupError(
        f"Модель «{raw}» не найдена. Укажите название из справочника LLM (model_name)."
    )


def create_project(
    *,
    marker: str,
    depth: list[tuple[str, int]],
    width: list[str],
    n_gramms: list[str],
    count_chapters: int,
    about_author: str,
    llm_model_id: int | None = None,
) -> str:
    project = ArticleProject.create_project(
        marker=marker,
        depth=depth,
        width=width,
        n_gramms=n_gramms,
        count_chapters=count_chapters,
        about_author=about_author,
        llm_model=_resolve_llm_model(llm_model_id),
    )
    return str(project.id)


def _resolve_llm_model(llm_model_id: int | None) -> LLMModels | None:
    if llm_model_id is None:
        return None
    try:
        return LLMModels.objects.get(pk=llm_model_id)
    except ObjectDoesNotExist as exc:
        raise LookupError(f"LLM-модель с id {llm_model_id} не найдена") from exc


def update_project(
    project_id: str,
    *,
    marker: str,
    depth: list[tuple[str, int]],
    width: list[str],
    n_gramms: list[str],
    count_chapters: int,
    about_author: str,
    llm_model_id: int | None = None,
) -> ArticleProject:
    project = get_project(project_id)
    if project.is_in_progress():
        raise ArticleProjectAlredyInProgressException(
            "Нельзя редактировать проект во время генерации"
        )

    validate_project_fields(
        marker=marker,
        depth=depth,
        width=width,
        n_gramms=n_gramms,
        count_chapters=count_chapters,
        about_author=about_author,
    )

    project.marker = marker
    project.depth = [[word, count] for word, count in depth]
    project.width = width
    project.n_gramms = n_gramms
    project.count_chapters = count_chapters
    project.about_author = about_author
    project.llm_model = _resolve_llm_model(llm_model_id)
    project.save(
        update_fields=[
            "marker",
            "depth",
            "width",
            "n_gramms",
            "count_chapters",
            "about_author",
            "llm_model",
        ]
    )
    return project


def get_project(project_id: str) -> ArticleProject:
    try:
        return ArticleProject.objects.select_related(
            "article_paper",
            "llm_model",
        ).get(pk=project_id)
    except ObjectDoesNotExist as exc:
        raise LookupError(f"Проект статьи с id {project_id} не найден") from exc


def delete_project(project_id: str) -> None:
    try:
        project = ArticleProject.objects.select_related("article_paper").get(pk=project_id)
    except ObjectDoesNotExist as exc:
        raise LookupError(f"Проект статьи с id {project_id} не найден") from exc
    if project.article_paper_id:
        project.article_paper.delete()
    project.delete()
