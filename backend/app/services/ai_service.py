import json
import re
import requests
from app.core.config import settings


def ai_chat(prompt: str) -> dict:
    if not settings.DASHSCOPE_API_KEY:
        # 模拟返回，方便开发测试
        return {"result": "[模拟AI返回] 请在 .env 中配置 DASHSCOPE_API_KEY"}

    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    try:
        resp = requests.post(
            f"{settings.DASHSCOPE_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        # 尝试解析 JSON
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"result": content}
    except Exception as e:
        return {"error": str(e)}
