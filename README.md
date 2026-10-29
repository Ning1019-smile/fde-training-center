# 北辰在线学院 · AI 学习支持与辅导协作（beichen-ai-support）

> 用 AI 把“学习支持与辅导协作”环节的求助漏单压到 2% 以内、首次响应从 26h 压到 8h、重复求助率从 35% 降到 15%。本仓库是面向试点的**最小可验证方案**：含行业分析、系统流程图、设计方案与报价单、可运行 MVP，以及一个零依赖的 RAG 知识库。

## 这是什么

学生问题散落在群聊、作业评论、LMS 里，助教常漏掉连续求助；交接缺少随单说明与接手确认，导致重复求助。本项目在**不自动给学生定性或评分**的硬边界下，用 AI 做三件事：

1. **识别**：从多源入口识别“支持需求”信号；
2. **合并**：按学生把连续求助合并为一张工单（解决漏单主因）；
3. **建议 + 人工复核**：生成建议（显示原记录与待确认字段），由助教确认后再联系学生。

配套随单交接、人工兜底（转人工/暂停）、审计链与降级快照，满足合规与试点验收要求。

## 仓库结构

```
beichen-ai-support/
├── README.md                 # 本文件
├── LICENSE                   # MIT
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── requirements.txt
├── src/my_tool/              # 核心代码
│   ├── main.py               # CLI：build / query / demo
│   ├── core/engine.py        # 支持需求识别 + 连续求助合并
│   └── core/kb.py            # 轻量 RAG 知识库（离线 TF-IDF）
├── docs/                     # 交付物
│   ├── industry-analysis.docx     # 行业分析
│   ├── design-proposal-quote.docx # 设计方案 + 报价单（≤9万）
│   ├── flowchart-current.svg      # 无 AI 现状业务流程图
│   ├── flowchart-ai.svg           # 增加 AI 后系统流程图
│   └── 01-业务需求发现报告.md      # 原始需求报告（知识库语料）
├── examples/
│   ├── demo.py               # 端到端示例
│   └── mvp/index.html        # 最小 MVP（纯静态网页，双击即开）
├── tests/test_core.py
├── scripts/build.sh          # 构建知识库索引
├── scripts/deploy.sh         # 本地预览 MVP
├── config/default.yaml
└── data/sample_messages.json
```

## 怎么装

核心代码**零依赖**即可运行（Python 3.10+）。可选增强见 `requirements.txt`：

```bash
cd beichen-ai-support
pip install -r requirements.txt   # 可选：pyyaml / pytest
```

## 怎么跑

```bash
export PYTHONPATH=src            # Windows: set PYTHONPATH=src

# 1) 业务引擎演示（识别 + 合并连续求助）
python -m my_tool.main demo

# 2) 构建知识库索引（扫描 docs/ 下所有 md/txt）
python -m my_tool.main build --docs docs --out data/kb.json

# 3) 离线检索问答（RAG）
python -m my_tool.main query "漏单率验收标准是多少"

# 4) 最小 MVP 网页
#    方式A：直接双击 examples/mvp/index.html
#    方式B：本地起服务
bash scripts/deploy.sh           # 打开 http://localhost:8080
```

## 关键设计约束（来自需求报告）

- **不自动给学生定性或评分**；任何建议必须附行为证据。
- **人工确认后再联系学生**（系统不直接触达）。
- 触发转人工须标注：触发原因、接手人、确认时间；错误结果不覆盖原记录。
- 审计链保留：业务编号 / 版本 / 事实引用 / 建议结果 / 人工改动 / 签核人。
- 接口中断时用带时间戳的只读快照，提示“暂未更新”，重连后按编号去重补齐。

## 验收硬线（两班级试点）

| 指标 | 现状 | 目标 |
| --- | --- | --- |
| 首次响应 | 26h | 8h |
| 重复求助率 | 35% | 15% |
| 求助漏单率 | 无基线 | < 2% |

## 许可证

MIT —— 详见 [LICENSE](LICENSE)。
