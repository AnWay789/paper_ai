from ...domain.entities.article_paper import ArticlePaper
from ..orm.article_paper import ArticlePaperORM

def to_domain(article_paper_orm: ArticlePaperORM | None) -> ArticlePaper | None:
    if article_paper_orm is None:
        return None
    return ArticlePaper(
        id=str(article_paper_orm.id),
        article_title=article_paper_orm.article_title,
        article_introduction=article_paper_orm.article_introduction,
        article_chapters_name=article_paper_orm.article_chapters_name,
        article_chapters_content=article_paper_orm.article_chapters_contents,
        final_article=article_paper_orm.final_article,
        problems=article_paper_orm.problems,
    )

def to_orm(article_paper: ArticlePaper | None) -> ArticlePaperORM | None:
    if article_paper is None:
        return None
    return ArticlePaperORM(
        id=article_paper.get_id(),
        article_title=article_paper.get_article_title(),
        article_introduction=article_paper.get_article_introduction(),
        article_chapters_name=article_paper.get_article_chapters_name(),
        article_chapters_contents=article_paper.get_article_chapters_contents(),
        final_article=article_paper.get_final_article(),
        problems=article_paper.get_problems(),
    )
