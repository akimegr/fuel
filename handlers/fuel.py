"""
Обработчики команды /fuel для расчета оптимальной заправки
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.crud import get_or_create_user
from services.recommender import RecommendationEngine
from services.formatter import MessageFormatter
from keyboards.fuel_kb import get_fuel_type_selection_keyboard
from config import ТИПЫ_ТОПЛИВА

router = Router()

recommender = RecommendationEngine()
formatter = MessageFormatter()


class FuelStates(StatesGroup):
    """Состояния для расчета топлива"""
    waiting_liters = State()


@router.message(Command("fuel"))
async def cmd_fuel(message: Message, state: FSMContext):
    """Начало расчета оптимальной заправки"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if len(args) >= 2:
        # Формат: /fuel 95 40
        fuel_type = args[0].lower()
        try:
            liters = float(args[1])
            await process_fuel_calculation(message, fuel_type, liters)
        except ValueError:
            await message.answer(
                "❌ Неверный формат количества литров.\n"
                "Использование: /fuel <тип> <литры>\n"
                "Пример: /fuel 95 40"
            )
    else:
        # Интерактивный режим
        await state.set_state(FuelStates.waiting_liters)
        await message.answer(
            "⛽ РАСЧЕТ ОПТИМАЛЬНОЙ ЗАПРАВКИ\n\n"
            "Шаг 1: Выберите тип топлива",
            reply_markup=get_fuel_type_selection_keyboard()
        )


@router.callback_query(F.data.startswith("fuelcalc_"), FuelStates.waiting_liters)
async def process_fuel_type_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа топлива"""
    fuel_type = callback.data.split("_")[1]
    
    if fuel_type not in ТИПЫ_ТОПЛИВА:
        await callback.answer("❌ Неверный тип топлива", show_alert=True)
        return
    
    await state.update_data(fuel_type=fuel_type)
    
    await callback.message.edit_text(
        f"✅ Выбран тип: {ТИПЫ_ТОПЛИВА.get(fuel_type, fuel_type)}\n\n"
        "Шаг 2: Введите количество литров\n"
        "Например: 40"
    )
    await callback.answer()


@router.message(FuelStates.waiting_liters, F.text.regexp(r'^\d+\.?\d*$'))
async def process_liters_input(message: Message, state: FSMContext):
    """Обработка ввода количества литров"""
    try:
        liters = float(message.text.replace(',', '.'))
        
        if liters <= 0 or liters > 200:
            await message.answer(
                "❌ Количество литров должно быть от 1 до 200.\n"
                "Введите корректное значение:"
            )
            return
        
        data = await state.get_data()
        fuel_type = data.get("fuel_type")
        
        if not fuel_type:
            await message.answer("❌ Ошибка. Начните заново: /fuel")
            await state.clear()
            return
        
        await process_fuel_calculation(message, fuel_type, liters)
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Неверный формат.\n"
            "Введите число, например: 40"
        )


@router.message(FuelStates.waiting_liters)
async def process_liters_invalid(message: Message):
    """Обработка неверного формата литров"""
    await message.answer(
        "❌ Неверный формат.\n"
        "Введите количество литров числом, например: 40"
    )


async def process_fuel_calculation(message: Message, fuel_type: str, liters: float):
    """Основная функция расчета"""
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    
    # Получаем рекомендации
    recommendations = recommender.get_recommendations(user, liters, fuel_type)
    
    if "error" in recommendations:
        await message.answer(f"❌ {recommendations['error']}")
        return
    
    driver_type = user.get("driver_type", "regular")
    
    if recommendations.get("has_dual", False):
        # Двойные рекомендации для обычных водителей
        text = formatter.format_regular_recommendations(recommendations)
    else:
        # Одна рекомендация для других категорий
        text = formatter.format_single_recommendation(recommendations, driver_type, user)
    
    await message.answer(text)

