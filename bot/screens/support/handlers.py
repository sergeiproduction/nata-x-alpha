from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from .keyboards import support_keyboard
from .states import SupportScreen

from bot.screens.start.keyboards import start_screen
from bot.screens.start.states import StartScreen

support_router = Router()

@support_router.message(Command("support"))
async def cmd_support(message: Message, state: FSMContext):
    await state.set_state(SupportScreen.waiting_for_message)
    await message.answer("Напишите ваше сообщение в поддержку:", reply_markup=support_keyboard())

@support_router.message(SupportScreen.waiting_for_message, F.text == "Отмена")
async def cancel_support(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Запрос в поддержку отменен.", reply_markup=start_screen())

@support_router.message(SupportScreen.waiting_for_message)
async def receive_support_message(message: Message, state: FSMContext):

    await message.answer(
        "Ваше сообщение отправлено в поддержку. Спасибо!",
        reply_markup=start_screen()
    )
    await state.set_state(StartScreen.start)