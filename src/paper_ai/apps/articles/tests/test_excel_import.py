from io import BytesIO

from django.test import SimpleTestCase, TestCase
from openpyxl import Workbook

from paper_ai.apps.articles.models import LLMModels
from paper_ai.apps.articles.services.excel_import import (
    parse_depth,
    parse_list,
    parse_workbook,
)
from paper_ai.apps.articles.services.project import resolve_llm_model_id


class ExcelImportParserTests(SimpleTestCase):
    def test_parse_depth(self) -> None:
        depth = parse_depth("учета 30, управленческий 20, компании 10")
        self.assertEqual(
            depth,
            [("учета", 30), ("управленческий", 20), ("компании", 10)],
        )

    def test_parse_depth_invalid_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_depth("только слово")

    def test_parse_list_strips_nbsp(self) -> None:
        items = parse_list("один,\xa0два, три")
        self.assertEqual(items, ["один", "два", "три"])

    def _workbook_bytes(self, rows: list[list]) -> BytesIO:
        workbook = Workbook()
        sheet = workbook.active
        for row in rows:
            sheet.append(row)
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return buffer

    def test_parse_workbook_valid_row(self) -> None:
        data = self._workbook_bytes(
            [
                ["маркер", "глубина", "ширина", "n-грамма", "кол-во разделов", "блок о авторе"],
                [
                    "Тест маркер",
                    "слово 5, другое 3",
                    "ширина1, ширина2",
                    "фраза один, фраза два",
                    4,
                    "Автор статьи для теста",
                ],
            ]
        )
        parsed, errors = parse_workbook(data)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(parsed), 1)
        _row, row = parsed[0]
        self.assertEqual(_row, 2)
        self.assertEqual(row.marker, "Тест маркер")
        self.assertEqual(row.count_chapters, 4)

    def test_parse_workbook_incomplete_row_returns_error(self) -> None:
        data = self._workbook_bytes(
            [
                ["маркер", "глубина", "ширина", "n-грамма", "кол-во разделов", "блок о авторе"],
                [
                    "Только маркер",
                    "",
                    "",
                    "",
                    "",
                    "",
                ],
            ]
        )
        parsed, errors = parse_workbook(data)
        self.assertEqual(len(parsed), 0)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].row, 2)


class ExcelImportModelColumnTests(TestCase):
    def setUp(self) -> None:
        self.llm_model = LLMModels.objects.create(
            model_name="GPT-4o Mini",
            model_system_name="gpt-4o-mini",
        )

    def _workbook_bytes(self, rows: list[list]) -> BytesIO:
        workbook = Workbook()
        sheet = workbook.active
        for row in rows:
            sheet.append(row)
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return buffer

    def test_parse_workbook_model_column(self) -> None:
        data = self._workbook_bytes(
            [
                [
                    "маркер",
                    "глубина",
                    "ширина",
                    "n-грамма",
                    "кол-во разделов",
                    "блок о авторе",
                    "модель",
                ],
                [
                    "Тест маркер",
                    "слово 5",
                    "ширина1, ширина2",
                    "фраза",
                    2,
                    "Автор статьи для теста",
                    "GPT-4o Mini",
                ],
            ]
        )
        parsed, errors = parse_workbook(data)
        self.assertEqual(errors, [])
        self.assertEqual(len(parsed), 1)
        _row, row = parsed[0]
        self.assertEqual(row.llm_model_id, self.llm_model.id)

    def test_resolve_llm_model_by_system_name(self) -> None:
        model_id = resolve_llm_model_id("gpt-4o-mini")
        self.assertEqual(model_id, self.llm_model.id)

    def test_resolve_llm_model_unknown_raises(self) -> None:
        with self.assertRaises(LookupError):
            resolve_llm_model_id("несуществующая-модель")
