from django import template

from ..models import ArticleProject
from ..ui_helpers import project_can_edit, status_badge_class, status_label

register = template.Library()


@register.filter
def project_status_label(status: str) -> str:
    return status_label(status)


@register.filter
def project_status_badge(status: str) -> str:
    return status_badge_class(status)


@register.filter
def can_edit_project(project: ArticleProject) -> bool:
    return project_can_edit(project)
