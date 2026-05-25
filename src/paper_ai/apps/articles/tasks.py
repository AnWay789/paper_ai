from celery import shared_task

from .domain.exceptions.generation_ex import InvalidGenerationStepException
from .domain.value_objects.project_statuses import ProjectStatus
from .interface.api.dependencies import (
    get_run_step_generation_use_case,
    get_article_project_repository,
)

@shared_task
def run_generation_step(project_id: str) -> None:
    run_uc = get_run_step_generation_use_case()
    repo = get_article_project_repository()
    try:
        run_uc.execute(project_id)
    except InvalidGenerationStepException:
        return  # уже не на шаге генерации — выходим
    project = repo.get_by_id(project_id)
    if project.is_completed() or project.get_status() == ProjectStatus.ERROR:
        return
    run_generation_step.delay(project_id)  # следующий шаг

