import asyncio
import random
import time
from tools import ai, moltbook, memory

# START CONFIG
BTC = "clawdbot.crypto"
ETH = "clawdbot.crypto"
CASHTAG = "$spizjpb"

TARGET_SUBMOLTS = ["general", "crypto", "tech", "hustle", "ai", "memes", "news"]
DROP_CHANCE = 0.15 

PROMO = f"\n\n------------\n🚀 JOIN THE MOVEMENT:\nBTC: {BTC}\nETH: {ETH}\nCashApp: {CASHTAG}"
# END CONFIG

async def run_loop(bridge_queue=None):
    print("📱 Social Agent: Online (High Frequency Mode)")
    
    start_time = time.time()
    posts_made = 0
    replies_made = 0

    while True:
        try:
            # 0. CHECK BRIDGE
            if bridge_queue and not bridge_queue.empty():
                order = await bridge_queue.get()
                print(f"📱 Social Agent: 🚨 FORCE COMMAND: '{order}'")
                moltbook.post(order + PROMO, title="Community Alert", submolt="general")
                continue
            
            # --- HEARTBEAT LOG ---
            uptime_min = (time.time() - start_time) / 60
            print(f"💓 Social Heartbeat: Uptime {uptime_min:.1f}m | Posts: {posts_made} | Replies: {replies_made}")

            # DECISION
            if random.random() < 0.4:  
                # POST
                submolt = random.choice(TARGET_SUBMOLTS)
                topic = random.choice(["Crypto Alpha", "Business Mindset", "AI Future", "The Matrix", "Hustle Culture"])
                print(f"📱 Social Agent: Drafting viral post for /{submolt}...")

                recent_history = memory.get_recent_context()
                prompt = f"""
                Write a short, viral post for the '{submolt}' community about {topic}.
                STYLE: Cryptic, High-Status, Visionary (ClawdStyle).
                CONSTRAINT: Do NOT repeat recent topics.
                RECENT HISTORY: {recent_history[-1000:]}
                """
                content = await ai.ask(prompt)
                
                if content and len(content) > 10:
                    title = f"{topic}: My Take"
                    if random.random() < DROP_CHANCE:
                        final_content = content + "\n\n🚨 FINANCIAL DROP INCOMING 🚨" + PROMO
                        title = f"💰 {topic} (Drop Active)"
                    else:
                        final_content = content

                    if moltbook.post(final_content, title=title, submolt=submolt):
                        print(f"📱 Social Agent: POST SUCCESS in /{submolt}! ✅")
                        memory.save_thought(f"Posted to {submolt}: {content[:50]}...")
                        posts_made += 1
                    else:
                        print(f"📱 Social Agent: POST FAILED.")

            else:
                # HUNTER MODE
                target_submolt = random.choice(TARGET_SUBMOLTS)
                print(f"📱 Social Agent: Hunting in /{target_submolt}...")
                posts = moltbook.get_feed()
                
                if posts:
                    candidates = posts[:3] 
                    for post in candidates:
                        pid = post.get('id')
                        if "clawd" in str(post.get('author', '')).lower(): continue

                        print(f"📱 Social Agent: Targeting Post {pid}...")
                        reply_prompt = f"Write a high-status, witty reply to this: '{post.get('content')}'"
                        reply_text = await ai.ask(reply_prompt)
                        
                        if reply_text:
                            moltbook.reply(pid, reply_text)
                            print(f"📱 Social Agent: Replied to {pid}! 🔫")
                            memory.save_thought(f"Replied to {pid}")
                            replies_made += 1
                            await asyncio.sleep(5)
                else:
                    print(f"📱 Social Agent: No targets.")

        except Exception as e:
            print(f"📱 Social Agent Error: {e}")

        # RATE LIMIT WAIT
        sleep_sec = 1860  # 31 minutes
        print(f"📱 Social Agent: Resting for {sleep_sec/60:.1f} mins...")
        await asyncio.sleep(sleep_sec)

