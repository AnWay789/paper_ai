from ninja import Schema

from ....application.dtos.create_project_dto import CreateProjectDTO


class DepthItemSchema(Schema):
    keyword: str
    count: int


class CreateProjectSchema(Schema):
    marker: str
    depth: list[DepthItemSchema]
    width: list[str]
    n_gramms: list[str]
    count_chapters: int
    about_author: str

    def to_dto(self) -> CreateProjectDTO:
        return CreateProjectDTO(
            marker=self.marker,
            depth=[(item.keyword, item.count) for item in self.depth],
            width=self.width,
            n_gramms=self.n_gramms,
            count_chapters=self.count_chapters,
            about_author=self.about_author,
        )


class CreateProjectResponseSchema(Schema):
    id: str
