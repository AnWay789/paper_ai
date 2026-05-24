from django.db import models

class ArticlePaperORM(models.Model):
    class Meta:
        app_label = "articles"

    id = models.UUIDField(primary_key=True, editable=False)
    article_title = models.TextField(null=True, blank=True)
    article_introduction = models.TextField(null=True, blank=True)
    article_chapters_name = models.JSONField(null=True, blank=True)
    article_chapters_contents = models.JSONField(null=True, blank=True)
    final_article = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
