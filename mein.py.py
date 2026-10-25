import asyncio
import json
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === НАЛАШТУВАННЯ ===
BOT_TOKEN = "8805546826:AAHRqgUr84wIhgpvYRuu1CuPg0v8ZH8OgHQ"  # Вставити свій токен тут
SEND_HOUR = 8  # Година надсилання (наприклад, 10:00 ранку)
SEND_MINUTE = 0  # Хвилини

# Ініціалізація
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Файл для збереження ID користувача, щоб бот знав, куди писати
USER_DATA_FILE = "user_id.txt"


def get_random_task() -> str:
    """Завантажує та повертає випадкове завдання з json-файлу."""
    try:
        with open("tasks.json", "r", encoding="utf-8") as f:
            tasks = json.load(f)
            return random.choice(tasks)
    except Exception as e:
        logging.error(f"Помилка читання tasks.json: {e}")
        return "🎯 Свободний день! Придумай собі легке завдання самостійно."


def save_user_id(user_id: int):
    """Зберігає chat_id у файл."""
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        f.write(str(user_id))


def load_user_id() -> int | None:
    """Зчитує chat_id з файлу."""
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return None


async def send_daily_quest():
    """Функція, яка викликається планувальником щодня."""
    user_id = load_user_id()
    if user_id:
        task = get_random_task()
        message_text = f"✨ **Твоє завдання на сьогодні:**\n\n{task}\n\nГарного дня!"
        await bot.send_message(chat_id=user_id, text=message_text, parse_mode="Markdown")


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обробка команди /start."""
    save_user_id(message.chat.id)
    await message.answer(
        "Привіт! Я твій щоденний квест-бот 🚀\n\n"
        f"Я підключив тебе до сповіщень. Щодня о {SEND_HOUR:02d}:{SEND_MINUTE:02d} "
        "я надсилатиму тобі одне випадкове завдання.\n\n"
        "Якщо хочеш отримати квест просто зараз, напиши команду /quest."
    )


@dp.message(Command("quest"))
async def cmd_quest(message: types.Message):
    """Обробка команди /quest — видати завдання прямо зараз."""
    task = get_random_task()
    await message.answer(f"🎲 **Випадковий квест:**\n\n{task}", parse_mode="Markdown")


async def main():
    logging.basicConfig(level=logging.INFO)

    # Налаштовуємо щоденний розклад
    scheduler.add_job(
        send_daily_quest,
        trigger="cron",
        hour=SEND_HOUR,
        minute=SEND_MINUTE
    )
    scheduler.start()

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())