"""端到端示例：用业务引擎 + 知识库跑一遍核心闭环。

运行：PYTHONPATH=src python examples/demo.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from my_tool.core.engine import analyze, Message
from my_tool.core.kb import KnowledgeBase


def main():
    # 1) 业务引擎：识别 + 合并连续求助
    msgs = [
        Message("张明", "群聊", "作业理解", "第三题完全不会做，能讲一下思路吗？"),
        Message("张明", "作业评论", "作业理解", "还是不懂第三题，第二步怎么来的？"),
        Message("李华", "群聊", "技术报错", "作业平台提交一直报错，提示 500。"),
        Message("李华", "群聊", "流程咨询", "期末成绩会不会受影响？我有点担心。"),
    ]
    print("== 业务引擎：合并后的工单 ==")
    for t in analyze(msgs):
        print(f"  {t.id} | {t.stu} | {t.category} | {t.owner} | conf={t.confidence}")

    # 2) 知识库：基于 docs 问答
    kb = KnowledgeBase()
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    if os.path.isdir(docs_dir):
        kb.index_directory(docs_dir)
        r = kb.answer("重复求助率和漏单率的目标是多少")
        print("\n== 知识库 RAG 问答 ==")
        print("问：", r["query"])
        print("答：", r["answer"])
        for h in r["context"][:2]:
            print(f"  - [{h['source']}] {h['text'][:80]}...")


if __name__ == "__main__":
    main()
