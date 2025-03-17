from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

keyboard_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance")],
    [InlineKeyboardButton(text="Получить ключ🔑", callback_data="get_key")],
    [InlineKeyboardButton(text="Мои ключи📱", callback_data="my_keys")],
    [InlineKeyboardButton(text="Как подключить🛠️", callback_data="pref")],
    [InlineKeyboardButton(text="ИНФО", callback_data="info")
     ]
])

tel_pref = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📱 iPhone", callback_data="pref_iphone")],
    [InlineKeyboardButton(text="🤖 Android", callback_data="pref_android")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
])

back_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Назад', callback_data='back')]
])

keyboard_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data="pay_stars", pay=True)],
    [InlineKeyboardButton(text='💳 Банковская карта', callback_data='pay_card', pay=True)],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='back')]
])

