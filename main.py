import argparse

parser = argparse.ArgumentParser(description="Run either tel or dis function")

parser.add_argument("command", choices=["tel", "dis"], help="Choose tel or dis")

args = parser.parse_args()

# Check the command and run the corresponding function
if args.command == "tel":
    from src.telegram.bot import telegram_bot_runner
    telegram_bot_runner()
elif args.command == "dis":
    from src.discord.bot import discord_bot_runner
    discord_bot_runner()