"""
Обработчики команд для работы с профилем
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.crud import get_or_create_user, update_user_profile
from keyboards.balance_kb import get_balance_keyboard
from services.discount_service import DiscountService
from config import DRIVER_TYPES, BALANCE_TYPES, DEFAULT_TIME_VALUES

discount_service = DiscountService()

router = Router()


class ProfileStates(StatesGroup):
    """Состояния для редактирования профиля"""
    waiting_consumption = State()
    waiting_distance = State()


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Просмотр профиля пользователя"""
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    
    driver_type = user.get("driver_type", "regular")
    driver_name = DRIVER_TYPES.get(driver_type, driver_type)
    
    text = f"👤 ВАШ ПРОФИЛЬ\n\n"
    text += f"🚗 Категория: {driver_name}\n"
    text += f"⛽ Расход авто: {user.get('car_consumption', 8.0):.1f} л/100км\n"
    
    if driver_type == "regular":
        balance = user.get("preferred_balance", "balanced")
        balance_name = BALANCE_TYPES.get(balance, balance)
        text += f"⚖️ Приоритет: {balance_name}\n"
        text += f"\n💡 Изменить приоритет: /balance\n"
    
    text += f"📏 Макс. расстояние: {user.get('max_willing_distance', 10.0):.1f} км\n"
    text += f"⏰ Стоимость времени: {user.get('time_value', 10.0):.0f} BYN/час\n"
    
    # Показываем дисконты
    user_discounts = await discount_service.get_user_discounts(message.from_user.id)
    if user_discounts:
        total_discount = sum(d["discount_percent"] for d in user_discounts)
        text += f"\n💳 Активных дисконтов: {len(user_discounts)} (итого {total_discount:.1f}%)\n"
        text += f"Просмотр: /discounts"
    else:
        text += f"\n💳 Дисконты не добавлены\n"
        text += f"Добавить: /discounts_list"
    
    text += f"\n📝 Редактировать: /profile_edit"
    
    await message.answer(text)


@router.message(Command("balance"))
async def cmd_balance(message: Message):
    """Выбор приоритета для обычных водителей"""
    user = await get_or_create_user(message.from_user.id, message.from_user.username)
    
    driver_type = user.get("driver_type", "regular")
    
    if driver_type != "regular":
        await message.answer(
            "❌ Эта команда доступна только для обычных водителей.\n"
            "Измените категорию в профиле: /profile"
        )
        return
    
    current_balance = user.get("preferred_balance", "balanced")
    current_name = BALANCE_TYPES.get(current_balance, current_balance)
    
    text = f"⚖️ ВЫБОР ПРИОРИТЕТА\n\n"
    text += f"Текущий: {current_name}\n\n"
    text += "Выберите приоритет:"
    
    await message.answer(text, reply_markup=get_balance_keyboard())


@router.callback_query(F.data.startswith("balance_"))
async def process_balance(callback: CallbackQuery):
    """Обработка выбора приоритета"""
    balance_type = callback.data.split("_")[1]
    
    if balance_type not in BALANCE_TYPES:
        await callback.answer("❌ Неверный приоритет", show_alert=True)
        return
    
    await update_user_profile(callback.from_user.id, preferred_balance=balance_type)
    
    balance_name = BALANCE_TYPES.get(balance_type, balance_type)
    
    await callback.message.edit_text(
        f"✅ Установлен приоритет: {balance_name}\n\n"
        f"💡 Бот будет учитывать этот приоритет при расчетах"
    )
    await callback.answer()


@router.message(Command("profile_edit"))
async def cmd_profile_edit(message: Message, state: FSMContext):
    """Редактирование профиля"""
    text = "📝 РЕДАКТИРОВАНИЕ ПРОФИЛЯ\n\n"
    text += "Выберите параметр для изменения:\n"
    text += "1. Расход авто: /set_consumption\n"
    text += "2. Макс. расстояние: /set_distance\n"
    text += "3. Категория водителя: /start (выбор категории)"
    
    await message.answer(text)

