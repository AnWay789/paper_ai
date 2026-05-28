from ..services.llm_token_counter import LlmTokenCounter
from .result import GenerationResult, TokenUsage


class FakeLLMClient:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        *,
        count_chapters: int = 3,
    ) -> GenerationResult:
        chapters = [f"Глава {index}" for index in range(1, count_chapters + 1)]
        text = ", ".join(chapters)
        counter = LlmTokenCounter(self.model_name)
        usage = TokenUsage(
            input_tokens=counter.estimate_tokens(prompt),
            output_tokens=counter.estimate_tokens(text),
            cached_input_tokens=0,
            source="estimate",
        )
        return GenerationResult(text=text, usage=usage)
