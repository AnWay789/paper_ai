from django.contrib import admin

# Register your models here.
from .models import ArticlePaperORM, ArticleProjectORM, PromtTemplateORM
@admin.register(ArticlePaperORM)
class ArticlePaperORMAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'article_title', 
        'created_at', 
        'article_introduction', 
        'article_chapters_name', 
        'article_chapters_contents', 
        'final_article', 
        'problems',
    ]

@admin.register(ArticleProjectORM)
class ArticleProjectORMAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'marker', 
        'status', 
        'created_at', 
        'article_paper',
        'depth', 
        'width', 
        'n_gramms', 
        'count_chapters', 
        'about_author', 
    ]

@admin.register(PromtTemplateORM)
class PromtTemplateORMAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'status',
        'template',
    ]
