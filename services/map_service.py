"""
Сервис для работы с картами (заглушка для будущего расширения)
"""
from config import YANDEX_MAPS_API_KEY


def generate_map_url(lat: float, lon: float, zoom: int = 15) -> str:
    """
    Генерация URL статической карты Яндекс.Карт
    
    Args:
        lat: Широта
        lon: Долгота
        zoom: Уровень масштаба
    
    Returns:
        URL статической карты
    """
    if YANDEX_MAPS_API_KEY:
        return (
            f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z={zoom}"
            f"&size=600,400&l=map&pt={lon},{lat},pm2rdm"
        )
    else:
        # Без API ключа используем базовый URL
        return (
            f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z={zoom}"
            f"&size=600,400&l=map"
        )

