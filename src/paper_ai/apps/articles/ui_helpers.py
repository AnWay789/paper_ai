from .generation.policies import can_start_generation
from .generation.statuses import ProjectStatus, in_progress_statuses
from .models import ArticleProject

STATUS_LABELS = {
    ProjectStatus.NEW.value: "Новый",
    ProjectStatus.NOT_STARTED.value: "Не запущен",
    ProjectStatus.STARTED.value: "Запущен",
    ProjectStatus.GENERATE_TITLE.value: "Заголовок",
    ProjectStatus.GENERATE_INTRODUCTION.value: "Введение",
    ProjectStatus.GENERATE_CHAPTERS_NAME.value: "Главы",
    ProjectStatus.GENERATE_CHAPTERS_CONTENT.value: "Содержание",
    ProjectStatus.MERGE_ARTICLE.value: "Сборка",
    ProjectStatus.SEO_FIX.value: "SEO",
    ProjectStatus.COMPLETED.value: "Готово",
    ProjectStatus.CANCELLED.value: "Отменён",
    ProjectStatus.ERROR.value: "Ошибка",
}

STATUS_BADGE_CLASS = {
    ProjectStatus.NEW.value: "badge-muted",
    ProjectStatus.NOT_STARTED.value: "badge-muted",
    ProjectStatus.STARTED.value: "badge-progress",
    ProjectStatus.GENERATE_TITLE.value: "badge-progress",
    ProjectStatus.GENERATE_INTRODUCTION.value: "badge-progress",
    ProjectStatus.GENERATE_CHAPTERS_NAME.value: "badge-progress",
    ProjectStatus.GENERATE_CHAPTERS_CONTENT.value: "badge-progress",
    ProjectStatus.MERGE_ARTICLE.value: "badge-progress",
    ProjectStatus.SEO_FIX.value: "badge-progress",
    ProjectStatus.COMPLETED.value: "badge-success",
    ProjectStatus.CANCELLED.value: "badge-danger",
    ProjectStatus.ERROR.value: "badge-danger",
}


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status)


def status_badge_class(status: str) -> str:
    return STATUS_BADGE_CLASS.get(status, "badge-muted")


def project_can_start(project: ArticleProject) -> bool:
    try:
        return can_start_generation(ProjectStatus.parse(project.status))
    except ValueError:
        return False


def has_in_progress_projects(projects: list[ArticleProject]) -> bool:
    in_progress_values = {status.value for status in in_progress_statuses}
    return any(project.status in in_progress_values for project in projects)


def project_is_in_progress(project: ArticleProject) -> bool:
    return project.status in {status.value for status in in_progress_statuses}


def project_can_edit(project: ArticleProject) -> bool:
    return not project_is_in_progress(project)
