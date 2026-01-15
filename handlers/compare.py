"""
Обработчики команды /compare для сравнения всех вариантов
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.crud import get_or_create_user
from services.calculator import FuelCalculator
from data.stations import get_all_stations
from config import ТИПЫ_ТОПЛИВА

router = Router()
calculator = FuelCalculator()


@router.message(Command("compare"))
async def cmd_compare(message: Message):
    """Сравнение всех вариантов АЗС"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if len(args) < 2:
        await message.answer(
            "❌ Неверный формат команды.\n\n"
            "Использование: /compare <тип_топлива> <литры>\n"
            "Пример: /compare 95 40"
        )
        return
    
    fuel_type = args[0].lower()
    try:
        liters = float(args[1])
    except ValueError:
        await message.answer("❌ Неверный формат количества литров")
        return
    
    if fuel_type not in ТИПЫ_ТОПЛИВА:
        await message.answer(f"❌ Тип топлива '{fuel_type}' не поддерживается")
        return
    
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    stations = get_all_stations()
    
    calculations = []
    for station in stations:
        calc = calculator.calculate(user, station, liters, fuel_type)
        if calc:
            calculations.append((station, calc))
    
    if not calculations:
        await message.answer("❌ Нет доступных АЗС для сравнения")
        return
    
    # Сортируем по полной стоимости
    calculations.sort(key=lambda x: x[1]["total_cost"])
    
    text = f"📊 СРАВНЕНИЕ ВСЕХ ВАРИАНТОВ\n\n"
    text += f"Топливо: {ТИПЫ_ТОПЛИВА.get(fuel_type, fuel_type)}\n"
    text += f"Количество: {liters:.1f} л\n\n"
    text += "Сортировка: по полной стоимости (возрастание)\n\n"
    
    for idx, (station, calc) in enumerate(calculations, 1):
        text += f"{idx}. {station['network']} {station['name']}\n"
        text += f"   💰 {calc['final_price']:.2f} BYN/л | "
        text += f"📍 {calc['distance']:.1f} км | "
        text += f"💸 {calc['total_cost']:.2f} BYN\n"
        text += f"   ⏱️ {calc['time_minutes']:.0f} мин | "
        text += f"🛣️ {calc['fuel_for_trip']:.1f}л на дорогу\n\n"
    
    await message.answer(text)

