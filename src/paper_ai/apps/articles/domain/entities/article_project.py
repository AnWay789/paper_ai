from datetime import datetime
from .article_paper import ArticlePaper
from ..value_objects.project_statuses import ProjectStatus
from ..value_objects.project_statuses import in_progress_statuses
from ..value_objects.generation_step import (
    get_generation_step,
    is_generation_step,
)
from ..policies.status_transition_policy import (
    ALLOWED_STATUS_TRANSITIONS,
    can_start_generation,
)
from ..services.article_seo_analyzer import ArticleSeoAnalyzer
from ..exceptions.article_project_ex import ArticleProjectAlredyInProgressException
from ..exceptions.status_ex import InvalidStatusChangeException
from ..exceptions.generation_ex import InvalidGenerationStepException
from ..exceptions.marker_ex import (
    EmptyMarkerException,
    MaxMarkerLengthException,
    MinMarkerLengthException,
)
from ..exceptions.keyword_ex import (
    MinKeywordLengthException,
    MaxKeywordLengthException,
    MinKeywordCountException,
    MaxKeywordCountException,
)
from ..exceptions.width_ex import (
    MinWidthLengthException,
    MaxWidthLengthException,
)
from ..exceptions.n_gramm_ex import (
    MinNGrammsLengthException,
    MaxNGrammsLengthException,
    MinNGrammsCountException,
    MaxNGrammsCountException,
)
from ..exceptions.atricle_paper_ex import (
    ArticlePaperDoesNotExist,
    ArticlePaperTitleDoesNotExist,
    ArticlePaperIntroductionDoesNotExist,
    ArticlePaperChaptersNameDoesNotExist,
    ArticlePaperChaptersContentDoesNotExist,
    ArticlePaperFinalArticleDoesNotExist,
)
from ..exceptions.count_chapters_ex import (
    MinCountChaptersException,
    MaxCountChaptersException,
)
from ..exceptions.about_autor_ex import (
    MinAboutAuthorException,
    MaxAboutAuthorException,
)
from ..exceptions.depth_ex import (
    MinDepthLengthException,
    MaxDepthLengthException,
)

# константы
max_marker_length = 100 # максимальная длина маркера
min_marker_length = 2 # минимальная длина маркера

min_keyword_length = 2 # минимальная длина ключевого слова
max_keyword_length = 100 # максимальная длина ключевого слова
min_keyword_count = 1 # минимальное количество ключевых слов
max_keyword_count = 100 # максимальное количество ключевых слов

min_depth_length = 1 # минимальная длина глубины статьи
max_depth_length = 100 # максимальная длина глубины статьи
min_width_length = 2 # минимальная длина ширины статьи
max_width_length = 200 # максимальная длина ширины статьи

max_n_gramms_length = 100 # максимальная длина n-граммы
min_n_gramms_length = 2 # минимальная длина n-граммы
max_n_gramms_count = 100 # максимальное количество n-грамм
min_n_gramms_count = 0 # минимальное количество n-грамм

min_count_chapters = 1 # минимальное количество глав
max_count_chapters = 20 # максимальное количество глав

min_about_author_length = 2 # минимальная длина о авторе
max_about_author_length = 300 # максимальная длина о авторе

# TODO: Разбить класс, сейчас он огромный God entity.
class ArticleProject:
    """
    Проект статьи включая саму статью, статус генерации и время создания
    """
    def __init__(
        self,
        id: str,
        marker: str, # смысл статьи
        depth: list[tuple[str, int]], # ключевые слова и их количество
        width: list[str], # доп ключевые слова
        n_gramms: list[str], # n-граммы
        count_chapters: int, # количество глав
        about_author: str, # о авторе
        status: ProjectStatus, # статус генерации
        created_at: datetime, # время создания проекта
        article_paper: ArticlePaper | None = None, # статья
    ):
        """
        ! Не использовать этот метод для создания проекта статьи !
        Используйте метод create для создания проекта статьи
        """
        self.id = id
        self.marker = marker
        self.depth = depth
        self.width = width
        self.n_gramms = n_gramms
        self.count_chapters = count_chapters
        self.about_author = about_author
        self.status = status
        self.created_at = created_at
        self.article_paper = article_paper

    @staticmethod
    def reconstitute(
        id: str,
        marker: str,
        depth: list[tuple[str, int]],
        width: list[str],
        n_gramms: list[str],
        count_chapters: int,
        about_author: str,
        status: ProjectStatus,
        created_at: datetime,
        article_paper: ArticlePaper | None = None,
    ) -> "ArticleProject":
        ArticleProject._validate_marker(marker)
        ArticleProject._validate_depth(depth)
        ArticleProject._validate_width(width)
        ArticleProject._validate_n_gramms(n_gramms)
        ArticleProject._validate_count_chapters(count_chapters)
        ArticleProject._validate_about_author(about_author)
        return ArticleProject(
            id=id,
            marker=marker,
            depth=depth,
            width=width,
            n_gramms=n_gramms,
            count_chapters=count_chapters,
            about_author=about_author,
            status=status,
            created_at=created_at,
            article_paper=article_paper,
        )

    @classmethod
    def create(
        cls, 
        id: str, 
        marker: str, 
        depth: list[tuple[str, int]], 
        width: list[str], 
        n_gramms: list[str], 
        count_chapters: int, 
        about_author: str,
        article_paper_id: str
    ) -> "ArticleProject":
        """ Создание проекта статьи с пустой статьей с заданным id """
        cls._validate_marker(marker)
        cls._validate_depth(depth)
        cls._validate_width(width)
        cls._validate_n_gramms(n_gramms)
        cls._validate_count_chapters(count_chapters)
        cls._validate_about_author(about_author)
        
        return ArticleProject(
            id=id,
            marker=marker,
            depth=depth,
            width=width,
            n_gramms=n_gramms,
            count_chapters=count_chapters,
            about_author=about_author,
            status=ProjectStatus.NEW,
            created_at=datetime.now(),
            article_paper=ArticlePaper(article_paper_id),
        )

    def start_generation(self) -> None:
        """Запускает пайплайн генерации, переводя проект на первый шаг."""
        if not can_start_generation(self.status):
            raise InvalidStatusChangeException(
                f"Нельзя запустить генерацию из статуса {self.status}"
            )
        self.change_status(ProjectStatus.GENERATE_TITLE)

    def apply_generation_step(self, response: str | list[str]) -> None:
        if not is_generation_step(self.status):
            raise InvalidGenerationStepException(
                f"Статус {self.status} не является шагом генерации"
            )
        step = get_generation_step(self.status)
        step.apply(self, response)
        if step.post_apply is not None:
            step.post_apply(self)
        step.advance(self)

    def is_completed(self) -> bool:
        return self.status == ProjectStatus.COMPLETED

    def get_id(self) -> str:
        return self.id
    
    def update(self, **kwargs) -> None:
        """
        Обновление проекта статьи
        """
        for key, value in kwargs.items():
            if key == "marker" and value is not None:
                self.set_marker(value)
            elif key == "depth" and value is not None:
                self.set_depth(value)
            elif key == "width" and value is not None:
                self.set_width(value)
            elif key == "n_gramms" and value is not None:
                self.set_n_gramms(value)
            elif key == "count_chapters" and value is not None:
                self.set_count_chapters(value)
            elif key == "about_author" and value is not None:
                self.set_about_author(value)

    def find_problems(self) -> None:
        """Находит SEO-проблемы в сгенерированной статье."""
        if not self.article_paper:
            raise ArticlePaperDoesNotExist("Статья еще не создана")
        problems = ArticleSeoAnalyzer().analyze(self)
        self.article_paper.set_problems(problems)

    def get_problems_by_text(self) -> str:
        problems = self.get_problems()
        if not problems:
            return "Нет проблем"
        return "\n".join(problems)

    def to_error_status(self) -> None:
        self.change_status(ProjectStatus.ERROR)

# маркер
    def get_marker(self) -> str:
        return self.marker

    def _set_marker(self, marker: str) -> None:
        self.marker = marker

    @staticmethod
    def _validate_marker(marker: str) -> None:
        if marker is None or marker == "":
            raise EmptyMarkerException(f"Маркер не может быть пустым")
        if len(marker) > max_marker_length:
            raise MaxMarkerLengthException(f"Маркер не может быть длиннее {max_marker_length} символов")
        if len(marker) < min_marker_length:
            raise MinMarkerLengthException(f"Маркер не может быть короче {min_marker_length} символов")

    def set_marker(self, marker: str) -> None:
        ArticleProject._validate_marker(marker)
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self._set_marker(marker)


# ключевые слова (ширина) и их количество
    def get_width(self) -> list[str]:
        return self.width

    def get_width_by_text(self) -> str:
        """
        Возвращает текст с шириной статьи
        """
        text = ""
        for width in self.width:
            text += f"\"{width}\", "
        return text

    @staticmethod
    def _validate_width(width: list[str]) -> None:
        for word in width:
            if len(word) < min_width_length:
                raise MinWidthLengthException(f"Ширина статьи не может быть короче {min_width_length} символов")
            if len(word) > max_width_length:
                raise MaxWidthLengthException(f"Ширина статьи не может быть длиннее {max_width_length} символов")

    def _set_width(self, width: list[str]) -> None:
        self.width = width

    def _add_width(self, width: str) -> None:
        self.width.append(width)

    def set_width(self, width: list[str]) -> None:
        ArticleProject._validate_width(width)
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self._set_width(width)

    def add_width(self, width: str) -> None:
        ArticleProject._validate_width([width])
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self._add_width(width)


# n-граммы
    def get_n_gramms(self) -> list[str]:
        return self.n_gramms

    def get_n_gramms_by_text(self) -> str:
        """
        Возвращает текст с n-граммами
        """
        text = ""
        for n_gramm in self.n_gramms:
            text += f"\"{n_gramm}\", "
        return text if text != "" else "Нет n-грамм"

    @staticmethod
    def _validate_n_gramms(n_gramms: list[str]) -> None:
        if len(n_gramms) < min_n_gramms_count:
                raise MinNGrammsCountException(f"Количество n-грамм не может быть меньше {min_n_gramms_count}")
        if len(n_gramms) > max_n_gramms_count:
            raise MaxNGrammsCountException(f"Количество n-грамм не может быть больше {max_n_gramms_count}")
        for n_gramm in n_gramms:
            if len(n_gramm) < min_n_gramms_length:
                raise MinNGrammsLengthException(f"N-грамма не может быть короче {min_n_gramms_length} символов")
            if len(n_gramm) > max_n_gramms_length:
                raise MaxNGrammsLengthException(f"N-грамма не может быть длиннее {max_n_gramms_length} символов")
            
    def _set_n_gramms(self, n_gramms: list[str]) -> None:
        self.n_gramms = n_gramms

    def set_n_gramms(self, n_gramms: list[str]) -> None:
        ArticleProject._validate_n_gramms(n_gramms)
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self._set_n_gramms(n_gramms)

    def _add_n_gramms(self, n_gramm: str) -> None:
        self.n_gramms.append(n_gramm)

    def add_n_gramms(self, n_gramm: str) -> None:
        ArticleProject._validate_n_gramms([n_gramm])
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self._add_n_gramms(n_gramm)


# количество глав
    def get_count_chapters(self) -> int:
        return self.count_chapters

    def _set_count_chapters(self, count_chapters: int) -> None:
        self.count_chapters = count_chapters

    def set_count_chapters(self, count_chapters: int) -> None:
        ArticleProject._validate_count_chapters(count_chapters)
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self._set_count_chapters(count_chapters)

    @staticmethod
    def _validate_count_chapters(count_chapters: int) -> None:
        if count_chapters < min_count_chapters:
            raise MinCountChaptersException(f"Количество глав не может быть меньше {min_count_chapters}")
        if count_chapters > max_count_chapters:
            raise MaxCountChaptersException(f"Количество глав не может быть больше {max_count_chapters}")


# о авторе
    def get_about_author(self) -> str:
        return self.about_author

    def _set_about_author(self, about_author: str) -> None:
        self.about_author = about_author

    def set_about_author(self, about_author: str) -> None:
        ArticleProject._validate_about_author(about_author)
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self._set_about_author(about_author)

    @staticmethod
    def _validate_about_author(about_author: str) -> None:
        if len(about_author) < min_about_author_length:
            raise MinAboutAuthorException(f"О авторе не может быть короче {min_about_author_length} символов")
        if len(about_author) > max_about_author_length:
            raise MaxAboutAuthorException(f"О авторе не может быть длиннее {max_about_author_length} символов")


# статус генерации
    def get_status(self) -> ProjectStatus:
        return self.status

    def _set_status(self, status: ProjectStatus) -> None:
        self.status = status

    def change_status(self, status: ProjectStatus) -> None:
        allowed = ALLOWED_STATUS_TRANSITIONS.get(self.status, [])
        if status not in allowed:
            raise InvalidStatusChangeException(
                f"Недопустимый переход из статуса {self.status} в статус {status}"
            )
        self._set_status(status)

    def is_in_progress(self) -> bool:
        return self.status in in_progress_statuses

    def get_next_status(self) -> ProjectStatus | None:
        if is_generation_step(self.status):
            return get_generation_step(self.status).next_status
        return None


# ключевые слова (глубина) и их количество
    def _set_depth(self, depth: list[tuple[str, int]]) -> None:
        self.depth = depth

    def _add_depth(self, depth: tuple[str, int]) -> None:
        self.depth.append(depth)

    @staticmethod
    def _validate_depth(depth: list[tuple[str, int]]) -> None:
        if len(depth) < min_depth_length:
            raise MinDepthLengthException(f"Глубина не может быть меньше {min_depth_length} символов")
        if len(depth) > max_depth_length:
            raise MaxDepthLengthException(f"Глубина не может быть длиннее {max_depth_length} символов")
        for keyword in depth:
            if len(keyword[0]) < min_keyword_length:
                raise MinKeywordLengthException(f"Ключевое слово не может быть короче {min_keyword_length} символов")
            if len(keyword[0]) > max_keyword_length:
                raise MaxKeywordLengthException(f"Ключевое слово не может быть длиннее {max_keyword_length} символов")
            if keyword[1] < min_keyword_count:
                raise MinKeywordCountException(f"Количество ключевых слов не может быть меньше {min_keyword_count}")
            if keyword[1] > max_keyword_count:
                raise MaxKeywordCountException(f"Количество ключевых слов не может быть больше {max_keyword_count}")

    def set_depth(self, depth: list[tuple[str, int]]) -> None:
        ArticleProject._validate_depth(depth)
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self._set_depth(depth)

    def add_depth(self, depth: tuple[str, int]) -> None:
        self._validate_depth([depth])
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self._add_depth(depth)

    def get_depth(self) -> list[tuple[str, int]]:
        return self.depth
    
    def get_depth_by_text(self) -> str:
        """
        Возвращает текст с ключевыми словами и их количеством
        в формате текста для промтов и тд
        """
        text = ""
        for keyword in self.depth:
            word = keyword[0]
            count = keyword[1]
            text += f"\"{word}\" count:{count}, "
        return text

    def get_depth_by_json(self) -> list[list[str | int]]:
        """
        Возвращает список с ключевыми словами и их количеством
        в формате json для промтов и тд
        """
        return [[word, count] for word, count in self.depth]


# статья
    def get_article_paper(self) -> ArticlePaper | None:
        return self.article_paper

    def _set_article_paper(self, article_paper: ArticlePaper) -> None:
        self.article_paper = article_paper

    def set_article_paper(self, article_paper: ArticlePaper) -> None:
        if self.is_in_progress():
            raise ArticleProjectAlredyInProgressException(f"Проект статьи уже в процессе")
        self.article_paper = article_paper

    def get_article_title(self) -> str:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        if not (article_title:=self.article_paper.get_article_title()):
            raise ArticlePaperTitleDoesNotExist(f"Заголовок статьи еще не создан")
        return article_title

    def get_article_introduction(self) -> str:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        if not (article_introduction:=self.article_paper.get_article_introduction()):
            raise ArticlePaperIntroductionDoesNotExist(f"Введение статьи еще не создано")
        return article_introduction

    def get_article_chapters_name(self) -> list[str]:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        if not (article_chapters_name:=self.article_paper.get_article_chapters_name()):
            raise ArticlePaperChaptersNameDoesNotExist(f"Названия глав статьи еще не созданы")
        return article_chapters_name

    def get_article_chapters_name_by_text(self) -> str:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        if not (article_chapters_name:=self.article_paper.get_article_chapters_name()):
            raise ArticlePaperChaptersNameDoesNotExist(f"Названия глав статьи еще не созданы")
        text_chapter_names = ""
        for chapter_name in article_chapters_name:
            text_chapter_names += f"\"{chapter_name}\",\n"
        return text_chapter_names

    def get_article_chapters_contents(self) -> list[str]:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        if not (article_chapters_contents:=self.article_paper.get_article_chapters_contents()):
            raise ArticlePaperChaptersContentDoesNotExist(f"Содержание глав статьи еще не создано")
        return article_chapters_contents

    def get_count_chapters_content(self) -> int:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        return self.article_paper.get_count_chapters_content()

    def get_article_chapters_contents_by_text(self) -> str:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        if not (article_chapters_contents:=self.article_paper.get_article_chapters_contents()):
            raise ArticlePaperChaptersContentDoesNotExist(f"Содержание глав статьи еще не создано")
        text_chapter_contents = ""
        for chapter_content in article_chapters_contents:
            text_chapter_contents += f"\"{chapter_content}\",\n"
        return text_chapter_contents

    def get_final_article(self) -> str:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        if not (final_article:=self.article_paper.get_final_article()):
            raise ArticlePaperFinalArticleDoesNotExist(f"Статья еще не создана")
        return final_article

    def get_problems(self) -> list[str | None]:
        """ Возвращает список проблем сгенерированной статьи """
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        if not (problems:=self.article_paper.get_problems()):
            return []
        return problems

    def set_article_title(self, article_title: str) -> None:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        self.article_paper.set_article_title(article_title)

    def set_article_introduction(self, article_introduction: str) -> None:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        self.article_paper.set_article_introduction(article_introduction)

    def set_article_chapters_name(self, article_chapters_name: list[str]) -> None:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        self.article_paper.set_article_chapters_name(article_chapters_name)

    def set_article_chapters_content(self, article_chapters_content: list[str]) -> None:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        self.article_paper.set_article_chapters_content(article_chapters_content)

    def add_article_chapters_content(self, article_chapters_content: str) -> None:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        self.article_paper.add_article_chapters_content(article_chapters_content)

    def set_final_article(self, final_article: str) -> None:
        if not self.article_paper:
            raise ArticlePaperDoesNotExist(f"Статья еще не создана")
        self.article_paper.set_final_article(final_article)


# время создания проекта
    def get_created_at(self) -> datetime:
        return self.created_at

    def set_created_at(self, created_at: datetime) -> None:
        self.created_at = created_at

