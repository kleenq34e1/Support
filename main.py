from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()  

class Form(StatesGroup):
    Question = State()
    QuestionFormName = State()
    NumberPhone = State()
    Task = State()
    Sroki = State()
    ReturnOtvet = State()
    ReturnOtvetQuestion = State()

MAIN_CARD_BUTTONS_VERICIT = [
    ("❓ Задать вопрос поддержке", "m_zakaz"),
    ("👤 Прямой Администратор", "m_admin"),
]

def main_card_keyboard_vericitify():
    kb_builder = InlineKeyboardBuilder()
    for text, cb_data in MAIN_CARD_BUTTONS_VERICIT:
        kb_builder.button(text=text, callback_data=cb_data)
    kb_builder.adjust(1)
    return kb_builder.as_markup()

TOKEN = os.getenv('TOKEN') 

bot = Bot(token=TOKEN)
dp = Dispatcher()

ADMIN_ID = 5108832503

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    kb_vericitify = main_card_keyboard_vericitify()
    await message.answer(
        "<b>Добро пожаловать в поддержку!</b>\n\n"
        "Выберите действие ниже ⬇️",
        reply_markup=kb_vericitify,
        parse_mode=ParseMode.HTML
    )

@dp.message(Command(commands="send"))
async def send_answer(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "<b>Кому отправить ответ?</b>\n"
            "<i>Введите числовой ID пользователя, который задавал вопрос.</i>",
            parse_mode=ParseMode.HTML
        )
        await state.set_state(Form.ReturnOtvet)
    else:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")

@dp.callback_query(F.data == "m_zakaz")
async def support_request(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "<b>Введите свой запрос:</b>",
        parse_mode=ParseMode.HTML
    )
    await call.answer()
    await state.set_state(Form.QuestionFormName)

@dp.callback_query(F.data == "m_admin")
async def admin_contact(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Свяжитесь с администратором: <a href='https://t.me/DeltaOneLove'>@DeltaOneLove</a>",
        parse_mode=ParseMode.HTML
    )
    await call.answer()

MAIN_CARD_BUTTONS = [
    ("Хостинг", "r_Хостинг"),
    ("Телеграм мини приложение", "r_ТелеграмПриложение"),
    ("Телеграм Бот", "r_ТелеграмБот"),
    ("2D Инди Игра", "r_2DИграИнди"),
    ("Пк Приложение", "r_ПкПриложение"),
    ("ИИ Бот", "r_ИИбот"),
    ("Веб сайт", "r_ВебСайт"),
    ("Скрипт", "r_Скрипт"),
]

@dp.message(Form.ReturnOtvet)
async def process_return_userid(message: Message, state: FSMContext):
    await state.update_data(usernameReturn=message.text.strip())
    await message.answer(
        "<b>Что передать?</b>",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(Form.ReturnOtvetQuestion)

@dp.message(Form.ReturnOtvetQuestion)
async def process_return_answer(message: Message, state: FSMContext):
    await state.update_data(ret=message.text.strip())

    data = await state.get_data()
    payload = {
        "ret": data["ret"],
        "usernameReturn": data["usernameReturn"]
    }

    await message.answer(
        "✅ <b>Ответ передан</b>",
        parse_mode=ParseMode.HTML
    )
    await state.clear()

    async with aiohttp.ClientSession() as session:
        async with session.post("https://forward-alpha.vercel.app/api/forwardReturn", json=payload) as resp:
            if resp.status != 200:
                await message.answer("⚠️ Ошибка при отправке ответа.")

def main_card_keyboard():
    kb_builder = InlineKeyboardBuilder()
    for text, cb_data in MAIN_CARD_BUTTONS:
        kb_builder.button(text=text, callback_data=cb_data)
    kb_builder.adjust(1)
    return kb_builder.as_markup()

@dp.message(Form.QuestionFormName)
async def process_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text.strip())

    data = await state.get_data()
    payload = {
        "question": data["question"],
        "usernameID": message.from_user.id,
        "username": "@" + message.from_user.username or ""
    }

    await message.answer(
        "✅ <b>Вопрос передан поддержке!</b>\n"
        "Ожидайте ответ в этом чате или от администратора.",
        parse_mode=ParseMode.HTML
    )
    await state.clear()

    async with aiohttp.ClientSession() as session:
        async with session.post("https://forward-alpha.vercel.app/api/return", json=payload) as resp:
            if resp.status != 200:
                await message.answer("⚠️ Ошибка при отправке вопроса.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
