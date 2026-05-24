from ...domain.exceptions.generation_ex import InvalidGenerationResponseException
from ...domain.value_objects.generation_step import (
    LlmResponseFormat,
    get_llm_response_format,
)
from ...domain.value_objects.project_statuses import ProjectStatus


class LlmResponseParser:
    @staticmethod
    def parse_for_step(
        status: ProjectStatus,
        raw: str,
        count_chapters: int,
    ) -> str | list[str]:
        match get_llm_response_format(status):
            case LlmResponseFormat.TEXT:
                return raw
            case LlmResponseFormat.COMMA_SEPARATED_LIST:
                return LlmResponseParser._parse_comma_separated_list(raw, count_chapters)

    @staticmethod
    def _parse_comma_separated_list(raw: str, expected_count: int) -> list[str]:
        items = [part.strip() for part in raw.split(",") if part.strip()]
        if len(items) != expected_count:
            raise InvalidGenerationResponseException(
                f"Ожидалось {expected_count} значений через запятую, "
                f"получено {len(items)}: {raw!r}"
            )
        return items
