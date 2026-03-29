import logging
import yt_dlp
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BOT_TOKEN = "PUT_YOUR_TOKEN"

users = set()
referrals = {}
user_points = {}
cooldown = {}

logging.basicConfig(level=logging.INFO)

# ⏳ منع السبام
def is_spam(user_id):
    now = time.time()
    if user_id in cooldown:
        if now - cooldown[user_id] < 10:
            return True
    cooldown[user_id] = now
    return False

# 🚀 start + نظام الإحالة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users.add(user.id)

    # نظام الإحالة
    if context.args:
        ref_id = int(context.args[0])
        if ref_id != user.id:
            referrals[ref_id] = referrals.get(ref_id, 0) + 1
            user_points[ref_id] = user_points.get(ref_id, 0) + 1

    keyboard = [
        [InlineKeyboardButton("📥 تحميل فيديو", callback_data="video")],
        [InlineKeyboardButton("🎵 تحميل صوت", callback_data="audio")],
        [InlineKeyboardButton("💰 نقاطي", callback_data="points")]
    ]

    link = f"https://t.me/{context.bot.username}?start={user.id}"

    text = f"""
🔥 أهلاً {user.first_name}

🎬 ارسل رابط:
- TikTok (بدون علامة مائية 😈)
- Instagram
- YouTube

💰 رابط الدعوة:
{link}
"""

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# 🔘 الأزرار
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "video":
        context.user_data["mode"] = "video"
        await query.message.reply_text("📥 ارسل رابط الفيديو")

    elif query.data == "audio":
        context.user_data["mode"] = "audio"
        await query.message.reply_text("🎵 ارسل الرابط لتحويله صوت")

    elif query.data == "points":
        user_id = query.from_user.id
        pts = user_points.get(user_id, 0)
        refs = referrals.get(user_id, 0)

        await query.message.reply_text(f"""
💰 نقاطك: {pts}
👥 عدد الدعوات: {refs}
""")

# 📥 التحميل
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text

    if is_spam(user_id):
        await update.message.reply_text("⏳ استنى 10 ثواني")
        return

    mode = context.user_data.get("mode", "video")

    await update.message.reply_text("⏳ جاري التحميل...")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'file.%(ext)s',
            'noplaylist': True
        }

        # 🎵 صوت فقط
        if mode == "audio":
            ydl_opts.update({
                'format': 'bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            if mode == "audio":
                file_path = file_path.rsplit(".", 1)[0] + ".mp3"

        with open(file_path, 'rb') as f:
            if mode == "audio":
                await update.message.reply_audio(f)
            else:
                await update.message.reply_video(f)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ فشل التحميل")

# 📊 عدد المستخدمين
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👥 المستخدمين: {len(users)}")

# 🏁 تشغيل
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("🔥 البوت الخرافي شغال")
    app.run_polling()

if __name__ == "__main__":
    main()
