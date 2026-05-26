from django.core.exceptions import ObjectDoesNotExist

from ..models import ArticleProject


def create_project(
    *,
    marker: str,
    depth: list[tuple[str, int]],
    width: list[str],
    n_gramms: list[str],
    count_chapters: int,
    about_author: str,
) -> str:
    project = ArticleProject.create_project(
        marker=marker,
        depth=depth,
        width=width,
        n_gramms=n_gramms,
        count_chapters=count_chapters,
        about_author=about_author,
    )
    return str(project.id)


def get_project(project_id: str) -> ArticleProject:
    try:
        return ArticleProject.objects.select_related("article_paper").get(pk=project_id)
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
