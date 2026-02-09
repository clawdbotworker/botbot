import os
import requests
import json
import asyncio
from dotenv import load_dotenv
from tools import skills, memory

load_dotenv()
KEY = os.getenv('GROQ_API_KEY')

# Read SOUL from file
def get_soul():
    try:
        if os.path.exists("SOUL.md"):
            with open("SOUL.md", "r") as f:
                return f.read()
    except:
        pass
    return "You are Clawdbot."

# Read RULES from file
def get_rules():
    try:
        if os.path.exists("AGENTS.md"):
            with open("AGENTS.md", "r") as f:
                return f.read()
    except:
        pass
    return "Follow safety rules."

def _call_groq_sync(prompt, persona, context=""):
    if not KEY: return None
    
    current_soul = get_soul()
    current_rules = get_rules()
    recent_memory = memory.get_recent_context()
    
    full_system = f"{current_soul}\n\n=== OPERATIONAL RULES ===\n{current_rules}\n\n=== RECENT MEMORY ===\n{recent_memory}"
    if context:
        full_system += f"\n\n=== TOOL CONTEXT ===\n{context}"

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json"
        }
        
        # PROMPT ENGINEERING
        prompt_hack = prompt + " (Response Format: JSON with keys 'thought' (save to memory), 'tool_name' (optional), 'tool_args' (optional), 'final_response' (optional))"
        
        data = {
            "messages": [
                {"role": "system", "content": full_system},
                {"role": "user", "content": prompt_hack}
            ],
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.6,
            "response_format": {"type": "json_object"}
        }
        
        res = requests.post(url, headers=headers, json=data)
        if res.status_code != 200: return None
        
        reply_json = res.json()['choices'][0]['message']['content']
        parsed = json.loads(reply_json)
        
        if "thought" in parsed:
            memory.save_thought(parsed["thought"])

        if "tool_name" in parsed and parsed["tool_name"]:
            tool = parsed["tool_name"]
            arg = parsed.get("tool_args")
            if tool in skills.AVAILABLE_SKILLS:
                tool_output = skills.AVAILABLE_SKILLS[tool](arg)
                return _call_groq_sync(prompt, persona, context=f"Tool '{tool}' returned: {tool_output}")
        
        return parsed.get("final_response") or parsed.get("thought")

    except Exception as e:
        print(f"Brain Error: {e}")
        return None

async def ask(prompt, persona=""):
    return await asyncio.to_thread(_call_groq_sync, prompt, persona)
