# 更新日志

## [0.1.0] - 2026-10-29

### 新增
- 业务引擎：支持需求识别 + 连续求助合并（`src/my_tool/core/engine.py`）
- RAG 知识库：离线 TF-IDF 检索，可接入 LLM 合成（`src/my_tool/core/kb.py`）
- CLI：`build` / `query` / `demo`（`src/my_tool/main.py`）
- 最小 MVP 静态网页（`examples/mvp/index.html`）
- 交付物：行业分析、两张流程图、设计方案与报价单（`docs/`）
- 测试、示例、脚本、CI 与项目框架文件

### 说明
- 预算 9 万元（含集成、培训与验证），报价单见 `docs/design-proposal-quote.docx`
- 漏单基线、合并规则、统计周期等口径待业务负责人书面确认后用于验收
