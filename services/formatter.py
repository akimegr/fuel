"""
Форматирование ответов бота
"""
from typing import Dict, Any
from config import DRIVER_TYPES, BALANCE_TYPES


class MessageFormatter:
    """Форматирование сообщений для пользователя"""
    
    def format_regular_recommendations(self, recommendations: Dict[str, Any]) -> str:
        """Форматирование двойных рекомендаций для обычных водителей"""
        cheapest = recommendations["cheapest"]
        best_value = recommendations["best_value"]
        nearest = recommendations["nearest"]
        
        calc_cheapest = cheapest["calculation"]
        calc_best = best_value["calculation"]
        calc_nearest = nearest["calculation"]
        
        station_cheapest = cheapest["station"]
        station_best = best_value["station"]
        
        text = "🤖 РАСЧЕТ ДЛЯ ОБЫЧНОГО ВОДИТЕЛЯ\n"
        text += "💡 Предлагаем ДВА оптимальных варианта:\n\n"
        
        # Вариант А: Максимальная экономия
        text += "🏆 ВАРИАНТ А: МАКСИМАЛЬНАЯ ЭКОНОМИЯ\n"
        text += f"📍 {station_cheapest['network']} {station_cheapest['name']} ({calc_cheapest['distance']:.1f} км)\n"
        text += f"💰 Цена: {calc_cheapest['base_price']:.2f} → {calc_cheapest['final_price']:.2f} BYN/л"
        if calc_cheapest.get('total_discount_percent', 0) > 0:
            text += f" (скидка {calc_cheapest['total_discount_percent']:.1f}%)"
        text += "\n"
        text += f"⏱️ Время в пути: {calc_cheapest['time_minutes']:.0f} мин\n"
        text += f"🛣️ Расход на дорогу: {calc_cheapest['fuel_for_trip']:.1f}л ({calc_cheapest['fuel_cost_for_trip']:.2f} BYN)\n"
        text += f"💸 Полная стоимость: {calc_cheapest['total_cost']:.2f} BYN\n"
        
        if calc_cheapest['savings'] > 0:
            text += f"✅ Экономия против ближайшей: {calc_cheapest['savings']:.2f} BYN\n"
        text += "💡 \"Если готовы проехать - максимальная выгода\"\n\n"
        
        # Вариант Б: Близкая и выгодная
        text += "⚖️ ВАРИАНТ Б: БЛИЗКАЯ И ВЫГОДНАЯ\n"
        text += f"📍 {station_best['network']} {station_best['name']} ({calc_best['distance']:.1f} км)\n"
        text += f"💰 Цена: {calc_best['base_price']:.2f} → {calc_best['final_price']:.2f} BYN/л"
        if calc_best.get('total_discount_percent', 0) > 0:
            text += f" (скидка {calc_best['total_discount_percent']:.1f}%)"
        text += "\n"
        text += f"⏱️ Время в пути: {calc_best['time_minutes']:.0f} мин\n"
        text += f"🛣️ Расход на дорогу: {calc_best['fuel_for_trip']:.1f}л ({calc_best['fuel_cost_for_trip']:.2f} BYN)\n"
        text += f"💸 Полная стоимость: {calc_best['total_cost']:.2f} BYN\n"
        
        if calc_best['savings'] > 0:
            text += f"✅ Экономия: {calc_best['savings']:.2f} BYN\n"
        
        diff_cost = calc_best['total_cost'] - calc_cheapest['total_cost']
        diff_time = calc_best['time_minutes'] - calc_cheapest['time_minutes']
        
        if diff_cost > 0:
            text += f"💡 \"Хороший баланс цены и времени\"\n\n"
            text += f"🎯 РАЗНИЦА:\n"
            text += f"Вариант Б дороже на {diff_cost:.2f} BYN, но ближе на {abs(diff_time):.0f} мин\n"
        else:
            text += f"💡 \"Оптимальный выбор\"\n"
        
        return text
    
    def format_single_recommendation(self, recommendation: Dict[str, Any], 
                                     driver_type: str, user: Dict[str, Any] = None) -> str:
        """Форматирование одной рекомендации для других категорий"""
        best = recommendation["best"]
        calc = best["calculation"]
        station = best["station"]
        
        driver_name = DRIVER_TYPES.get(driver_type, driver_type)
        time_value = user.get("time_value", 10.0) if user else 10.0
        
        text = f"🤖 РАСЧЕТ ДЛЯ {driver_name.upper()}\n"
        
        if driver_type == "taxi":
            text += f"💰 Время = {time_value:.0f} BYN/час\n\n"
        elif driver_type == "budget":
            text += f"🕐 Время не критично ({time_value:.0f} BYN/час)\n\n"
        else:
            text += f"💡 Оптимальный вариант для путешествий\n\n"
        
        text += f"🏆 РЕКОМЕНДУЕМЫЙ ВАРИАНТ: {station['network']} {station['name']} ({calc['distance']:.1f} км)\n"
        text += f"💰 Цена: {calc['base_price']:.2f} → {calc['final_price']:.2f} BYN/л"
        if calc.get('total_discount_percent', 0) > 0:
            text += f" (скидка {calc['total_discount_percent']:.1f}%)"
        text += "\n"
        text += f"⏱️ Время в пути: {calc['time_minutes']:.0f} мин\n"
        text += f"🛣️ Расход на дорогу: {calc['fuel_for_trip']:.1f}л ({calc['fuel_cost_for_trip']:.2f} BYN)\n"
        text += f"💸 Полная стоимость: {calc['total_cost']:.2f} BYN\n"
        
        if calc['savings'] > 0:
            text += f"✅ Экономия против ближайшей: {calc['savings']:.2f} BYN\n"
        
        if driver_type == "taxi":
            text += "💡 \"Не отвлекайтесь на дальние заправки во время работы\""
        elif driver_type == "budget":
            text += "💡 \"Можно съездить, экономия значительная\""
        else:
            text += "💡 \"Оптимальный баланс для дальних поездок\""
        
        return text

