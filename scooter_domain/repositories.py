from typing import Dict, Optional, Protocol

from .aggregates.scooter import Scooter
from .value_objects import ScooterId


class ScooterRepository(Protocol):
    """Порт репозитория самокатов."""

    def get(self, scooter_id: ScooterId) -> Optional[Scooter]:
        ...

    def save(self, scooter: Scooter) -> None:
        ...


class InMemoryScooterRepository:
    """In-memory реализация репозитория самокатов."""

    def __init__(self) -> None:
        self._storage: Dict[str, Scooter] = {}

    def get(self, scooter_id: ScooterId) -> Optional[Scooter]:
        return self._storage.get(scooter_id.value)

    def save(self, scooter: Scooter) -> None:
        self._storage[scooter.scooter_id.value] = scooter