"""
[INPUT]: 依赖 momentsos.cli 的 main 入口。
[OUTPUT]: 提供 python -m momentsos 命令。
[POS]: 命令行薄入口，不承载业务逻辑。
[PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md
"""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
