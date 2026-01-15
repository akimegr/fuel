"""
Inline клавиатуры для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import СЕТИ_АЗС, ТИПЫ_ТОПЛИВА


def get_network_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора сети АЗС"""
    buttons = []
    for code, name in СЕТИ_АЗС.items():
        buttons.append([
            InlineKeyboardButton(text=name, callback_data=f"network_{code}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_fuel_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа топлива"""
    buttons = []
    row = []
    for code, name in ТИПЫ_ТОПЛИВА.items():
        row.append(InlineKeyboardButton(text=name, callback_data=f"fuel_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_azs_keyboard(azs_list: list) -> InlineKeyboardMarkup:
    """Клавиатура выбора АЗС"""
    buttons = []
    for azs in azs_list[:10]:  # Ограничиваем 10 АЗС для удобства
        text = f"{azs['network']} - {azs['address']}"
        # Обрезаем текст, если слишком длинный
        if len(text) > 50:
            text = text[:47] + "..."
        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"azs_{azs['id']}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

