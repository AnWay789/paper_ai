import re
import string

from ..models import ArticleProject


def analyze_seo_problems(project: ArticleProject) -> list[str]:
    chapters_contents = project.get_article_chapters_contents()
    raw_content = "\n".join(chapters_contents)
    clear_content = raw_content.lower().translate(str.maketrans("", "", string.punctuation))
    content_words = clear_content.split()

    return (
        _depth_problems(project, content_words)
        + _width_problems(project, content_words)
        + _n_gramms_problems(project, clear_content)
    )


def _depth_problems(project: ArticleProject, content_words: list[str]) -> list[str]:
    problems = []
    for word, count in project.get_depth():
        found = content_words.count(word.lower())
        if found < count:
            problems.append(
                f'Проблема с глубиной: "{word}" найдено: {found}, необходимо {count}'
            )
    return problems


def _width_problems(project: ArticleProject, content_words: list[str]) -> list[str]:
    problems = []
    for word in project.width:
        if content_words.count(word.lower()) < 1:
            problems.append(f'Проблема с шириной: "{word}" не найдено')
    return problems


def _n_gramms_problems(project: ArticleProject, content: str) -> list[str]:
    problems = []
    for n_gramm in project.n_gramms:
        if len(re.findall(re.escape(n_gramm.lower()), content)) < 1:
            problems.append(f'Проблема с n-граммой: "{n_gramm}" не найдено')
    return problems
