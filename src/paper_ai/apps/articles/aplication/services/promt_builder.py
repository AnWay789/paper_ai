from ...domain.entities.article_project import ArticleProject
from ...domain.exceptions.atricle_paper_ex import ArticlePaperException


class PromtBuilder:
    """Application service: сборка контекста и промпта для LLM."""

    def __init__(self, article_project: ArticleProject):
        self.article_project = article_project

    def _optional(self, getter) -> str:
        try:
            return getter()
        except ArticlePaperException:
            return ""

    def promt_context(self) -> dict[str, str | int]:
        return {
            "marker": self.article_project.get_marker(),
            "depth": self.article_project.get_depth_by_text(),
            "width": self.article_project.get_width_by_text(),
            "n_gramms": self.article_project.get_n_gramms_by_text(),
            "count_chapters": self.article_project.get_count_chapters(),
            "about_author": self.article_project.get_about_author(),
            "article_title": self._optional(self.article_project.get_article_title),
            "article_introduction": self._optional(self.article_project.get_article_introduction),
            "article_chapters_name": self._optional(
                self.article_project.get_article_chapters_name_by_text
            ),
            "article_chapters_content": self._optional(
                self.article_project.get_article_chapters_contents_by_text
            ),
            "final_article": self._optional(self.article_project.get_final_article),
            "problems": self.article_project.get_problems_by_text(),
        }

    def build_promt(self, prompt_template: str) -> str:
        return prompt_template.format(**self.promt_context())
