"""
Клавиатуры для выбора категории водителя
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import DRIVER_TYPES


def get_category_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора категории водителя"""
    buttons = []
    
    buttons.append([
        InlineKeyboardButton(
            text="🚕 Таксист",
            callback_data="category_taxi"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="🚗 Обычный водитель",
            callback_data="category_regular"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="🗺️ Путешественник",
            callback_data="category_traveler"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="💰 Бюджетный водитель",
            callback_data="category_budget"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

