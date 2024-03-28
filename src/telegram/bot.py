import asyncio
import logging
import sys

from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from common.utils import load_config

from mongoengine import connect

import src.telegram.messages as messages
import src.telegram.keyboards as keyboards

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
config = {}


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if len(message.text.split()) == 1:
        await message.answer(messages.start, reply_markup=keyboards.start_keyboard())
        return
    
    ـ, query_command = message.text.split()
    if query_command.startswith("ref_"):
        if message.from_user.id == int(query_command.split('_')[1]):
            await message.answer("خودتو دعوت مردک", reply_markup=keyboards.start_keyboard())
        else:
            await message.answer("خوش اومدی قشنگم", reply_markup=keyboards.start_keyboard())

    


@dp.callback_query()
async def handle_callback_query(callback_query: types.CallbackQuery):
    # Extracting callback_data from the InlineKeyboardButton
    callback_data = callback_query.data
    # Here you can parse the callback_data and take actions accordingly

    match (callback_data):
        case "about_bootcamp":
            await callback_query.message.answer("about bot camp!")
        case "invite_link":
            await callback_query.message.answer(
                messages.invite_link.format(
                    bot_username=config["telegram"]["username"], 
                    user_id=callback_query.from_user.id
                )
            )
        case "wallet":
            await callback_query.message.answer("You clicked the button!")
        case "video_list":
            await callback_query.message.answer("You clicked the button!")
        case "my_videos":
            await callback_query.message.answer("You clicked the button!")
        case "class_time":
            await callback_query.message.answer("You clicked the button!")



async def main() -> None:
    # Load configs from yaml file
    global config
    config = load_config("config.yaml")
    # Connect to db
    connect(
        db=config["db"]["dbname"],
        host=config["db"]["url"]
    )
    # Bot token can be obtained via https://t.me/BotFather
    TOKEN = config['telegram']['token']
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


def telegram_bot_runner():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())