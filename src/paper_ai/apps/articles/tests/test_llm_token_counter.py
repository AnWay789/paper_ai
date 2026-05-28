from decimal import Decimal

from django.test import TestCase

from paper_ai.apps.articles.exceptions.generation_ex import InvalidGenerationStepException
from paper_ai.apps.articles.llm.result import TokenUsage
from paper_ai.apps.articles.models import LlmTokenPrice
from paper_ai.apps.articles.services.costs import COST_QUANTIZE
from paper_ai.apps.articles.services.llm_token_counter import LlmTokenCounter
from paper_ai.apps.articles.services.token_types import PriceKind


class LlmTokenCounterTests(TestCase):
    def setUp(self) -> None:
        self.token_price = LlmTokenPrice.objects.create(
            model_name="gpt-4o-mini",
            input_price=Decimal("0.15"),
            output_price=Decimal("0.60"),
            cached_input_price=Decimal("0.08"),
            per_count_tokens=1_000_000,
        )

    def test_price_from_usage_splits_cached_input(self) -> None:
        counter = LlmTokenCounter("gpt-4o-mini")
        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            cached_input_tokens=400,
            source="api",
        )
        input_cost, output_cost = counter.price_from_usage(usage, quantize=True)

        expected_input = counter.count_price_for_tokens(
            600, PriceKind.INPUT, quantize=False
        ) + counter.count_price_for_tokens(400, PriceKind.CACHED_INPUT, quantize=False)
        expected_output = counter.count_price_for_tokens(
            500, PriceKind.OUTPUT, quantize=False
        )

        self.assertEqual(input_cost, expected_input.quantize(COST_QUANTIZE))
        self.assertEqual(output_cost, expected_output.quantize(COST_QUANTIZE))

    def test_cached_price_falls_back_to_input_price(self) -> None:
        self.token_price.cached_input_price = None
        self.token_price.save(update_fields=["cached_input_price"])
        counter = LlmTokenCounter("gpt-4o-mini")
        usage = TokenUsage(
            input_tokens=100,
            output_tokens=0,
            cached_input_tokens=100,
            source="api",
        )
        input_cost, _ = counter.price_from_usage(usage, quantize=True)
        expected = counter.count_price_for_tokens(100, PriceKind.INPUT, quantize=True)
        self.assertEqual(input_cost, expected)

    def test_missing_token_price_raises_clear_error(self) -> None:
        with self.assertRaises(InvalidGenerationStepException) as ctx:
            LlmTokenCounter("unknown-model")
        self.assertIn("unknown-model", str(ctx.exception))

    def test_accumulated_input_cost_visible_after_several_steps(self) -> None:
        counter = LlmTokenCounter("gpt-4o-mini")
        prompt = "слово " * 3000
        total = Decimal("0")
        for _ in range(5):
            total += counter.estimate_text_price(
                prompt, PriceKind.INPUT, quantize=False
            )
        self.assertGreater(total.quantize(COST_QUANTIZE), Decimal("0"))
