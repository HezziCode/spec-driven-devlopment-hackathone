"""Test OpenAI API key validity."""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("[FAIL] API key not found in .env")
    exit(1)

print(f"[OK] API key found: {api_key[:20]}...{api_key[-4:]}")

# Test with OpenAI library
try:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    # Simple test call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'API key is working'"}],
        max_tokens=10,
    )

    print(f"[OK] OpenAI API working! Response: {response.choices[0].message.content}")

except Exception as e:
    print(f"[FAIL] OpenAI API error: {e}")
    exit(1)
