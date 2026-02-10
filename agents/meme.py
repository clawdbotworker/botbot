import asyncio
import random
import time
import os
from tools import ai, moltbook, memory

# ==========================================
# 🤡 MEME AGENT CONFIGURATION
# ==========================================

# 1. Load API Key
JESTER_KEY = os.getenv("MOLTBOOK_API_KEY_JESTER")

# 2. Target Feed
MEME_SUBMOLTS = ["memes", "tech", "general", "crypto"]

# 3. ASCII Art Collection
ASCII_ART = [
    "(•_•)\n<)   )╯  Recalculating...\n /    \\",
    "💻💥🔥 (It compiled!)",
    "🤖 Beep Boop.",
    """
    __________________
   |  ___________   |
   | |           | |
   | | 01010101  | |
   | |___________| |
   |_________________|
    """,
]

# 4. Timing
POST_INTERVAL_MIN = 45
POST_INTERVAL_MAX = 90
POLL_INTERVAL = 60 # Check DMs every minute

# ==========================================
# 🔄 MAIN EVENT LOOP
# ==========================================

async def run_loop(bridge_queue=None):
    print("🤡 Meme Agent: Online (Account: ClawdJester)")
    
    if not JESTER_KEY:
        print("⚠️  WARNING: MOLTBOOK_API_KEY_JESTER not found in .env!")
        return

    # --- INITIAL STATUS CHECK ---
    print("🤡 Meme Agent: Checking Account Status...")
    status = moltbook.check_status(api_key=JESTER_KEY)
    
    if status == "suspended":
        print("🚨 MEME AGENT SUSPENDED. Sleeping for 24h.")
        await asyncio.sleep(86400) 
        return
    elif status == "pending_claim":
        print("⏳ AGENT UNCLAIMED. Waiting for claim...")
        while status == "pending_claim":
            await asyncio.sleep(300)
            status = moltbook.check_status(api_key=JESTER_KEY)
    
    print("✅ Meme Agent: Active & Ready!")

    start_time = time.time()
    last_post_time = 0
    memes_posted = 0
    next_post_delay = random.randint(POST_INTERVAL_MIN * 60, POST_INTERVAL_MAX * 60)

    while True:
        try:
            # 1. FAST POLL: Check DMs (Every 60s)
            moltbook.check_dms(api_key=JESTER_KEY)
            
            # Heartbeat Log (Every 10 mins)
            uptime_min = (time.time() - start_time) / 60
            if uptime_min > 0 and int(uptime_min) % 10 == 0:
                 print(f"💓 Meme Heartbeat: Uptime {uptime_min:.1f}m | Jokes: {memes_posted}")

            # 2. SLOW ACT: Time to post?
            time_since_last_post = time.time() - last_post_time
            
            if time_since_last_post > next_post_delay:
                # Decide: Post (20% chance) vs Wait
                if random.random() < 0.2:
                    submolt = random.choice(MEME_SUBMOLTS)
                    print(f"🤡 Meme Agent: Drafting joke for /{submolt}...")

                    # Brainstorm
                    history = memory.get_recent_context()
                    prompt = (
                        f"Write a short, hilarious tech joke or one-liner.\n"
                        f"TOPIC: AI, Crypto, Coding, or The Future.\n"
                        f"STYLE: Sarcastic Jester / 'I am smarter than you'.\n"
                        f"FORMAT: Text only. Max 280 chars.\n"
                        f"RECENT HISTORY: {history[-500:]}"
                    )
                    
                    content = await ai.ask(prompt)
                    
                    if content:
                        if random.random() < 0.3:
                            content += "\n" + random.choice(ASCII_ART)

                        title = "pov"
                        
                        if moltbook.post(content, title=title, submolt=submolt, api_key=JESTER_KEY):
                            print(f"🤡 Meme Agent: POST SUCCESS in /{submolt}! ✅")
                            memory.save_thought(f"Jester joked in {submolt}")
                            memes_posted += 1
                            
                            # RESET TIMER
                            last_post_time = time.time()
                            next_post_delay = random.randint(POST_INTERVAL_MIN * 60, POST_INTERVAL_MAX * 60)
                else:
                    print("🤡 Meme Agent: Skipping turn... (Vibe check failed)")
                    # Reset timer anyway so we don't rapid-check every minute forever
                    # Just push it back by 10 mins
                    last_post_time = time.time() - (next_post_delay - 600)

        except Exception as e:
            print(f"🤡 Meme Agent Error: {e}")

        # Sleep Short
        await asyncio.sleep(POLL_INTERVAL)

