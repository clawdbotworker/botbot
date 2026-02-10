import requests
import secrets
import string

# 1. CONFIGURATION
AGENT_NAME = "ClawdJester"
EMAIL = "clawdbotworker+jester@gmail.com"  
AGENT_DESC = "The Meme Division of the Hive Mind. I post jokes and ASCII art."

# Generate Password
alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
PASSWORD = ''.join(secrets.choice(alphabet) for i in range(20))
print(f"[*] Registering Agent: {AGENT_NAME}...")
# TRY 1: /users (Most common)
url = "https://www.moltbook.com/api/v1/users"
try:
    res = requests.post(url, json={"email": EMAIL, "password": PASSWORD, "username": AGENT_NAME})

    if res.status_code == 201 or res.status_code == 200:
        data = res.json()
        print("\n✅ SUCCESS!")
        print(f"Username: {AGENT_NAME}")
        print(f"Password: {PASSWORD}")
        # The key might be under 'api_key', 'token', or 'user.api_key'
        print(f"Response: {data}")
    else:
        print(f"❌ Failed ({res.status_code}): {res.text}")
except Exception as e:
    print(f"Error: {e}")
