from enum import Enum


class PriceKind(Enum):
    INPUT = "input_price"
    OUTPUT = "output_price"
    CACHED_INPUT = "cached_input_price"

    @property
    def price_field(self) -> str:
        return self.value
