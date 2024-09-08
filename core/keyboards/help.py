from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

help_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Помощь',
            callback_data='get_help'
        )
    ]
])