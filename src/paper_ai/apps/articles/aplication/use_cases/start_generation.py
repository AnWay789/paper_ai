from ...aplication.adapters.article_project_rep import ArticleProjectRepository


class StartGenerationUseCase:
    def __init__(self, article_project_repository: ArticleProjectRepository):
        self.article_project_repository = article_project_repository

    def execute(self, article_project_id: str) -> None:
        article_project = self.article_project_repository.get_by_id(article_project_id)
        article_project.start_generation()
        self.article_project_repository.save(article_project)
