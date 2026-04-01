from aiogram import Router, types
from database.db import connect
from keyboards.user_menu import menu
from config import VIP_POINTS

router = Router()

@router.message(commands=["start"])
async def start(msg: types.Message):
    db = await connect()

    uid = msg.from_user.id
    args = msg.text.split()

    await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))

    if len(args) > 1:
        ref = int(args[1])

        if ref != uid:
            await db.execute("UPDATE users SET points = points + 1 WHERE user_id=?", (ref,))

    await db.commit()

    await msg.answer("🔥 أهلاً بك", reply_markup=menu())
