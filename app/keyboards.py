from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
def get_action_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с наводящими вопросами и сохранением"""
    buttons = [
        [
            InlineKeyboardButton(text="⭐ В Избранное", callback_data="save_to_fav"),
            InlineKeyboardButton(text="🛒 В To-Do / Покупки", callback_data="create_todo")
        ],
        [
            InlineKeyboardButton(text="⏱️ Сделать быстрее", callback_data="ask_faster"),
            InlineKeyboardButton(text="❓ Заменить ингредиент", callback_data="ask_substitute")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)