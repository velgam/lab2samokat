from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ..exceptions import DomainInvariantViolation
from ..value_objects import BatteryLevel, ScooterId


class ScooterStatus(Enum):
    """Статус самоката."""

    AVAILABLE = "available"     
    IN_USE = "in_use"            
    MAINTENANCE = "maintenance"  


@dataclass
class Scooter:
    """Агрегат самоката.

    Инварианты:
    - самокат с зарядом ниже минимального порога не может быть выдан в аренду;
    - самокат не может быть выдан, если он уже арендован или на обслуживании.
    """

    scooter_id: ScooterId
    battery: BatteryLevel
    minimum_battery: int = 20  # минимальный порог заряда (в %)
    _status: ScooterStatus = field(default=ScooterStatus.AVAILABLE, repr=False)

    @property
    def status(self) -> ScooterStatus:
        return self._status

    @property
    def is_available(self) -> bool:
        return self._status is ScooterStatus.AVAILABLE


    def issue(self) -> None:
        """Выдать самокат в аренду.

        Инварианты:
        - заряд должен быть не ниже минимального порога;
        - самокат должен быть свободен.
        """
        if self._status is ScooterStatus.MAINTENANCE:
            raise DomainInvariantViolation(
                f"Самокат {self.scooter_id.value} находится на обслуживании"
            )
        if self._status is ScooterStatus.IN_USE:
            raise DomainInvariantViolation(
                f"Самокат {self.scooter_id.value} уже арендован"
            )
        if self.battery.is_below(self.minimum_battery):
            raise DomainInvariantViolation(
                f"Заряд самоката {self.scooter_id.value} ниже минимального порога "
                f"({self.battery.percent}% < {self.minimum_battery}%)"
            )
        self._status = ScooterStatus.IN_USE

    def release(self) -> None:
        """Вернуть самокат после поездки."""
        if self._status is not ScooterStatus.IN_USE:
            raise DomainInvariantViolation(
                f"Самокат {self.scooter_id.value} не находится в аренде"
            )
        self._status = ScooterStatus.AVAILABLE

    def send_to_maintenance(self) -> None:
        """Отправить самокат на обслуживание."""
        if self._status is ScooterStatus.IN_USE:
            raise DomainInvariantViolation(
                f"Нельзя отправить на обслуживание арендованный самокат "
                f"{self.scooter_id.value}"
            )
        self._status = ScooterStatus.MAINTENANCE