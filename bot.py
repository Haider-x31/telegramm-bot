import os
import asyncio
import sqlite3
import random
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# --- 1. الإعدادات والمتغيرات (Config) ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
VIP_PRICE = 25

if not TOKEN:
    print("❌ خطأ: BOT_TOKEN غير موجود في إعدادات السيرفر!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- 2. قاعدة البيانات (Database) ---
def init_db():
    conn = sqlite3.connect('bot_pro.db')
    c = conn.cursor()
    # جدول المستخدمين الشامل
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        username TEXT, 
        points INTEGER DEFAULT 0,
        is_vip INTEGER DEFAULT 0, 
        referred_by INTEGER, 
        ref_count INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1, 
        last_wheel DATE,
        join_date DATE,
        is_banned INTEGER DEFAULT 0)''')
    
    # جدول التحميلات لمنع التكرار
    c.execute('CREATE TABLE IF NOT EXISTS downloads (link_hash TEXT PRIMARY KEY, file_id TEXT)')
    
    # جدول السجلات (Logs)
    c.execute('CREATE TABLE IF NOT EXISTS logs (user_id INTEGER, action TEXT, date DATE)')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('bot_pro.db')
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def add_user(user_id, username, ref_by=None):
    conn = sqlite3.connect('bot_pro.db')
    try:
        conn.execute('INSERT OR IGNORE INTO users (user_id, username, referred_by, join_date) VALUES (?, ?, ?, ?)', 
                     (user_id, username, ref_by, datetime.now().date()))
        if ref_by:
            # إضافة نقطة للمدعي وتحديث عدد دعواته
            conn.execute('UPDATE users SET points = points + 1, ref_count = ref_count + 1 WHERE user_id = ?', (ref_by,))
            # مكافأة كل 10 دعوات (5 نقاط إضافية)
            u_ref = conn.execute('SELECT ref_count FROM users WHERE user_id = ?', (ref_by,)).fetchone()
            if u_ref and u_ref[0] % 10 == 0:
                conn.execute('UPDATE users SET points = points + 5 WHERE user_id = ?', (ref_by,))
        conn.commit()
    except: pass
    finally: conn.close()

# --- 3. لوحات المفاتيح (Keyboards) ---
def main_menu(user_id):
    builder = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 بياناتي", callback_query_data="profile"),
         InlineKeyboardButton(text="🎡 عجلة الحظ", callback_query_data="wheel")],
        [InlineKeyboardButton(text="🔗 رابط الدعوة", callback_query_data="invite"),
         InlineKeyboardButton(text="⭐ شراء VIP", callback_query_data="buy_vip")],
        [InlineKeyboardButton(text="📺 مشاهدة إعلان (+1)", callback_query_data="watch_ad")]
    ])
    if user_id == ADMIN_ID:
        builder.inline_keyboard.append([InlineKeyboardButton(text="⚙️ لوحة الأدمن", callback_query_data="admin_stats")])
    return builder

# --- 4. المعالجات (Handlers) ---

@dp.message(Command("start"))
async def start(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user:
        ref_by = int(command.args) if command.args and command.args.isdigit() else None
        add_user(user_id, message.from_user.username, ref_by)
        if ref_by:
            try: await bot.send_message(ref_by, "🎉 مستخدم جديد انضم عبر رابطك! حصلت على نقطة.")
            except: pass

    await message.answer(f"مرحباً بك {message.from_user.first_name} في بوت الخدمات المتكاملة! 🚀", 
                         reply_markup=main_menu(user_id))

@dp.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    u = get_user(call.from_user.id)
    status = "👑 VIP" if u['is_vip'] else "عادي"
    text = (f"👤 **بياناتك الشخصية:**\n\n"
            f"💰 النقاط: `{u['points']}`\n"
            f"👥 الدعوات: `{u['ref_count']}`\n"
            f"🆙 المستوى: `{u['level']}`\n"
            f"💎 الحالة: `{status}`")
    await call.message.edit_text(text, reply_markup=main_menu(call.from_user.id), parse_mode="Markdown")

@dp.callback_query(F.data == "wheel")
async def wheel(call: CallbackQuery):
    u = get_user(call.from_user.id)
    today = datetime.now().date().isoformat()
    
    if u['last_wheel'] == today:
        return await call.answer("❌ استخدمتها اليوم! عد غداً.", show_alert=True)
    
    prize = random.choices([1, 2, 3], weights=[95, 4, 1], k=1)[0]
    conn = sqlite3.connect('bot_pro.db')
    conn.execute('UPDATE users SET points = points + ?, last_wheel = ? WHERE user_id = ?', (prize, today, u['user_id']))
    conn.commit()
    conn.close()
    await call.answer(f"🎡 فزت بـ {prize} نقطة!", show_alert=True)

@dp.callback_query(F.data == "invite")
async def invite(call: CallbackQuery):
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={call.from_user.id}"
    await call.message.answer(f"🔗 رابط الدعوة الخاص بك:\n`{link}`\n\n🎁 كل شخص يدخل تحصل على 1 نقطة.\n🎁 كل 10 أشخاص تحصل على 5 نقاط إضافية!")

@dp.callback_query(F.data == "buy_vip")
async def buy_vip(call: CallbackQuery):
    u = get_user(call.from_user.id)
    if u['points'] >= VIP_PRICE:
        conn = sqlite3.connect('bot_pro.db')
        conn.execute('UPDATE users SET points = points - ?, is_vip = 1 WHERE user_id = ?', (VIP_PRICE, u['user_id']))
        conn.commit()
        conn.close()
        await call.answer("🎉 مبروك! تم تفعيل اشتراك VIP بنجاح.", show_alert=True)
    else:
        await call.answer(f"❌ نقاطك غير كافية (تحتاج {VIP_PRICE})", show_alert=True)

# --- نظام التحميل (مثال للمنطق) ---
@dp.message(F.text.contains("tiktok.com") | F.text.contains("instagram.com"))
async def handle_download(message: types.Message):
    u = get_user(message.from_user.id)
    url_hash = hashlib.md5(message.text.encode()).hexdigest()
    
    conn = sqlite3.connect('bot_pro.db')
    exist = conn.execute('SELECT file_id FROM downloads WHERE hash = ?', (url_hash,)).fetchone()
    if exist:
        conn.close()
        return await message.answer_video(exist[0], caption="✅ تم تحميله سابقاً")
    
    msg = await message.answer("⏳ جاري التحميل... يرجى الانتظار")
    # هنا يوضع كود yt-dlp الفعلي
    await msg.edit_text("هذا الرابط جديد، سيتم معالجته (يتطلب إعداد مكتبة التحميل بالسيرفر).")

# --- لوحة الأدمن (Admin Panel) ---
@dp.callback_query(F.data == "admin_stats")
async def admin_panel(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID: return
    conn = sqlite3.connect('bot_pro.db')
    total = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    vips = conn.execute('SELECT COUNT(*) FROM users WHERE is_vip = 1').fetchone()[0]
    conn.close()
    
    text = (f"⚙️ **لوحة التحكم:**\n\n"
            f"👥 إجمالي المستخدمين: `{total}`\n"
            f"👑 مستخدمي VIP: `{vips}`\n"
            f"📅 التاريخ: `{datetime.now().date()}`")
    await call.message.answer(text, parse_mode="Markdown")

# --- التشغيل الرئيسي ---
async def main():
    init_db()
    print("✅ البوت قيد التشغيل بنجاح...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("❌ تم إيقاف البوت.")
