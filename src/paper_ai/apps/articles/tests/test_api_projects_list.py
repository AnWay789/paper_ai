import json
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from openpyxl import Workbook

from paper_ai.apps.articles.models import ArticlePaper, ArticleProject, LLMModels


class ProjectsApiTests(TestCase):
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
            estimated_cost_total=Decimal("1.5000"),
        )

    def test_list_projects(self) -> None:
        response = self.client.get("/api/projects")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(payload["total"], 1)
        self.assertTrue(any(item["id"] == str(self.project.id) for item in payload["items"]))

    def test_list_llm_models(self) -> None:
        response = self.client.get("/api/projects/llm-models")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(any(item["id"] == self.llm_model.id for item in payload))

    @patch("paper_ai.apps.articles.api.routes.run_generation_step.delay")
    def test_bulk_estimate(self, delay_mock) -> None:
        delay_mock.return_value = None
        with patch(
            "paper_ai.apps.articles.api.routes.save_generation_estimate",
            return_value=self.project,
        ):
            response = self.client.post(
                "/api/projects/bulk/estimate",
                data=json.dumps({"project_ids": [str(self.project.id)]}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["ok"], [str(self.project.id)])
        self.assertEqual(payload["failed"], [])

    def test_import_workbook(self) -> None:
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["маркер", "глубина", "ширина", "n-грамма", "кол-во разделов", "блок о авторе"])
        sheet.append(
            [
                "Импорт тест",
                "ключ 10",
                "слово1, слово2",
                "биграмма",
                2,
                "Автор импортированного проекта",
            ]
        )
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        upload = SimpleUploadedFile(
            "import.xlsx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response = self.client.post(
            "/api/projects/import",
            {"llm_model_id": str(self.llm_model.id), "file": upload},
        )
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertEqual(len(payload["created"]), 1)
        self.assertEqual(payload["errors"], [])
