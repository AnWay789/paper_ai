from ...application.ports.llm_client import LLMClientPort


class FakeLLMClient(LLMClientPort):
    def generate_text(self, prompt: str) -> str:
        # Имитация ответа «названия через запятую» (3 главы)
        return "Глава 1, Глава 2, Глава 3"
