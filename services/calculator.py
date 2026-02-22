"""
Расчетный движок для вычисления полной стоимости заправки
"""
from typing import Dict, Any, List
from data.stations import get_all_stations
from services.discount_service import DiscountService


class FuelCalculator:
    """Калькулятор полной стоимости заправки"""
    
    def __init__(self):
        self.discount_service = DiscountService()
    
    async def calculate(self, user: Dict[str, Any], station: Dict[str, Any], 
                       liters: float, fuel_type: str, 
                       user_discounts: List[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        
        # Получаем дисконты пользователя, если не переданы
        if user_discounts is None:
            user_id = user.get("user_id")
            if user_id:
                user_discounts = await self.discount_service.get_user_discounts(user_id)
            else:
                user_discounts = []
        
        # Применяем дисконты пользователя
        discount_calc = self.discount_service.calculate_total_discount(
            user_discounts, base_price
        )
        
        # Также учитываем скидку АЗС (если есть)
        azs_discount = station.get("discount_card", 0) / 100
        azs_discounted_price = base_price * (1 - azs_discount)
        
        # Итоговая цена: применяем пользовательские дисконты к цене АЗС
        # Если есть скидка АЗС, применяем к ней пользовательские дисконты
        if azs_discount > 0:
            # Применяем пользовательские дисконты к уже скидочной цене АЗС
            final_discount_calc = self.discount_service.calculate_total_discount(
                user_discounts, azs_discounted_price
            )
            final_price = final_discount_calc["final_price"]
            total_user_discount = final_discount_calc["total_discount_percent"]
        else:
            final_price = discount_calc["final_price"]
            total_user_discount = discount_calc["total_discount_percent"]
        
        # Общая скидка (АЗС + пользователь)
        total_discount_percent = azs_discount * 100 + total_user_discount
        
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
            "azs_discount": azs_discount * 100,
            "user_discount": total_user_discount,
            "total_discount_percent": total_discount_percent,
            "final_price": final_price,
            "fuel_cost": fuel_cost,
            "distance": distance,
            "fuel_for_trip": fuel_for_trip,
            "fuel_cost_for_trip": fuel_cost_for_trip,
            "time_minutes": time_minutes,
            "time_cost": time_cost,
            "total_cost": total_cost,
            "savings": savings,
            "liters": liters,
            "discount_breakdown": discount_calc.get("breakdown", {}),
            "applied_discounts": discount_calc.get("applied_discounts", [])
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

