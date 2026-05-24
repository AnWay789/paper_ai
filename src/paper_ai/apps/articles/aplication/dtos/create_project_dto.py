from dataclasses import dataclass

@dataclass(frozen=True)
class CreateProjectDTO:
    marker: str
    depth: list[tuple[str, int]]
    width: list[str]
    n_gramms: list[str]
    count_chapters: int
    about_author: str
