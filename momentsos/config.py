"""
[INPUT]: 依赖标准库 json、os、pathlib 读取本地配置与运行目录。
[OUTPUT]: 提供默认配置、路径展开、配置加载与首次初始化。
[POS]: momentsos 的配置边界；只创建模板，不覆盖用户文件。
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

import copy
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_SETTINGS: Dict[str, Any] = {
    "candidate_count": 9,
    "context": {
        "daily_dir": "$MOMENTSOS_HOME/context/daily",
        "lookback_days": 3,
        "max_chars_per_source": 12000,
        "max_total_chars": 60000,
        "sources": [],
    },
    "model": {
        "provider": "manual",
        "name": "",
        "base_url": "http://127.0.0.1:11434/v1",
        "api_key_env": "MOMENTSOS_API_KEY",
        "allow_cloud_context": False,
        "timeout_seconds": 120,
        "temperature": 0.7,
        "json_mode": True,
    },
}


PROFILE_TEMPLATE = """# 我是谁

用事实描述你的身份、长期项目和公开边界。

## 可以公开

- 示例：公开产品的名称与用途。

## 不可公开

- 家庭住址、手机号、证件号、密钥和未公开商业信息。
"""


VOICE_TEMPLATE = """# 我的声音

粘贴 3～10 条你亲手写过、且允许模型读取的公开文本。
不要粘贴他人的原话，也不要把聊天记录当作文风样本。
"""


RULES_TEMPLATE = """# 写作规则

1. 只使用上下文中明确出现的事实。
2. 不补写地点、人物、金额、结果或现场细节。
3. 每条只表达一个中心意思。
4. 不引用他人私聊内容。
5. 输出前删除密钥、账号、联系方式和精确住址。
"""


def runtime_home(explicit: Optional[str] = None) -> Path:
    """返回运行目录；仓库和运行数据保持分离。"""
    raw = explicit or os.environ.get("MOMENTSOS_HOME") or "~/.momentsos"
    return Path(os.path.expanduser(os.path.expandvars(raw))).resolve()


def expand_runtime_path(raw: str, home: Path) -> Path:
    """展开配置路径中的运行目录占位符和用户目录。"""
    value = raw.replace("$MOMENTSOS_HOME", str(home))
    return Path(os.path.expanduser(os.path.expandvars(value))).resolve()


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_settings(home: Path) -> Dict[str, Any]:
    """读取设置并补齐新增默认项。"""
    path = home / "config" / "settings.json"
    if not path.exists():
        raise FileNotFoundError("尚未初始化。请先运行 momentsos init。")
    with path.open("r", encoding="utf-8") as handle:
        user_settings = json.load(handle)
    if not isinstance(user_settings, dict):
        raise ValueError("settings.json 顶层必须是 JSON 对象。")
    settings = _deep_merge(DEFAULT_SETTINGS, user_settings)
    _validate_settings(settings)
    return settings


def _validate_settings(settings: Dict[str, Any]) -> None:
    context = settings.get("context", {})
    model = settings.get("model", {})
    if int(settings.get("candidate_count", 0)) < 1:
        raise ValueError("candidate_count 必须大于 0。")
    if int(context.get("lookback_days", 0)) < 1:
        raise ValueError("context.lookback_days 必须大于 0。")
    if int(context.get("max_chars_per_source", 0)) < 100:
        raise ValueError("context.max_chars_per_source 不能小于 100。")
    if int(context.get("max_total_chars", 0)) < int(context.get("max_chars_per_source", 0)):
        raise ValueError("context.max_total_chars 不能小于 max_chars_per_source。")
    if model.get("provider") not in {"manual", "openai_compatible"}:
        raise ValueError("model.provider 只支持 manual 或 openai_compatible。")


def init_home(home: Path) -> Dict[str, bool]:
    """创建运行目录与安全模板；现有文件永不覆盖。"""
    paths = {
        "settings": home / "config" / "settings.json",
        "profile": home / "context" / "profile.md",
        "voice": home / "context" / "voice.md",
        "rules": home / "context" / "rules.md",
    }
    for directory in (
        home / "config",
        home / "context" / "daily",
        home / "output",
        home / "runs",
    ):
        directory.mkdir(parents=True, exist_ok=True)

    payloads = {
        "settings": json.dumps(DEFAULT_SETTINGS, ensure_ascii=False, indent=2) + "\n",
        "profile": PROFILE_TEMPLATE,
        "voice": VOICE_TEMPLATE,
        "rules": RULES_TEMPLATE,
    }
    created: Dict[str, bool] = {}
    for name, path in paths.items():
        if path.exists():
            created[name] = False
            continue
        path.write_text(payloads[name], encoding="utf-8")
        created[name] = True
    return created
