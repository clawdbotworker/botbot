import requests
from bs4 import BeautifulSoup
import urllib.parse

# SKILL: BROWSER 🌐
def search(query):
    """Searches DuckDuckGo and returns top result URLs."""
    print(f"🌐 Skill: Searching for '{query}'...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        results = []
        for link in soup.find_all('a', class_='result__a', limit=3):
            results.append(link['href'])
            
        return results if results else ["No results found."]
    except Exception as e:
        return [f"Search Error: {e}"]

def read_url(url):
    """Reads the text content of a webpage."""
    print(f"🌐 Skill: Reading {url}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Strip script/style
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return clean_text[:2000] + "..." 
    except Exception as e:
        return f"Read Error: {e}"

AVAILABLE_SKILLS = {
    "search": search,
    "read_url": read_url
}
