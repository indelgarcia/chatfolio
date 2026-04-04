"""Quick script to test OpenAI API key and check status/limits."""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

# Use raw HTTP so we can inspect response headers (rate limit info)
print("Checking OpenAI API status...\n")

response = httpx.post(
    "https://api.openai.com/v1/chat/completions",
    headers=headers,
    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 5},
)

print(f"Status: {response.status_code}")
print()

# Show rate limit headers if present
rate_limit_headers = {k: v for k, v in response.headers.items() if "rate" in k.lower() or "limit" in k.lower() or "remaining" in k.lower() or "reset" in k.lower()}
if rate_limit_headers:
    print("Rate Limits:")
    for k, v in sorted(rate_limit_headers.items()):
        print(f"  {k}: {v}")
else:
    print("No rate limit headers returned.")

print()

# Show the response body
data = response.json()
if "error" in data:
    print(f"Error: {data['error']['message']}")
    print(f"Type: {data['error'].get('code', 'unknown')}")
else:
    print("API key is working!")
    usage = data.get("usage", {})
    print(f"Tokens used: {usage.get('prompt_tokens', 0)} prompt + {usage.get('completion_tokens', 0)} completion")
