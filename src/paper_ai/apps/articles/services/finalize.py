from ..generation import ProjectStatus
from ..models import ArticleProject
from .seo import analyze_seo_problems


def merge_article_parts(project: ArticleProject) -> str:
    return "\n\n".join(
        [
            project.get_article_title(),
            project.get_article_introduction(),
            *project.get_article_chapters_contents(),
        ]
    )


def finalize_article(project: ArticleProject) -> None:
    """Склейка частей статьи, SEO-проверка и завершение без LLM."""
    project.set_final_article(merge_article_parts(project))
    project.set_problems(analyze_seo_problems(project))
    project.change_status(ProjectStatus.COMPLETED)
    project.article_paper.save()
    project.save(update_fields=["status"])
