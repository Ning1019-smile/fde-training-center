# 贡献指南

欢迎以 Issue / Pull Request 形式参与。

1. Fork 并克隆本仓库
2. 创建分支（`feature/xxx` 或 `fix/xxx`）
3. 安装依赖：`pip install -r requirements.txt`
4. 运行自检：`export PYTHONPATH=src && python -m my_tool.main demo`（Windows：`set PYTHONPATH=src`）
5. 提交 PR，填写模板并关联 Issue

## 代码约定
- 核心逻辑保持零依赖、可单测；新增功能请补 `tests/`
- 知识库检索相关改动请同步验证 `python -m my_tool.main build`
- 文档类交付物（docx / svg）由 `scripts/gen_*.py` 生成，修改源脚本而非产物
