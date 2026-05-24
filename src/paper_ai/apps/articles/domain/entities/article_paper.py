class ArticlePaper:
    def __init__(
        self,
        id: str,
        article_title: str | None = None,
        article_introduction: str | None = None,
        article_chapters_name: list[str] | None = None,
        article_chapters_content: list[str] | None = None,
        final_article: str | None = None,
        problems: list[str] = [],
    ):
        self.id = id
        self.article_title = article_title
        self.article_introduction = article_introduction
        self.article_chapters_name = article_chapters_name
        self.article_chapters_content = article_chapters_content
        self.final_article = final_article
        self.problems = problems

    def get_id(self) -> str:
        return self.id

    def get_article_title(self) -> str | None:
        return self.article_title

    def get_article_introduction(self) -> str | None:
        return self.article_introduction

    def get_article_chapters_name(self) -> list[str] | None:
        return self.article_chapters_name

    def get_article_chapters_contents(self) -> list[str] | None:
        return self.article_chapters_content

    def get_count_chapters_content(self) -> int:
        if self.article_chapters_content is None:
            return 0
        return len(self.article_chapters_content)

    def get_final_article(self) -> str | None:
        return self.final_article

    def get_problems(self) -> list[str]:
        return self.problems

    def set_article_title(self, article_title: str) -> None:
        self.article_title = article_title

    def set_article_introduction(self, article_introduction: str) -> None:
        self.article_introduction = article_introduction

    def set_article_chapters_name(self, article_chapters_name: list[str]) -> None:
        self.article_chapters_name = article_chapters_name

    def set_article_chapters_content(self, article_chapters_content: list[str]) -> None:
        self.article_chapters_content = article_chapters_content

    def add_article_chapters_content(self, article_chapters_content: str) -> None:
        if self.article_chapters_content is None:
            self.article_chapters_content = []
        self.article_chapters_content.append(article_chapters_content)

    def set_final_article(self, final_article: str) -> None:
        self.final_article = final_article

    def set_problems(self, problems: list[str]) -> None:
        self.problems = problems

    def add_problem(self, problem: str) -> None:
        self.problems.append(problem)
