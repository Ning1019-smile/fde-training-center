# -*- coding: utf-8 -*-
"""IO 小工具：读取样例数据、安全的文本读取等。"""
from __future__ import annotations
import json
import os
from typing import List, Dict, Any


def load_messages(path: str) -> List[Dict[str, Any]]:
    """从 json 文件加载消息列表：[{{stu, src, typ, text}}, ...]。"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def safe_join(base: str, *parts: str) -> str:
    """拼接路径并确保不越出 base 目录（防目录穿越）。"""
    out = os.path.normpath(os.path.join(base, *parts))
    if not out.startswith(os.path.normpath(base)):
        raise ValueError("路径越界")
    return out
