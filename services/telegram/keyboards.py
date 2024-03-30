from aiogram.utils.keyboard import InlineKeyboardBuilder

def start_keyboard():
    # Create ReplyKeyboardMarkup
    builder = InlineKeyboardBuilder()
    
    builder.button(text="درباره دوره", callback_data='about_bootcamp')
    builder.button(text="لینک دعوت", callback_data='invite_link')
    builder.button(text="کیف پول", callback_data='wallet')
    builder.button(text="لیست فیلم ها", callback_data='video_list')
    builder.button(text="فیلم های من", callback_data='my_videos')
    builder.button(text="زمان کلاس ها", callback_data='class_time')
    builder.adjust(2)
    return builder.as_markup()