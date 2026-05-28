from openai import OpenAI

from ..services.llm_token_counter import LlmTokenCounter
from .result import GenerationResult, TokenUsage


class OpenAILLMClient:
    def __init__(self, api_key: str, model_name: str):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        *,
        count_chapters: int = 3,
    ) -> GenerationResult:
        _ = count_chapters
        response = self.client.responses.create(model=self.model_name, input=prompt)
        text = response.output_text
        usage = self._parse_usage(response, prompt, text)
        return GenerationResult(text=text, usage=usage)

    def _parse_usage(self, response, prompt: str, text: str) -> TokenUsage:
        raw_usage = getattr(response, "usage", None)
        if raw_usage is None:
            return self._estimate_usage(prompt, text)

        input_tokens = int(getattr(raw_usage, "input_tokens", 0) or 0)
        output_tokens = int(getattr(raw_usage, "output_tokens", 0) or 0)
        cached_input_tokens = 0
        input_details = getattr(raw_usage, "input_tokens_details", None)
        if input_details is not None:
            cached_input_tokens = int(getattr(input_details, "cached_tokens", 0) or 0)

        if input_tokens == 0 and output_tokens == 0:
            return self._estimate_usage(prompt, text)

        return TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=cached_input_tokens,
            source="api",
        )

    def _estimate_usage(self, prompt: str, text: str) -> TokenUsage:
        counter = LlmTokenCounter(self.model_name)
        return TokenUsage(
            input_tokens=counter.estimate_tokens(prompt),
            output_tokens=counter.estimate_tokens(text),
            cached_input_tokens=0,
            source="estimate",
        )
