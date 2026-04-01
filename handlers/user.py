from aiogram import Router, types
from database.db import connect

router = Router()

@router.callback_query(lambda c: c.data == "me")
async def me(call: types.CallbackQuery):
    db = await connect()
    cur = await db.execute("SELECT * FROM users WHERE user_id=?", (call.from_user.id,))
    u = await cur.fetchone()

    await call.message.answer(f"""
👤 حسابك

⭐ نقاط: {u[1]}
📥 تحميلات: {u[3]}
💎 VIP: {'نعم' if u[4] else 'لا'}
""")
