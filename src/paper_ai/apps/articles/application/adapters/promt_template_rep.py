from abc import ABC, abstractmethod


class PromtTemplateRepository(ABC):
    @abstractmethod
    def get_template_by_status(self, status: str) -> str:
        pass
