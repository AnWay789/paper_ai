from ..exceptions.generation_ex import InvalidGenerationStepException
from ..generation import ProjectStatus, is_generation_step
from ..llm import get_llm_client
from ..models import ArticleProject, PromtTemplate
from .llm_response_parser import LlmResponseParser
from .project import get_project
from .prompts import PromtBuilder


def start_generation(project_id: str) -> None:
    project = get_project(project_id)
    project.start_generation()
    project.save(update_fields=["status"])


def run_generation_step(project_id: str) -> None:
    project = get_project(project_id)

    if not is_generation_step(project.status_enum):
        raise InvalidGenerationStepException(
            f"Проект {project_id} не на шаге LLM-генерации "
            f"(текущий статус: {project.status})"
        )

    try:
        template = PromtTemplate.objects.get(status=project.status)
        prompt = PromtBuilder(project).build_promt(template.template)
        raw = get_llm_client().generate_text(
            prompt,
            count_chapters=project.count_chapters,
        )
        parsed = LlmResponseParser.parse_for_step(
            project.status_enum,
            raw,
            project.count_chapters,
        )
        project.apply_generation_step(parsed)
        project.article_paper.save()
        project.save()
    except Exception:
        project.to_error_status()
        project.save(update_fields=["status"])
        raise
