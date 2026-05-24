from ...aplication.ports.llm_client import LLMClientPort
from ...infrastructure.other.promt_builder import PromtBuilder

class FakeLLMClient(LLMClientPort):
    def generate_text(self, prompt: str) -> str:
        print(prompt)
        return 'fake response'
