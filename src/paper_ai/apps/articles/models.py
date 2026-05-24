"""
Django загружает только models.py при старте app.
ORM-модели лежат в infrastructure — импортируем их здесь, чтобы
makemigrations / admin / ORM их увидели.
"""

from .infrastructure.orm.article_paper import ArticlePaperORM
from .infrastructure.orm.article_project import ArticleProjectORM
from .infrastructure.orm.promts import PromtTemplateORM

__all__ = [
    "ArticlePaperORM",
    "ArticleProjectORM",
    "PromtTemplateORM",
]
