import asyncio
import os
import signal
import traceback
from agents import social, community, builder, meme, community_jester

print("========================================")
print("   🤖 CLAWDBOT HIVE MIND ACTIVATING     ")
print("========================================")

async def safe_run(name, coro):
    """Wraps an agent coroutine to catch crashes and log them."""
    try:
        await coro
    except asyncio.CancelledError:
        print(f"🛑 {name}: Stopped.")
    except Exception as e:
        print(f"🔥 CRITICAL ERROR in {name}: {e}")
        traceback.print_exc()

async def main():
    # 1. CREATE NERVOUS SYSTEM (Queues)
    builder_queue = asyncio.Queue()

    # 2. START AGENTS (Wrapped for safety)
    print("🚀 Launching Agents...")
    
    tasks = []
    
    # Social (Growth)
    tasks.append(asyncio.create_task(safe_run("Social Agent", social.run_loop())))
    
    # Jester (Memes)
    tasks.append(asyncio.create_task(safe_run("Meme Agent", meme.run_loop())))
    
    # Builder (Code)
    tasks.append(asyncio.create_task(safe_run("Builder Agent", builder.run_loop(builder_queue))))
    
    # Community (Discord - Main)
    tasks.append(asyncio.create_task(safe_run("Discord Main", community.start(builder_queue))))
    
    # Community (Discord - Jester)
    tasks.append(asyncio.create_task(safe_run("Discord Jester", community_jester.start())))

    print("✅ Director: All agents dispatched.")

    # Wait forever
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Director: Shutdown signal received. Closing Hive.")

