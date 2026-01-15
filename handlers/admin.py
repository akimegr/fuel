"""
Административные команды (на будущее)
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Административные команды (заглушка)"""
    await message.answer("🔧 Административные функции будут добавлены позже.")

