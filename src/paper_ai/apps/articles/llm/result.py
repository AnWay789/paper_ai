from dataclasses import dataclass
from typing import Literal

UsageSource = Literal["api", "estimate"]


@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int = 0
    source: UsageSource = "api"

    def __post_init__(self) -> None:
        if self.input_tokens < 0 or self.output_tokens < 0 or self.cached_input_tokens < 0:
            raise ValueError("token counts must be non-negative")
        if self.cached_input_tokens > self.input_tokens:
            object.__setattr__(
                self,
                "cached_input_tokens",
                self.input_tokens,
            )


@dataclass(frozen=True)
class GenerationResult:
    text: str
    usage: TokenUsage
