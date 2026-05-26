from .client import LLMClient


class FakeLLMClient:
    def generate_text(self, prompt: str, *, count_chapters: int = 3) -> str:
        chapters = [f"Глава {index}" for index in range(1, count_chapters + 1)]
        return ", ".join(chapters)
