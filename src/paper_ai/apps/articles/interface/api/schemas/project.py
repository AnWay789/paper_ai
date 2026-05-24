from datetime import datetime

from ninja import Schema

from ....domain.entities.article_project import ArticleProject


class ProjectResponseSchema(Schema):
    id: str
    marker: str
    depth: list[tuple[str, int]]
    width: list[str]
    n_gramms: list[str]
    count_chapters: int
    about_author: str
    status: str
    created_at: datetime
    article_title: str | None = None
    article_introduction: str | None = None
    article_chapters_name: list[str] | None = None
    article_chapters_content: list[str] | None = None
    final_article: str | None = None
    problems: list[str] | None = None


def project_to_response(project: ArticleProject) -> ProjectResponseSchema:
    paper = project.get_article_paper()
    return ProjectResponseSchema(
        id=project.get_id(),
        marker=project.get_marker(),
        depth=project.get_depth(),
        width=project.get_width(),
        n_gramms=project.get_n_gramms(),
        count_chapters=project.get_count_chapters(),
        about_author=project.get_about_author(),
        status=project.get_status().value,
        created_at=project.created_at,
        article_title=paper.get_article_title() if paper else None,
        article_introduction=paper.get_article_introduction() if paper else None,
        article_chapters_name=paper.get_article_chapters_name() if paper else None,
        article_chapters_content=paper.get_article_chapters_contents() if paper else None,
        final_article=paper.get_final_article() if paper else None,
        problems=paper.get_problems() if paper else None,
    )
