from ...domain.entities.article_project import ArticleProject
from ..orm.article_project import ArticleProjectORM
from ...domain.value_objects.project_statuses import ProjectStatus

from .article_paper_mapper import to_domain as to_domain_article_paper
from .article_paper_mapper import to_orm as to_orm_article_paper

def to_domain(article_project_orm: ArticleProjectORM) -> ArticleProject:
    return ArticleProject.reconstitute(
        id=str(article_project_orm.id),
        marker=article_project_orm.marker,
        depth=[(keyword[0], keyword[1]) for keyword in article_project_orm.depth],
        width=article_project_orm.width,
        n_gramms=article_project_orm.n_gramms,
        count_chapters=article_project_orm.count_chapters,
        about_author=article_project_orm.about_author,
        status=ProjectStatus(article_project_orm.status),
        created_at=article_project_orm.created_at,
        article_paper=to_domain_article_paper(article_project_orm.article_paper),
    )

def to_orm(article_project: ArticleProject) -> ArticleProjectORM:
    return ArticleProjectORM(
        id=article_project.get_id(),
        marker=article_project.get_marker(),
        depth=article_project.get_depth_by_json(),
        width=article_project.get_width(),
        n_gramms=article_project.get_n_gramms(),
        count_chapters=article_project.get_count_chapters(),
        about_author=article_project.get_about_author(),
        status=article_project.get_status().value,
        created_at=article_project.get_created_at(),
        article_paper=to_orm_article_paper(article_project.get_article_paper()),
    )
