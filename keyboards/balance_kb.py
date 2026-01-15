"""
Клавиатуры для выбора приоритета (только для обычных водителей)
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BALANCE_TYPES


def get_balance_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора приоритета для обычных водителей"""
    buttons = []
    
    buttons.append([
        InlineKeyboardButton(
            text="💰 МАКСИМАЛЬНАЯ ЭКОНОМИЯ",
            callback_data="balance_economy"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="⚖️ БАЛАНС ЦЕНЫ И ВРЕМЕНИ",
            callback_data="balance_balanced"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="🏠 МАКСИМАЛЬНОЕ УДОБСТВО",
            callback_data="balance_convenience"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

