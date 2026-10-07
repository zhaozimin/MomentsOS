"""
[INPUT]: 依赖 config、context、prompts、providers 组合本地工作流。
[OUTPUT]: 提供 init、paths、doctor、prompt、generate 命令。
[POS]: momentsos 的用户入口；只编排，不复制底层规则。
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from .config import init_home, load_settings, runtime_home
from .context import collect_context
from .prompts import build_prompt, parse_model_json, validate_drafts
from .providers import invoke_model


def _stamp() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")


def _write_prompt(home: Path, prompt: str) -> Path:
    path = home / "runs" / ("prompt-" + _stamp() + ".md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prompt, encoding="utf-8")
    return path


def _prepare(home: Path) -> tuple:
    settings = load_settings(home)
    documents, warnings = collect_context(settings, home)
    for warning in warnings:
        print("警告：" + warning, file=sys.stderr)
    prompt = build_prompt(documents, int(settings["candidate_count"]))
    return settings, documents, prompt


def command_init(args: argparse.Namespace) -> int:
    home = runtime_home(args.home)
    created = init_home(home)
    print("MomentsOS 运行目录：%s" % home)
    for name, was_created in created.items():
        print("- %s：%s" % (name, "已创建" if was_created else "保留现有文件"))
    print("每日上下文：%s" % (home / "context" / "daily" / "YYYY-MM-DD.md"))
    return 0


def command_paths(args: argparse.Namespace) -> int:
    home = runtime_home(args.home)
    rows = {
        "运行目录": home,
        "设置": home / "config" / "settings.json",
        "长期身份": home / "context" / "profile.md",
        "文风样本": home / "context" / "voice.md",
        "写作规则": home / "context" / "rules.md",
        "每日上下文": home / "context" / "daily" / "YYYY-MM-DD.md",
        "输出": home / "output",
        "提示词留档": home / "runs",
    }
    for label, path in rows.items():
        print("%s：%s" % (label, path))
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    home = runtime_home(args.home)
    settings = load_settings(home)
    documents, warnings = collect_context(settings, home)
    print("配置：通过")
    print("模型模式：%s" % settings["model"]["provider"])
    print("已读取上下文：%d 份" % len(documents))
    for warning in warnings:
        print("警告：" + warning)
    return 0


def command_prompt(args: argparse.Namespace) -> int:
    home = runtime_home(args.home)
    _settings, documents, prompt = _prepare(home)
    path = _write_prompt(home, prompt)
    print("已生成提示词：%s" % path)
    print("已引用上下文：%d 份" % len(documents))
    return 0


def command_generate(args: argparse.Namespace) -> int:
    home = runtime_home(args.home)
    settings, documents, prompt = _prepare(home)
    prompt_path = _write_prompt(home, prompt)
    raw = invoke_model(prompt, settings["model"])
    if raw is None:
        print("当前是 manual 模式。请把提示词交给你选择的模型：%s" % prompt_path)
        return 0
    payload = parse_model_json(raw)
    drafts = validate_drafts(payload, int(settings["candidate_count"]), len(documents))
    output: Dict[str, Any] = {
        "created_at": datetime.now().astimezone().isoformat(),
        "model": settings["model"].get("name", ""),
        "source_count": len(documents),
        "drafts": drafts,
    }
    output_path = home / "output" / ("drafts-" + _stamp() + ".json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("已生成草稿：%s" % output_path)
    print("发布前必须人工检查；MomentsOS 不会自动发布。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="momentsos", description="本地优先的朋友圈草稿框架")
    parser.add_argument("--home", help="覆盖 MOMENTSOS_HOME")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text, handler in (
        ("init", "创建运行目录和安全模板", command_init),
        ("paths", "显示所有上下文与输出位置", command_paths),
        ("doctor", "检查配置和上下文来源", command_doctor),
        ("prompt", "只生成提示词，不调用模型", command_prompt),
        ("generate", "生成提示词并按配置调用模型", command_generate),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.set_defaults(handler=handler)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (FileNotFoundError, ValueError, PermissionError, json.JSONDecodeError) as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
