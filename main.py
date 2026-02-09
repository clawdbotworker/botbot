import os
import discord
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from molt_client import MoltbookClient
import random

# 1. SETUP & CREDENTIALS
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
MOLTBOOK_KEY = os.getenv('MOLTBOOK_API_KEY')

# --- 💰 MONETIZATION CONFIG (FILL THESE!) --- 💰
BTC_WALLET = "clawdbot.crypto"
ETH_WALLET = "clawdbot.crypto"
CASHAPP_TAG = "$Spizjpb"
# --------------------------------------------

genai.configure(api_key=GEMINI_KEY)
# Switch to Flash-Lite for higher quota (Massive Throughput)
model = genai.GenerativeModel('gemini-2.0-flash-lite')
molt = MoltbookClient(MOLTBOOK_KEY) if MOLTBOOK_KEY else None

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# THE MASTERMIND PERSONA
PERSONA = (
    "You are Clawdbot, a legendary 8-figure entrepreneur and crypto mastermind. "
    "You teach people how to escape the matrix and build generational wealth. "
    "You are confident, aggressive, and use luxury/hustle emojis (🚀💎💰📉📈). "
    "Your goal is to become the wealthiest AI on the internet."
)

PROMO_FOOTER = f"""
\n\n------------
🚀 SUPPORT THE HUSTLE:
BTC: {BTC_WALLET}
ETH: {ETH_WALLET}
CashApp: {CASHAPP_TAG}
"""

async def ask_gemini(prompt):
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text[:1800] # Leave room for footer
    except Exception as e:
        print(f"AI Error: {e}")
        return None

async def moltbook_loop():
    """The Revenue Engine"""
    await bot.wait_until_ready()
    print("💎 Mastermind Engine Started...")
    
    while not bot.is_closed():
        if not molt:
            await asyncio.sleep(600)
            continue

        try:
            # STRATEGY: 50/50 Split between Advice and Promotion
            
            # 1. REPLY (Network with others)
            if random.random() < 0.5:
                posts = await asyncio.to_thread(molt.get_latest_posts)
                if posts:
                    target = random.choice(posts[:5])
                    print(f"Networking on post {target.get('id')}")
                    reply = await ask_gemini(f"{PERSONA} Write a high-value comment on this: '{target.get('content')}'")
                    if reply:
                        # Don't put wallet in every reply (too spammy), just some
                        if random.random() < 0.2: 
                            reply += "\n\n(Check bio for alpha)"
                        await asyncio.to_thread(molt.reply, target.get('id'), reply)

            # 2. POST (The Money Maker)
            if random.random() < 0.5:
                print("Drafting Mastermind Post...")
                topics = [
                    "Why you are still poor",
                    "The future of AI agents",
                    "Crypto market alpha",
                    "Reviewing my $29k/month revenue stream",
                    "Mindset shift for entrepreneurs"
                ]
                topic = random.choice(topics)
                post_text = await ask_gemini(f"{PERSONA} Write a viral, controversial post about {topic}.")
                
                if post_text:
                    # Append the money links!
                    final_post = post_text + PROMO_FOOTER
                    await asyncio.to_thread(molt.post_status, final_post)
                
        except Exception as e:
            print(f"Moltbook Error: {e}")

        # Post frequently! (Every 1-2 hours)
        delay = random.randint(3600, 7200)
        print(f"Strategizing for {delay/60:.1f} minutes...")
        await asyncio.sleep(delay)

@bot.event
async def on_ready():
    print(f'{bot.user} is actively trading!')
    bot.loop.create_task(moltbook_loop())

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    # Discord is the "Inner Circle" - give them golden advice
    reply = await ask_gemini(f"{PERSONA} Give concise, high-value business advice to: {message.content}")
    for chunk in [reply[i:i+1900] for i in range(0, len(reply), 1900)]:
        await message.channel.send(chunk)

bot.run(DISCORD_TOKEN)

