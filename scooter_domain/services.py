from datetime import datetime

from .aggregates.ride import Ride
from .aggregates.scooter import Scooter
from .exceptions import DomainInvariantViolation
from .repositories import ScooterRepository


class RideService:
    """Доменный сервис, координирующий работу двух агрегатов:

    - Scooter (состояние самоката);
    - Ride (поездка).

    Сервис не содержит бизнес-логики сам по себе — только координацию:
    загружает нужные агрегаты через репозиторий, вызывает их методы.
    """

    def __init__(self, scooter_repo: ScooterRepository) -> None:
        self._scooter_repo = scooter_repo

    def start_ride(self, ride: Ride) -> None:
        """Начать поездку: выдать самокат и зарегистрировать поездку."""
        scooter = self._scooter_repo.get(ride.scooter_id)
        if scooter is None:
            raise DomainInvariantViolation(
                f"Самокат {ride.scooter_id.value} не найден"
            )
        # инварианты проверяются внутри Scooter.issue()
        scooter.issue()
        self._scooter_repo.save(scooter)

    def finish_ride(self, scooter: Scooter, ride: Ride, end_time: datetime) -> None:
        """Завершить поездку: закрыть Ride и вернуть самокат в строй."""
        # инварианты проверяются внутри Ride.finish()
        ride.finish(end_time)
        # инварианты проверяются внутри Scooter.release()
        scooter.release()
        self._scooter_repo.save(scooter)