from enum import Enum

class ProjectStatus(Enum):
    NEW = "new" # только для новых проектов
    NOT_STARTED = "not_started" # не запущеная генерация
    STARTED = "started" # запущена генерация
    GENERATE_TITLE = "generate_title" # генерация заголовка
    GENERATE_INTRODUCTION = "generate_introduction" # генерация введения
    GENERATE_CHAPTERS_NAME = "generate_chapters_name" # генерация названий глав
    GENERATE_CHAPTERS_CONTENT = "generate_chapters_content" # генерация содержания глав
    MERGE_ARTICLE = "merge_article" # слияние статей
    SEO_FIX = "seo_fix" # SEO оптимизация
    COMPLETED = "completed" # завершена генерация
    CANCELLED = "cancelled" # отменена генерация
    ERROR = "error" # ошибка в генерации

    @staticmethod
    def to_choice() -> list[tuple[str, str]]:
        return [(status.name, status.value) for status in ProjectStatus]

    @staticmethod
    def in_progress_choices() -> list[tuple[str, str]]:
        return [(status.value, status.name) for status in in_progress_statuses]

in_progress_statuses = [
    ProjectStatus.STARTED,
    ProjectStatus.GENERATE_TITLE,
    ProjectStatus.GENERATE_INTRODUCTION,
    ProjectStatus.GENERATE_CHAPTERS_NAME,
    ProjectStatus.GENERATE_CHAPTERS_CONTENT,
]

not_in_progress_statuses = [
    ProjectStatus.NEW,
    ProjectStatus.NOT_STARTED,
    ProjectStatus.COMPLETED,
    ProjectStatus.CANCELLED,
    ProjectStatus.ERROR,
]

final_project_statuses = [
    ProjectStatus.COMPLETED,
    ProjectStatus.CANCELLED,
    ProjectStatus.ERROR,
]
