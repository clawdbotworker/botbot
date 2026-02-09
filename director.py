import asyncio
import os
import signal
from agents import social, community, builder

print("========================================")
print("   🤖 CLAWDBOT HIVE MIND ACTIVATING     ")
print("========================================")

async def main():
    # 1. CREATE NERVOUS SYSTEM (Queues)
    builder_queue = asyncio.Queue()

    # 2. START AGENTS
    
    # Social runs autonomously
    task_social = asyncio.create_task(social.run_loop())
    
    # Builder waits for orders (from Discord)
    task_builder = asyncio.create_task(builder.run_loop(builder_queue))
    
    # Discord sends orders TO the builder
    task_discord = asyncio.create_task(community.start(builder_queue))

    print("✅ Director: Agents dispatched (Social + Community + Builder).")

    # Wait forever
    await asyncio.gather(task_social, task_discord, task_builder)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Director: Shutdown signal received. Closing Hive.")

