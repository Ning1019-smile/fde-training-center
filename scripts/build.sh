#!/usr/bin/env bash
# 构建知识库索引并跑一次引擎自检
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python}"
export PYTHONPATH="$ROOT/src:$PYTHONPATH"
"$PYTHON" -m my_tool.main build --docs docs --out data/kb.json
"$PYTHON" -m my_tool.main demo
echo "build done."
