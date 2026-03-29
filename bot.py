import os
import telebot
from telebot import types
from openai import OpenAI

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

users = set()
channels = []
vip_users = set()

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    users.add(user_id)

    if user_id in vip_users:
        status = "VIP 👑"
    else:
        status = "عادي"

    text = f"""
✨ اهلاً بك في البوت 🔥

👤 ID: {user_id}
⭐ الحالة: {status}

📥 ارسل أي رابط تحميل
🤖 أو احچي ويا AI

"""
    bot.send_message(msg.chat.id, text)

# ================= ADMIN PANEL =================
@bot.message_handler(commands=['admin'])
def admin_panel(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 الاحصائيات", "➕ اضافة قناة")
    markup.add("👑 اضافة VIP")

    bot.send_message(msg.chat.id, "لوحة تحكم المدير 👑", reply_markup=markup)

# ================= STATS =================
@bot.message_handler(func=lambda m: m.text == "📊 الاحصائيات")
def stats(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    bot.send_message(msg.chat.id, f"""
👥 المستخدمين: {len(users)}
👑 VIP: {len(vip_users)}
📡 القنوات: {len(channels)}
""")

# ================= ADD CHANNEL =================
@bot.message_handler(func=lambda m: m.text == "➕ اضافة قناة")
def add_channel(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    msg2 = bot.send_message(msg.chat.id, "ارسل معرف القناة:")
    bot.register_next_step_handler(msg2, save_channel)

def save_channel(msg):
    channels.append(msg.text)
    bot.send_message(msg.chat.id, "تم اضافة القناة ✅")

# ================= VIP =================
@bot.message_handler(func=lambda m: m.text == "👑 اضافة VIP")
def add_vip(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    msg2 = bot.send_message(msg.chat.id, "ارسل ID المستخدم:")
    bot.register_next_step_handler(msg2, save_vip)

def save_vip(msg):
    vip_users.add(int(msg.text))
    bot.send_message(msg.chat.id, "تم تفعيل VIP 👑")

# ================= AI =================
@bot.message_handler(func=lambda m: True)
def ai_chat(msg):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": msg.text}
            ]
        )

        bot.reply_to(msg, response.choices[0].message.content)

    except Exception as e:
        bot.reply_to(msg, "⚠️ صار خطأ")

# ================= RUN =================
print("Bot is running...")
bot.infinity_polling()
