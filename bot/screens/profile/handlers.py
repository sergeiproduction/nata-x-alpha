from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from bot.services.image import ImageService
from bot.services.user import UserService
from bot.services.user_promocode import UserPromocodeService
from bot.services.user_subscription import UserSubscriptionService
from utils.templates import load_template_text

from .filters import ProfileCallback
from .keyboards import profile_keyboard

from bot.screens import start_screen
from bot.screens import StartScreen

profile_router = Router()


@profile_router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext,
                        user_service: UserService,
                        user_subscription_service: UserSubscriptionService,
                        user_promocode_service: UserPromocodeService):


    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    user_tariff = await user_subscription_service.get_active_subscription(user_id=user.id)

    expire_date = await user_subscription_service.get_subscription_expiry_date(user.id)

    is_premium = True if user_tariff.tariff_name == "premium" else False

    text = await load_template_text("subscription_info", templates_dir="./templates/profile/",
                                    is_premium = is_premium,
                                    subscription_end_date=expire_date.strftime("%d.%m.%Y"))


    referral_promocode = await user_promocode_service.get_user_promocode_by_campaign_name(user.id, "Приведи друга")

    picture = await ImageService.generate_offer(referral_promocode.name, "./files/referal.jpg")

    await message.answer_photo(picture, caption=text, reply_markup=profile_keyboard(is_premium))
    await state.clear()


@profile_router.callback_query(ProfileCallback.filter(F.action == "back"))
async def go_back(callback_query: CallbackQuery, state: FSMContext):

    text = await load_template_text("start_text")

    await callback_query.message.answer(text, reply_markup=start_screen())
    await callback_query.answer()
    await state.set_state(StartScreen.start)