from django.contrib import admin

from .models import ArticlePaper, ArticleProject, PromtTemplate


@admin.register(ArticlePaper)
class ArticlePaperAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "article_title",
        "created_at",
        "article_introduction",
        "article_chapters_name",
        "article_chapters_contents",
        "final_article",
        "problems",
    ]


@admin.register(ArticleProject)
class ArticleProjectAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "marker",
        "status",
        "created_at",
        "article_paper",
        "depth",
        "width",
        "n_gramms",
        "count_chapters",
        "about_author",
    ]


@admin.register(PromtTemplate)
class PromtTemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "template"]
