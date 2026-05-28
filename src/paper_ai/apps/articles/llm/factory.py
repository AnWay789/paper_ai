from django.conf import settings

from .client import LLMClient
from .fake import FakeLLMClient
from .openai_client import OpenAILLMClient


def get_llm_client(model_name: str) -> LLMClient:
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if api_key and model_name:
        return OpenAILLMClient(api_key=api_key, model_name=model_name)
    return FakeLLMClient(model_name=model_name or "gpt-4o-mini")
