"""
[INPUT]: 依赖模型配置、环境变量密钥与标准库 HTTP 客户端。
[OUTPUT]: 提供手工模式和 OpenAI 兼容接口调用。
[POS]: momentsos 的模型边界；云端传输必须经过显式隐私开关。
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

import json
import os
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def _is_loopback(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in {"127.0.0.1", "localhost", "::1"}


def invoke_model(
    prompt: str,
    model_settings: Dict[str, Any],
    opener: Any = urlopen,
) -> Optional[str]:
    provider = model_settings.get("provider", "manual")
    if provider == "manual":
        return None
    if provider != "openai_compatible":
        raise ValueError("不支持的模型提供方：%s" % provider)

    base_url = str(model_settings.get("base_url", "")).rstrip("/")
    if not base_url:
        raise ValueError("openai_compatible 模式必须配置 base_url。")
    if not _is_loopback(base_url) and not bool(model_settings.get("allow_cloud_context", False)):
        raise PermissionError("云端模型会接收上下文。确认风险后设置 allow_cloud_context=true。")

    name = str(model_settings.get("name", "")).strip()
    if not name:
        raise ValueError("openai_compatible 模式必须配置 model.name。")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    key_env = str(model_settings.get("api_key_env", "MOMENTSOS_API_KEY"))
    api_key = os.environ.get(key_env, "")
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    elif not _is_loopback(base_url):
        raise ValueError("缺少环境变量 %s。密钥不得写进 settings.json。" % key_env)

    body = {
        "model": name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": float(model_settings.get("temperature", 0.7)),
    }
    if bool(model_settings.get("json_mode", True)):
        body["response_format"] = {"type": "json_object"}
    request = Request(
        base_url + "/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    timeout = int(model_settings.get("timeout_seconds", 120))
    with opener(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    try:
        return str(payload["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("模型接口返回了无法识别的结构。") from exc
