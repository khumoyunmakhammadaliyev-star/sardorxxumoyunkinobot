from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import database as db
from keyboards import subscribe_keyboard, genres_keyboard, movies_list_keyboard
from utils import is_subscribed

router = Router()


def movie_caption(movie: dict) -> str:
    return (
        f"🎬 <b>{movie['title']}</b>\n\n"
        f"📅 Yil: {movie['year']}\n"
        f"🎭 Janr: {movie['genre']}\n"
        f"⏱ Davomiyligi: {movie['duration']}\n"
        f"🗣 Til: {movie['language']}\n"
        f"📺 Sifat: {movie['quality']}\n"
        f"🔢 Kod: {movie['code']}"
    )


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    db.add_user(message.from_user.id, message.from_user.username)

    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(
            "Botdan foydalanish uchun avval kanalimizga a'zo bo'ling 👇",
            reply_markup=subscribe_keyboard(),
        )
        return

    await message.answer(
        "🎬 Xush kelibsiz!\n\n"
        "Kino kodini yuboring (masalan: 1) — men sizga kinoni topib beraman.\n\n"
        "⏳ Eslatma: agar bot biroz vaqt ishlatilmagan bo'lsa, birinchi xabarga "
        "javob qaytarish bir necha soniyadan to bir DAQIQAGACHA cho'zilishi mumkin — "
        "bu normal holat, iltimos shoshilmasdan kuting."
    )


@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        await callback.message.edit_text(
            "✅ Rahmat! Endi botdan foydalanishingiz mumkin.\n\nKino kodini yuboring."
        )
    else:
        await callback.answer("❌ Siz hali kanalga a'zo bo'lmagansiz.", show_alert=True)


@router.message(Command("genres"))
async def cmd_genres(message: Message, bot: Bot):
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer("Avval kanalga a'zo bo'ling 👇", reply_markup=subscribe_keyboard())
        return

    genres = db.get_genres()
    if not genres:
        await message.answer("Hozircha janrlar mavjud emas.")
        return

    await message.answer("🎭 Janrni tanlang:", reply_markup=genres_keyboard())


@router.callback_query(F.data.startswith("genre:"))
async def genre_callback(callback: CallbackQuery):
    parts = callback.data.split(":")
    genre = parts[1]
    offset = int(parts[2])

    movies = db.list_movies(genre=genre, limit=10, offset=offset)
    total = db.count_movies(genre=genre)

    if not movies:
        await callback.answer("Bu janrda kino topilmadi.", show_alert=True)
        return

    await callback.message.edit_text(
        f"🎭 {genre} ({total} ta kino):",
        reply_markup=movies_list_keyboard(movies, f"genre:{genre}", offset, total),
    )


@router.message(Command("list"))
async def cmd_list(message: Message, bot: Bot):
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer("Avval kanalga a'zo bo'ling 👇", reply_markup=subscribe_keyboard())
        return

    movies = db.list_movies(limit=10, offset=0)
    total = db.count_movies()

    if not movies:
        await message.answer("Hozircha botda kinolar mavjud emas.")
        return

    await message.answer(
        f"🎬 Mavjud kinolar ({total} ta):",
        reply_markup=movies_list_keyboard(movies, "list", 0, total),
    )


@router.callback_query(F.data.startswith("list:"))
async def list_callback(callback: CallbackQuery):
    offset = int(callback.data.split(":")[1])
    movies = db.list_movies(limit=10, offset=offset)
    total = db.count_movies()

    await callback.message.edit_text(
        f"🎬 Mavjud kinolar ({total} ta):",
        reply_markup=movies_list_keyboard(movies, "list", offset, total),
    )


async def send_movie(target_message: Message, bot: Bot, code: int):
    movie = db.get_movie(code)
    if not movie:
        await target_message.answer(
            "❌ Bu raqamda kino topilmadi.\n"
            "Iltimos boshqa raqamni tanlang yoki /list orqali mavjud kinolarni ko'ring."
        )
        return

    db.increment_views(code)
    await bot.send_video(
        chat_id=target_message.chat.id,
        video=movie["file_id"],
        caption=movie_caption(movie),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("get:"))
async def get_movie_callback(callback: CallbackQuery, bot: Bot):
    code = int(callback.data.split(":")[1])
    await send_movie(callback.message, bot, code)
    await callback.answer()


@router.message(F.text.regexp(r"^\d{1,6}$"))
async def handle_code(message: Message, bot: Bot):
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer("Avval kanalga a'zo bo'ling 👇", reply_markup=subscribe_keyboard())
        return

    code = int(message.text)
    await send_movie(message, bot, code)