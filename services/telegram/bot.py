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

import services.telegram.messages as messages
import services.telegram.keyboards as keyboards

from models.mgo_models import User

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
config = {}
bot = None


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Handle the /start command from users.

    Args:
        message (Message): The message object sent by the user.

    Returns:
        None
    """
    # Check if the user exists in the database
    user = User.objects.filter(telegram_id=message.from_user.id).first()
    new_user = False
    # If user doesn't exist, mark as new user and prepare user data
    if not user:
        new_user = True
        user_data = {
            "telegram_id": message.from_user.id,
            "username": message.from_user.username,
            "full_name": message.from_user.full_name,
            "is_premium": message.from_user.is_premium
        }
    
    # Determine the number of arguments in the command
    num_args = len(message.text.split())
    
    # Based on the number of arguments, take appropriate action
    match num_args:
        # If only the command is sent (just /start)
        case 1:
            # If it's a new user, create a user in the database
            if new_user:
                User.objects.create(**user_data)
        # If command has two arguments (ex: /start ref_111111)
        case 2:
            # Split the command into two parts
            ـ, query_command = message.text.split()
            if query_command.startswith("ref_"):
                # Get the inviter user from the referral code
                inviter = User.objects.filter(telegram_id=int(query_command.split('_')[1])).first()
                # If it's a new user and inviter exists, update inviter's invites count,
                # save the new user with inviter's reference, and send a message to inviter
                if new_user and inviter:
                    inviter.invites += 1
                    inviter.save()
                    user_data["inviter"] = inviter.telegram_id
                    User.objects.create(**user_data)
                    await bot.send_message(
                        chat_id=inviter.telegram_id, 
                        text=messages.inviter_message.format(
                            full_name=message.from_user.full_name
                        )
                    )
                # If it's a new user but inviter doesn't exist, just create the user
                else:
                    User.objects.create(**user_data)

    # Send the start message with start keyboard to the user
    await message.answer(messages.start, reply_markup=keyboards.start_keyboard())


@dp.callback_query()
async def handle_callback_query(callback_query: types.CallbackQuery):
    # Extracting callback_data from the InlineKeyboardButton
    callback_data = callback_query.data
    # Here you can parse the callback_data and take actions accordingly

    match (callback_data):
        case "about_bootcamp":
            await callback_query.message.answer("about bot camp!", reply_markup=keyboards.start_keyboard())
        case "invite_link":
            await callback_query.message.answer(
                messages.invite_link.format(
                    bot_username=config["telegram"]["username"], 
                    user_id=callback_query.from_user.id
                )
            )
        case "wallet":
            user = User.objects.get(telegram_id=int(callback_query.from_user.id))
            await callback_query.message.answer(messages.wallet_balance.format(user.wallet), reply_markup=keyboards.start_keyboard())
        case "video_list":
            await callback_query.message.answer("You clicked the button!", reply_markup=keyboards.start_keyboard())
        case "my_videos":
            await callback_query.message.answer("You clicked the button!", reply_markup=keyboards.start_keyboard())
        case "class_time":
            await callback_query.message.answer(messages.class_time, reply_markup=keyboards.start_keyboard())



async def main() -> None:
    # Load configs from yaml file
    global config, bot
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