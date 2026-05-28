from datetime import datetime
from decimal import Decimal

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
    llm_model_id: int | None = None


class UpdateProjectSchema(CreateProjectSchema):
    pass


class CreateProjectResponseSchema(Schema):
    id: str


class ProjectListItemSchema(Schema):
    id: str
    marker: str
    status: str
    created_at: datetime
    estimated_cost_total: Decimal | None = None
    cost_total: Decimal | None = None


class ProjectListResponseSchema(Schema):
    items: list[ProjectListItemSchema]
    total: int


class LlmModelSchema(Schema):
    id: int
    model_name: str


class ImportCreatedItemSchema(Schema):
    id: str
    marker: str


class ImportErrorItemSchema(Schema):
    row: int
    message: str


class ImportProjectsResponseSchema(Schema):
    created: list[ImportCreatedItemSchema]
    errors: list[ImportErrorItemSchema]


class BulkProjectIdsSchema(Schema):
    project_ids: list[str]


class BulkFailedItemSchema(Schema):
    id: str
    error: str


class BulkOperationResponseSchema(Schema):
    ok: list[str]
    failed: list[BulkFailedItemSchema]


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
    llm_model_id: int | None = None
    estimated_cost_input: Decimal | None = None
    estimated_cost_output: Decimal | None = None
    estimated_cost_total: Decimal | None = None
    cost_input: Decimal | None = None
    cost_output: Decimal | None = None
    cost_total: Decimal | None = None
    article_title: str | None = None
    article_introduction: str | None = None
    article_chapters_name: list[str] | None = None
    article_chapters_content: list[str] | None = None
    final_article: str | None = None
    problems: list[str] | None = None


def project_to_list_item(project: ArticleProject) -> ProjectListItemSchema:
    return ProjectListItemSchema(
        id=str(project.id),
        marker=project.marker,
        status=project.status,
        created_at=project.created_at,
        estimated_cost_total=project.estimated_cost_total,
        cost_total=project.cost_total,
    )


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
        llm_model_id=project.llm_model_id,
        estimated_cost_input=project.estimated_cost_input,
        estimated_cost_output=project.estimated_cost_output,
        estimated_cost_total=project.estimated_cost_total,
        cost_input=project.cost_input,
        cost_output=project.cost_output,
        cost_total=project.cost_total,
        article_title=paper.article_title if paper else None,
        article_introduction=paper.article_introduction if paper else None,
        article_chapters_name=paper.article_chapters_name if paper else None,
        article_chapters_content=paper.article_chapters_contents if paper else None,
        final_article=paper.final_article if paper else None,
        problems=paper.problems if paper else None,
    )
