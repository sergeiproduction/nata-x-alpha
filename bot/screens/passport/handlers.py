from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

from dadata import DadataAsync

from bot.middlewares.user_init import UserInitializationMiddleware
from bot.screens.profile.keyboards import profile_keyboard
from bot.services.image import ImageService
from bot.services.user import UserService
from bot.services.user_promocode import UserPromocodeService
from bot.services.user_subscription import UserSubscriptionService
from schemas.user import UserResponse, UserUpdate
from utils.templates import load_template_text


from .use_cases import get_company_info, timestamp_to_date, prepare_company_data_for_template
from .states import PassportScreen
from .filters import PassportCallbackData
from .keyboards import get_passport_inline_kb

from neural import processor
from config import DADATA_KEY

passport_router = Router()
passport_router.message.middleware(UserInitializationMiddleware())
passport_router.callback_query.middleware(UserInitializationMiddleware())


@passport_router.callback_query(PassportCallbackData.filter(F.action == "fill_by_inn"))
async def start_fill(callback: CallbackQuery, state: FSMContext):

    await state.set_state(PassportScreen.inn)
    await callback.message.answer("Введите ИНН", reply_markup=get_passport_inline_kb())


@passport_router.message(StateFilter(PassportScreen), F.text)
async def enter_inn(message: Message, state: FSMContext, user_service: UserService):
    dadata = DadataAsync(DADATA_KEY)
    inn = message.text.strip()    
    result = await dadata.find_by_id("party", inn)

    if not result:
        await message.answer("Неверно указан ИНН. Попробуйте ещё раз", reply_markup=get_passport_inline_kb())
        return
    
    user_data = await user_service.get_user_by_telegram_id(message.from_user.id)
    await user_service.update_user(
        id=user_data.id,
        user_data=UserUpdate(
            id=user_data.id,
            inn=inn
        )
    )
    await state.clear()
    dadata = DadataAsync(DADATA_KEY)
    registration_date = timestamp_to_date(result[0]['data']['state']['registration_date'])

    template_data = {
        'suggestions': result,
        'registration_date': registration_date
    }

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    result = await load_template_text('passport', **template_data)
    
    await message.answer(result, parse_mode="HTML", reply_markup=get_passport_inline_kb())



@passport_router.callback_query(PassportCallbackData.filter(F.action == "my_company"))
async def show_my_company(callback: CallbackQuery, user: UserResponse):
    template_data = await get_company_info(user)

    if template_data.get("error"):
        await callback.message.answer(template_data["error"], reply_markup=get_passport_inline_kb())
        await callback.answer()
        return

    result_text = await load_template_text('passport', **template_data)

    await callback.message.answer(result_text, parse_mode="HTML", reply_markup=get_passport_inline_kb())
    await callback.answer()



async def show_my_company_from_neuro(message: Message, user: UserResponse):
    template_data = await get_company_info(user)

    if template_data.get("error"):
        await message.answer(template_data["error"], reply_markup=get_passport_inline_kb())
        return

    result_text = await load_template_text('passport', **template_data)

    await message.answer(result_text, parse_mode="HTML", reply_markup=get_passport_inline_kb())




@passport_router.callback_query(PassportCallbackData.filter(F.action == "more_info"))
async def llc_check_html(callback: CallbackQuery, user_service: UserService):
    dadata = DadataAsync(DADATA_KEY)

    user_data = await user_service.get_user_by_telegram_id(callback.from_user.id)

    result = await dadata.find_by_id("party", user_data.inn)

    if user_data.inn is None or user_data.inn == "":
        await callback.message.edit_text("Необходимо заполнить ИНН организации")
        return

    template_data = prepare_company_data_for_template(result[0] if result else {})

    result_html = await load_template_text('passport_html', **template_data)

    html_bytes = result_html.encode('utf-8')

    html_file = BufferedInputFile(html_bytes, filename="Карточка организации.html")

    await callback.message.bot.send_chat_action(chat_id=callback.message.chat.id, action="upload_document")
    await callback.message.answer_document(html_file)



@passport_router.callback_query(PassportCallbackData.filter(F.action == "back"))
async def go_back(callback: CallbackQuery, state: FSMContext,
                user_service: UserService,
                user_subscription_service: UserSubscriptionService,
                user_promocode_service: UserPromocodeService):
    

    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    user_tariff = await user_subscription_service.get_active_subscription(user_id=user.id)

    expire_date = await user_subscription_service.get_subscription_expiry_date(user.id)

    is_premium = True if user_tariff.tariff_name == "premium" else False

    text = await load_template_text("subscription_info", templates_dir="./templates/profile/",
                                    is_premium = is_premium,
                                    subscription_end_date=expire_date.strftime("%d.%m.%Y"))

    referral_promocode = await user_promocode_service.get_user_promocode_by_campaign_name(user.id, "Приведи друга")

    picture = await ImageService.generate_offer(referral_promocode.name, "./files/referal.jpg")

    await callback.message.answer_photo(picture, caption=text, reply_markup=profile_keyboard(is_premium))
    await state.clear()