from aiogram import BaseMiddleware
from loader import bot
from database.db import connect

class CheckSub(BaseMiddleware):
    async def __call__(self, handler, event, data):
        db = await connect()
        cur = await db.execute("SELECT channel FROM channels")
        channels = await cur.fetchall()

        for ch in channels:
            member = await bot.get_chat_member(ch[0], event.from_user.id)

            if member.status == "left":
                await event.answer("⚠️ اشترك بالقناة أولاً")
                return

        return await handler(event, data)
