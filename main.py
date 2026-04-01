import asyncio
from loader import dp, bot
from database.models import init

from handlers import start, download, user, admin

async def main():
    await init()

    dp.include_router(start.router)
    dp.include_router(download.router)
    dp.include_router(user.router)
    dp.include_router(admin.router)

    print("🚀 Bot Running on Render")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
