import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from openai import AsyncOpenAI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
import os

# --- Переменные окружения ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)
scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Warsaw"))

# --- Ежедневный запрос GPT ---
async def daily_gpt_request():
    prompt = (
        "Выбери для меня случайное часто употребляемое слово в польском языке (существительное или глагол) и напиши его перевод на русский. Если это существительное — просклоняй по всем падежам в единственном и множественном числе. Если это глагол — проспрягай в настоящем,будущем и прошлом времени. Отформатируй текст красиво для Telegram с переносами строк и заголовками."
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content.strip()

    # Отправка в Telegram
    await bot.send_message(CHAT_ID, f"🕖 Слово дня:\n{text}")

# --- Команда /start ---
@dp.message(commands=["start"])
async def start(message: Message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    await message.answer(
        "Бот запущен ✅. Каждый день в 7:00 по Варшавскому времени "
        "буду присылать слово дня."
    )
    scheduler.add_job(daily_gpt_request, "cron", hour=7, minute=0)
    scheduler.start()

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
