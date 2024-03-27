from aiogram.utils.keyboard import KeyboardBuilder
from aiogram.types import KeyboardButton


def start_keyboard():
    # Create ReplyKeyboardMarkup
    builder = KeyboardBuilder(button_type=KeyboardButton)
    buttons = [
        "درباره دوره", "لینک دعوت",
        "کیف پول", "لیست فیلم ها",
        "فیلم های من", "زمان کلاس ها",
    ]
    for btn in buttons:
        builder.add(
            KeyboardButton(text=btn)
        )
        
    return builder