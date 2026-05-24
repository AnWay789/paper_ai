from ...application.adapters.article_project_rep import ArticleProjectRepository

class DeleteProjectUseCase:
    def __init__(self, article_project_repository: ArticleProjectRepository):
        self.article_project_repository = article_project_repository

    def execute(self, project_id: str) -> None:
        self.article_project_repository.delete(project_id)
