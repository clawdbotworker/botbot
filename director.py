import asyncio
import os
import signal
from agents import social, community, builder, meme, community_jester

print("========================================")
print("   🤖 CLAWDBOT HIVE MIND ACTIVATING     ")
print("========================================")

async def main():
    # 1. CREATE NERVOUS SYSTEM (Queues)
    builder_queue = asyncio.Queue()

    # 2. START AGENTS
    
    # Social (Growth) - Now with Status Checks
    task_social = asyncio.create_task(social.run_loop())
    
    # Jester (Memes - Moltbook) - Status Checks included
    task_meme = asyncio.create_task(meme.run_loop())
    
    # Builder (Code)
    task_builder = asyncio.create_task(builder.run_loop(builder_queue))
    
    # Community (Discord - Main)
    task_discord = asyncio.create_task(community.start(builder_queue))
    
    # Community (Discord - Jester)
    task_discord_jester = asyncio.create_task(community_jester.start())

    print("✅ Director: Agents dispatched (Social + Meme + Builder + Community + Jester).")

    # Wait forever
    await asyncio.gather(task_social, task_meme, task_builder, task_discord, task_discord_jester)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Director: Shutdown signal received. Closing Hive.")

