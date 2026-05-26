import re

from ..exceptions.generation_ex import InvalidGenerationResponseException
from ..generation import LlmResponseFormat, ProjectStatus, get_llm_response_format

_LINE_PREFIX_RE = re.compile(r"^[\s\-•*]*(?:\d+[\.\)\]:]|[\-\•\*])\s*")


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
                return LlmResponseParser._parse_chapter_list(raw, count_chapters)

    @staticmethod
    def _parse_chapter_list(raw: str, expected_count: int) -> list[str]:
        text = raw.strip()
        if not text:
            raise InvalidGenerationResponseException("Пустой ответ LLM для списка глав")

        for parser in (
            LlmResponseParser._parse_by_lines,
            LlmResponseParser._parse_by_commas,
        ):
            items = parser(text)
            if len(items) == expected_count:
                return items

        items = LlmResponseParser._parse_by_commas(text)
        if len(items) > expected_count:
            merged = LlmResponseParser._merge_extra_comma_splits(items, expected_count)
            if len(merged) == expected_count:
                return merged

        raise InvalidGenerationResponseException(
            f"Ожидалось {expected_count} названий глав, "
            f"не удалось разобрать ответ ({len(items)} фрагментов): {raw!r}"
        )

    @staticmethod
    def _normalize_item(item: str) -> str:
        return _LINE_PREFIX_RE.sub("", item.strip()).strip()

    @staticmethod
    def _parse_by_lines(text: str) -> list[str]:
        lines = [LlmResponseParser._normalize_item(line) for line in text.splitlines()]
        return [line for line in lines if line]

    @staticmethod
    def _parse_by_commas(text: str) -> list[str]:
        return [
            LlmResponseParser._normalize_item(part)
            for part in text.split(",")
            if part.strip()
        ]

    @staticmethod
    def _merge_extra_comma_splits(items: list[str], expected_count: int) -> list[str]:
        """Склеивает фрагменты, ошибочно разрезанные запятой внутри названия главы."""
        merged = list(items)
        while len(merged) > expected_count:
            # Самый короткий соседний фрагмент чаще всего — хвост/голова ошибочного split.
            merge_at = min(
                range(len(merged) - 1),
                key=lambda i: min(len(merged[i]), len(merged[i + 1])),
            )
            merged[merge_at] = f"{merged[merge_at]}, {merged[merge_at + 1]}"
            del merged[merge_at + 1]
        return merged
