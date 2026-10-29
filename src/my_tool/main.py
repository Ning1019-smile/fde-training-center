# -*- coding: utf-8 -*-
"""
命令行入口：构建知识库 / 检索问答 / 引擎演示。

示例：
  # 构建知识库索引（扫描 docs/ 下所有 md/txt）
  PYTHONPATH=src python -m my_tool.main build --docs docs --out data/kb.json

  # 离线检索问答
  PYTHONPATH=src python -m my_tool.main query "漏单率验收标准是多少"

  # 运行业务引擎演示（识别 + 合并连续求助）
  PYTHONPATH=src python -m my_tool.main demo
"""
from __future__ import annotations
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from my_tool.core.engine import analyze, Message  # noqa: E402
from my_tool.core.kb import KnowledgeBase         # noqa: E402


def cmd_build(args):
    kb = KnowledgeBase()
    n = kb.index_directory(args.docs)
    kb.save(args.out)
    print(f"[build] 已索引 {n} 个文本块 -> {args.out}")


def cmd_query(args):
    kb = KnowledgeBase()
    if not os.path.exists(args.index):
        print(f"[query] 索引不存在：{args.index}，请先运行 build。")
        return
    kb.load(args.index)
    r = kb.answer(args.text, top_k=args.top_k)
    print(f"问：{r['query']}")
    print(f"答：{r['answer']}")
    for i, h in enumerate(r["context"], 1):
        snippet = h["text"][:140].replace("\n", " ")
        print(f"  [{i}] score={h['score']} source={h['source']} :: {snippet}...")


def cmd_demo(args):
    msgs = [
        Message("张明", "群聊", "作业理解", "第三题完全不会做，能讲一下思路吗？"),
        Message("张明", "作业评论", "作业理解", "还是不懂第三题，第二步怎么来的？"),
        Message("李华", "群聊", "技术报错", "作业平台提交一直报错，提示 500。"),
        Message("李华", "群聊", "流程咨询", "期末成绩会不会受影响？我有点担心。"),
        Message("王芳", "作业评论", "概念疑问", "听不懂今天讲的梯度下降原理，为什么能收敛？"),
    ]
    print("[demo] 业务引擎：识别支持需求 + 按学生合并连续求助")
    for t in analyze(msgs):
        flag = " ⚠需转人工" if t.escalate else ""
        print(f"  {t.id} | {t.stu} | {t.category} | {t.owner} | 置信度 {t.confidence}{flag}")
        for o in t.original:
            print(f"       - {o}")


def main():
    p = argparse.ArgumentParser(prog="my_tool", description="北辰在线学院 AI 学习支持工具")
    sub = p.add_subparsers(dest="cmd")

    b = sub.add_parser("build", help="构建知识库索引")
    b.add_argument("--docs", default=os.path.join(ROOT, "docs"))
    b.add_argument("--out", default=os.path.join(ROOT, "data", "kb.json"))

    q = sub.add_parser("query", help="检索问答")
    q.add_argument("text")
    q.add_argument("--index", default=os.path.join(ROOT, "data", "kb.json"))
    q.add_argument("--top_k", type=int, default=5)

    sub.add_parser("demo", help="运行业务引擎演示")

    args = p.parse_args()
    if args.cmd == "build":
        cmd_build(args)
    elif args.cmd == "query":
        cmd_query(args)
    elif args.cmd == "demo":
        cmd_demo(args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
