import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BotCommand
from dotenv import dotenv_values

TOKEN = dotenv_values(".env")["BOT_KEY"]

from db import VectorStorage
from llm import SaigaLLM

db = VectorStorage()
llm = SaigaLLM()

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="add", description="Добавить факт: /add <текст>"),
        BotCommand(command="get_all", description="Показать все факты"),
        BotCommand(command="search", description="Найти похожий факт: /search <текст>"),
        BotCommand(command="generate", description="Сгенерировать текст: /generate <текст>"),
        BotCommand(command="rag", description="Сгенерировать текст по факту: /rag <текст>"),
        BotCommand(command="help", description="Список всех команд")
    ]
    await bot.set_my_commands(commands)

@dp.message(Command("help"))
async def help_handler(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/add <текст> — сохранить новый факт в базу\n"
        "/get_all — вывести список всех сохраненных фактов\n"
        "/search <запрос> — найти наиболее похожий факт\n"
        "/generate <промпт> — сгенерировать текст\n"
        "/rag <промпт> — сгенерировать текст по факту\n"
        "/help — показать это сообщение"
    )
    await message.reply(help_text)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я бот для хранения фактов и генерации текстов. Используй /help, чтобы узнать мои команды.")

@dp.message(Command("add"))
async def add_fact(message: types.Message):
    fact = message.text.replace("/add", "").strip()
    if not fact:
        return await message.reply("Введи факт после команды. Пример: /add Солнце — это звезда.")
    
    db.add(fact)
    await message.reply("Факт сохранён!")

@dp.message(Command("get_all"))
async def get_all_facts(message: types.Message):
    results = db.get_all()
    if not results.strip():
        return await message.reply("База пока пуста.")
    await message.reply(f"Вот, что я знаю:\n\n{results}")

@dp.message(Command("search"))
async def search_fact(message: types.Message):
    query = message.text.replace("/search", "").strip()
    if not query:
        return await message.reply("Введи запрос после команды. Пример: /search Что ты знаешь о кошках?")
    
    result = db.search_one(query)
    if not result.strip():
        await message.reply("Похожих фактов не найдено.")
    else:
        await message.reply(f"Найдено похожее:\n{result}")

@dp.message(Command("generate"))
async def handle_generate(message: types.Message):
    prompt = message.text.replace("/generate", "").strip()
    if not prompt:
        return await message.reply("Введи текст после команды. Пример: /generate Что такое искусственный интеллект?")
    
    status_message = await message.reply("Думаю над ответом...")
    try:
        response = llm.generate(prompt)
        await status_message.delete()
        await message.reply(response)
    except Exception as e:
        await status_message.delete()
        await message.reply(f"Произошла ошибка при генерации ответа. Ошибка: {str(e)}")

@dp.message(Command("rag"))
async def handle_rag(message: types.Message):
    user_query = message.text.replace("/rag", "").strip()
    if not user_query:
        return await message.reply("Введи запрос после команды. Пример: /rag Расскажи что-нибудь интересное о космосе.")

    status_msg = await message.reply("Ищу информацию в базе...")
    context = db.search_one(user_query)

    if not context.strip():
        await status_msg.edit_text("Не найдено релевантной информации в базе. Попробуй другой запрос или добавь факты через /add")
        return

    prompt = (
        "Ответь на вопрос, используя только информацию из базы данных. Если информации недостаточно, ответь максимально полно на основе того, что есть.\n\n"        
        f"Контекст: {context}\n\n"
        f"Вопрос: {user_query}"
    )

    try:
        response = llm.generate(prompt) 
        await status_msg.delete()
        await message.reply(f"Ответ на основе базы:\n\n{response}")
    except Exception as e:
        await status_msg.delete()
        await message.reply(f"Произошла ошибка при генерации. Ошибка: {str(e)}")

async def main():
    await set_commands(bot)
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())