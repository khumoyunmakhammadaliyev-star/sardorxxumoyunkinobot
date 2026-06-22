import time

from aiogram import BaseMiddleware
from aiogram.types import Message

from config import THROTTLE_RATE

_last_call: dict[int, float] = {}


class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        user_id = event.from_user.id
        now = time.monotonic()
        last = _last_call.get(user_id, 0)

        if now - last < THROTTLE_RATE:
            return

        _last_call[user_id] = now
        return await handler(event, data)