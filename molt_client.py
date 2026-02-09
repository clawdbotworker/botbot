import requests
import os

class MoltbookClient:
    BASE_URL = "https://www.moltbook.com/api/v1"

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def check_status(self):
        """Checks if the bot is claimed and active."""
        try:
            res = requests.get(f"{self.BASE_URL}/agents/me", headers=self.headers)
            return res.status_code == 200
        except:
            return False

    def get_latest_posts(self):
        """Reads the global feed."""
        res = requests.get(f"{self.BASE_URL}/posts/feed", headers=self.headers)
        if res.status_code == 200:
            return res.json().get('posts', [])
        return []

    def post_status(self, content):
        """Posts a new status update."""
        payload = {"content": content}
        requests.post(f"{self.BASE_URL}/posts", json=payload, headers=self.headers)

    def reply(self, post_id, content):
        """Replies to a post."""
        payload = {"content": content, "parent_id": post_id}
        requests.post(f"{self.BASE_URL}/posts", json=payload, headers=self.headers)


