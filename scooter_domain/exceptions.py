class DomainError(Exception):
    """Базовое доменное исключение."""


class DomainInvariantViolation(DomainError):
    """Нарушение инварианта предметной области."""


class InvalidValueObject(DomainError):
    """Некорректное значение объекта-значения."""