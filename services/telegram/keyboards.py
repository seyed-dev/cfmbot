from aiogram.utils.keyboard import InlineKeyboardBuilder
from models.mgo_models import ClassRecord

def start_keyboard():
    # Create ReplyKeyboardMarkup
    builder = InlineKeyboardBuilder()
    
    builder.button(text="درباره دوره", callback_data='about_bootcamp')
    builder.button(text="لینک دعوت", callback_data='invite_link')
    builder.button(text="کیف پول", callback_data='wallet')
    builder.button(text="لیست کلاس ها", callback_data='class_list')
    builder.button(text="فیلم های من", callback_data='my_videos')
    builder.button(text="زمان کلاس ها", callback_data='class_time')
    builder.adjust(2)
    return builder.as_markup()

def class_keyboard():
        # Create ReplyKeyboardMarkup
    builder = InlineKeyboardBuilder()
    for cls in ClassRecord.objects.all():
        builder.button(text=cls.title, callback_data=f'class_{cls.id}')

    builder.adjust(1)
    return builder.as_markup()