import asyncio
import json
import logging
import re
import sys

from os import getenv
from typing import List, Tuple

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from common.utils import load_config

from mongoengine import connect

import services.telegram.messages as messages
import services.telegram.keyboards as keyboards

from models.mgo_models import ClassRecord, User, UserStep

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

@dp.message()
async def message_handler(message: types.Message) -> None:
    """
    handle any messages
    """
    user = User.objects.get(telegram_id=message.from_user.id)
    user_step = UserStep.objects.filter(user=user).first()

    if message.text == "cancel":
        user_step.delete()

    if not user_step:
        if message.text == "create_class":
            UserStep.objects.create(
                user=user,
                step="INPUT_CLASS_NAME"
            )
            await message.answer("please input class name")
    else:
        if user_step.step == "INPUT_CLASS_NAME":
            user_step.data = json.dumps({
                "title": message.text
            })
            user_step.step = "INPUT_CLASS_DESC"
            user_step.save()
            await message.answer("please input class description")
        elif user_step.step == "INPUT_CLASS_DESC":
            user_step.data = json.dumps(
                json.loads(user_step.data) | {
                    "desc": message.text
                }
            )
            user_step.step = "INPUT_CLASS_APPROVE"
            user_step.save()
            await message.answer("create class ? if you send no , cancel else approve")
        elif user_step.step == "INPUT_CLASS_APPROVE":
            if message.text == "no":
                user_step.delete()
                await message.answer("canceled")
            else:
                data = json.loads(user_step.data)
                class_record = ClassRecord.objects.create(
                    title=data["title"],
                    description=data["desc"],
                )
                user_step.delete()
                await message.answer(f"class record created : `{class_record.id}`")
            


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
        case "class_list":
            await callback_query.message.answer("class records list", reply_markup=keyboards.class_keyboard())
        case "my_videos":
            video_list: List[Tuple[int, str]] = ... # TODO - code the method to return list of videos ; args : start: int
            await callback_query.message.answer("choose video", reply_markup=keyboards.video_list_keyboard(video_list))
        case "class_time":
            await callback_query.message.answer(messages.class_time, reply_markup=keyboards.start_keyboard())
        case _:
            if callback_data.startswith("class_"):
                cls = ClassRecord.objects.get(id=callback_data.split('_')[1])
                await callback_query.message.answer(cls.title)
                
    # TODO : write callback query vidlst-nxt-page:{index}') 
    #                             vidlst-bck-page:{video_list[0][0]}

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