import re
import string
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.article_project import ArticleProject


class ArticleSeoAnalyzer:
    """Domain service: проверка SEO-требований сгенерированной статьи."""

    def analyze(self, project: "ArticleProject") -> list[str]:
        chapters_contents = project.get_article_chapters_contents()
        raw_content = "\n".join(chapters_contents)
        lower_raw_content = raw_content.lower()
        clear_content = lower_raw_content.translate(str.maketrans("", "", string.punctuation))
        content_words = clear_content.split()

        return (
            self._find_depth_problems(project, content_words)
            + self._find_width_problems(project, content_words)
            + self._find_n_gramms_problems(project, clear_content)
        )

    def _find_depth_problems(self, project: "ArticleProject", content_words: list[str]) -> list[str]:
        depth_problems = []
        for word, count in project.get_depth():
            founded = content_words.count(word)
            if founded < count:
                depth_problems.append(
                    f'Проблема с глубиной: "{word}" найдено: {founded}, необходимо {count}'
                )
        return depth_problems

    def _find_width_problems(self, project: "ArticleProject", content_words: list[str]) -> list[str]:
        width_problems = []
        for word in project.get_width():
            if content_words.count(word) < 1:
                width_problems.append(f'Проблема с шириной: "{word}" не найдено')
        return width_problems

    def _find_n_gramms_problems(self, project: "ArticleProject", content: str) -> list[str]:
        n_gramms_problems = []
        for n_gramm in project.get_n_gramms():
            pattern = rf"{re.escape(n_gramm)}"
            if len(re.findall(pattern, content)) < 1:
                n_gramms_problems.append(f'Проблема с n-граммой: "{n_gramm}" не найдено')
        return n_gramms_problems
