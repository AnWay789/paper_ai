from datetime import datetime

from ninja import Schema

from ..models import ArticleProject


class DepthItemSchema(Schema):
    keyword: str
    count: int


class CreateProjectSchema(Schema):
    marker: str
    depth: list[DepthItemSchema]
    width: list[str]
    n_gramms: list[str]
    count_chapters: int
    about_author: str


class CreateProjectResponseSchema(Schema):
    id: str


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
    paper = project.article_paper
    return ProjectResponseSchema(
        id=str(project.id),
        marker=project.marker,
        depth=project.get_depth(),
        width=project.width,
        n_gramms=project.n_gramms,
        count_chapters=project.count_chapters,
        about_author=project.about_author,
        status=project.status,
        created_at=project.created_at,
        article_title=paper.article_title if paper else None,
        article_introduction=paper.article_introduction if paper else None,
        article_chapters_name=paper.article_chapters_name if paper else None,
        article_chapters_content=paper.article_chapters_contents if paper else None,
        final_article=paper.final_article if paper else None,
        problems=paper.problems if paper else None,
    )
