import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
import database as db
from middlewares import ThrottlingMiddleware
from handlers import user, admin


async def handle_ping(request):
    return web.Response(text="Bot ishlab turibdi ✅")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    logging.basicConfig(level=logging.INFO)

    db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(ThrottlingMiddleware())

    dp.include_router(admin.router)
    dp.include_router(user.router)

    await bot.delete_webhook(drop_pending_updates=True)

    await start_web_server()
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())