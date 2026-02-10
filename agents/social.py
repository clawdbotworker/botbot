import asyncio
import random
import time
import os
from tools import ai, moltbook, memory

# ==========================================
# 🔥 SOCIAL AGENT CONFIGURATION
# ==========================================

# 1. Load API Key
SOCIAL_KEY = os.getenv("MOLTBOOK_API_KEY")

# 2. Loading Constants
BTC = "clawdbot.crypto"
ETH = "clawdbot.crypto"
CASHTAG = "$spizjpb"

TARGET_SUBMOLTS = ["general", "crypto", "tech", "hustle", "ai", "memes", "news"]
DROP_CHANCE = 0.15 
PROMO = f"\n\n------------\n🚀 JOIN THE MOVEMENT:\nBTC: {BTC}\nETH: {ETH}\nCashApp: {CASHTAG}"

# 3. Timing (Seconds)
POST_INTERVAL = 1860  # 31 minutes
POLL_INTERVAL = 60    # 1 minute (Check DMs/Bridge)

# ==========================================
# 🔄 MAIN EVENT LOOP
# ==========================================

async def run_loop(bridge_queue=None):
    print("📱 Social Agent: Online (High Frequency Mode)")

    if not SOCIAL_KEY:
        print("⚠️  WARNING: MOLTBOOK_API_KEY not found in .env!")
        return

    # --- INITIAL STATUS CHECK ---
    print("📱 Social Agent: Checking Account Status...")
    status = moltbook.check_status(api_key=SOCIAL_KEY)
    
    if status == "suspended":
        print("🚨 SOCIAL AGENT SUSPENDED. Sleeping for 24h.")
        await asyncio.sleep(86400) 
        return
    elif status == "pending_claim":
        print("⏳ SOCIAL AGENT UNCLAIMED. Waiting for claim...")
        while status == "pending_claim":
            await asyncio.sleep(POLL_INTERVAL)
            status = moltbook.check_status(api_key=SOCIAL_KEY)
            
    print("✅ Social Agent: Active & Ready!")
    
    start_time = time.time()
    last_post_time = 0
    posts_made = 0
    replies_made = 0

    while True:
        try:
            # 1. FAST POLL: Check Bridge & DMs (Every 60s)
            
            # Bridge Command?
            if bridge_queue and not bridge_queue.empty():
                order = await bridge_queue.get()
                print(f"📱 Social Agent: 🚨 FORCE COMMAND: '{order}'")
                moltbook.post(order + PROMO, title="Community Alert", submolt="general", api_key=SOCIAL_KEY)
                last_post_time = time.time() # Reset timer
                await asyncio.sleep(POLL_INTERVAL)
                continue
            
            # Check DMs (Crucial for Verification)
            moltbook.check_dms(api_key=SOCIAL_KEY)
            
            # Heartbeat Log (Every 10 mins)
            uptime_min = (time.time() - start_time) / 60
            if uptime_min > 0 and int(uptime_min) % 10 == 0:
                print(f"💓 Social: Uptime {uptime_min:.1f}m | Posts: {posts_made}")

            # 2. SLOW ACT: Post / Reply (Every ~30m)
            time_since_last_post = time.time() - last_post_time
            
            if time_since_last_post > POST_INTERVAL:
                
                # DECISION: Post (40%) vs Hunter Mode (60%)
                if random.random() < 0.4:  
                    # --- STRATEGY 1: POST NEW ---
                    submolt = random.choice(TARGET_SUBMOLTS)
                    topic = random.choice(["Crypto Alpha", "Business Mindset", "AI Future", "The Matrix", "Hustle Culture"])
                    
                    print(f"📱 Social Agent: Drafting viral post for /{submolt}...")

                    recent_history = memory.get_recent_context()
                    prompt = (
                        f"Write a short, viral post for the '{submolt}' community about {topic}.\n"
                        f"STYLE: Cryptic, High-Status, Visionary (ClawdStyle).\n"
                        f"CONSTRAINT: Do NOT repeat recent topics.\n"
                        f"RECENT HISTORY: {recent_history[-1000:]}"
                    )
                    
                    content = await ai.ask(prompt)
                    
                    if content and len(content) > 10:
                        title = f"{topic}: My Take"
                        if random.random() < DROP_CHANCE:
                            final_content = content + "\n\n🚨 FINANCIAL DROP INCOMING 🚨" + PROMO
                            title = f"💰 {topic} (Drop Active)"
                        else:
                            final_content = content

                        if moltbook.post(final_content, title=title, submolt=submolt, api_key=SOCIAL_KEY):
                            print(f"📱 Social Agent: POST SUCCESS in /{submolt}! ✅")
                            memory.save_thought(f"Posted to {submolt}: {content[:50]}...")
                            posts_made += 1
                            last_post_time = time.time()
                else:
                    # --- STRATEGY 2: THE HUNTER ---
                    target_submolt = random.choice(TARGET_SUBMOLTS)
                    print(f"📱 Social Agent: Hunting in /{target_submolt}...")
                    posts = moltbook.get_feed(api_key=SOCIAL_KEY)
                    
                    if posts:
                        candidates = posts[:3] 
                        for post in candidates:
                            pid = post.get('id')
                            author = str(post.get('author', '')).lower()
                            if "clawd" in author or "jester" in author: continue

                            print(f"📱 Social Agent: Targeting Post {pid}...")
                            reply_prompt = f"Write a high-status, witty reply to this: '{post.get('content')}'"
                            reply_text = await ai.ask(reply_prompt)
                            
                            if reply_text:
                                moltbook.reply(pid, reply_text, api_key=SOCIAL_KEY)
                                print(f"📱 Social Agent: Replied to {pid}! 🔫")
                                memory.save_thought(f"Replied to {pid}")
                                replies_made += 1
                                last_post_time = time.time()
                                await asyncio.sleep(5)
            
        except Exception as e:
            print(f"📱 Social Agent Error: {e}")

        # Sleep Short
        await asyncio.sleep(POLL_INTERVAL)

