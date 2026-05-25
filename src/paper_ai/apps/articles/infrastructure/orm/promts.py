import uuid

from django.db import models
from ...domain.value_objects.project_statuses import ProjectStatus

prompt_template_help_text = """
<br> Здесь пишется шаблон промпта для генерации. В шаблон можно использовать следующие переменные:
<br>
<br> - marker: маркер статьи (смысл статьи)
<br> - depth: глубина статьи (ключевые слова)
<br> - width: ширина статьи (доп ключевые слова)
<br> - n_gramms: n-граммы статьи 
<br> - count_chapters: количество глав статьи
<br> - about_author: о авторе статьи
<br> - chapter_index: номер текущей главы
<br><br> ! На момент заполнения шаблона переменные ниже могут еще не существовать, в этом случае будут пустые строки !
<br> - article_title: заголовок статьи 
<br> - article_introduction: введение статьи 
<br> - article_chapters_name: названия глав статьи (после шага generate_chapters_name)
<br> - article_chapters_content: содержимое глав статьи (после шага generate_chapters_content)
<br> - final_article: финальная статья (после шага merge)
<br> - problems: SEO-проблемы статьи (после шага merge)
<br><br> Подставлять значения переменных нужно в таком виде: текст {переменная} текст
"""

class PromtTemplateORM(models.Model):
    class Meta:
        app_label = "articles"
        verbose_name = "Шаблон промпта"
        verbose_name_plural = "Шаблоны промптов"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=255, choices=ProjectStatus.in_progress_choices())
    template = models.TextField(help_text=prompt_template_help_text)
