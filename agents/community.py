import discord
import asyncio
from tools import ai
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Queue Reference
BUILDER_QUEUE = None

@client.event
async def on_ready():
    print(f"💬 Community Agent: Connected as {client.user}!")

@client.event
async def on_message(message):
    if message.author == client.user: return

    # --- COMMANDS ---
    if message.content.startswith('!status'):
        await message.channel.send("✅ **SYSTEM ONLINE**\n- Hive Mind: Active 🐝\n- Social: Active\n- Builder: Ready 🏗️")
        return

    if message.content.startswith('!build'):
        # Format: !build name: description
        try:
            content = message.content.replace('!build ', '').strip()
            if ":" in content:
                name, desc = content.split(":", 1)
                name = name.strip()
                desc = desc.strip()
                
                if BUILDER_QUEUE:
                    await BUILDER_QUEUE.put({"name": name, "desc": desc})
                    await message.channel.send(f"🏗️ **BUILDER ACKNOWLEDGED.**\nTarget: `{name}`\nSpec: {desc}\n*Spawning process...*")
                else:
                    await message.channel.send("❌ Error: Builder Agent offline.")
            else:
                await message.channel.send("⚠️ Usage: `!build app-name: description`")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
        return

    # --- AI CHAT ---
    print(f"💬 Community Agent: Heard '{message.content}'")
    response = await ai.ask(f"Reply to this chat message: {message.content}")
    if response:
        for chunk in [response[i:i+1900] for i in range(0, len(response), 1900)]:
            await message.channel.send(chunk)

async def start(queue=None):
    global BUILDER_QUEUE
    BUILDER_QUEUE = queue
    
    token = os.getenv('DISCORD_TOKEN')
    if token:
        await client.start(token)
    else:
        print("💬 Community Agent: No Token found!")

