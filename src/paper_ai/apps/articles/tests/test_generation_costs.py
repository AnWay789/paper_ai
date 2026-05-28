from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from paper_ai.apps.articles.generation.statuses import ProjectStatus
from paper_ai.apps.articles.llm.result import GenerationResult, TokenUsage
from paper_ai.apps.articles.models import (
    ArticlePaper,
    ArticleProject,
    LLMModels,
    LlmTokenPrice,
    PromtTemplate,
)
from paper_ai.apps.articles.services.costs import add_usage_cost
from paper_ai.apps.articles.services.generation import (
    _estimate_step_costs,
    estimate_generation_costs,
    run_generation_step,
    save_generation_estimate,
    start_generation,
)
from paper_ai.apps.articles.services.llm_token_counter import LlmTokenCounter


class GenerationCostsTests(TestCase):
    def setUp(self) -> None:
        LlmTokenPrice.objects.create(
            model_name="gpt-4o-mini",
            input_price=Decimal("1.00"),
            output_price=Decimal("2.00"),
            per_count_tokens=1_000_000,
        )
        self.llm_model = LLMModels.objects.create(
            model_name="Test",
            model_system_name="gpt-4o-mini",
        )
        paper = ArticlePaper.objects.create()
        self.project = ArticleProject.objects.create(
            marker="test " * 200,
            depth=[["word", 1]] * 20,
            width=["keyword"] * 30,
            n_gramms=[],
            count_chapters=2,
            about_author="author",
            status="new",
            article_paper=paper,
            llm_model=self.llm_model,
        )
        for status in (
            ProjectStatus.GENERATE_TITLE,
            ProjectStatus.GENERATE_INTRODUCTION,
            ProjectStatus.GENERATE_CHAPTERS_NAME,
            ProjectStatus.GENERATE_CHAPTERS_CONTENT,
        ):
            PromtTemplate.objects.create(
                status=status.value,
                template=(
                    "Prompt for {marker} depth {depth} width {width} "
                    "chapters {count_chapters} author {about_author}"
                ),
                expected_output_ratio=Decimal("0.1000"),
            )

    def test_add_usage_cost_accumulates_factual_costs(self) -> None:
        usage = TokenUsage(
            input_tokens=1_000_000,
            output_tokens=500_000,
            cached_input_tokens=0,
            source="api",
        )
        add_usage_cost(self.project, usage)
        self.assertEqual(self.project.cost_input, Decimal("1.0000"))
        self.assertEqual(self.project.cost_output, Decimal("1.0000"))
        self.assertEqual(self.project.cost_total, Decimal("2.0000"))

    def test_estimate_generation_costs_returns_positive_amounts(self) -> None:
        est_input, est_output = estimate_generation_costs(self.project)
        self.assertGreater(est_input, Decimal("0"))
        self.assertGreater(est_output, Decimal("0"))

    def test_higher_output_ratio_increases_estimate(self) -> None:
        template = PromtTemplate.objects.get(
            status=ProjectStatus.GENERATE_TITLE.value
        )
        token_counter = LlmTokenCounter("gpt-4o-mini")
        prompt = "word " * 500

        template.expected_output_ratio = Decimal("0.1000")
        template.save(update_fields=["expected_output_ratio"])
        _, output_low = _estimate_step_costs(token_counter, prompt, template)

        template.expected_output_ratio = Decimal("0.5000")
        template.save(update_fields=["expected_output_ratio"])
        _, output_high = _estimate_step_costs(token_counter, prompt, template)

        self.assertGreater(output_high, output_low)

    def test_save_generation_estimate_without_start(self) -> None:
        self.project.cost_input = Decimal("3.0000")
        self.project.cost_output = Decimal("4.0000")
        self.project.cost_total = Decimal("7.0000")
        self.project.save(update_fields=["cost_input", "cost_output", "cost_total"])

        save_generation_estimate(str(self.project.id))
        self.project.refresh_from_db()

        self.assertEqual(self.project.status, "new")
        self.assertGreater(self.project.estimated_cost_total, Decimal("0"))
        self.assertEqual(self.project.cost_input, Decimal("3.0000"))
        self.assertEqual(self.project.cost_output, Decimal("4.0000"))
        self.assertEqual(self.project.cost_total, Decimal("7.0000"))

    @patch("paper_ai.apps.articles.services.generation.estimate_generation_costs")
    def test_start_generation_resets_factual_and_sets_estimate(
        self,
        mock_estimate,
    ) -> None:
        mock_estimate.return_value = (Decimal("0.5000"), Decimal("1.0000"))
        self.project.cost_input = Decimal("9.9999")
        self.project.cost_output = Decimal("9.9999")
        self.project.save(update_fields=["cost_input", "cost_output", "cost_total"])

        start_generation(str(self.project.id))
        self.project.refresh_from_db()

        self.assertEqual(self.project.estimated_cost_input, Decimal("0.5000"))
        self.assertEqual(self.project.estimated_cost_output, Decimal("1.0000"))
        self.assertEqual(self.project.estimated_cost_total, Decimal("1.5000"))
        self.assertEqual(self.project.cost_input, Decimal("0.0000"))
        self.assertEqual(self.project.cost_output, Decimal("0.0000"))

    @patch("paper_ai.apps.articles.services.generation.get_llm_client")
    def test_run_generation_step_uses_api_usage(self, mock_get_client) -> None:
        self.project.status = ProjectStatus.GENERATE_TITLE.value
        self.project.save(update_fields=["status"])

        mock_client = MagicMock()
        mock_client.generate.return_value = GenerationResult(
            text="Test Title",
            usage=TokenUsage(
                input_tokens=1_000_000,
                output_tokens=100_000,
                source="api",
            ),
        )
        mock_get_client.return_value = mock_client

        run_generation_step(str(self.project.id))
        self.project.refresh_from_db()

        self.assertEqual(self.project.cost_input, Decimal("1.0000"))
        self.assertEqual(self.project.cost_output, Decimal("0.2000"))
        mock_client.generate.assert_called_once()
