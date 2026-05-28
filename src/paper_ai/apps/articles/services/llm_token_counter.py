import math
from decimal import Decimal

import tiktoken
from django.core.exceptions import ObjectDoesNotExist

from ..exceptions.generation_ex import InvalidGenerationStepException
from ..llm.result import TokenUsage
from ..models import LlmTokenPrice
from .costs import COST_QUANTIZE
from .token_types import PriceKind

FALLBACK_CHARS_PER_TOKEN = 3

__all__ = ["FALLBACK_CHARS_PER_TOKEN", "LlmTokenCounter", "PriceKind"]


class LlmTokenCounter:
    """
    Считает количество и цену токенов для текста
    (предназначен для GPT-подобных моделей, для Claude и других моделей нужно переписывать)
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        try:
            self.token_price = LlmTokenPrice.objects.get(model_name=model_name)
        except ObjectDoesNotExist as exc:
            raise InvalidGenerationStepException(
                f"Не найдена цена токенов для модели {model_name!r}. "
                "Добавьте запись LlmTokenPrice с model_name = model_system_name модели."
            ) from exc
        self.encoding = self._get_encoding()

    def _get_encoding(self) -> tiktoken.Encoding | None:
        try:
            return tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            pass
        try:
            return tiktoken.get_encoding("cl100k_base")
        except Exception:
            pass
        return None

    def estimate_tokens(self, text: str) -> int:
        if self.encoding is None:
            return math.ceil(len(text) / FALLBACK_CHARS_PER_TOKEN)
        return len(self.encoding.encode(text))

    def _price_per_token(self, kind: PriceKind) -> Decimal:
        if kind == PriceKind.CACHED_INPUT:
            price = self.token_price.cached_input_price
            if price is None:
                price = self.token_price.input_price
        else:
            price = getattr(self.token_price, kind.price_field)
        return price / Decimal(self.token_price.per_count_tokens)

    def count_price_for_tokens(
        self,
        count_tokens: int,
        kind: PriceKind,
        *,
        quantize: bool = True,
    ) -> Decimal:
        if count_tokens <= 0:
            return Decimal("0")
        amount = Decimal(count_tokens) * self._price_per_token(kind)
        return amount.quantize(COST_QUANTIZE) if quantize else amount

    def price_from_usage(
        self,
        usage: TokenUsage,
        *,
        quantize: bool = False,
    ) -> tuple[Decimal, Decimal]:
        cached = min(usage.cached_input_tokens, usage.input_tokens)
        uncached = usage.input_tokens - cached
        input_cost = self.count_price_for_tokens(
            uncached, PriceKind.INPUT, quantize=False
        ) + self.count_price_for_tokens(cached, PriceKind.CACHED_INPUT, quantize=False)
        output_cost = self.count_price_for_tokens(
            usage.output_tokens, PriceKind.OUTPUT, quantize=False
        )
        if quantize:
            return (
                input_cost.quantize(COST_QUANTIZE),
                output_cost.quantize(COST_QUANTIZE),
            )
        return input_cost, output_cost

    def estimate_text_price(
        self,
        text: str,
        kind: PriceKind,
        *,
        quantize: bool = True,
    ) -> Decimal:
        return self.count_price_for_tokens(
            self.estimate_tokens(text),
            kind,
            quantize=quantize,
        )
