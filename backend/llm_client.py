import httpx
import json
import os

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b" # Upgraded for better reasoning as discussed

# NON-STREAMING (for intent classification etc.) 
async def call_llm_once(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"]


# STREAMING (for chat UI) 
async def call_llm_stream(prompt: str):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": True
            }
        )

        async for line in response.aiter_lines():
            if not line:
                continue

            data = json.loads(line)
            token = data.get("response", "")
            if token:
                yield token