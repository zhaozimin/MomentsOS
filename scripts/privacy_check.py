"""
[INPUT]: 依赖 Git 候选文件列表与仓库文本内容。
[OUTPUT]: 报告绝对用户路径、常见密钥和运行数据文件。
[POS]: scripts 的发布门禁；只读扫描，不声明取代人工审查。
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".json", ".toml", ".yml", ".yaml", ".sh", ".svg", ".txt"}
FORBIDDEN_FILES = {".env", "settings.json"}
FORBIDDEN_SUFFIXES = {".sqlite3", ".sqlite3-wal", ".sqlite3-shm"}
PATTERNS = (
    ("macOS 用户绝对路径", re.compile(r"/(?:Users|Volumes)/[^\s\"'<>]+")),
    ("OpenAI 风格密钥", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
    ("GitHub 访问令牌", re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{16,}\b")),
    ("Google API 密钥", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
    ("私钥", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
)


def candidate_files() -> Iterable[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=str(ROOT),
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    for raw in result.stdout.splitlines():
        path = ROOT / raw
        if path.is_file():
            yield path


def scan() -> List[Tuple[str, str]]:
    findings: List[Tuple[str, str]] = []
    for path in candidate_files():
        relative = str(path.relative_to(ROOT))
        if path.name in FORBIDDEN_FILES or any(relative.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
            findings.append((relative, "运行数据文件不得提交"))
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS:
            if pattern.search(text):
                findings.append((relative, label))
    return findings


def main() -> int:
    findings = scan()
    if findings:
        for path, reason in findings:
            print("%s: %s" % (path, reason))
        return 1
    print("隐私扫描通过：未发现用户绝对路径、常见密钥或运行数据库。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
