"""
Расчетный движок для вычисления полной стоимости заправки
"""
from typing import Dict, Any
from data.stations import get_all_stations


class FuelCalculator:
    """Калькулятор полной стоимости заправки"""
    
    def calculate(self, user: Dict[str, Any], station: Dict[str, Any], 
                  liters: float, fuel_type: str) -> Dict[str, Any]:
        """
        Рассчитывает полную стоимость заправки с учетом:
        - Цены топлива
        - Расстояния до АЗС
        - Расхода на дорогу
        - Стоимости времени
        - Скидок по картам
        
        Args:
            user: Профиль пользователя
            station: Данные АЗС
            liters: Количество литров
            fuel_type: Тип топлива
            
        Returns:
            Словарь с расчетами
        """
        # Базовая цена за литр
        base_price = station["prices"].get(fuel_type, 0)
        if base_price == 0:
            return None
        
        # Применяем скидку по карте (если есть)
        discount = station.get("discount_card", 0) / 100
        final_price = base_price * (1 - discount)
        
        # Стоимость топлива
        fuel_cost = final_price * liters
        
        # Расстояние до АЗС (туда и обратно)
        distance = station.get("distance", 0)
        total_distance = distance * 2  # туда и обратно
        
        # Расход топлива на дорогу
        consumption = user.get("car_consumption", 8.0)  # л/100км
        fuel_for_trip = (total_distance / 100) * consumption
        
        # Стоимость топлива на дорогу
        fuel_cost_for_trip = fuel_for_trip * final_price
        
        # Время в пути (примерно 1 км = 1 минута в городе)
        time_minutes = distance * 1.2  # с учетом пробок
        time_hours = time_minutes / 60
        
        # Стоимость времени
        time_value = user.get("time_value", 10.0)  # BYN/час
        time_cost = time_hours * time_value
        
        # Полная стоимость
        total_cost = fuel_cost + fuel_cost_for_trip + time_cost
        
        # Для сравнения: стоимость у ближайшей АЗС
        nearest_station = self._get_nearest_station()
        if nearest_station:
            nearest_price = nearest_station["prices"].get(fuel_type, base_price)
            nearest_discount = nearest_station.get("discount_card", 0) / 100
            nearest_final_price = nearest_price * (1 - nearest_discount)
            nearest_fuel_cost = nearest_final_price * liters
            savings = nearest_fuel_cost - total_cost
        else:
            savings = 0
        
        return {
            "station": station,
            "base_price": base_price,
            "final_price": final_price,
            "fuel_cost": fuel_cost,
            "distance": distance,
            "fuel_for_trip": fuel_for_trip,
            "fuel_cost_for_trip": fuel_cost_for_trip,
            "time_minutes": time_minutes,
            "time_cost": time_cost,
            "total_cost": total_cost,
            "savings": savings,
            "liters": liters
        }
    
    def _get_nearest_station(self) -> Dict[str, Any]:
        """Получить ближайшую АЗС (для сравнения)"""
        stations = get_all_stations()
        if not stations:
            return None
        return min(stations, key=lambda s: s.get("distance", 999))
    
    def calculate_value_score(self, calculation: Dict[str, Any], 
                             balance_type: str = "balanced") -> float:
        """
        Рассчитывает оценку "ценности" варианта
        Чем меньше - тем лучше
        
        Args:
            calculation: Результат расчета
            balance_type: Тип баланса (economy, balanced, convenience)
        """
        total_cost = calculation["total_cost"]
        distance = calculation["distance"]
        
        if balance_type == "economy":
            # Только цена (100% веса)
            return total_cost
        
        elif balance_type == "convenience":
            # Только расстояние (100% веса)
            return distance * 100  # умножаем для нормализации
        
        else:  # balanced
            # 70% цене, 30% расстоянию
            price_score = total_cost * 0.7
            distance_score = distance * 30
            return price_score + distance_score

