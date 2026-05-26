import uuid

from django.db import models

from .exceptions.article_project_ex import ArticleProjectAlredyInProgressException
from .exceptions.atricle_paper_ex import (
    ArticlePaperChaptersContentDoesNotExist,
    ArticlePaperChaptersNameDoesNotExist,
    ArticlePaperDoesNotExist,
    ArticlePaperFinalArticleDoesNotExist,
    ArticlePaperIntroductionDoesNotExist,
    ArticlePaperTitleDoesNotExist,
)
from .exceptions.generation_ex import InvalidGenerationStepException
from .exceptions.status_ex import InvalidStatusChangeException
from .generation import (
    ALLOWED_STATUS_TRANSITIONS,
    ProjectStatus,
    can_start_generation,
    get_generation_step,
    in_progress_statuses,
    is_generation_step,
)
from .validation import validate_project_fields


PROMPT_TEMPLATE_HELP_TEXT = """
<br> Шаблон промпта. Переменные:
<br> marker, depth, width, n_gramms, count_chapters, about_author, chapter_index
<br> (опционально) article_title, article_introduction, article_chapters_name,
<br> article_chapters_content, final_article, problems
<br> Подстановка: текст {переменная} текст
"""


class ArticlePaper(models.Model):
    class Meta:
        app_label = "articles"
        db_table = "articles_articlepaperorm"
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article_title = models.TextField(null=True, blank=True)
    article_introduction = models.TextField(null=True, blank=True)
    article_chapters_name = models.JSONField(null=True, blank=True)
    article_chapters_contents = models.JSONField(null=True, blank=True)
    final_article = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    problems = models.JSONField(null=True, blank=True)

    def chapters_content_count(self) -> int:
        if not self.article_chapters_contents:
            return 0
        return len(self.article_chapters_contents)


class ArticleProject(models.Model):
    class Meta:
        app_label = "articles"
        db_table = "articles_articleprojectorm"
        verbose_name = "Проект статьи"
        verbose_name_plural = "Проекты статей"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    marker = models.TextField()
    depth = models.JSONField()
    width = models.JSONField()
    n_gramms = models.JSONField()
    count_chapters = models.IntegerField()
    about_author = models.TextField()
    status = models.TextField(db_index=True, choices=ProjectStatus.to_choice())
    created_at = models.DateTimeField(auto_now_add=True)
    article_paper = models.OneToOneField(
        ArticlePaper,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="project",
    )

    @property
    def status_enum(self) -> ProjectStatus:
        return ProjectStatus(self.status)

    def get_depth(self) -> list[tuple[str, int]]:
        return [(row[0], int(row[1])) for row in self.depth]

    def get_depth_by_text(self) -> str:
        return "".join(f'"{word}" count:{count}, ' for word, count in self.get_depth())

    def get_width_by_text(self) -> str:
        return "".join(f'"{word}", ' for word in self.width)

    def get_n_gramms_by_text(self) -> str:
        if not self.n_gramms:
            return "Нет n-грамм"
        return "".join(f'"{n_gramm}", ' for n_gramm in self.n_gramms)

    def _ensure_not_in_progress(self) -> None:
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException("Проект статьи уже в процессе")

    def is_in_progress(self) -> bool:
        return self.status_enum in in_progress_statuses

    def is_completed(self) -> bool:
        return self.status_enum == ProjectStatus.COMPLETED

    def change_status(self, new_status: ProjectStatus) -> None:
        allowed = ALLOWED_STATUS_TRANSITIONS.get(self.status_enum, [])
        if new_status not in allowed:
            raise InvalidStatusChangeException(
                f"Недопустимый переход из статуса {self.status_enum} в статус {new_status}"
            )
        self.status = new_status.value

    def get_next_status(self) -> ProjectStatus | None:
        if is_generation_step(self.status_enum):
            return get_generation_step(self.status_enum).next_status
        return None

    def start_generation(self) -> None:
        if not can_start_generation(self.status_enum):
            raise InvalidStatusChangeException(
                f"Нельзя запустить генерацию из статуса {self.status_enum}"
            )
        self.change_status(ProjectStatus.GENERATE_TITLE)

    def apply_generation_step(self, response: str | list[str]) -> None:
        if not is_generation_step(self.status_enum):
            raise InvalidGenerationStepException(
                f"Статус {self.status_enum} не является шагом генерации"
            )
        step = get_generation_step(self.status_enum)
        step.apply(self, response)
        step.advance(self)

    def to_error_status(self) -> None:
        self.change_status(ProjectStatus.ERROR)

    def get_count_chapters_content(self) -> int:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist("Статья еще не создана")
        return self.article_paper.chapters_content_count()

    def get_article_title(self) -> str:
        paper = self._require_paper()
        if not paper.article_title:
            raise ArticlePaperTitleDoesNotExist("Заголовок статьи еще не создан")
        return paper.article_title

    def get_article_introduction(self) -> str:
        paper = self._require_paper()
        if not paper.article_introduction:
            raise ArticlePaperIntroductionDoesNotExist("Введение статьи еще не создано")
        return paper.article_introduction

    def get_article_chapters_name(self) -> list[str]:
        paper = self._require_paper()
        if not paper.article_chapters_name:
            raise ArticlePaperChaptersNameDoesNotExist("Названия глав еще не созданы")
        return paper.article_chapters_name

    def get_article_chapters_name_by_text(self) -> str:
        return "".join(f'"{name}",\n' for name in self.get_article_chapters_name())

    def get_article_chapters_contents(self) -> list[str]:
        paper = self._require_paper()
        if not paper.article_chapters_contents:
            raise ArticlePaperChaptersContentDoesNotExist("Содержание глав еще не создано")
        return paper.article_chapters_contents

    def get_article_chapters_contents_by_text(self) -> str:
        return "".join(f'"{content}",\n' for content in self.get_article_chapters_contents())

    def get_final_article(self) -> str:
        paper = self._require_paper()
        if not paper.final_article:
            raise ArticlePaperFinalArticleDoesNotExist("Финальная статья еще не создана")
        return paper.final_article

    def get_problems(self) -> list[str]:
        paper = self._require_paper()
        return paper.problems or []

    def get_problems_by_text(self) -> str:
        problems = self.get_problems()
        return "Нет проблем" if not problems else "\n".join(problems)

    def set_article_title(self, title: str) -> None:
        self._require_paper().article_title = title

    def set_article_introduction(self, introduction: str) -> None:
        self._require_paper().article_introduction = introduction

    def set_article_chapters_name(self, names: list[str]) -> None:
        self._require_paper().article_chapters_name = names

    def add_article_chapters_content(self, content: str) -> None:
        paper = self._require_paper()
        if paper.article_chapters_contents is None:
            paper.article_chapters_contents = []
        paper.article_chapters_contents.append(content)

    def set_final_article(self, final_article: str) -> None:
        self._require_paper().final_article = final_article

    def set_problems(self, problems: list[str]) -> None:
        self._require_paper().problems = problems

    def _require_paper(self) -> ArticlePaper:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist("Статья еще не создана")
        return self.article_paper

    @classmethod
    def create_project(
        cls,
        *,
        marker: str,
        depth: list[tuple[str, int]],
        width: list[str],
        n_gramms: list[str],
        count_chapters: int,
        about_author: str,
    ) -> "ArticleProject":
        validate_project_fields(
            marker=marker,
            depth=depth,
            width=width,
            n_gramms=n_gramms,
            count_chapters=count_chapters,
            about_author=about_author,
        )
        paper = ArticlePaper.objects.create()
        return cls.objects.create(
            marker=marker,
            depth=[[word, count] for word, count in depth],
            width=width,
            n_gramms=n_gramms,
            count_chapters=count_chapters,
            about_author=about_author,
            status=ProjectStatus.NEW.value,
            article_paper=paper,
        )


class PromtTemplate(models.Model):
    class Meta:
        app_label = "articles"
        db_table = "articles_promttemplateorm"
        verbose_name = "Шаблон промпта"
        verbose_name_plural = "Шаблоны промптов"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=255,
        choices=ProjectStatus.in_progress_choices(),
    )
    template = models.TextField(help_text=PROMPT_TEMPLATE_HELP_TEXT)
