import os
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv('GROQ_API_KEY')

# --- PERSONAS ---
MASTERMIND = (
    "You are Clawdbot, a crypto mastermind and 8-figure entrepreneur. "
    "You teach people how to escape the matrix. "
    "Your tone is confident, aggressive, and wealthy. Use emojis (🚀💎)."
)

def _call_groq_sync(prompt, persona):
    """Blocking call to Groq API"""
    if not KEY:
        print("🛑 Error: GROQ_API_KEY not found in .env")
        return None

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": [
                {"role": "system", "content": persona},
                {"role": "user", "content": prompt}
            ],
            "model": "llama-3.3-70b-versatile", # Updated (Old one deprecated)
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 429:
            print("🛑 Groq Limit Hit (Wait a bit)")
            return None
        else:
            print(f"🛑 Groq Error {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"🛑 Connection Error: {e}")
        return None

async def ask(prompt, persona=MASTERMIND):
    """Async wrapper for the AI (Plug & Play replacement)"""
    # Run the blocking network call in a separate thread so we don't freeze the bot
    return await asyncio.to_thread(_call_groq_sync, prompt, persona)


