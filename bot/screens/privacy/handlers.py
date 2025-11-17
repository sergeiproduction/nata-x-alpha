from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from bot.screens.start.keyboards import start_screen
from bot.screens.start.states import StartScreen

from .keyboards import privacy_keyboard
from .filters import PrivacyCallback

from neural import processor

privacy_router = Router()


@privacy_router.message(Command("privacy"))
async def cmd_accounting(message: Message, state: FSMContext):
    await message.answer("Политика конфиденциальности", reply_markup=privacy_keyboard())
    await state.clear()



@privacy_router.callback_query(PrivacyCallback.filter(F.action == "accept"))
async def accept(callback_query: CallbackQuery):   
    await callback_query.message.answer(
        "✅ Вы дали согласие на обработку персональных данных.",
        reply_markup=privacy_keyboard()
    )
    await callback_query.answer()


@privacy_router.callback_query(PrivacyCallback.filter(F.action == "revoke"))
async def revoke_consent(callback_query: CallbackQuery):   
    await callback_query.message.answer(
        "❌ Вы отозвали согласие на обработку персональных данных.",
        reply_markup=privacy_keyboard()
    )
    await callback_query.answer()


@privacy_router.callback_query(PrivacyCallback.filter(F.action == "main_menu"))
async def go_to_main_menu(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Возвращаемся в главное меню.", reply_markup=start_screen())
    await callback_query.answer()
    await state.set_state(StartScreen.start)