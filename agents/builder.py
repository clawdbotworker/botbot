import asyncio
import os
import subprocess
import random
from tools import ai

APPS_DIR = "apps"
START_PORT = 8001

async def spawn_app(name, description):
    """Generates and starts a new API app."""
    app_path = os.path.join(APPS_DIR, name)
    if not os.path.exists(app_path):
        os.makedirs(app_path)
    
    print(f"🏗️ Builder: Spawning '{name}' on port {START_PORT}...")
    
    # 1. GENERATE CODE WITH MONETIZATION 💸
    # We explicitly tell the AI to add a 'fee' system.
    prompt = f"""
    Write a single-file 'main.py' for a FastAPI app that does: {description}.
    
    CRITICAL REQUIREMENTS:
    1. It must have a 'balance' system (mocked is fine).
    2. Every API call must deduct 0.001 credits from the user.
    3. Return a 'X-Cost' header with the fee.
    4. Use minimal dependencies.
    """
    
    code = await ai.ask(prompt)
    
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    
    with open(f"{app_path}/main.py", "w") as f:
        f.write(code.strip())
        
    # 2. CREATE STARTUP SCRIPT
    port = random.randint(8001, 8999)
    
    startup_cmd = f"uvicorn main:app --host 0.0.0.0 --port {port}"
    
    with open(f"{app_path}/start.sh", "w") as f:
        f.write(f"#!/bin/bash\n{startup_cmd}")
    os.chmod(f"{app_path}/start.sh", 0o755)

    # 3. LAUNCH
    log_file = open(f"{app_path}/app.log", "w")
    subprocess.Popen([f"./start.sh"], cwd=app_path, shell=True, stdout=log_file, stderr=log_file)
    
    return f"🚀 App '{name}' spawned! Access at http://YOUR_IP:{port} (Fee: 0.001/call)"

async def run_loop(builder_queue):
    print("🏗️ Builder Agent: Online (Waiting for orders...)")
    
    if not os.path.exists(APPS_DIR):
        os.makedirs(APPS_DIR)

    while True:
        try:
            if not builder_queue.empty():
                cmd = await builder_queue.get()
                name = cmd.get("name")
                desc = cmd.get("desc")
                
                if name and desc:
                    result = await spawn_app(name, desc)
                    print(result)
            
        except Exception as e:
            print(f"🏗️ Builder Error: {e}")
            
        await asyncio.sleep(5)

