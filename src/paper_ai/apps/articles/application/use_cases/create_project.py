import uuid
from ...application.dtos.create_project_dto import CreateProjectDTO
from ...application.adapters.article_project_rep import ArticleProjectRepository
from ...domain.entities.article_project import ArticleProject
from ...domain.value_objects.project_statuses import ProjectStatus
from datetime import datetime

class CreateProjectUseCase:
    def __init__(self, article_project_repository: ArticleProjectRepository):
        self.article_project_repository = article_project_repository

    def execute(self, create_project_dto: CreateProjectDTO) -> str:
        """ 
        Создание проекта статьи
        Args: 
            create_project_dto (CreateProjectDTO): Данные для создания проекта статьи
        Returns:
            str: ID проекта статьи
        """
        article_project = ArticleProject.create(
            id=str(uuid.uuid4()),
            marker=create_project_dto.marker,
            depth=create_project_dto.depth,
            width=create_project_dto.width,
            n_gramms=create_project_dto.n_gramms,
            count_chapters=create_project_dto.count_chapters,
            about_author=create_project_dto.about_author,
            article_paper_id=str(uuid.uuid4())
        )
        self.article_project_repository.save(article_project)
        return article_project.id
