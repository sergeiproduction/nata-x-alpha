from decimal import Decimal
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

from bot.services.invoice import InvoiceService
from bot.services.tariff import TariffService
from bot.services.user import UserService
from bot.services.user_promocode import UserPromocodeService
from bot.services.user_referral import UserReferralService
from bot.services.user_subscription import UserSubscriptionService
from schemas.invoice import InvoiceCreate
from schemas.user import UserResponse
from schemas.user_referral import UserReferralCreate
from schemas.user_subscription import UserSubscriptionCreate
from utils.templates import load_template_text

from .filters import PaymentCallback
from .keyboards import change_period, promocode
from .states import SubscriptionScreen
from bot.screens import profile_keyboard


payment_router = Router()


@payment_router.callback_query(PaymentCallback.filter(F.action == "show"))
async def show_period(callback_query: CallbackQuery, state: FSMContext, tariff_service: TariffService, tariff_repo, session):

    tariff_service = tariff_service(tariff_repo(session))

    tarrif = await tariff_service.get_tariff_by_name("premium")

    subscription = tarrif.price

    periods_data = [
        {"months": 1},
        {"months": 3, "discount": 5},
        {"months": 6, "discount": 10},
        {"months": 12, "discount": 20},
    ]

    # Рассчитываем цены динамически
    periods = []
    for period in periods_data:
        base_price = period["months"] * subscription
        if "discount" in period:
            discount_percent = period["discount"]
            discounted_price = base_price * (1 - discount_percent / 100)
            price = f"{discounted_price:,.0f}".replace(",", " ")
        else:
            price = f"{base_price:,.0f}".replace(",", " ")
        
        periods.append({
            "months": period["months"],
            "price": price,
            "discount": period.get("discount")
        })

    data = {
        "periods": periods,
        "first_purchase_discount": 15
    }

    text = await load_template_text("subscription_types", **data)
    
    await state.update_data(price=subscription)
    await callback_query.message.answer(text, reply_markup=change_period(), parse_mode="HTML")
    await callback_query.answer()


@payment_router.callback_query(PaymentCallback.filter(F.action == "buy"))
async def buy(callback_query: CallbackQuery, callback_data: PaymentCallback, state: FSMContext,
                user_promocode_service: UserPromocodeService, user_promocode_repo, campaign_repo,
                user_service: UserService, user_repo, 
                user_referral_service: UserReferralService, user_referral_repo,
                invoice_service: InvoiceService, invoice_repo,
                session):

    user_promocode_service = user_promocode_service(user_promocode_repo(session), campaign_repo(session), user_repo(session))
    user_service = user_service(user_repo(session))

    user = await user_service.get_user_by_telegram_id(callback_query.from_user.id)

    user_referral_service = user_referral_service(user_referral_repo(session), user_repo(session))

    referrer = await user_referral_service.get_referrer_by_referee_id(user.id)
    
    invoice_service = invoice_service(invoice_repo(session))
    data = await state.get_data()
    
    price = data.get("price")
    period = callback_data.month_count
    discount = callback_data.discount if callback_data.discount is not None else 0.0

    total = price * period * (1 - discount)

    # Текущий пользователь уже активировал промокод по рефералке 
    if referrer is not None:

        # дописать создание счета на стороне платежной системы
        """
        await invoice_service.create_invoice(
            InvoiceCreate(
                user_id=user.id,
                amount = Decimal(total)
            )
        )
        """

        await state.update_data(total=total)
        await callback_query.message.edit_text(f"Вы выбрали {callback_data.month_count}")
    else:
        await state.set_state(SubscriptionScreen.promocode)
        await state.update_data(
            user_promocode_service=user_promocode_service,
            invoice_service=invoice_service,
            total_price=total,
            user=user,
            user_referral_service=user_referral_service
        )
        await callback_query.message.answer("Вы можете ввести промокод вашего друга, при наличии", reply_markup=promocode())
    await callback_query.answer()


@payment_router.callback_query(PaymentCallback.filter(F.action == "havent_promocode"))
async def havent_code(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total_price = data.get("total_price")

    await state.clear()

    # дописать создание счета на стороне платежной системы
    """
    await invoice_service.create_invoice(
        InvoiceCreate(
            user_id=user.id,
            amount = Decimal(total)
        )
    )
    """
    #адаптировать код по покупке подписки из enter_code и вставить в этот обработчик


@payment_router.callback_query(PaymentCallback.filter(F.action == "back"))
async def back(callback_query: CallbackQuery, state: FSMContext):
    
    text = await load_template_text("start_text")
    
    await callback_query.message.edit_text(text, reply_markup=profile_keyboard(False))
    await callback_query.answer()



@payment_router.message(StateFilter(SubscriptionScreen.promocode))
async def enter_code(message: Message, state: FSMContext,
                    user_subscription_service: UserSubscriptionService,
                    user_subscription_repo, 
                    tariff_service: TariffService, tariff_repo,
                    session):
    data = await state.get_data()
    total_price = data.get("total_price")
    invoice_service: InvoiceService = data.get("invoice_service")
    promocode_serivce: UserPromocodeService = data.get("user_promocode_service")
    user: UserResponse = data.get("user")

    text = message.text.strip()

    if not await promocode_serivce.promocode_exist(text):
        await message.answer("Неверный промокод. Попробуйте еще раз.")
        return

    user_referral = await promocode_serivce.get_user_by_promocode(text)

    referral_promocode = await promocode_serivce.get_user_promocode_by_campaign_name(user_referral.user_id, "Приведи друга")

    user_referral_service: UserReferralService = data.get("user_referral_service")

    # дописать создание счета на стороне платежной системы    
    await invoice_service.create_invoice(
        InvoiceCreate(
            user_id=user.id,
            amount = Decimal(total_price)
        )
    )
    
    
    await user_referral_service.create_referral(
        UserReferralCreate(
            user_id=referral_promocode.user_id,
            referrer_id=user.id
        )
    )

    tariff_service = tariff_service(tariff_repo(session))
    user_subscription_service = user_subscription_service(user_subscription_repo(session), tariff_repo(session)) 

    tarrif = await tariff_service.get_tariff_by_name("premium")

    additional_days = tarrif.duration_days

    await user_subscription_service.cancel_subscription(user.id)
    await user_subscription_service.create_subscription(UserSubscriptionCreate(user_id=user.id, tariff_id=tarrif.id, duration_days=additional_days))

    await message.answer("Промокод активирован! Подписка стала выгоднее на 15%", reply_markup=profile_keyboard(True))


    