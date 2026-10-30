import json
import re
import requests
from ..config import Config


def llm_available():
    return bool(Config.LLM_API_KEY)


def chat(messages, temperature=0.4, max_tokens=700, timeout=40):
    r = requests.post(
        f"{Config.LLM_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {Config.LLM_API_KEY}", "Content-Type": "application/json"},
        json={"model": Config.LLM_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
        timeout=timeout)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def chat_json(messages, **kw):
    text = chat(messages, temperature=0.3, max_tokens=1800, **kw)
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)
