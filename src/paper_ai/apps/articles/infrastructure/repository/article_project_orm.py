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
        article_project_orm = to_orm_article_project(article_project)
        paper_orm = article_project_orm.article_paper
        if paper_orm is not None:
            paper_orm.save()
        article_project_orm.save()

    @transaction.atomic
    def delete(self, article_project_id: str) -> None:
        try:
            article_project_orm = ArticleProjectORM.objects.get(id=article_project_id)
        except ArticleProjectORM.DoesNotExist:
            raise ArticleProjectNotFoundException(f"Проект статьи с id {article_project_id} не найден")
        if article_project_orm.article_paper is not None:
            article_project_orm.article_paper.delete()
        article_project_orm.delete()
