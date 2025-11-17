from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from bot.middlewares.chat_action import ChatActionMiddleware
from bot.middlewares.user_init import UserInitializationMiddleware
from bot.screens import StartScreen

from bot.screens.checklists.keyboards import checklist_keyboard
from bot.screens.start.keyboards import start_screen
from bot.screens.startup.user_cases import get_checklists, handle_stage_request
from bot.services.checklist import ChecklistService

from bot.screens.faq.keyboard import build_categories_keyboard

from bot.services.checklist_item import ChecklistItemService
from bot.services.checklist_user_item import UserChecklistItemService
from bot.services.user_subscription import UserSubscriptionService
from schemas.user import UserResponse

from .filters import StartupCallback
from .keyboards import startup_keyboard
from utils.templates import load_template_text

from neural import processor

startup_router = Router()

startup_router.message.middleware(ChatActionMiddleware())
startup_router.message.middleware(UserInitializationMiddleware())
startup_router.callback_query.middleware(ChatActionMiddleware())
startup_router.callback_query.middleware(UserInitializationMiddleware())

@startup_router.message(Command("startup"))
async def cmd_startup(message: Message, state: FSMContext):
    text = await load_template_text("startup_menu")
    await message.answer(text, reply_markup=startup_keyboard())
    await state.clear()


@startup_router.callback_query(StartupCallback.filter(F.action == "first_stage"))
async def first_stage_callback(
    callback_query: CallbackQuery,
    user: UserResponse,
    user_subscription_service: UserSubscriptionService
):
    await handle_stage_request(callback_query, user, user_subscription_service, "I этап")


@startup_router.callback_query(StartupCallback.filter(F.action == "second_stage"))
async def second_stage_callback(
    callback_query: CallbackQuery,
    user: UserResponse,
    user_subscription_service: UserSubscriptionService
):
    await handle_stage_request(callback_query, user, user_subscription_service, "II этап")



@startup_router.callback_query(StartupCallback.filter(F.action == "faq"))
async def faq(callback_query: CallbackQuery):
    text = await load_template_text("faq_menu")
    await callback_query.message.edit_text(text, reply_markup=await build_categories_keyboard())
    await callback_query.answer()


async def faq_from_neuro(message: Message):
    text = await load_template_text("faq_menu")
    await message.answer(text, reply_markup=await build_categories_keyboard())


@startup_router.callback_query(StartupCallback.filter(F.action == "finances"))
async def finances(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Финансы стартапа.")
    await callback_query.answer()


@startup_router.callback_query(StartupCallback.filter(F.action == "checklists"))
async def checklists(callback_query: CallbackQuery, checklist_service: ChecklistService,
                    checklist_item_service: ChecklistItemService, user_checklist_item_service: UserChecklistItemService,
                    user: UserResponse
):

    checklists = await get_checklists(
        checklist_service,
        checklist_item_service,
        user_checklist_item_service,
        user
    )
    
    text = await load_template_text("startup_menu")
    await callback_query.message.edit_text(text, reply_markup=await checklist_keyboard(checklists))
    await callback_query.answer()


async def checklists_from_neuro(
    message: Message,
    checklist_service: ChecklistService,
    checklist_item_service: ChecklistItemService,
    user_checklist_item_service: UserChecklistItemService,
    user: UserResponse
):
    checklists = await get_checklists(
        checklist_service,
        checklist_item_service,
        user_checklist_item_service,
        user
    )
    
    text = await load_template_text("startup_menu")
    await message.answer(text, reply_markup=await checklist_keyboard(checklists))


@startup_router.callback_query(StartupCallback.filter(F.action == "back"))
async def back_to_start(callback_query: CallbackQuery, state: FSMContext):
    
    text = await load_template_text("start_text")
    await callback_query.message.answer(
        text=text,
        reply_markup=start_screen()
    )
    await callback_query.answer()
    await state.set_state(StartScreen.start)