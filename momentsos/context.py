"""
[INPUT]: 依赖 settings 中的本地 Markdown 路径与可选 LifeOS 只读接口。
[OUTPUT]: 提供带来源标识的上下文采集结果和非致命告警。
[POS]: momentsos 的只读采集层；不修改任何外部数据源。
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

import json
import os
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from .config import expand_runtime_path


@dataclass(frozen=True)
class SourceDocument:
    name: str
    origin: str
    text: str


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    marker = "\n\n[内容因长度限制被截断]"
    if limit <= len(marker):
        return text[:limit]
    return text[: limit - len(marker)] + marker


def _read_markdown(path: Path, name: str, limit: int, origin: Optional[str] = None) -> SourceDocument:
    safe_origin = origin or path.name
    return SourceDocument(name=name, origin=safe_origin, text=_clip(path.read_text(encoding="utf-8"), limit))


def _file_date(path: Path) -> date:
    match = re.search(r"\d{4}-\d{2}-\d{2}", path.name)
    if match:
        try:
            return date.fromisoformat(match.group(0))
        except ValueError:
            pass
    return date.fromtimestamp(path.stat().st_mtime)


def _fit_total_budget(documents: List[SourceDocument], limit: int) -> Tuple[List[SourceDocument], bool]:
    fitted: List[SourceDocument] = []
    remaining = limit
    clipped = False
    for document in documents:
        if remaining <= 0:
            clipped = True
            break
        text = document.text
        if len(text) > remaining:
            text = _clip(text, remaining)
            clipped = True
        fitted.append(SourceDocument(document.name, document.origin, text))
        remaining -= len(text)
    if len(fitted) < len(documents):
        clipped = True
    return fitted, clipped


def _is_loopback(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in {"127.0.0.1", "localhost", "::1"}


def _collect_lifeos(
    source: Dict[str, Any],
    start: date,
    end: date,
    limit: int,
    opener: Callable[..., Any],
) -> SourceDocument:
    base_url = str(source.get("base_url", "http://127.0.0.1:59418")).rstrip("/")
    if not _is_loopback(base_url) and not bool(source.get("allow_remote", False)):
        raise ValueError("LifeOS 非本机地址需要显式设置 allow_remote=true。")
    query = urlencode({"from": start.isoformat(), "to": end.isoformat()})
    endpoint = "%s/v1/time/segments?%s" % (base_url, query)
    headers = {"Accept": "application/json"}
    token_env = str(source.get("token_env", "LIFEOS_TOKEN"))
    token = os.environ.get(token_env, "")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(endpoint, headers=headers, method="GET")
    with opener(request, timeout=int(source.get("timeout_seconds", 10))) as response:
        payload = response.read(limit * 4)
    parsed = json.loads(payload.decode("utf-8"))
    text = json.dumps(parsed, ensure_ascii=False, indent=2)
    return SourceDocument(name=str(source.get("name", "LifeOS")), origin=endpoint, text=_clip(text, limit))


def collect_context(
    settings: Dict[str, Any],
    home: Path,
    today: Optional[date] = None,
    opener: Callable[..., Any] = urlopen,
) -> Tuple[List[SourceDocument], List[str]]:
    """按确定顺序收集上下文；单个可选来源失败时继续运行。"""
    current = today or date.today()
    context_settings = settings["context"]
    lookback = int(context_settings["lookback_days"])
    limit = int(context_settings["max_chars_per_source"])
    total_limit = int(context_settings["max_total_chars"])
    start = current - timedelta(days=lookback - 1)
    documents: List[SourceDocument] = []
    warnings: List[str] = []

    for filename, label in (
        ("profile.md", "长期身份"),
        ("voice.md", "文风样本"),
        ("rules.md", "写作规则"),
    ):
        path = home / "context" / filename
        if path.exists():
            documents.append(_read_markdown(path, label, limit, filename))

    daily_dir = expand_runtime_path(str(context_settings["daily_dir"]), home)
    for offset in range(lookback):
        day = start + timedelta(days=offset)
        path = daily_dir / (day.isoformat() + ".md")
        if path.exists():
            documents.append(_read_markdown(path, "每日上下文 " + day.isoformat(), limit, path.name))

    for source in context_settings.get("sources", []):
        if not isinstance(source, dict) or not source.get("enabled", True):
            continue
        source_type = source.get("type")
        name = str(source.get("name", source_type or "未命名来源"))
        try:
            if source_type == "markdown_file":
                path = expand_runtime_path(str(source["path"]), home)
                if path.exists():
                    documents.append(_read_markdown(path, name, limit, path.name))
                else:
                    warnings.append("%s：文件不存在：%s" % (name, path))
            elif source_type == "markdown_dir":
                directory = expand_runtime_path(str(source["path"]), home)
                pattern = str(source.get("glob", "*.md"))
                if not directory.exists():
                    warnings.append("%s：目录不存在：%s" % (name, directory))
                    continue
                source_days = int(source.get("lookback_days", lookback))
                if source_days < 1:
                    raise ValueError("lookback_days 必须大于 0。")
                source_start = current - timedelta(days=source_days - 1)
                max_files = int(source.get("max_files", 10))
                if max_files < 1:
                    raise ValueError("max_files 必须大于 0。")
                matches = [
                    path
                    for path in directory.glob(pattern)
                    if path.is_file() and source_start <= _file_date(path) <= current
                ]
                matches.sort(key=lambda item: item.stat().st_mtime, reverse=True)
                for path in reversed(matches[:max_files]):
                    relative = str(path.relative_to(directory))
                    documents.append(_read_markdown(path, name + " / " + path.name, limit, relative))
            elif source_type == "lifeos":
                documents.append(_collect_lifeos(source, start, current, limit, opener))
            else:
                warnings.append("%s：不支持的来源类型：%s" % (name, source_type))
        except Exception as exc:  # 来源失败不应阻断本地手工上下文。
            warnings.append("%s：读取失败：%s" % (name, exc))
    documents, was_clipped = _fit_total_budget(documents, total_limit)
    if was_clipped:
        warnings.append("上下文达到 max_total_chars，剩余内容未送入模型。")
    return documents, warnings
