from ..exceptions.atricle_paper_ex import ArticlePaperException
from ..models import ArticleProject


class PromtBuilder:
    """Сборка контекста и промпта для LLM."""

    def __init__(
        self,
        project: ArticleProject,
        *,
        chapter_index: int | None = None,
    ):
        self.project = project
        self._chapter_index = chapter_index

    def _optional(self, getter) -> str:
        try:
            return getter()
        except ArticlePaperException:
            return ""

    def _resolve_chapter_index(self) -> int:
        if self._chapter_index is not None:
            return self._chapter_index
        return self.project.get_count_chapters_content()

    def build_context(self) -> dict[str, str | int]:
        chapter_index = self._resolve_chapter_index()
        return {
            "marker": self.project.marker,
            "depth": self.project.get_depth_by_text(),
            "width": self.project.get_width_by_text(),
            "n_gramms": self.project.get_n_gramms_by_text(),
            "count_chapters": self.project.count_chapters,
            "about_author": self.project.about_author,
            "article_title": self._optional(self.project.get_article_title),
            "article_introduction": self._optional(self.project.get_article_introduction),
            "chapter_index": chapter_index,
            "article_chapters_name": self._optional(
                self.project.get_article_chapters_name_by_text
            ),
            "chapter_index_name": self._optional(
                lambda: self.project.get_chapter_index_name(chapter_index)
            ),
            "article_chapters_content": self._optional(
                self.project.get_article_chapters_contents_by_text
            ),
            "final_article": self._optional(self.project.get_final_article),
            "problems": self.project.get_problems_by_text(),
        }

    def build_promt(self, template: str) -> str:
        return template.format(**self.build_context())
