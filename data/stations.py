"""
Тестовые данные АЗС с ценами и расстояниями
"""
STATIONS = [
    # Центр (близко, но дороже)
    {
        "id": 1,
        "name": "Лукойл Центр",
        "network": "Лукойл",
        "address": "пр. Победителей, 10",
        "city": "Минск",
        "zone": "center",
        "distance": 1.5,  # км от центра
        "prices": {"95": 2.48, "92": 2.38, "98": 2.58, "дт": 2.43, "газ": 1.85},
        "discount_card": 2,
        "traffic": "high",
        "lat": 53.9045,
        "lon": 27.5615
    },
    
    # Спальный район (умеренная цена, умеренное расстояние)
    {
        "id": 2,
        "name": "А100 Серебрянка",
        "network": "А100",
        "address": "ул. Тимирязева, 50",
        "city": "Минск",
        "zone": "residential",
        "distance": 3.2,
        "prices": {"95": 2.45, "92": 2.35, "98": 2.55, "дт": 2.40, "газ": 1.82},
        "discount_card": 3,
        "traffic": "medium",
        "lat": 53.9150,
        "lon": 27.5750
    },
    
    # Окраина (далеко, но дешево)
    {
        "id": 3,
        "name": "Газпром Окраина",
        "network": "Газпром",
        "address": "пр. Дзержинского, 125",
        "city": "Минск",
        "zone": "suburb",
        "distance": 8.7,
        "prices": {"95": 2.40, "92": 2.30, "98": 2.50, "дт": 2.35, "газ": 1.78},
        "discount_card": 2,
        "traffic": "low",
        "lat": 53.8700,
        "lon": 27.5200
    },
    
    # Трасса (самая дешевая, но очень далеко)
    {
        "id": 4,
        "name": "Белнефтехим МКАД",
        "network": "Белнефтехим",
        "address": "пр. Партизанский, 150",
        "city": "Минск",
        "zone": "highway",
        "distance": 12.5,
        "prices": {"95": 2.38, "92": 2.28, "98": 2.48, "дт": 2.33, "газ": 1.75},
        "discount_card": 1,
        "traffic": "low",
        "lat": 53.8800,
        "lon": 27.5300
    },
    
    # Еще несколько для разнообразия
    {
        "id": 5,
        "name": "Shell Центр",
        "network": "Shell",
        "address": "пр. Победителей, 65",
        "city": "Минск",
        "zone": "center",
        "distance": 2.1,
        "prices": {"95": 2.46, "92": 2.36, "98": 2.56, "дт": 2.41, "газ": 1.83},
        "discount_card": 2,
        "traffic": "high",
        "lat": 53.9150,
        "lon": 27.5700
    },
    
    {
        "id": 6,
        "name": "Танко Спальник",
        "network": "Танко",
        "address": "ул. Притыцкого, 83",
        "city": "Минск",
        "zone": "residential",
        "distance": 4.5,
        "prices": {"95": 2.43, "92": 2.33, "98": 2.53, "дт": 2.38, "газ": 1.80},
        "discount_card": 2,
        "traffic": "medium",
        "lat": 53.9050,
        "lon": 27.5450
    }
]


def get_station_by_id(station_id: int) -> dict:
    """Получить АЗС по ID"""
    for station in STATIONS:
        if station["id"] == station_id:
            return station
    return None


def get_all_stations() -> list:
    """Получить все АЗС"""
    return STATIONS


def get_stations_by_city(city: str) -> list:
    """Получить АЗС по городу"""
    return [s for s in STATIONS if s["city"] == city]

