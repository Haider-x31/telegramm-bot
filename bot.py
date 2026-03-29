import os
import subprocess
from uuid import uuid4

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

TOKEN = "8686945908:AAEfOj2C-MK6oUrjR0Wan-yHBzHU-wPduO8"
CHANNEL_USERNAME = "@your_channel"  # بدون رابط

# ------------------ تحقق الاشتراك ------------------
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def force_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_subscribed(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{CHANNEL_USERNAME.replace('@Gd5bot_bot','')}")],
            [InlineKeyboardButton("✅ تحقق", callback_data="check_sub")]
        ]
        await update.message.reply_text(
            "❌ لازم تشترك بالقناة حتى تستخدم البوت",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return False
    return True

# ------------------ تحميل yt-dlp ------------------
def download_video(url):
    try:
        filename = f"{uuid4().hex}.mp4"
        command = [
            "yt-dlp",
            "-f", "mp4",
            "-o", filename,
            url
        ]

        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(filename):
            return filename
        return None

    except Exception as e:
        print("Download Error:", e)
        return None

# ------------------ START ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 تحميل فيديو", callback_data="download")],
        [InlineKeyboardButton("ℹ️ شرح الاستخدام", callback_data="help")],
        [InlineKeyboardButton("📢 قناتي", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")]
    ]

    await update.message.reply_text(
        "🔥 أهلاً بك في أقوى بوت تحميل\n\n"
        "🎬 TikTok + Instagram\n"
        "⚡ سريع جداً\n\n"
        "📌 اضغط زر أو أرسل رابط",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ------------------ أزرار ------------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await query.message.reply_text(
            "📌 الاستخدام:\n\n"
            "1. انسخ رابط الفيديو\n"
            "2. أرسله للبوت\n"
            "3. انتظر التحميل\n\n"
            "🔥 سهل وسريع"
        )

    elif query.data == "download":
        await query.message.reply_text("📥 أرسل الرابط الآن")

    elif query.data == "check_sub":
        user_id = query.from_user.id
        if await is_subscribed(user_id, context):
            await query.message.reply_text("✅ تم التحقق، أرسل الرابط الآن")
        else:
            await query.message.reply_text("❌ بعدك ما مشترك")

# ------------------ استقبال الروابط ------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await force_subscribe(update, context):
        return

    url = update.message.text

    if "http" not in url:
        await update.message.reply_text("❌ أرسل رابط صحيح")
        return

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    file = download_video(url)

    if file:
        try:
            with open(file, "rb") as f:
                await update.message.reply_video(f)

            os.remove(file)
            await msg.delete()

        except Exception as e:
            print("Send Error:", e)
            await update.message.reply_text("❌ فشل الإرسال")

    else:
        await update.message.reply_text("❌ الرابط ما يشتغل أو خاص")

# ------------------ تشغيل ------------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🔥 البوت شغال احترافي")
app.run_polling()