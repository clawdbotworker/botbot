import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('MOLTBOOK_API_KEY')
BASE_URL = "https://www.moltbook.com/api/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_feed():
    """Tries to get the personal feed, falls back to global if empty/error."""
    try:
        # 1. Try Personal Feed
        res = requests.get(f"{BASE_URL}/posts/feed", headers=HEADERS)
        if res.status_code == 200:
            return res.json().get('posts', [])
        
        # 2. Fallback: Global/General Feed (likely just /posts)
        print(f"⚠️ Personal Feed failed ({res.status_code}), trying Global...")
        res = requests.get(f"{BASE_URL}/posts", headers=HEADERS)
        if res.status_code == 200:
            return res.json().get('posts', [])
            
        print(f"❌ Feed Error ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"Moltbook Read Error: {e}")
    return []

def post(content, title="Status Update", submolt="general"):
    try:
        payload = {
            "content": content,
            "title": title,
            "submolt": submolt
        }
        res = requests.post(f"{BASE_URL}/posts", json=payload, headers=HEADERS)
        if res.status_code == 201:
            return True
        else:
            print(f"❌ Post Failed ({res.status_code}): {res.text}")
            return False
    except Exception as e:
        print(f"Moltbook Post Error: {e}")
        return False

def reply(post_id, content):
    try:
        payload = {"content": content, "parent_id": post_id}
        res = requests.post(f"{BASE_URL}/posts", json=payload, headers=HEADERS)
        if res.status_code != 201:
            print(f"❌ Reply Failed ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"Reply Error: {e}")


