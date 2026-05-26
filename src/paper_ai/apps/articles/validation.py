from dataclasses import dataclass

from .exceptions.about_autor_ex import (
    MaxAboutAuthorException,
    MinAboutAuthorException,
)
from .exceptions.count_chapters_ex import (
    MaxCountChaptersException,
    MinCountChaptersException,
)
from .exceptions.depth_ex import MaxDepthLengthException, MinDepthLengthException
from .exceptions.keyword_ex import (
    MaxKeywordCountException,
    MaxKeywordLengthException,
    MinKeywordCountException,
    MinKeywordLengthException,
)
from .exceptions.marker_ex import (
    EmptyMarkerException,
    MaxMarkerLengthException,
    MinMarkerLengthException,
)
from .exceptions.n_gramm_ex import (
    MaxNGrammsCountException,
    MaxNGrammsLengthException,
    MinNGrammsCountException,
    MinNGrammsLengthException,
)
from .exceptions.width_ex import MaxWidthLengthException, MinWidthLengthException


@dataclass(frozen=True)
class TextLengthLimit:
    min_len: int
    max_len: int


@dataclass(frozen=True)
class CountLimit:
    min_count: int
    max_count: int


MARKER = TextLengthLimit(2, 100)
KEYWORD = TextLengthLimit(2, 100)
KEYWORD_COUNT = CountLimit(1, 100)
DEPTH_ITEMS = CountLimit(1, 100)
WIDTH_WORD = TextLengthLimit(2, 200)
N_GRAM = TextLengthLimit(2, 100)
N_GRAM_COUNT = CountLimit(0, 100)
CHAPTERS = CountLimit(1, 20)
ABOUT_AUTHOR = TextLengthLimit(2, 300)


def validate_marker(marker: str) -> None:
    if not marker:
        raise EmptyMarkerException("Маркер не может быть пустым")
    if len(marker) > MARKER.max_len:
        raise MaxMarkerLengthException(
            f"Маркер не может быть длиннее {MARKER.max_len} символов"
        )
    if len(marker) < MARKER.min_len:
        raise MinMarkerLengthException(
            f"Маркер не может быть короче {MARKER.min_len} символов"
        )


def validate_depth(depth: list[tuple[str, int]]) -> None:
    if len(depth) < DEPTH_ITEMS.min_count:
        raise MinDepthLengthException(
            f"Глубина не может содержать меньше {DEPTH_ITEMS.min_count} ключевых слов"
        )
    if len(depth) > DEPTH_ITEMS.max_count:
        raise MaxDepthLengthException(
            f"Глубина не может содержать больше {DEPTH_ITEMS.max_count} ключевых слов"
        )
    for word, count in depth:
        if len(word) < KEYWORD.min_len:
            raise MinKeywordLengthException(
                f"Ключевое слово не может быть короче {KEYWORD.min_len} символов"
            )
        if len(word) > KEYWORD.max_len:
            raise MaxKeywordLengthException(
                f"Ключевое слово не может быть длиннее {KEYWORD.max_len} символов"
            )
        if count < KEYWORD_COUNT.min_count:
            raise MinKeywordCountException(
                f"Количество вхождений не может быть меньше {KEYWORD_COUNT.min_count}"
            )
        if count > KEYWORD_COUNT.max_count:
            raise MaxKeywordCountException(
                f"Количество вхождений не может быть больше {KEYWORD_COUNT.max_count}"
            )


def validate_width(width: list[str]) -> None:
    for word in width:
        if len(word) < WIDTH_WORD.min_len:
            raise MinWidthLengthException(
                f"Слово ширины не может быть короче {WIDTH_WORD.min_len} символов"
            )
        if len(word) > WIDTH_WORD.max_len:
            raise MaxWidthLengthException(
                f"Слово ширины не может быть длиннее {WIDTH_WORD.max_len} символов"
            )


def validate_n_gramms(n_gramms: list[str]) -> None:
    if len(n_gramms) < N_GRAM_COUNT.min_count:
        raise MinNGrammsCountException(
            f"Количество n-грамм не может быть меньше {N_GRAM_COUNT.min_count}"
        )
    if len(n_gramms) > N_GRAM_COUNT.max_count:
        raise MaxNGrammsCountException(
            f"Количество n-грамм не может быть больше {N_GRAM_COUNT.max_count}"
        )
    for n_gramm in n_gramms:
        if len(n_gramm) < N_GRAM.min_len:
            raise MinNGrammsLengthException(
                f"N-грамма не может быть короче {N_GRAM.min_len} символов"
            )
        if len(n_gramm) > N_GRAM.max_len:
            raise MaxNGrammsLengthException(
                f"N-грамма не может быть длиннее {N_GRAM.max_len} символов"
            )


def validate_count_chapters(count_chapters: int) -> None:
    if count_chapters < CHAPTERS.min_count:
        raise MinCountChaptersException(
            f"Количество глав не может быть меньше {CHAPTERS.min_count}"
        )
    if count_chapters > CHAPTERS.max_count:
        raise MaxCountChaptersException(
            f"Количество глав не может быть больше {CHAPTERS.max_count}"
        )


def validate_about_author(about_author: str) -> None:
    if len(about_author) < ABOUT_AUTHOR.min_len:
        raise MinAboutAuthorException(
            f"О авторе не может быть короче {ABOUT_AUTHOR.min_len} символов"
        )
    if len(about_author) > ABOUT_AUTHOR.max_len:
        raise MaxAboutAuthorException(
            f"О авторе не может быть длиннее {ABOUT_AUTHOR.max_len} символов"
        )


def validate_project_fields(
    *,
    marker: str,
    depth: list[tuple[str, int]],
    width: list[str],
    n_gramms: list[str],
    count_chapters: int,
    about_author: str,
) -> None:
    validate_marker(marker)
    validate_depth(depth)
    validate_width(width)
    validate_n_gramms(n_gramms)
    validate_count_chapters(count_chapters)
    validate_about_author(about_author)
