from aiogram import Bot, Router
from aiogram.types import Message
from bot.middlewares.user_init import UserInitializationMiddleware
from neural import processor

all_router = Router()
all_router.message.middleware(UserInitializationMiddleware())

@all_router.message()
async def handle_all_messages(message: Message, bot: Bot, **kwargs):

    await bot.send_chat_action(message.chat.id, action="typing")

    if message.text:
        await processor.update_storage_args_id(
            user_id=message.from_user.id,
            message=message,
            bot=bot,
            **kwargs
        )

        try:
            await processor.process_command(
                message.text,
                user_id=message.from_user.id
            )
        except Exception as e:
            print(e)
            await message.answer("Извините, произошла ошибка при обработке вашего запроса.")


    elif message.voice:
        await processor.update_storage_args_id(
            user_id=message.from_user.id,
            message=message,
            bot=bot,
            **kwargs
        )
        
        file_info = await bot.get_file(message.voice.file_id)
        file_data = await bot.download_file(file_info.file_path)
        voice_bytes = file_data.read()
        
        try:
            result = await processor.process_voice_message(
                voice_bytes, 
                "ogg", 
                user_id=message.from_user.id
            )
            if not result["success"]:
                await message.answer("Извините, произошла ошибка при обработке вашего запроса.")
        except Exception as e:
            print(e)
            await message.answer("Извините, произошла ошибка при обработке вашего запроса.")