from decimal import Decimal
from typing import TYPE_CHECKING

from ..llm.result import TokenUsage

if TYPE_CHECKING:
    from ..models import ArticleProject

COST_QUANTIZE = Decimal("0.0001")


def update_cost_total(project: "ArticleProject") -> None:
    cost_input = (project.cost_input or Decimal("0")).quantize(COST_QUANTIZE)
    cost_output = (project.cost_output or Decimal("0")).quantize(COST_QUANTIZE)
    project.cost_input = cost_input
    project.cost_output = cost_output
    project.cost_total = (cost_input + cost_output).quantize(COST_QUANTIZE)


def update_estimated_cost_total(project: "ArticleProject") -> None:
    est_input = (project.estimated_cost_input or Decimal("0")).quantize(COST_QUANTIZE)
    est_output = (project.estimated_cost_output or Decimal("0")).quantize(COST_QUANTIZE)
    project.estimated_cost_input = est_input
    project.estimated_cost_output = est_output
    project.estimated_cost_total = (est_input + est_output).quantize(COST_QUANTIZE)


def set_estimated_costs(
    project: "ArticleProject",
    estimated_input: Decimal,
    estimated_output: Decimal,
) -> None:
    project.estimated_cost_input = estimated_input
    project.estimated_cost_output = estimated_output
    update_estimated_cost_total(project)


def add_usage_cost(project: "ArticleProject", usage: TokenUsage) -> None:
    from .llm_token_counter import LlmTokenCounter

    token_counter = LlmTokenCounter(project.llm_model.model_system_name)
    input_cost, output_cost = token_counter.price_from_usage(usage, quantize=False)
    project.cost_input = (project.cost_input or Decimal("0")) + input_cost
    project.cost_output = (project.cost_output or Decimal("0")) + output_cost
    update_cost_total(project)
