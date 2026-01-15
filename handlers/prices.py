"""
Обработчики команд для работы с ценами
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.crud import (
    get_latest_prices_by_city_and_fuel,
    get_price_age_minutes,
    add_price,
    get_all_azs_by_city,
    get_azs_by_id
)
from keyboards.inline_kb import (
    get_network_keyboard,
    get_fuel_type_keyboard,
    get_azs_keyboard
)
from services.validation import validate_price, validate_city, validate_fuel_type
from config import СЕТИ_АЗС, ТИПЫ_ТОПЛИВА, ЛИМИТ_ВЫВОДА_ЦЕН

router = Router()


class AddPriceStates(StatesGroup):
    """Состояния для добавления цены"""
    waiting_network = State()
    waiting_fuel_type = State()
    waiting_azs = State()
    waiting_price = State()


@router.message(Command("codes"))
async def cmd_codes(message: Message):
    """Вывод списка кодов АЗС"""
    codes_text = "📋 Список сетей АЗС:\n\n"
    for code, name in СЕТИ_АЗС.items():
        codes_text += f"• {code} - {name}\n"
    await message.answer(codes_text)


@router.message(Command("prices"))
async def cmd_prices(message: Message):
    """Обработчик команды /prices"""
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if len(args) < 2:
        await message.answer(
            "❌ Неверный формат команды.\n\n"
            "Использование: /prices <город> <тип_топлива>\n"
            "Пример: /prices Минск 95"
        )
        return
    
    city = args[0].capitalize()
    fuel_type = args[1].lower()
    
    # Валидация
    if not validate_city(city):
        await message.answer(
            f"❌ Город '{city}' не найден в списке.\n"
            f"Доступные города: {', '.join(['Минск', 'Гомель', 'Брест', 'Витебск', 'Гродно', 'Могилев'])}..."
        )
        return
    
    if not validate_fuel_type(fuel_type):
        await message.answer(
            f"❌ Тип топлива '{fuel_type}' не поддерживается.\n"
            f"Доступные типы: 92, 95, 98, дт, газ"
        )
        return
    
    # Получаем цены
    prices = await get_latest_prices_by_city_and_fuel(
        city, fuel_type, ЛИМИТ_ВЫВОДА_ЦЕН
    )
    
    if not prices:
        await message.answer(
            f"😔 Пока нет данных о ценах на {ТИПЫ_ТОПЛИВА.get(fuel_type, fuel_type)} "
            f"в городе {city}.\n\n"
            f"Будьте первым! Добавьте цену командой /addprice"
        )
        return
    
    # Формируем ответ
    fuel_name = ТИПЫ_ТОПЛИВА.get(fuel_type, fuel_type)
    result_text = f"🏆 Топ-{len(prices)} цен на {fuel_name} в {city}:\n\n"
    
    for idx, price_data in enumerate(prices, 1):
        result_text += (
            f"{idx}. {price_data['network']} "
            f"({price_data['address']}) - "
            f"{price_data['price']:.2f} BYN\n"
        )
    
    # Добавляем информацию о последнем обновлении
    if prices:
        last_age = await get_price_age_minutes(prices[0]['id'])
        age_text = f"{last_age} мин. назад" if last_age else "только что"
        result_text += f"\nОбновлено: {age_text}"
    
    await message.answer(result_text)


@router.message(Command("addprice"))
async def cmd_addprice(message: Message, state: FSMContext):
    """Начало процесса добавления цены"""
    await state.set_state(AddPriceStates.waiting_network)
    await message.answer(
        "➕ Добавление новой цены\n\n"
        "Шаг 1: Выберите сеть АЗС",
        reply_markup=get_network_keyboard()
    )


@router.callback_query(F.data.startswith("network_"), AddPriceStates.waiting_network)
async def process_network(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора сети АЗС"""
    network_code = callback.data.split("_")[1]
    network_name = СЕТИ_АЗС.get(network_code)
    
    if not network_name:
        await callback.answer("❌ Неверная сеть АЗС", show_alert=True)
        return
    
    await state.update_data(network=network_name, network_code=network_code)
    await state.set_state(AddPriceStates.waiting_fuel_type)
    
    await callback.message.edit_text(
        f"✅ Выбрана сеть: {network_name}\n\n"
        "Шаг 2: Выберите тип топлива",
        reply_markup=get_fuel_type_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fuel_"), AddPriceStates.waiting_fuel_type)
async def process_fuel_type(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа топлива"""
    fuel_code = callback.data.split("_")[1]
    fuel_name = ТИПЫ_ТОПЛИВА.get(fuel_code)
    
    if not fuel_name:
        await callback.answer("❌ Неверный тип топлива", show_alert=True)
        return
    
    data = await state.get_data()
    network = data.get('network')
    
    await state.update_data(fuel_type=fuel_code, fuel_name=fuel_name)
    await state.set_state(AddPriceStates.waiting_azs)
    
    # Получаем список АЗС выбранной сети (пока для Минска, можно расширить)
    azs_list = await get_all_azs_by_city("Минск")
    filtered_azs = [azs for azs in azs_list if azs['network'] == network]
    
    if not filtered_azs:
        await callback.message.edit_text(
            f"❌ АЗС сети {network} не найдены в базе.\n"
            f"Пожалуйста, выберите другую сеть."
        )
        await state.set_state(AddPriceStates.waiting_network)
        await callback.message.answer(
            "Выберите сеть АЗС:",
            reply_markup=get_network_keyboard()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        f"✅ Выбрано топливо: {fuel_name}\n\n"
        "Шаг 3: Выберите АЗС",
        reply_markup=get_azs_keyboard(filtered_azs)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("azs_"), AddPriceStates.waiting_azs)
async def process_azs(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора АЗС"""
    azs_id = int(callback.data.split("_")[1])
    azs = await get_azs_by_id(azs_id)
    
    if not azs:
        await callback.answer("❌ АЗС не найдена", show_alert=True)
        return
    
    await state.update_data(azs_id=azs_id, azs_address=azs['address'])
    await state.set_state(AddPriceStates.waiting_price)
    
    await callback.message.edit_text(
        f"✅ Выбрана АЗС: {azs['network']}, {azs['address']}\n\n"
        "Шаг 4: Введите цену (например: 2.45)\n\n"
        "Цена должна быть от 1.0 до 5.0 BYN"
    )
    await callback.answer()


@router.message(AddPriceStates.waiting_price, F.text.regexp(r'^\d+\.?\d*$'))
async def process_price(message: Message, state: FSMContext):
    """Обработка ввода цены"""
    try:
        price = float(message.text.replace(',', '.'))
        
        if not validate_price(price):
            await message.answer(
                f"❌ Цена должна быть от 1.0 до 5.0 BYN.\n"
                f"Вы ввели: {price}"
            )
            return
        
        data = await state.get_data()
        azs_id = data.get('azs_id')
        fuel_type = data.get('fuel_type')
        user_id = message.from_user.id
        
        # Добавляем цену в БД
        price_id = await add_price(azs_id, fuel_type, price, user_id)
        
        fuel_name = data.get('fuel_name', fuel_type)
        azs_address = data.get('azs_address', '')
        
        await message.answer(
            f"✅ Цена успешно добавлена!\n\n"
            f"АЗС: {azs_address}\n"
            f"Топливо: {fuel_name}\n"
            f"Цена: {price:.2f} BYN\n\n"
            f"Спасибо за ваш вклад! 🙏"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Неверный формат цены.\n"
            "Введите число, например: 2.45"
        )


@router.message(AddPriceStates.waiting_price)
async def process_price_invalid(message: Message):
    """Обработка неверного формата цены"""
    await message.answer(
        "❌ Неверный формат.\n"
        "Введите цену числом, например: 2.45"
    )

