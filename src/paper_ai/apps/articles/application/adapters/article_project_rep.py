from abc import ABC, abstractmethod
from ...domain.entities.article_project import ArticleProject

class ArticleProjectRepository(ABC):
    @abstractmethod
    def get_by_id(self, article_project_id: str) -> ArticleProject:
        pass
    @abstractmethod
    def save(self, article_project: ArticleProject) -> None:
        pass

    @abstractmethod
    def delete(self, article_project_id: str) -> None:
        pass
