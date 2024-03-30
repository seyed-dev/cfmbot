# This example requires the 'message_content' intent.
import yaml
import sys
import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

config = {}

with open("config.yaml") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        sys.exit(0)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

def discord_bot_runner():
    client.run(config['discord']['token'])
