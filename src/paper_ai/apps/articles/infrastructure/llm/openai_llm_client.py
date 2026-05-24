from openai import OpenAI
from ...application.ports.llm_client import LLMClientPort

class OpenAILLMClient(LLMClientPort):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_text(self, prompt: str, model: str = "gpt-5.4-mini") -> str:
        response = self.client.responses.create(
            model=model,
            input=prompt
        )
        return response.output_text
