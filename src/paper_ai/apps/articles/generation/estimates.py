import math
from decimal import Decimal


def expected_output_tokens(prompt_token_count: int, output_ratio: Decimal) -> int:
    """
    Ожидаемое число output-токенов: input_tokens × output_ratio.
    Минимум 1 токен при ненулевом промпте и положительном коэффициенте.
    """
    if prompt_token_count <= 0 or output_ratio <= 0:
        return 0
    return max(1, math.ceil(Decimal(prompt_token_count) * output_ratio))
