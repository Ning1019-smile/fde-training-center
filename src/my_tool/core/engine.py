# -*- coding: utf-8 -*-
"""
支持需求识别与连续求助合并引擎（纯 Python，零依赖）。

逻辑与 docs 中 MVP 网页保持一致，便于复用与单元测试。
核心规则来自《业务需求发现报告》：
  - 学生问题散在群聊/作业评论，连续求助常被漏接（f10）
  - 关键说明不随单交接（f14）
  - 不自动给学生定性或评分（硬边界）
  - 涉及成绩/处分等红线必须转人工（f32/f40）
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

# 支持需求信号词（命中即视为“有求助意图”）
NEED_WORDS = [
    "不会", "不懂", "怎么", "如何", "卡住", "错了", "疑问", "求助", "不明白", "不会做",
    "解不出", "看不懂", "报错", "失败", "异常", "还是不懂", "听不懂", "没思路", "求教",
    "急", "搞不定", "不知道怎么",
]
# 红线信号词：命中则需转人工，不可由系统自动处理
ESCALATE_WORDS = ["成绩", "处分", "退学", "保研", "投诉", "赔偿", "起诉", "分数", "考试"]

# 建议分类规则（顺序匹配，先到先得）
CATEGORY_RULES = [
    ("技术报错", ["报错", "异常", "失败", "bug", "运行", "500"]),
    ("学业评价（需人工）", ["成绩", "考试", "分数", "处分"]),
    ("概念疑问", ["概念", "原理", "为什么", "听不懂"]),
    ("作业理解", ["作业", "题", "思路"]),
]


@dataclass
class Message:
    stu: str
    src: str
    typ: str
    text: str


@dataclass
class Ticket:
    id: str
    stu: str
    srcs: List[str]
    original: List[str]
    category: str
    owner: str
    confidence: float
    escalate: bool
    status: str = "new"          # new | done | manual | hold
    confirm_by: str = ""
    reason: str = ""
    ts: str = ""


def is_need(text: str) -> bool:
    return any(w in text for w in NEED_WORDS)


def needs_escalation(text: str) -> bool:
    return any(w in text for w in ESCALATE_WORDS)


def pick_category(texts: List[str]) -> str:
    blob = " ".join(texts)
    for cat, kws in CATEGORY_RULES:
        if any(k in blob for k in kws):
            return cat
    return "流程咨询"


def analyze(messages: List[Message], date_str: Optional[str] = None) -> List[Ticket]:
    """将多条散落消息识别为支持需求，并按学生合并连续求助为一张工单。"""
    ds = date_str or date.today().strftime("%Y%m%d")
    by_stu: Dict[str, List[Message]] = {}
    for m in messages:
        by_stu.setdefault(m.stu, []).append(m)

    tickets: List[Ticket] = []
    no = 0
    for stu, msgs in by_stu.items():
        need = [m for m in msgs if is_need(m.text)]
        if not need:
            continue  # 非求助不建单
        no += 1
        escalate = any(needs_escalation(m.text) for m in need)
        cat = pick_category([m.text + m.typ for m in need])
        owner = "转人工（数据专员/讲师）" if escalate else "助教复核"
        conf = min(0.95, 0.6 + len(need) * 0.12)
        tickets.append(Ticket(
            id=f"T-{ds}-{no:03d}",
            stu=stu,
            srcs=sorted({m.src for m in msgs}),
            original=[f"[{m.src}·{m.typ}] {m.text}" for m in need],
            category=cat,
            owner=owner,
            confidence=round(conf, 2),
            escalate=escalate,
        ))
    return tickets
