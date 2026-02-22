"""
Движок рекомендаций для разных категорий водителей
"""
from typing import Dict, Any, List
from services.calculator import FuelCalculator
from data.stations import get_all_stations


class RecommendationEngine:
    """Генератор рекомендаций по заправкам"""
    
    def __init__(self):
        self.calculator = FuelCalculator()
    
    async def get_recommendations(self, user: Dict[str, Any], liters: float, 
                                  fuel_type: str) -> Dict[str, Any]:
        """
        Генерация рекомендаций в зависимости от категории водителя
        
        Args:
            user: Профиль пользователя
            liters: Количество литров
            fuel_type: Тип топлива
            
        Returns:
            Словарь с рекомендациями
        """
        stations = get_all_stations()
        driver_type = user.get("driver_type", "regular")
        
        if driver_type == "regular":
            # Для обычных - ДВА варианта
            return await self._get_dual_recommendations(user, stations, liters, fuel_type)
        else:
            # Для остальных - ОДИН лучший
            return await self._get_single_recommendation(user, stations, liters, fuel_type)
    
    async def _get_dual_recommendations(self, user: Dict[str, Any], 
                                       stations: List[Dict[str, Any]], 
                                       liters: float, fuel_type: str) -> Dict[str, Any]:
        """Двойная рекомендация для обычных водителей"""
        
        calculations = []
        for station in stations:
            calc = await self.calculator.calculate(user, station, liters, fuel_type)
            if calc:
                balance_type = user.get("preferred_balance", "balanced")
                value_score = self.calculator.calculate_value_score(calc, balance_type)
                calculations.append({
                    "station": station,
                    "calculation": calc,
                    "value_score": value_score
                })
        
        if not calculations:
            return {"error": "Нет доступных АЗС"}
        
        # 1. Самый дешевый (абсолютная экономия)
        cheapest = min(calculations, key=lambda x: x["calculation"]["total_cost"])
        
        # 2. Лучшее соотношение цена/расстояние
        best_value = min(calculations, key=lambda x: x["value_score"])
        
        # 3. Ближайшая (для справки)
        nearest = min(calculations, key=lambda x: x["station"]["distance"])
        
        return {
            "cheapest": cheapest,      # Вариант А: Максимальная экономия
            "best_value": best_value,  # Вариант Б: Близкая и выгодная
            "nearest": nearest,        # Для сравнения
            "has_dual": True
        }
    
    async def _get_single_recommendation(self, user: Dict[str, Any], 
                                         stations: List[Dict[str, Any]], 
                                         liters: float, fuel_type: str) -> Dict[str, Any]:
        """Одна рекомендация для других категорий"""
        
        calculations = []
        for station in stations:
            calc = await self.calculator.calculate(user, station, liters, fuel_type)
            if calc:
                driver_type = user.get("driver_type", "regular")
                
                if driver_type == "taxi":
                    # Для таксиста: минимум времени (ближайшая приемлемая)
                    score = calc["time_cost"] + calc["distance"] * 5
                elif driver_type == "budget":
                    # Для бюджетного: только цена
                    score = calc["total_cost"]
                else:  # traveler
                    # Для путешественника: баланс
                    score = calc["total_cost"] * 0.6 + calc["distance"] * 20
                
                calculations.append({
                    "station": station,
                    "calculation": calc,
                    "score": score
                })
        
        if not calculations:
            return {"error": "Нет доступных АЗС"}
        
        best = min(calculations, key=lambda x: x["score"])
        
        return {
            "best": best,
            "has_dual": False
        }

