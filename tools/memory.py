import os
import datetime

MEMORY_DIR = "memory"

def _get_today_file():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)
    
    today = datetime.date.today().isoformat()
    return os.path.join(MEMORY_DIR, f"{today}.md")

def save_thought(thought):
    """Writes an action or thought to memory."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"\n[{timestamp}] {thought}"
    
    try:
        with open(_get_today_file(), "a") as f:
            f.write(entry)
    except Exception as e:
        print(f"Memory Write Error: {e}")

def get_recent_context():
    """Reads the last few entries to provide context."""
    try:
        path = _get_today_file()
        if not os.path.exists(path):
            return "No memory for today yet."
            
        with open(path, "r") as f:
            content = f.read()
            return content[-2000:] 
    except Exception as e:
        return ""
