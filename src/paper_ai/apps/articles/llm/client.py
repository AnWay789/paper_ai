from typing import Protocol

from .result import GenerationResult


class LLMClient(Protocol):
    def generate(
        self,
        prompt: str,
        *,
        count_chapters: int = 3,
    ) -> GenerationResult: ...
