from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard():
    # Create ReplyKeyboardMarkup
    builder = InlineKeyboardBuilder()
    buttons = [
        "درباره دوره", "لینک دعوت",
        "کیف پول", "لیست فیلم ها",
        "فیلم های من", "زمان کلاس ها",
    ]
    for btn in buttons:
        builder.button(text=btn, callback_data='test')
    builder.adjust(2,2,1)
    return builder.as_markup()