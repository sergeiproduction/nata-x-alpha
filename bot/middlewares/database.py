from typing import Any, Callable, Dict
from aiogram import BaseMiddleware
from database.session import AsyncSessionLocal 

class DatabaseSessionMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable,
        event: object,
        data: Dict[str, Any]
    ) -> Any:
        async with AsyncSessionLocal() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
            finally:
                await session.commit()
            return result