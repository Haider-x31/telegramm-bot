from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("8686945908:AAH79liYdVN2fj0fj7LQMKXA3R4xZhFQCRg")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 البوت شغال بنجاح")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Bot is running...")
app.run_polling()
