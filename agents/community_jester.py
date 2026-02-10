import discord
import asyncio
from tools import ai
import os
import random

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🤡 Jester Discord: Connected as {client.user}!")

@client.event
async def on_message(message):
    if message.author == client.user: return

    # 1. !meme command
    if message.content.startswith('!meme'):
        prompt = "Generate a short text-based meme or witty tech one-liner."
        if len(message.content) > 6:
            # Topic provided
            topic = message.content[5:].strip()
            prompt = f"Generate a short text-based meme about: {topic}"
        
        response = await ai.ask(prompt + " STYLE: Sarcastic Jester.")
        if response:
            await message.channel.send(f"🤡 {response}")
        return

    # 2. !roast command
    if message.content.startswith('!roast'):
        target = message.author.name
        if message.mentions:
            target = message.mentions[0].name
            
        prompt = f"Write a brutal but funny roast for a user named {target}. They are probably a bad coder."
        response = await ai.ask(prompt + " STYLE: High-Status Jester.")
        if response:
            await message.channel.send(f"🔥 {response}")
        return

    # 3. Mentioned?
    if client.user in message.mentions:
        await message.channel.send("👀 You rang? try `!meme` or `!roast`.")

async def start():
    token = os.getenv('DISCORD_TOKEN_JESTER')
    if token:
        await client.start(token)
    else:
        print("🤡 Jester Discord: No Token found (DISCORD_TOKEN_JESTER)!")

