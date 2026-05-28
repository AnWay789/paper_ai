from django.test import TestCase

from paper_ai.apps.articles.exceptions.article_project_ex import ArticleProjectAlredyInProgressException
from paper_ai.apps.articles.generation.statuses import ProjectStatus
from paper_ai.apps.articles.models import LLMModels
from paper_ai.apps.articles.services.project import create_project, get_project, update_project


class UpdateProjectTests(TestCase):
    def setUp(self) -> None:
        self.llm_model = LLMModels.objects.create(
            model_name="Test",
            model_system_name="gpt-4o-mini",
        )
        self.project_id = create_project(
            marker="Старый маркер",
            depth=[("слово", 5)],
            width=["ширина1", "ширина2"],
            n_gramms=["n грам"],
            count_chapters=3,
            about_author="Автор тестового проекта",
            llm_model_id=self.llm_model.id,
        )

    def test_update_project_changes_fields(self) -> None:
        project = update_project(
            self.project_id,
            marker="Новый маркер",
            depth=[("ключ", 10), ("другой", 2)],
            width=["новая"],
            n_gramms=[],
            count_chapters=4,
            about_author="Новый автор проекта",
            llm_model_id=self.llm_model.id,
        )
        self.assertEqual(project.marker, "Новый маркер")
        self.assertEqual(project.count_chapters, 4)
        self.assertEqual(project.get_depth(), [("ключ", 10), ("другой", 2)])

    def test_update_project_blocked_while_in_progress(self) -> None:
        project = get_project(self.project_id)
        project.status = ProjectStatus.GENERATE_TITLE.value
        project.save(update_fields=["status"])

        with self.assertRaises(ArticleProjectAlredyInProgressException):
            update_project(
                self.project_id,
                marker="Новый маркер",
                depth=[("ключ", 10)],
                width=["ширина1", "ширина2"],
                n_gramms=[],
                count_chapters=3,
                about_author="Автор тестового проекта",
            )
