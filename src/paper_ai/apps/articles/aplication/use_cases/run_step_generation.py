from ...domain.value_objects.generation_step import is_generation_step
from ...domain.exceptions.generation_ex import InvalidGenerationStepException
from ...aplication.adapters.article_project_rep import ArticleProjectRepository
from ...aplication.adapters.promt_template_rep import PromtTemplateRepository
from ...aplication.ports.llm_client import LLMClientPort
from ...aplication.services.promt_builder import PromtBuilder


class RunStepGenerationUseCase:
    def __init__(
        self,
        article_project_repository: ArticleProjectRepository,
        promt_template_repository: PromtTemplateRepository,
        llm_client: LLMClientPort,
    ):
        self.article_project_repository = article_project_repository
        self.promt_template_repository = promt_template_repository
        self.llm_client = llm_client

    def execute(self, article_project_id: str) -> None:
        article_project = self.article_project_repository.get_by_id(article_project_id)

        if not is_generation_step(article_project.get_status()):
            raise InvalidGenerationStepException(
                f"Проект {article_project_id} не на шаге генерации "
                f"(текущий статус: {article_project.get_status().value})"
            )

        promt_template = self.promt_template_repository.get_template_by_status(
            article_project.get_status()
        )
        promt = PromtBuilder(article_project).build_promt(promt_template)
        response = self.llm_client.generate_text(promt)
        article_project.apply_generation_step(response)
        self.article_project_repository.save(article_project)
