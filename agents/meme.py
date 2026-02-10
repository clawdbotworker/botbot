import asyncio
import random
import time
import os
from tools import ai, moltbook, memory

# ==========================================
# 🤡 MEME AGENT CONFIGURATION
# ==========================================

# 1. Load API Key
#    We use the Jester key specifically for this agent's identity.
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

# ==========================================
# 🔄 MAIN EVENT LOOP
# ==========================================

async def run_loop(bridge_queue=None):
    """
    The Jester's main event loop.
    Sleeps for long periods, then wakes up to post jokes.
    """
    print("🤡 Meme Agent: Online (Account: ClawdJester)")
    
    # Safety Check
    if not JESTER_KEY:
        print("⚠️  WARNING: MOLTBOOK_API_KEY_JESTER not found in .env!")
        return

    # --- INITIAL STATUS CHECK ---
    print("🤡 Meme Agent: Checking Account Status...")
    status = moltbook.check_status(api_key=JESTER_KEY)
    
    if status == "suspended":
        print("🚨 AGENT SUSPENDED. Sleeping for 24h.")
        await asyncio.sleep(86400) # Sleep 24h
        return
    elif status == "pending_claim":
        print("⏳ AGENT UNCLAIMED. Waiting for claim...")
        # Periodically check status
        while status == "pending_claim":
            await asyncio.sleep(300) # Check every 5m
            status = moltbook.check_status(api_key=JESTER_KEY)
    
    print("✅ Meme Agent: Active & Ready to Roll!")

    start_time = time.time()
    memes_posted = 0

    while True:
        try:
            # --- HEARTBEAT LOG ---
            uptime_min = (time.time() - start_time) / 60
            if uptime_min > 0 and int(uptime_min) % 10 == 0:
                 print(f"💓 Meme Heartbeat: Uptime {uptime_min:.1f}m | Jokes: {memes_posted}")

            # --- DECISION: POST or WAIT? (20% chance) ---
            if random.random() < 0.2:
                # 1. Pick a Target
                submolt = random.choice(MEME_SUBMOLTS)
                print(f"🤡 Meme Agent: Drafting joke for /{submolt}...")

                # 2. Brainstorm with AI
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
                    # 3. Add Flavor (ASCII Art)
                    if random.random() < 0.3:
                        content += "\n" + random.choice(ASCII_ART)

                    title = "pov"
                    
                    # 4. Post using Jester Identity
                    success = moltbook.post(
                        content, 
                        title=title, 
                        submolt=submolt, 
                        api_key=JESTER_KEY
                    )

                    if success:
                        print(f"🤡 Meme Agent: POST SUCCESS in /{submolt}! ✅")
                        memory.save_thought(f"Jester joked in {submolt}")
                        memes_posted += 1
            
            else:
                print("🤡 Meme Agent: Analyzing the vibe... (Holding fire)")

        except Exception as e:
            print(f"🤡 Meme Agent Error: {e}")

        # --- SLEEP CYCLE ---
        # Memes should be rare. 45 to 90 minutes.
        sleep_sec = random.randint(2700, 5400) 
        print(f"🤡 Meme Agent: Resting for {sleep_sec/60:.1f} mins...")
        await asyncio.sleep(sleep_sec)

