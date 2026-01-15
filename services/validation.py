"""
Валидация ввода пользователя
"""
from config import ГОРОДА, ТИПЫ_ТОПЛИВА, МИН_ЦЕНА, МАКС_ЦЕНА


def validate_city(city: str) -> bool:
    """Проверка валидности города"""
    return city in ГОРОДА


def validate_fuel_type(fuel_type: str) -> bool:
    """Проверка валидности типа топлива"""
    return fuel_type.lower() in ТИПЫ_ТОПЛИВА


def validate_price(price: float) -> bool:
    """Проверка валидности цены"""
    return МИН_ЦЕНА <= price <= МАКС_ЦЕНА


def validate_network(network: str) -> bool:
    """Проверка валидности сети АЗС"""
    from config import СЕТИ_АЗС
    return network.lower() in СЕТИ_АЗС

