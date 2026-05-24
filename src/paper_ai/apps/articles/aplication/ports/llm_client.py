from abc import ABC, abstractmethod
from ...domain.entities.article_project import ArticleProject

class LLMClientPort(ABC):
    @abstractmethod
    def generate_text(self, promt: str) -> str:
        pass
