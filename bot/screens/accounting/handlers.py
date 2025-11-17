from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from bot.screens import start_screen
from bot.services.image import ImageService
from bot.services.user import UserService
from bot.services.user_promocode import UserPromocodeService
from utils.templates import load_template_text
from .keyboards import accounting_keyboard, back

from .filters import AccountingCallback
from bot.screens import StartScreen

account_router = Router()


@account_router.message(Command("accounting"))
async def cmd_accounting(message: Message, state: FSMContext, user_service: UserService,
                        user_promocode_service: UserPromocodeService):
    
    info_text = await load_template_text('accounting_info', extended=False)

    user = await user_service.get_user_by_telegram_id(message.from_user.id)

    accounting_promocode = await user_promocode_service.get_user_promocode_by_campaign_name(user.id, "Бухгалтерия")
    
    picture = await ImageService.generate_offer(accounting_promocode.name, "./files/accounting.jpg")

    await message.answer_photo(picture, caption=info_text, reply_markup=accounting_keyboard())
    await state.clear()


@account_router.callback_query(AccountingCallback.filter(F.action == "info"))
async def show_info(callback_query: CallbackQuery):
    
    info_text = await load_template_text('accounting_info', extended=True)

    await callback_query.message.edit_caption(caption=info_text, reply_markup=back())
    await callback_query.answer()

@account_router.callback_query(AccountingCallback.filter(F.action == "back"))
async def go_back(callback_query: CallbackQuery, state: FSMContext):
    text = await load_template_text("start_text")
    await callback_query.message.answer(text, reply_markup=start_screen())
    await callback_query.answer()
    await state.set_state(StartScreen.start)