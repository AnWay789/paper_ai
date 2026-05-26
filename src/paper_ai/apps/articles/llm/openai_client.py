from openai import OpenAI

from .client import LLMClient


class OpenAILLMClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_text(
        self,
        prompt: str,
        *,
        count_chapters: int = 3,
        model: str = "gpt-5.4-mini",
    ) -> str:
        _ = count_chapters
        response = self.client.responses.create(model=model, input=prompt)
        return response.output_text
