from django.db import transaction

from ...application.adapters.article_project_rep import ArticleProjectRepository
from ...infrastructure.orm.article_project import ArticleProjectORM
from ...domain.entities.article_project import ArticleProject
from ...infrastructure.mappers.article_project_mapper import to_domain as to_domain_article_project
from ...infrastructure.mappers.article_project_mapper import to_orm as to_orm_article_project
from ...infrastructure.mappers.article_paper_mapper import to_orm as to_orm_article_paper
from ..orm.article_paper import ArticlePaperORM
from ...infrastructure.exceptions.article_project_ex import (
    ArticleProjectNotFoundException,
)
class ArticleProjectORMRepository(ArticleProjectRepository):
    
    def get_by_id(self, article_project_id: str) -> ArticleProject:
        article_project_orm = ArticleProjectORM.objects.get(id=article_project_id)
        return to_domain_article_project(article_project_orm)

    @transaction.atomic
    def save(self, article_project: ArticleProject) -> None:
        paper = article_project.get_article_paper()
        paper_pk = None
        if paper is not None:
            paper_orm = to_orm_article_paper(paper)
            ArticlePaperORM.objects.update_or_create(
                id=paper_orm.id,
                defaults={
                    "article_title": paper_orm.article_title,
                    "article_introduction": paper_orm.article_introduction,
                    "article_chapters_name": paper_orm.article_chapters_name,
                    "article_chapters_contents": paper_orm.article_chapters_contents,
                    "final_article": paper_orm.final_article,
                    "problems": paper_orm.problems,
                },
            )
            paper_pk = paper_orm.id

        project_orm = to_orm_article_project(article_project)
        ArticleProjectORM.objects.update_or_create(
            id=project_orm.id,
            defaults={
                "marker": project_orm.marker,
                "depth": project_orm.depth,
                "width": project_orm.width,
                "n_gramms": project_orm.n_gramms,
                "count_chapters": project_orm.count_chapters,
                "about_author": project_orm.about_author,
                "status": project_orm.status,
                "created_at": project_orm.created_at,
                "article_paper_id": paper_pk,
            },
        )

    @transaction.atomic
    def delete(self, article_project_id: str) -> None:
        try:
            article_project_orm = ArticleProjectORM.objects.get(id=article_project_id)
        except ArticleProjectORM.DoesNotExist:
            raise ArticleProjectNotFoundException(f"Проект статьи с id {article_project_id} не найден")
        if article_project_orm.article_paper is not None:
            article_project_orm.article_paper.delete()
        article_project_orm.delete()
