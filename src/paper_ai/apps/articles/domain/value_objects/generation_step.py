from dataclasses import dataclass
from enum import Enum
from typing import Callable, TYPE_CHECKING


class LlmResponseFormat(Enum):
    TEXT = "text"
    COMMA_SEPARATED_LIST = "comma_separated_list"

from ..exceptions.generation_ex import InvalidGenerationResponseException
from .project_statuses import ProjectStatus

if TYPE_CHECKING:
    from ..entities.article_project import ArticleProject

PostApplyHook = Callable[["ArticleProject"], None]
StepApplyHandler = Callable[["ArticleProject", str | list[str]], None]
AdvanceHandler = Callable[["ArticleProject"], None]


def _require_str(response: str | list[str]) -> str:
    if not isinstance(response, str):
        raise InvalidGenerationResponseException("Ожидалась строка")
    return response


def _require_str_list(response: str | list[str]) -> list[str]:
    if not isinstance(response, list):
        raise InvalidGenerationResponseException("Ожидался список строк")
    return response


def _apply_title(project: "ArticleProject", response: str | list[str]) -> None:
    project.set_article_title(_require_str(response))


def _apply_introduction(project: "ArticleProject", response: str | list[str]) -> None:
    project.set_article_introduction(_require_str(response))


def _apply_chapters_name(project: "ArticleProject", response: str | list[str]) -> None:
    project.set_article_chapters_name(_require_str_list(response))


def _apply_chapters_content(project: "ArticleProject", response: str | list[str]) -> None:
    project.add_article_chapters_content(_require_str(response))


def _apply_final_article(project: "ArticleProject", response: str | list[str]) -> None:
    project.set_final_article(_require_str(response))


def _post_apply_find_problems(project: "ArticleProject") -> None:
    project.find_problems()


def _advance_to_next_step(project: "ArticleProject") -> None:
    # TODO: Слабое место так как get_next_status может вернуть None
    # Нужно подумать что делать в случае None
    project.change_status(project.get_next_status())

def _advance_chapters_content_to_next_step(project: "ArticleProject") -> None:
    needed = project.get_count_chapters()
    generated = project.get_count_chapters_content()
    
    if generated < needed:
        return # не нужно переходить на следующий шаг, т.к. не все главы созданы
    
    _advance_to_next_step(project)

@dataclass(frozen=True)
class GenerationStep:
    next_status: ProjectStatus
    apply: StepApplyHandler
    advance: AdvanceHandler
    post_apply: PostApplyHook | None = None
    llm_response_format: LlmResponseFormat = LlmResponseFormat.TEXT


GENERATION_STEPS: dict[ProjectStatus, GenerationStep] = {
    ProjectStatus.GENERATE_TITLE: GenerationStep(
        next_status=ProjectStatus.GENERATE_INTRODUCTION,
        apply=_apply_title,
        advance=_advance_to_next_step,
    ),
    ProjectStatus.GENERATE_INTRODUCTION: GenerationStep(
        next_status=ProjectStatus.GENERATE_CHAPTERS_NAME,
        apply=_apply_introduction,
        advance=_advance_to_next_step,
    ),
    ProjectStatus.GENERATE_CHAPTERS_NAME: GenerationStep(
        next_status=ProjectStatus.GENERATE_CHAPTERS_CONTENT,
        apply=_apply_chapters_name,
        advance=_advance_to_next_step,
        llm_response_format=LlmResponseFormat.COMMA_SEPARATED_LIST,
    ),
    ProjectStatus.GENERATE_CHAPTERS_CONTENT: GenerationStep(
        next_status=ProjectStatus.MERGE_ARTICLE,
        apply=_apply_chapters_content,
        advance=_advance_chapters_content_to_next_step,
    ),
    ProjectStatus.MERGE_ARTICLE: GenerationStep(
        next_status=ProjectStatus.SEO_FIX,
        apply=_apply_final_article,
        post_apply=_post_apply_find_problems,
        advance=_advance_to_next_step,
    ),
    ProjectStatus.SEO_FIX: GenerationStep(
        next_status=ProjectStatus.COMPLETED,
        apply=_apply_final_article,
        advance=_advance_to_next_step,
    ),
}


GENERATION_STEP_STATUSES = frozenset(GENERATION_STEPS.keys())


def is_generation_step(status: ProjectStatus) -> bool:
    return status in GENERATION_STEPS


def get_generation_step(status: ProjectStatus) -> GenerationStep:
    return GENERATION_STEPS[status]


def get_llm_response_format(status: ProjectStatus) -> LlmResponseFormat:
    return get_generation_step(status).llm_response_format
