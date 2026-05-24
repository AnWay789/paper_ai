from abc import ABC, abstractmethod


class LLMClientPort(ABC):
    @abstractmethod
    def generate_text(self, promt: str) -> str:
        """Сырой текстовый ответ LLM."""
        pass
