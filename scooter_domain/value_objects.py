from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from .exceptions import InvalidValueObject


@dataclass(frozen=True)
class ScooterId:
    """Идентификатор самоката."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise InvalidValueObject("Идентификатор самоката не может быть пустым")


@dataclass(frozen=True)
class BatteryLevel:
    """Уровень заряда батареи (в процентах)."""

    percent: int

    def __post_init__(self) -> None:
        if not (0 <= self.percent <= 100):
            raise InvalidValueObject(
                f"Уровень заряда должен быть от 0 до 100, получено {self.percent}"
            )

    def is_below(self, threshold: int) -> bool:
        """Проверить, что заряд ниже порога."""
        return self.percent < threshold


@dataclass(frozen=True)
class Money:
    """Сумма денег с валютой."""

    amount: Decimal
    currency: str = "RUB"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidValueObject("Сумма не может быть отрицательной")
        if not self.currency or len(self.currency) != 3:
            raise InvalidValueObject("Код валюты должен состоять из 3 символов")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise InvalidValueObject("Нельзя складывать разные валюты")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: int) -> "Money":
        return Money(self.amount * factor, self.currency)


@dataclass(frozen=True)
class Tariff:
    """Тариф поездки: цена за минуту и минимальная стоимость."""

    price_per_minute: Money
    minimum_price: Money

    def __post_init__(self) -> None:
        if self.price_per_minute.amount <= 0:
            raise InvalidValueObject("Цена за минуту должна быть положительной")
        if self.minimum_price.amount <= 0:
            raise InvalidValueObject("Минимальная стоимость должна быть положительной")

    def calculate(self, minutes: int) -> Money:
        """Рассчитать стоимость поездки с учётом минимума."""
        if minutes <= 0:
            raise InvalidValueObject("Длительность поездки должна быть положительной")
        cost = self.price_per_minute * minutes
        if cost.amount < self.minimum_price.amount:
            return self.minimum_price
        return cost


@dataclass(frozen=True)
class TimeSlot:
    """Интервал времени."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise InvalidValueObject("Окончание не может быть раньше начала")

    @property
    def duration_minutes(self) -> int:
        """Длительность в минутах (минимум 1 минута)."""
        delta = self.end - self.start
        seconds = delta.total_seconds()
        minutes = int(seconds // 60)
        return max(1, minutes)