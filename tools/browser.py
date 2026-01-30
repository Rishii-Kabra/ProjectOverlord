import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class WebBrowser:
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        self.url = "https://google.serper.dev/search"

    def search(self, query):
        if not self.api_key:
            return "Error: No SERPER_API_KEY found."

        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': self.api_key, 'Content-Type': 'application/json'}

        try:
            response = requests.post(self.url, headers=headers, data=payload)
            results = response.json()

            snippets = []
            # Only take top 2 results and keep them VERY short
            for result in results.get('organic', [])[:2]:
                title = result.get('title', 'No Title')
                # Only take the first 150 characters of the snippet
                info = result.get('snippet', '')[:150]
                snippets.append(f"[{title}]: {info}...")

            return "\n".join(snippets) if snippets else "No results found."
        except Exception as e:
            return f"Search Error: {str(e)}"