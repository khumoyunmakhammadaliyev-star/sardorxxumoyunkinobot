from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import CHANNEL_LINK
import database as db


def subscribe_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Kanalga o'tish", url=CHANNEL_LINK or "https://t.me")
    builder.button(text="✅ A'zo bo'ldim", callback_data="check_sub")
    builder.adjust(1)
    return builder.as_markup()


def genres_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    genres = db.get_genres()
    for genre in genres:
        builder.button(text=genre, callback_data=f"genre:{genre}:0")
    builder.adjust(2)
    return builder.as_markup()


def movies_list_keyboard(movies, base_callback, offset, total) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for movie in movies:
        builder.button(text=f"{movie['code']} - {movie['title']}", callback_data=f"get:{movie['code']}")
    builder.adjust(1)

    nav_row = []
    if offset > 0:
        nav_row.append(
            InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"{base_callback}:{max(0, offset - 10)}")
        )
    if offset + 10 < total:
        nav_row.append(
            InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"{base_callback}:{offset + 10}")
        )
    if nav_row:
        builder.row(*nav_row)

    return builder.as_markup()