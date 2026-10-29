# -*- coding: utf-8 -*-
"""
轻量 RAG 知识库（纯 Python，零依赖，可离线运行）。

能力：
  - 读取 .md/.txt 文档并切分为 chunk
  - 构建 TF-IDF 倒排索引
  - 自然语言查询返回 Top-K 相关片段
  - answer() 默认返回检索到的上下文（可接入 LLM 做合成，见 llm_hook）

适用于本项目“知识库 RAG / LLMwiki”需求：把业务需求报告、设计方案、
行业分析等文档纳入检索，支持“问 → 答（带引用）”的闭环。
"""
from __future__ import annotations
import json
import math
import os
import re
from typing import Callable, Dict, List, Optional

# 可选 LLM 合成钩子：若配置，answer() 会调用它做最终归纳。
LLMHook = Optional[Callable[[str, List[dict]], str]]


def chunk_text(text: str, size: int = 400, overlap: int = 60) -> List[str]:
    """按段落切分，长段落再按字数切，保留少量重叠以维持上下文连续。"""
    paras = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    chunks: List[str] = []
    buf = ""
    for p in paras:
        if len(buf) + len(p) > size and buf:
            chunks.append(buf.strip())
            buf = buf[-overlap:] + "\n" + p if overlap else p
        else:
            buf = (buf + "\n" + p).strip()
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


class _Tokenizer:
    @staticmethod
    def tokenize(text: str) -> List[str]:
        text = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text.lower())
        toks: List[str] = []
        for w in text.split():
            # 中文按字、英文/数字按词
            if re.search(r"[\u4e00-\u9fff]", w):
                toks.extend(list(w))
            else:
                toks.append(w)
        return [t for t in toks if t]


class KnowledgeBase:
    def __init__(self, llm_hook: LLMHook = None):
        self.docs: List[Dict] = []          # {id, source, text}
        self.inv: Dict[str, List[int]] = {} # term -> [doc_idx]
        self.df: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.N = 0
        self.vecs: List[Dict[str, float]] = []
        self.llm_hook = llm_hook

    # ---- 构建 ----
    def add_document(self, text: str, source: str = "", doc_id: Optional[str] = None) -> int:
        did = doc_id or f"d{len(self.docs)}"
        chunks = chunk_text(text)
        for i, c in enumerate(chunks):
            self.docs.append({"id": f"{did}#{i}", "source": source, "text": c})
        return len(chunks)

    def add_from_file(self, path: str) -> int:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return self.add_document(f.read(), source=os.path.basename(path))

    def build(self) -> None:
        self.N = len(self.docs)
        tf_per_doc: List[Dict[str, int]] = []
        for d in self.docs:
            toks = _Tokenizer.tokenize(d["text"])
            tf: Dict[str, int] = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            tf_per_doc.append(tf)
            for t in tf:
                self.df[t] = self.df.get(t, 0) + 1
        for t, dfv in self.df.items():
            self.idf[t] = math.log((self.N + 1) / (dfv + 1)) + 1
        self.vecs = []
        for tf in tf_per_doc:
            vec = {t: (1 + math.log(tf[t])) * self.idf[t] for t in tf}
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            self.vecs.append({t: v / norm for t, v in vec.items()})

    # ---- 查询 ----
    def query(self, q: str, top_k: int = 5) -> List[Dict]:
        qt = _Tokenizer.tokenize(q)
        qv: Dict[str, float] = {}
        for t in qt:
            qv[t] = qv.get(t, 0) + 1
        qv = {t: (1 + math.log(c)) * self.idf.get(t, 0.0) for t, c in qv.items()}
        qn = math.sqrt(sum(v * v for v in qv.values())) or 1.0
        qv = {t: v / qn for t, v in qv.items()}
        scored = []
        for i, vec in enumerate(self.vecs):
            dot = sum(vec[t] * qv[t] for t in qv if t in vec)
            if dot > 0:
                scored.append((dot, i))
        scored.sort(reverse=True)
        return [
            {"id": self.docs[i]["id"], "source": self.docs[i]["source"],
             "score": round(s, 4), "text": self.docs[i]["text"]}
            for s, i in scored[:top_k]
        ]

    def answer(self, q: str, top_k: int = 5) -> Dict:
        hits = self.query(q, top_k)
        if self.llm_hook and hits:
            synthesized = self.llm_hook(q, hits)
            ans = synthesized
        else:
            ans = "根据项目文档检索到以下相关内容：" if hits else "未检索到相关内容，建议补充知识库文档。"
        return {"query": q, "answer": ans, "context": hits}

    # ---- 持久化 ----
    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"docs": self.docs}, f, ensure_ascii=False)

    def load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            self.docs = json.load(f)["docs"]
        self.build()

    def index_directory(self, directory: str) -> int:
        cnt = 0
        for root, _, files in os.walk(directory):
            for fn in files:
                if fn.endswith((".md", ".txt")):
                    cnt += self.add_from_file(os.path.join(root, fn))
        self.build()
        return cnt
