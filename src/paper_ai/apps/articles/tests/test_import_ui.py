from io import BytesIO

from django.test import Client, TestCase
from django.urls import reverse
from openpyxl import Workbook

from paper_ai.apps.articles.models import ArticleProject, LLMModels


class ImportUiTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.llm_model = LLMModels.objects.create(
            model_name="GPT Test",
            model_system_name="gpt-4o-mini",
        )

    def _workbook_upload(self) -> bytes:
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["маркер", "глубина", "ширина", "n-грамма", "кол-во разделов", "блок о авторе"])
        sheet.append(
            [
                "Импорт UI тест",
                "ключ 10",
                "слово1, слово2",
                "фраза",
                2,
                "Автор для UI импорта теста",
            ]
        )
        buffer = BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()

    def test_import_ui_applies_selected_llm_model(self) -> None:
        from django.core.files.uploadedfile import SimpleUploadedFile

        upload = SimpleUploadedFile(
            "import.xlsx",
            self._workbook_upload(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response = self.client.post(
            reverse("articles:project_import"),
            {"llm_model_id": str(self.llm_model.id), "file": upload},
        )
        self.assertEqual(response.status_code, 302)
        project = ArticleProject.objects.get()
        self.assertEqual(project.llm_model_id, self.llm_model.id)

    def test_import_ui_empty_model_column_uses_form_selection(self) -> None:
        from django.core.files.uploadedfile import SimpleUploadedFile

        workbook = Workbook()
        sheet = workbook.active
        sheet.append(
            [
                "маркер",
                "глубина",
                "ширина",
                "n-грамма",
                "кол-во разделов",
                "блок о авторе",
                "модель",
            ]
        )
        sheet.append(
            [
                "Импорт с пустой моделью",
                "ключ 10",
                "слово1, слово2",
                "фраза",
                2,
                "Автор для теста пустой модели",
                None,
            ]
        )
        buffer = BytesIO()
        workbook.save(buffer)
        upload = SimpleUploadedFile(
            "import.xlsx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response = self.client.post(
            reverse("articles:project_import"),
            {"llm_model_id": str(self.llm_model.id), "file": upload},
        )
        self.assertEqual(response.status_code, 302)
        project = ArticleProject.objects.get()
        self.assertEqual(project.llm_model_id, self.llm_model.id)
