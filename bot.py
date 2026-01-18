import asyncio
import gspread
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from oauth2client.service_account import ServiceAccountCredentials

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "В8596851770:AAGJZNGJS7g3ZvYytZsWLM7zhwHcf0cxLPE"
ADMIN_CHAT_ID = 123456789  # makaridin_bot

SPREADSHEET_NAME = "Wedding Forms"
SHEET_NAME = "Weddings"

# ================= GOOGLE SHEETS =================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)

# ================= BOT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================= FSM =================
class Bride(StatesGroup):
    name = State()
    date = State()
    style = State()
    humor = State()
    story = State()
    forbidden = State()
    guests = State()
    parents = State()
    traditions = State()
    music = State()
    wishes = State()
    contact = State()

# ================= KEYBOARDS =================
def kb(*buttons):
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=b)] for b in buttons],
        resize_keyboard=True
    )

# ================= HANDLERS =================
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer(
        "Привет! 💍\n\n"
        "Я помогу подготовить идеальную свадебную программу.\n"
        "Ответь, пожалуйста, на несколько вопросов — это займёт 5–7 минут 💛\n\n"
        "Как тебя зовут?",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Bride.name)

@dp.message(Bride.name)
async def name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Дата свадьбы?")
    await state.set_state(Bride.date)

@dp.message(Bride.date)
async def date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer(
        "Какой формат свадьбы вам ближе?",
        reply_markup=kb("Классическая", "Современная", "Вечеринка", "Камерная")
    )
    await state.set_state(Bride.style)

@dp.message(Bride.style)
async def style(message: types.Message, state: FSMContext):
    await state.update_data(style=message.text)
    await message.answer(
        "Какой уровень юмора допустим?",
        reply_markup=kb("Лёгкий", "Смелый", "Очень аккуратно")
    )
    await state.set_state(Bride.humor)

@dp.message(Bride.humor)
async def humor(message: types.Message, state: FSMContext):
    await state.update_data(humor=message.text)
    await message.answer("Коротко: история вашего знакомства 💕")
    await state.set_state(Bride.story)

@dp.message(Bride.story)
async def story(message: types.Message, state: FSMContext):
    await state.update_data(story=message.text)
    await message.answer("Есть ли темы, которые точно нельзя упоминать?")
    await state.set_state(Bride.forbidden)

@dp.message(Bride.forbidden)
async def forbidden(message: types.Message, state: FSMContext):
    await state.update_data(forbidden=message.text)
    await message.answer("Какие будут гости? (дети, пожилые, активные друзья)")
    await state.set_state(Bride.guests)

@dp.message(Bride.guests)
async def guests(message: types.Message, state: FSMContext):
    await state.update_data(guests=message.text)
    await message.answer("Как родители относятся к интерактиву и юмору?")
    await state.set_state(Bride.parents)

@dp.message(Bride.parents)
async def parents(message: types.Message, state: FSMContext):
    await state.update_data(parents=message.text)
    await message.answer("Какие традиции хотите оставить?")
    await state.set_state(Bride.traditions)

@dp.message(Bride.traditions)
async def traditions(message: types.Message, state: FSMContext):
    await state.update_data(traditions=message.text)
    await message.answer("Любимая музыка / что точно включать?")
    await state.set_state(Bride.music)

@dp.message(Bride.music)
async def music(message: types.Message, state: FSMContext):
    await state.update_data(music=message.text)
    await message.answer("Ваши пожелания ведущему ✨")
    await state.set_state(Bride.wishes)

@dp.message(Bride.wishes)
async def wishes(message: types.Message, state: FSMContext):
    await state.update_data(wishes=message.text)
    await message.answer("Контакт для связи (Telegram / телефон)")
    await state.set_state(Bride.contact)

@dp.message(Bride.contact)
async def finish(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    # --- Google Sheets ---
    sheet.append_row([
        data["date"], data["name"], data["style"], data["humor"],
        data["story"], data["forbidden"], data["guests"],
        data["parents"], data["traditions"], data["music"],
        data["wishes"], data["contact"]
    ])

    # --- Telegram admin ---
    text = (
        "💍 НОВАЯ АНКЕТА НЕВЕСТЫ\n\n"
        f"👰 Имя: {data['name']}\n"
        f"📅 Дата: {data['date']}\n"
        f"🎉 Формат: {data['style']}\n"
        f"😂 Юмор: {data['humor']}\n"
        f"❤️ История: {data['story']}\n"
        f"⛔ Запреты: {data['forbidden']}\n"
        f"👥 Гости: {data['guests']}\n"
        f"👨‍👩‍👧 Родители: {data['parents']}\n"
        f"🔥 Традиции: {data['traditions']}\n"
        f"🎵 Музыка: {data['music']}\n"
        f"✨ Пожелания: {data['wishes']}\n"
        f"📞 Контакт: {data['contact']}"
    )

    await bot.send_message(ADMIN_CHAT_ID, text)

    # --- ВОРОНКА ---
    await message.answer(
        "Спасибо большое 💛\n\n"
        "Я внимательно изучу ответы и предложу идеальную программу именно под вас.\n"
        "В ближайшее время свяжусь с вами для короткого созвона ✨"
    )
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
