#!/bin/sh
# [INPUT]: 依赖项目根目录、Python 3.9+ 与标准 venv 模块。
# [OUTPUT]: 创建仓库内隔离环境，安装 MomentsOS 并初始化用户运行目录。
# [POS]: scripts 的可重复安装入口；不读取或覆盖用户上下文。
# [PROTOCOL]: 变更时更新此头部，然后检查 CLAUDE.md

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
PYTHON_BIN=${MOMENTSOS_PYTHON:-python3}

"$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' || {
  echo "MomentsOS 需要 Python 3.9 或更高版本。" >&2
  exit 1
}

"$PYTHON_BIN" -m venv "$REPO_DIR/.venv"
"$REPO_DIR/.venv/bin/python" -m pip install --quiet "$REPO_DIR"
"$REPO_DIR/.venv/bin/momentsos" init

echo
echo "安装完成。下一步："
echo "  $REPO_DIR/.venv/bin/momentsos paths"
echo "  $REPO_DIR/.venv/bin/momentsos doctor"
echo "  $REPO_DIR/.venv/bin/momentsos generate"
