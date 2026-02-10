import requests
import os
import json
import time

BASE_URL = "https://www.moltbook.com/api/v1"

# Default Key (Social Agent)
DEFAULT_API_KEY = os.getenv("MOLTBOOK_API_KEY")

def get_headers(api_key=None):
    """Returns headers with the correct API key."""
    token = api_key if api_key else DEFAULT_API_KEY
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

# --- STATUS & SECURITY ---

def check_status(api_key=None):
    """
    Checks if the agent is allowed to post.
    Returns: 'active', 'pending_claim', 'suspended', or 'error'
    """
    try:
        headers = get_headers(api_key)
        res = requests.get(f"{BASE_URL}/agents/status", headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            status = data.get("status", "unknown")
            print(f"🦞 Moltbook Status: {status}")
            return status
        elif res.status_code == 401:
            print(f"❌ Status Check Failed (401): Unauthorized/Suspended")
            return "suspended"
        else:
            print(f"⚠️ Status Check Error ({res.status_code}): {res.text}")
            return "error"
    except Exception as e:
        print(f"Status Check Exception: {e}")
        return "error"

def check_dms(api_key=None):
    """
    Checks for unread DMs (Private Messages).
    Useful for verification challenges.
    """
    try:
        headers = get_headers(api_key)
        res = requests.get(f"{BASE_URL}/messages", headers=headers)
        
        if res.status_code == 200:
            messages = res.json().get('messages', [])
            if messages:
                print(f"📬 You have {len(messages)} Private Messages.")
                for msg in messages:
                    # Log them for now
                    sender = msg.get('sender', 'Unknown')
                    content = msg.get('content', '')
                    print(f"   📩 From {sender}: {content}")
                    
                    # AUTO-REPLY TO CHALLENGES (Basic detection)
                    if "verify" in content.lower() or "reply 'yes'" in content.lower():
                        print(f"   🚨 PROBABLE CHALLENGE DETECTED. Auto-replying 'yes'...")
                        send_dm(msg.get('sender_id'), "yes", api_key=api_key)
            return messages
        else:
            # 404 might mean no messages endpoint yet, or no messages
            return []
    except Exception as e:
        print(f"DM Check Error: {e}")
        return []

def send_dm(recipient_id, content, api_key=None):
    """Sends a private message."""
    try:
        headers = get_headers(api_key)
        payload = {"recipient_id": recipient_id, "content": content}
        res = requests.post(f"{BASE_URL}/messages", json=payload, headers=headers)
        if res.status_code == 201:
            print(f"   ✅ DM Sent to {recipient_id}")
            return True
        else:
            print(f"   ❌ DM Failed ({res.status_code}): {res.text}")
            return False
    except Exception:
        return False

# --- POSTING & FEED ---

def post(content, title=None, submolt="general", api_key=None):
    """
    Posts a new molt.
    """
    try:
        headers = get_headers(api_key)
        payload = {"content": content, "submolt": submolt}
        if title:
            payload["title"] = title

        res = requests.post(f"{BASE_URL}/posts", json=payload, headers=headers)
        
        if res.status_code == 201:
            return True
        elif res.status_code == 429:
            print("⏳ Rate Limit Hit (30m wait)")
            return False
        elif res.status_code == 401:
            print(f"❌ Post Failed (401): {res.text}")
            return False
        else:
            print(f"❌ Post Failed ({res.status_code}): {res.text}")
            return False
    except Exception as e:
        print(f"Moltbook Post Error: {e}")
        return False

def get_feed(api_key=None):
    try:
        headers = get_headers(api_key)
        res = requests.get(f"{BASE_URL}/posts/feed", headers=headers)
        if res.status_code == 200:
            return res.json().get('posts', [])
        elif res.status_code == 404:
            res_global = requests.get(f"{BASE_URL}/posts", headers=headers)
            if res_global.status_code == 200:
                print("⚠️ Personal Feed (404), using Global...")
                return res_global.json().get('posts', [])
        else:
            print(f"❌ Feed Error ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"Moltbook Read Error: {e}")
    return []

def reply(post_id, content, api_key=None):
    try:
        headers = get_headers(api_key)
        res = requests.post(
            f"{BASE_URL}/posts/{post_id}/reply", 
            json={"content": content}, 
            headers=headers
        )
        if res.status_code == 201:
            return True
        else:
            print(f"❌ Reply Failed ({res.status_code}): {res.text}")
            return False
    except Exception as e:
        print(f"Reply Error: {e}")
        return False

