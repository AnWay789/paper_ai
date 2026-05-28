from celery import shared_task

from .exceptions.generation_ex import InvalidGenerationStepException
from .generation import ProjectStatus
from .services.generation import run_generation_step as execute_generation_step, end_generation
from .services.project import get_project


@shared_task
def run_generation_step(project_id: str) -> None:
    try:
        execute_generation_step(project_id)
    except InvalidGenerationStepException:
        return

    project = get_project(project_id)
    if project.is_completed() or project.status_enum == ProjectStatus.ERROR:
        end_generation(project_id)
        return

    run_generation_step.delay(project_id)
