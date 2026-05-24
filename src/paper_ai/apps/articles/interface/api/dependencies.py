from django.conf import settings

from ...application.ports.llm_client import LLMClientPort
from ...application.use_cases.create_project import CreateProjectUseCase
from ...application.use_cases.delete_project import DeleteProjectUseCase
from ...application.use_cases.run_step_generation import RunStepGenerationUseCase
from ...application.use_cases.start_generation import StartGenerationUseCase
from ...infrastructure.llm.fake_llm_client import FakeLLMClient
from ...infrastructure.llm.openai_llm_client import OpenAILLMClient
from ...infrastructure.repository.article_project_orm import ArticleProjectORMRepository
from ...infrastructure.repository.promt_template_orm import PromtTemplateORMRepository


def get_article_project_repository() -> ArticleProjectORMRepository:
    return ArticleProjectORMRepository()


def get_promt_template_repository() -> PromtTemplateORMRepository:
    return PromtTemplateORMRepository()


def get_llm_client() -> LLMClientPort:
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if api_key:
        return OpenAILLMClient(api_key=api_key)
    return FakeLLMClient()


def get_create_project_use_case() -> CreateProjectUseCase:
    return CreateProjectUseCase(get_article_project_repository())


def get_delete_project_use_case() -> DeleteProjectUseCase:
    return DeleteProjectUseCase(get_article_project_repository())


def get_start_generation_use_case() -> StartGenerationUseCase:
    return StartGenerationUseCase(get_article_project_repository())


def get_run_step_generation_use_case() -> RunStepGenerationUseCase:
    return RunStepGenerationUseCase(
        get_article_project_repository(),
        get_promt_template_repository(),
        get_llm_client(),
    )
