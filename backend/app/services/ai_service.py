import json
import re
import requests
from app.core.config import settings
from app.models.ai_config import AIConfig


def get_ai_config(db=None):
    """获取 AI 配置：优先数据库，其次环境变量"""
    if db:
        config = db.query(AIConfig).first()
        if config and config.api_key:
            return {
                "base_url": config.base_url or settings.AI_BASE_URL,
                "api_key": config.api_key,
                "model": config.model or settings.AI_MODEL,
            }
    return {
        "base_url": settings.AI_BASE_URL,
        "api_key": settings.AI_API_KEY,
        "model": settings.AI_MODEL,
    }


def ai_chat(prompt: str, db=None) -> dict:
    config = get_ai_config(db)

    if not config["api_key"]:
        # 模拟返回，方便开发测试
        return {"result": "[模拟AI返回] 请配置 AI API Key"}

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    try:
        resp = requests.post(
            f"{config['base_url']}/chat/completions",
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


def ai_chat_stream(prompt: str, db=None):
    """流式 AI 聊天，逐步 yield 内容片段"""
    config = get_ai_config(db)

    if not config["api_key"]:
        yield "[模拟AI返回] 请配置 AI API Key"
        return

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "stream": True,
    }
    try:
        resp = requests.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=60,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if line.startswith("data:"):
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except Exception:
                    continue
    except Exception as e:
        yield f"\n[错误] {str(e)}"
