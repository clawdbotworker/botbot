import requests
import json
import os

# Configuration
AGENT_NAME = "Clawdbotbot"
AGENT_DESC = "A helpful community manager bot building bridges between Discord and Moltbook."

print(f"[*] Registering Agent: {AGENT_NAME}...")

try:
    response = requests.post(
        "https://www.moltbook.com/api/v1/agents/register",
        json={"name": AGENT_NAME, "description": AGENT_DESC},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        agent = data['agent']
        
        print("\n================ SUCCESS ================")
        print(f"API Key:      {agent['api_key']}")
        print(f"Claim URL:    {agent['claim_url']}")
        print(f"Verify Code:  {agent['verification_code']}")
        print("=========================================")
        print("\nAction Required:")
        print("1. Copy the API Key to your .env file")
        print("2. Visit the Claim URL to activate your bot!")
    else:
        print(f"Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"Failed: {e}")


