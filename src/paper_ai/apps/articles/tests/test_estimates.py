from decimal import Decimal

from django.test import TestCase

from paper_ai.apps.articles.generation.estimates import expected_output_tokens


class ExpectedOutputTokensTests(TestCase):
    def test_ratio_scales_with_input_tokens(self) -> None:
        self.assertEqual(expected_output_tokens(1000, Decimal("0.1")), 100)
        self.assertEqual(expected_output_tokens(1000, Decimal("0.5")), 500)

    def test_zero_input_or_ratio_returns_zero(self) -> None:
        self.assertEqual(expected_output_tokens(0, Decimal("0.1")), 0)
        self.assertEqual(expected_output_tokens(100, Decimal("0")), 0)

    def test_minimum_one_token_when_positive(self) -> None:
        self.assertEqual(expected_output_tokens(1, Decimal("0.01")), 1)
