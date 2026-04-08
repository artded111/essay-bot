import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from aiogram.types import MenuButtonCommands, BotCommand

# ---------- НАСТРОЙКИ ----------
BOT_TOKEN = "8500529217:AAFTtvL1F3jq8_xz9dk-D-eYpLIBSrO8RB4"  # ← Вставь сюда токен от BotFather

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- БАЗА ДАННЫХ ----------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            free_trial_used INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_user_status(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT free_trial_used FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result is None:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (user_id, free_trial_used) VALUES (?, 0)", (user_id,))
        conn.commit()
        conn.close()
        return 0
    return result[0]

def mark_trial_used(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET free_trial_used = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# ---------- ЗАГЛУШКА ПРОВЕРКИ ЭССЕ ----------
async def check_essay(text: str) -> str:
    # Здесь позже будет вызов OpenAI API
    return f"✅ Эссе проверено!\n\nОбъём: {len(text)} символов\n\nОшибки: не найдено (тестовый режим)"

# ---------- ОБРАБОТЧИКИ ----------
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для проверки эссе по английскому.\n\n"
        "📝 Первая проверка — БЕСПЛАТНО.\n"
        "💰 Последующие — 50 руб.\n\n"
        "Отправь мне текст эссе!"
    )

@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    status = get_user_status(user_id)

    if status == 0:
        await message.answer("🔍 Проверяю эссе...")
        result = await check_essay(message.text)
        mark_trial_used(user_id)
        await message.answer(
            result + "\n\n"
            "⚠️ Бесплатная попытка использована.\n"
            "Следующая проверка — 50 руб."
        )
    else:
        await message.answer(
            "💰 Бесплатная проверка уже использована.\n\n"
            "Стоимость проверки — 50 руб.\n"
            "Оплата временно недоступна (ждём одобрения ЮKassa)."
        )

# ---------- ЗАПУСК ----------
async def main():
    init_db()
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота")
    ])
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())