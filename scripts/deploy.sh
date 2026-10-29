#!/usr/bin/env bash
# 本地演示部署：启动静态服务浏览 MVP 与文档
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PORT="${PORT:-8080}"
PYTHON="${PYTHON:-python}"
echo "打开 http://localhost:$PORT/index.html 查看最小 MVP"
cd examples/mvp && "$PYTHON" -m http.server "$PORT"
