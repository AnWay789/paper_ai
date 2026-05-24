from dataclasses import dataclass

@dataclass(frozen=True)
class UpdateProjectDTO:
    marker: str | None = None
    depth: list[tuple[str, int]] | None = None
    width: list[str] | None = None
    n_gramms: list[str] | None = None
    count_chapters: int | None = None
    about_author: str | None = None
