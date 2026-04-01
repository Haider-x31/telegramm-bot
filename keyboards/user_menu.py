from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 تحميل", callback_data="dl")],
        [InlineKeyboardButton(text="👤 حسابي", callback_data="me")],
        [InlineKeyboardButton(text="⭐ نقاطي", callback_data="points")],
        [InlineKeyboardButton(text="🎁 دعوة", callback_data="ref")],
        [InlineKeyboardButton(text="🏆 الترتيب", callback_data="top")],
    ])
