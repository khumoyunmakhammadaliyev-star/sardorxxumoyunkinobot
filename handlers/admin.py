from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import database as db
from config import ADMIN_IDS

router = Router()
router.message.filter(F.from_user.id.in_(ADMIN_IDS))


class AddMovie(StatesGroup):
    code = State()
    title = State()
    year = State()
    genre = State()
    duration = State()
    language = State()
    quality = State()
    file = State()


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    await state.set_state(AddMovie.code)
    await message.answer(
        "🔢 Kino uchun kod (raqam) kiriting:\n(masalan: 1)\n\nBekor qilish uchun /cancel"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.")


@router.message(AddMovie.code)
async def add_code(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos faqat raqam kiriting.")
        return

    code = int(message.text)
    if db.code_exists(code):
        await message.answer("⚠️ Bu kod band. Boshqa raqam kiriting.")
        return

    await state.update_data(code=code)
    await state.set_state(AddMovie.title)
    await message.answer("🎬 Kino nomini kiriting:")


@router.message(AddMovie.title)
async def add_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddMovie.year)
    await message.answer("📅 Chiqarilgan yilini kiriting:")


@router.message(AddMovie.year)
async def add_year(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(AddMovie.genre)
    await message.answer("🎭 Janrini kiriting (masalan: Jangari):")


@router.message(AddMovie.genre)
async def add_genre(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await state.set_state(AddMovie.duration)
    await message.answer("⏱ Davomiyligini kiriting (masalan: 1soat 45daqiqa):")


@router.message(AddMovie.duration)
async def add_duration(message: Message, state: FSMContext):
    await state.update_data(duration=message.text)
    await state.set_state(AddMovie.language)
    await message.answer("🗣 Tilini kiriting (masalan: O'zbek tilida):")


@router.message(AddMovie.language)
async def add_language(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await state.set_state(AddMovie.quality)
    await message.answer("📺 Sifatini kiriting (masalan: HD):")


@router.message(AddMovie.quality)
async def add_quality(message: Message, state: FSMContext):
    await state.update_data(quality=message.text)
    await state.set_state(AddMovie.file)
    await message.answer("📤 Endi kino videosini yuboring (yoki kanaldan forward qiling):")


@router.message(AddMovie.file, F.video)
async def add_file(message: Message, state: FSMContext):
    data = await state.get_data()
    db.add_movie(
        code=data["code"],
        title=data["title"],
        year=data["year"],
        genre=data["genre"],
        duration=data["duration"],
        language=data["language"],
        quality=data["quality"],
        file_id=message.video.file_id,
    )
    await state.clear()
    await message.answer(f"✅ Kino muvaffaqiyatli qo'shildi!\nKod: {data['code']}")


@router.message(AddMovie.file)
async def add_file_invalid(message: Message):
    await message.answer("Iltimos video fayl yuboring (rasm yoki matn emas).")


@router.message(Command("delete"))
async def cmd_delete(message: Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Foydalanish: /delete <kod>\nMasalan: /delete 5")
        return

    code = int(args[1])
    if db.delete_movie(code):
        await message.answer(f"🗑 {code}-kod o'chirildi.")
    else:
        await message.answer("Bu kodda kino topilmadi.")


@router.message(Command("edit"))
async def cmd_edit(message: Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4 or not parts[1].isdigit():
        await message.answer(
            "Foydalanish: /edit <kod> <maydon> <yangi qiymat>\n"
            "Maydonlar: title, year, genre, duration, language, quality\n"
            "Masalan: /edit 5 title Yangi nom"
        )
        return

    code = int(parts[1])
    field = parts[2]
    value = parts[3]

    if db.update_movie_field(code, field, value):
        await message.answer(f"✅ {code}-kod uchun '{field}' yangilandi.")
    else:
        await message.answer("Xatolik: kod topilmadi yoki maydon nomi noto'g'ri.")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    total_users = db.count_users()
    total_movies = db.count_movies()
    top = db.top_movies(10)

    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: {total_users}\n"
        f"🎬 Kinolar: {total_movies}\n\n"
        f"🔥 Eng ko'p so'ralganlar:\n"
    )
    if not top:
        text += "Hozircha ma'lumot yo'q."
    else:
        for i, movie in enumerate(top, start=1):
            text += f"{i}. {movie['title']} (kod: {movie['code']}) — {movie['views']} marta\n"

    await message.answer(text, parse_mode="HTML")