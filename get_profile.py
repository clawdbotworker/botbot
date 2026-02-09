import requests
import os
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv('MOLTBOOK_API_KEY')

try:
    res = requests.get(
        "https://www.moltbook.com/api/v1/agents/me",
        headers={"Authorization": f"Bearer {KEY}"}
    )
    if res.status_code == 200:
        agent = res.json().get('agent', {})
        name = agent.get('name')
        print(f"\n✅ FOUND IT!")
        print(f"Agent Name: {name}")
        print(f"Profile URL: https://www.moltbook.com/u/{name}")
    else:
        print(f"Error: {res.text}")
except Exception as e:
    print(e)
