"""
Клавиатуры для работы с топливом
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_fuel_type_selection_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа топлива для расчета"""
    buttons = []
    
    buttons.append([
        InlineKeyboardButton(text="АИ-92", callback_data="fuelcalc_92"),
        InlineKeyboardButton(text="АИ-95", callback_data="fuelcalc_95")
    ])
    buttons.append([
        InlineKeyboardButton(text="АИ-98", callback_data="fuelcalc_98"),
        InlineKeyboardButton(text="ДТ", callback_data="fuelcalc_дт")
    ])
    buttons.append([
        InlineKeyboardButton(text="Газ", callback_data="fuelcalc_газ")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

