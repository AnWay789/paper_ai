from typing import Protocol


class LLMClient(Protocol):
    def generate_text(self, prompt: str, *, count_chapters: int = 3) -> str: ...
