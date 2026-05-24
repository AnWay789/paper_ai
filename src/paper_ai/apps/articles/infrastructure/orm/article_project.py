from django.db import models
from .article_paper import ArticlePaperORM
from ...domain.value_objects.project_statuses import ProjectStatus

class ArticleProjectORM(models.Model):
    class Meta:
        app_label = "articles"
        verbose_name = "Проект статьи"
        verbose_name_plural = "Проекты статей"

    id = models.UUIDField(primary_key=True, editable=False)
    marker = models.TextField()
    depth = models.JSONField()
    width = models.JSONField()
    n_gramms = models.JSONField()
    count_chapters = models.IntegerField()
    about_author = models.TextField()
    status = models.TextField(db_index=True, choices=ProjectStatus.to_choice())
    created_at = models.DateTimeField(auto_now_add=True)
    article_paper = models.OneToOneField(ArticlePaperORM, 
                                        on_delete=models.CASCADE, 
                                        null=True, blank=True)

