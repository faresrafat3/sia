#!/usr/bin/env python3
"""Test Pioneer API with DeepSeek-V4-Pro"""
import httpx, json, os

# Read key from file
with open(os.path.join(os.path.dirname(__file__), ".pioneer_key")) as f:
    key = f.read().strip()

base = "https://api.pioneer.ai/v1"

# Test Pro model
resp = httpx.post(
    f"{base}/chat/completions",
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity"
    },
    json={
        "model": "deepseek-ai/DeepSeek-V4-Pro",
        "messages": [{"role": "user", "content": "Say hello world"}],
        "max_tokens": 200,
        "temperature": 0.3
    },
    timeout=120
)
print(f"Pro Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    msg = data["choices"][0]["message"]
    print(f"Content: {repr(msg.get('content',''))}")
    print(f"Reasoning (first 200): {repr(msg.get('reasoning_content','')[:200])}")
    print(f"Tokens: {data.get('token_usage', data.get('usage', {}))}")
else:
    print(f"Error: {resp.text[:500]}")

# Test Flash model
resp2 = httpx.post(
    f"{base}/chat/completions",
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity"
    },
    json={
        "model": "deepseek-ai/DeepSeek-V4-Flash",
        "messages": [{"role": "user", "content": "Say hello world"}],
        "max_tokens": 200
    },
    timeout=120
)
print(f"\nFlash Status: {resp2.status_code}")
if resp2.status_code == 200:
    data2 = resp2.json()
    msg2 = data2["choices"][0]["message"]
    print(f"Content: {repr(msg2.get('content',''))}")
    print(f"Tokens: {data2.get('token_usage', data2.get('usage', {}))}")
else:
    print(f"Error: {resp2.text[:300]}")