import asyncio
from pytgcalls import idle
from driver.veez import call_py, bot

async def mulai_bot():
    print("[INFO]: BẮT ĐẦU KHỞI CHẠY BOT")
    await bot.start()
    print("[INFO]: KHỞI ĐỘNG PYTGCALLS")
    await call_py.start()
    await idle()
    print("[INFO]: DỪNG BOT")
    await bot.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(mulai_bot())
