from aiogram import Router, types
from config import ADMINS
from database.db import connect

router = Router()

def admin(id):
    return id in ADMINS

@router.message(commands=["vip"])
async def vip(msg: types.Message):
    if not admin(msg.from_user.id):
        return

    uid = int(msg.text.split()[1])

    db = await connect()
    await db.execute("UPDATE users SET is_vip=1 WHERE user_id=?", (uid,))
    await db.commit()

    await msg.answer("✅ تم تفعيل VIP")


@router.message(commands=["broadcast"])
async def broadcast(msg: types.Message):
    if not admin(msg.from_user.id):
        return

    text = msg.text.replace("/broadcast ", "")

    db = await connect()
    cur = await db.execute("SELECT user_id FROM users")
    users = await cur.fetchall()

    for u in users:
        try:
            await msg.bot.send_message(u[0], text)
        except:
            pass
