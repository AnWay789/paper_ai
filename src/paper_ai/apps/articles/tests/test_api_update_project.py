import json
from decimal import Decimal

from django.test import Client, TestCase

from paper_ai.apps.articles.models import ArticlePaper, ArticleProject, LLMModels


class UpdateProjectApiTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.llm_model = LLMModels.objects.create(
            model_name="Test",
            model_system_name="gpt-4o-mini",
        )
        paper = ArticlePaper.objects.create()
        self.project = ArticleProject.objects.create(
            marker="Маркер тест",
            depth=[["слово", 5]],
            width=["ширина1", "ширина2"],
            n_gramms=["n грамма"],
            count_chapters=3,
            about_author="Автор для тестового проекта",
            status="new",
            article_paper=paper,
            llm_model=self.llm_model,
        )

    def test_put_project(self) -> None:
        payload = {
            "marker": "Обновлённый маркер",
            "depth": [{"keyword": "новый", "count": 7}],
            "width": ["ширина1", "ширина2"],
            "n_gramms": ["n грамма"],
            "count_chapters": 5,
            "about_author": "Обновлённый автор проекта",
            "llm_model_id": self.llm_model.id,
        }
        response = self.client.put(
            f"/api/projects/{self.project.id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["marker"], "Обновлённый маркер")
        self.assertEqual(data["count_chapters"], 5)
