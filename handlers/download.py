from aiogram import Router, types
from services.downloader import download
from services.cache import get, set
from database.db import connect

router = Router()

@router.message()
async def download_handler(msg: types.Message):
    url = msg.text

    if "http" not in url:
        return

    cached = get(url)

    if cached:
        await msg.answer_video(cached.decode())
        return

    wait = await msg.answer("⏳ جاري التحميل...")

    try:
        file_path, info = download(url)

        sent = await msg.answer_video(open(file_path, "rb"))

        set(url, sent.video.file_id)

        db = await connect()
        await db.execute("""
        UPDATE users 
        SET points = points + 1,
            downloads = downloads + 1
        WHERE user_id=?
        """, (msg.from_user.id,))
        await db.commit()

        await wait.delete()

    except Exception as e:
        await msg.answer("❌ فشل التحميل")
