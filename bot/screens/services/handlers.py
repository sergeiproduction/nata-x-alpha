from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from .keyboards import services_keyboard, ServiceCallback
from bot.screens.start.keyboards import start_screen
from bot.screens.start.states import StartScreen


services_router = Router()

@services_router.message(Command("services"))
async def cmd_service(message: Message, state: FSMContext):
    await message.answer("Выберите услугу:", reply_markup=services_keyboard())
    await state.clear()

@services_router.callback_query(ServiceCallback.filter(F.action == "web"))
async def web(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали: Разработка сайта", reply_markup=services_keyboard())
    await callback_query.answer()

@services_router.callback_query(ServiceCallback.filter(F.action == "report"))
async def report(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали: Отчет под ключ", reply_markup=services_keyboard())
    await callback_query.answer()

@services_router.callback_query(ServiceCallback.filter(F.action == "back"))
async def go_back(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Возвращаемся в главное меню.", reply_markup=start_screen())
    await callback_query.answer()
    await state.set_state(StartScreen.start)