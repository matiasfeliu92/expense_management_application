from dataclasses import dataclass
from typing import Optional

from src_v2.domain.exceptions import BalanceZeroError, NegativeBalanceError


@dataclass(frozen=True)
class Balance:
    value: int
    allow_zero: bool = True

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise ValueError("Balance must be an integer")
        if self.value < 0:
            raise NegativeBalanceError("Balance cannot be negative")
        if not self.allow_zero and self.value == 0:
            raise BalanceZeroError("Balance cannot be zero")
