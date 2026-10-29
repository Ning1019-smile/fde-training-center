import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from my_tool.core.engine import analyze, Message, is_need, needs_escalation
from my_tool.core.kb import KnowledgeBase, chunk_text


def test_is_need():
    assert is_need("这题不会做")
    assert not is_need("今天天气不错")


def test_merge_continuous():
    msgs = [
        Message("张明", "群聊", "作业理解", "第三题不会做"),
        Message("张明", "作业评论", "作业理解", "还是不懂第三题"),
    ]
    t = analyze(msgs)
    assert len(t) == 1
    assert t[0].stu == "张明"
    assert len(t[0].original) == 2


def test_escalation():
    msgs = [Message("李华", "群聊", "流程咨询", "期末成绩会不会受影响？我有点担心。")]
    t = analyze(msgs)
    assert t[0].escalate is True
    assert "人工" in t[0].owner


def test_kb_retrieval():
    kb = KnowledgeBase()
    kb.add_document("求助漏单率需低于2%，人工确认后再联系学生。", "report.md")
    kb.build()
    r = kb.query("漏单率验收标准是多少")
    assert r and r[0]["score"] > 0


def test_chunk_text():
    chunks = chunk_text("第一段内容。\n\n第二段内容比较长需要切分测试。\n\n第三段。")
    assert len(chunks) >= 1
