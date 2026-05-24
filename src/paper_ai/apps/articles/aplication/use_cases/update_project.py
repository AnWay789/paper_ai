from ...aplication.dtos.update_project_dto import UpdateProjectDTO
from ...aplication.adapters.article_project_rep import ArticleProjectRepository

class UpdateProjectUseCase:
    def __init__(self, article_project_repository: ArticleProjectRepository):
        self.article_project_repository = article_project_repository

    def execute(self, project_id: str, update_project_dto: UpdateProjectDTO) -> None:
        article_project = self.article_project_repository.get_by_id(project_id)
        article_project.update(**update_project_dto.__dict__)
        self.article_project_repository.save(article_project)
