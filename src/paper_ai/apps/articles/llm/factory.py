from django.conf import settings

from .client import LLMClient
from .fake import FakeLLMClient
from .openai_client import OpenAILLMClient


def get_llm_client() -> LLMClient:
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if api_key:
        return OpenAILLMClient(api_key=api_key)
    return FakeLLMClient()
