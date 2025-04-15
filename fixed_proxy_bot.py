
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiohttp import ClientSession
import re
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "7696979981:AAFFmynvUB4AtEuMlo7IOZNI_YDzgF1XmA8")
OWNER_ID = int(os.getenv("OWNER_ID", 8114177038))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

approved_users = {OWNER_ID}
proxies = []


def extract_proxies(text):
    pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+:\d+)")
    return pattern.findall(text)


async def check_proxy(session, proxy):
    try:
        async with session.get("http://httpbin.org/ip", proxy=f"http://{proxy}", timeout=5) as response:
            if response.status == 200:
                return proxy, True
    except Exception:
        pass
    return proxy, False


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    if message.from_user.id not in approved_users:
        await message.answer("⛔ You are not authorized to use this bot.")
        return

    text = (
        "🔥 Welcome to Shamshed Proxy Checker Bot
"
        "If you need contact click @Shamshed_Boss

"
        "Available Commands:
"
        "1. /start
"
        "2. /check
"
        "3. /live
"
        "4. /dead"
    )
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=["check"])
async def check(message: types.Message):
    if message.from_user.id not in approved_users:
        await message.answer("⛔ You are not authorized to use this command.")
        return

    global proxies
    proxies = extract_proxies(message.text)
    if not proxies:
        await message.answer("⚠️ No proxies found in your message.")
        return

    good = []
    bad = []
    async with ClientSession() as session:
        for proxy in proxies:
            _, status = await check_proxy(session, proxy)
            if status:
                good.append(proxy)
            else:
                bad.append(proxy)

    await message.answer(f"✅ Live: {len(good)} | ❌ Dead: {len(bad)}")
    if good:
        await message.answer("\n".join(good))
    if bad:
        await message.answer("\n".join(bad))


@dp.message_handler(commands=["live"])
async def live(message: types.Message):
    if message.from_user.id not in approved_users:
        await message.answer("⛔ You are not authorized to use this command.")
        return

    good = [p for p in proxies if ":" in p]  # Simplified filter
    await message.answer("\n".join(good) if good else "😶 No live proxies found.")


@dp.message_handler(commands=["dead"])
async def dead(message: types.Message):
    if message.from_user.id not in approved_users:
        await message.answer("⛔ You are not authorized to use this command.")
        return

    bad = []  # Simplified for now
    await message.answer("\n".join(bad) if bad else "🎉 No dead proxies!")

if __name__ == "__main__":
    print("Bot is running...")
    executor.start_polling(dp, skip_updates=True)
