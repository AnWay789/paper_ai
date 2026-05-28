from decimal import Decimal

from ..exceptions.generation_ex import InvalidGenerationStepException
from ..generation import GENERATION_STEPS, ProjectStatus, is_generation_step
from ..generation.estimates import expected_output_tokens
from ..llm.factory import get_llm_client
from ..models import ArticleProject, PromtTemplate
from .costs import add_usage_cost, set_estimated_costs, update_cost_total
from .llm_response_parser import LlmResponseParser
from .llm_token_counter import LlmTokenCounter
from .project import get_project
from .prompts import PromtBuilder
from .token_types import PriceKind


def _require_llm_model(project: ArticleProject) -> None:
    if not project.llm_model_id:
        raise InvalidGenerationStepException(
            f"У проекта {project.id} не выбрана LLM-модель"
        )


def _estimate_step_costs(
    token_counter: LlmTokenCounter,
    prompt: str,
    template: PromtTemplate,
) -> tuple[Decimal, Decimal]:
    input_tokens = token_counter.estimate_tokens(prompt)
    output_tokens = expected_output_tokens(
        input_tokens,
        template.expected_output_ratio,
    )
    input_cost = token_counter.count_price_for_tokens(
        input_tokens, PriceKind.INPUT, quantize=False
    )
    output_cost = token_counter.count_price_for_tokens(
        output_tokens, PriceKind.OUTPUT, quantize=False
    )
    return input_cost, output_cost


def estimate_generation_costs(project: ArticleProject) -> tuple[Decimal, Decimal]:
    """
    Оценивает стоимость генерации (смета):
    input — по токенам промпта, output — input_tokens × expected_output_ratio шаблона.
    """
    _require_llm_model(project)

    token_counter = LlmTokenCounter(project.llm_model.model_system_name)
    builder = PromtBuilder(project)
    estimated_input = Decimal("0")
    estimated_output = Decimal("0")

    generation_statuses = [status.value for status in GENERATION_STEPS]
    templates_by_status = {
        template.status: template
        for template in PromtTemplate.objects.filter(status__in=generation_statuses)
    }

    for status in GENERATION_STEPS:
        template = templates_by_status.get(status.value)
        if template is None:
            raise InvalidGenerationStepException(
                f"Не найден шаблон промпта для статуса {status.value}"
            )

        if status == ProjectStatus.GENERATE_CHAPTERS_CONTENT:
            for chapter_index in range(project.count_chapters):
                step_builder = PromtBuilder(project, chapter_index=chapter_index)
                prompt = step_builder.build_promt(template.template)
                step_input, step_output = _estimate_step_costs(
                    token_counter, prompt, template
                )
                estimated_input += step_input
                estimated_output += step_output
        else:
            prompt = builder.build_promt(template.template)
            step_input, step_output = _estimate_step_costs(
                token_counter, prompt, template
            )
            estimated_input += step_input
            estimated_output += step_output

    return estimated_input, estimated_output


def update_generation_estimate(project: ArticleProject) -> None:
    """Пересчитывает и записывает в объект поля estimated_cost_* (без сохранения в БД)."""
    estimated_input, estimated_output = estimate_generation_costs(project)
    set_estimated_costs(project, estimated_input, estimated_output)


def save_generation_estimate(project_id: str) -> ArticleProject:
    """Считает смету и сохраняет только estimated_cost_*. Статус и факт не меняет."""
    project = get_project(project_id)
    update_generation_estimate(project)
    project.save(update_fields=[
        "estimated_cost_input",
        "estimated_cost_output",
        "estimated_cost_total",
    ])
    return project


def start_generation(project_id: str) -> None:
    project = get_project(project_id)
    _require_llm_model(project)
    project.start_generation()

    update_generation_estimate(project)

    project.cost_input = Decimal("0")
    project.cost_output = Decimal("0")
    update_cost_total(project)

    project.save(update_fields=[
        "status",
        "estimated_cost_input",
        "estimated_cost_output",
        "estimated_cost_total",
        "cost_input",
        "cost_output",
        "cost_total",
    ])


def end_generation(project_id: str) -> None:
    project = get_project(project_id)
    update_cost_total(project)
    project.save(update_fields=["cost_input", "cost_output", "cost_total"])


def run_generation_step(project_id: str) -> None:
    project = get_project(project_id)

    if not is_generation_step(project.status_enum):
        raise InvalidGenerationStepException(
            f"Проект {project_id} не на шаге LLM-генерации "
            f"(текущий статус: {project.status})"
        )

    _require_llm_model(project)

    cost_fields = [
        "status",
        "cost_input",
        "cost_output",
        "cost_total",
    ]

    try:
        template = PromtTemplate.objects.get(status=project.status)
        prompt = PromtBuilder(project).build_promt(template.template)
        result = get_llm_client(project.llm_model.model_system_name).generate(
            prompt,
            count_chapters=project.count_chapters,
        )
        add_usage_cost(project, result.usage)
        parsed = LlmResponseParser.parse_for_step(
            project.status_enum,
            result.text,
            project.count_chapters,
        )
        project.apply_generation_step(parsed)
        project.article_paper.save()
        project.save(update_fields=cost_fields)
    except Exception:
        project.to_error_status()
        project.save(update_fields=cost_fields)
        raise
