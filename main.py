"""Демонстрация работы доменной модели проката самокатов."""

from datetime import datetime, timedelta
from decimal import Decimal

from scooter_domain.aggregates.ride import Ride
from scooter_domain.aggregates.scooter import Scooter, ScooterStatus
from scooter_domain.exceptions import DomainInvariantViolation, InvalidValueObject
from scooter_domain.repositories import InMemoryScooterRepository
from scooter_domain.services import RideService
from scooter_domain.value_objects import (
    BatteryLevel,
    Money,
    ScooterId,
    Tariff,
)


def print_separator(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    # --- 1. Настройка ---
    print_separator("1. Настройка репозитория и сервиса")

    repo = InMemoryScooterRepository()
    service = RideService(repo)

    scooter_id = ScooterId("S-01")
    scooter = Scooter(
        scooter_id=scooter_id,
        battery=BatteryLevel(85),
        minimum_battery=20,
    )
    repo.save(scooter)

    print(f"Создан самокат: {scooter_id.value}")
    print(f"Заряд: {scooter.battery.percent}%")
    print(f"Статус: {scooter.status.value}")

    # --- 2. Начало поездки ---
    print_separator("2. Начало поездки")

    tariff = Tariff(
        price_per_minute=Money(Decimal("5.00")),
        minimum_price=Money(Decimal("50.00")),
    )
    start = datetime(2026, 1, 1, 10, 0)

    ride = Ride(
        ride_id="R-1",
        scooter_id=scooter_id,
        start_time=start,
        tariff=tariff,
    )

    service.start_ride(ride)

    print(f"Поездка {ride.ride_id} начата")
    print(f"Статус поездки: {ride.status.value}")
    print(f"Статус самоката: {scooter.status.value}")

    # --- 3. Попытка выдать уже арендованный самокат ---
    print_separator("3. Попытка выдать уже арендованный самокат")

    try:
        scooter.issue()
        print("ОШИБКА: инвариант не сработал!")
    except DomainInvariantViolation as e:
        print(f"Инвариант сработал: {e}")

    # --- 4. Завершение поездки ---
    print_separator("4. Завершение поездки")

    end = start + timedelta(minutes=25)
    print(f"Начало: {start}")
    print(f"Окончание: {end}")
    print(f"Длительность: 25 минут -> 25 * 5 = 125 руб (> минимума 50)")

    service.finish_ride(scooter, ride, end)

    print(f"Стоимость: {ride.cost.amount} {ride.cost.currency}")
    print(f"Статус поездки: {ride.status.value}")
    print(f"Статус самоката: {scooter.status.value}")

    # --- 5. Попытка завершить поездку дважды ---
    print_separator("5. Попытка завершить поездку дважды")

    try:
        ride.finish(end + timedelta(minutes=10))
        print("ОШИБКА: инвариант не сработал!")
    except DomainInvariantViolation as e:
        print(f"Инвариант сработал: {e}")

    # --- 6. Время окончания раньше начала ---
    print_separator("6. Время окончания раньше начала")

    scooter2_id = ScooterId("S-02")
    scooter2 = Scooter(scooter_id=scooter2_id, battery=BatteryLevel(90))
    repo.save(scooter2)

    ride2 = Ride(
        ride_id="R-2",
        scooter_id=scooter2_id,
        start_time=datetime(2026, 1, 1, 12, 0),
        tariff=tariff,
    )
    service.start_ride(ride2)

    try:
        ride2.finish(datetime(2026, 1, 1, 11, 0))
        print("ОШИБКА: инвариант не сработал!")
    except DomainInvariantViolation as e:
        print(f"Инвариант сработал: {e}")

    # --- 7. Самокат с низким зарядом ---
    print_separator("7. Попытка выдать самокат с низким зарядом")

    low_id = ScooterId("S-03")
    low_scooter = Scooter(
        scooter_id=low_id,
        battery=BatteryLevel(10),
        minimum_battery=20,
    )
    repo.save(low_scooter)

    try:
        low_scooter.issue()
        print("ОШИБКА: инвариант не сработал!")
    except DomainInvariantViolation as e:
        print(f"Инвариант сработал: {e}")

    # --- 8. Самокат не найден ---
    print_separator("8. Попытка начать поездку на несуществующем самокате")

    ghost_ride = Ride(
        ride_id="R-3",
        scooter_id=ScooterId("Z-99"),
        start_time=datetime(2026, 1, 1, 14, 0),
        tariff=tariff,
    )

    try:
        service.start_ride(ghost_ride)
        print("ОШИБКА: исключение не брошено!")
    except DomainInvariantViolation as e:
        print(f"Сервис бросил исключение: {e}")

    # --- 9. Проверка невалидных объектов-значений ---
    print_separator("9. Проверка невалидных объектов-значений")

    checks = [
        ("Отрицательная сумма", lambda: Money(Decimal("-100"))),
        ("Пустой ScooterId", lambda: ScooterId("")),
        ("ScooterId из пробелов", lambda: ScooterId("   ")),
        ("Заряд выше 100", lambda: BatteryLevel(150)),
        ("Заряд ниже 0", lambda: BatteryLevel(-5)),
        (
            "Нулевая цена тарифа",
            lambda: Tariff(
                price_per_minute=Money(Decimal("0")),
                minimum_price=Money(Decimal("50")),
            ),
        ),
    ]

    for label, factory in checks:
        try:
            factory()
            print(f"[ОШИБКА] {label}: объект создан, хотя не должен")
        except InvalidValueObject as e:
            print(f"[OK] {label}: {e}")

    print()
    print("=" * 60)
    print("Все проверки завершены")
    print("=" * 60)


if __name__ == "__main__":
    main()