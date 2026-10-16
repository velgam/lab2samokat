from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from ..exceptions import DomainInvariantViolation
from ..value_objects import Money, ScooterId, Tariff, TimeSlot


class RideStatus(Enum):
    """Статус поездки."""

    ACTIVE = "active"    # идёт
    FINISHED = "finished"  # завершена


@dataclass
class Ride:
    """Агрегат поездки.

    Инварианты:
    - поездку нельзя завершить дважды;
    - время окончания не может быть раньше времени начала;
    - стоимость поездки не может быть меньше минимальной по тарифу.

    Связь с агрегатом Scooter — только через scooter_id.
    """

    ride_id: str
    scooter_id: ScooterId
    start_time: datetime
    tariff: Tariff
    _end_time: Optional[datetime] = field(default=None, repr=False)
    _status: RideStatus = field(default=RideStatus.ACTIVE, repr=False)
    _cost: Optional[Money] = field(default=None, repr=False)

    # ---------- публичное чтение ----------

    @property
    def status(self) -> RideStatus:
        return self._status

    @property
    def end_time(self) -> Optional[datetime]:
        return self._end_time

    @property
    def cost(self) -> Optional[Money]:
        return self._cost

    # ---------- поведение ----------

    def finish(self, end_time: datetime) -> Money:
        """Завершить поездку и рассчитать стоимость.

        Инварианты:
        - поездку нельзя завершить дважды;
        - время окончания не может быть раньше времени начала.
        """
        if self._status is RideStatus.FINISHED:
            raise DomainInvariantViolation(
                f"Поездка {self.ride_id} уже завершена"
            )
        if end_time < self.start_time:
            raise DomainInvariantViolation(
                "Время окончания не может быть раньше времени начала"
            )

        slot = TimeSlot(start=self.start_time, end=end_time)
        cost = self.tariff.calculate(slot.duration_minutes)

        self._end_time = end_time
        self._cost = cost
        self._status = RideStatus.FINISHED
        return cost