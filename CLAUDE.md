# Claude Code / DeepSeek V4 Pro 接力规则

Claude Code / DeepSeek V4 Pro 是 Codex 额度不足时的备用执行者，不是主项目经理。

## 必须遵守

- 先读取 `prompts/CODEX_INIT.md`、`PROJECT_STATE.md`、`TASKS.md`、`HANDOFF.md` 和 `AGENTS.md`。
- 只继续 `HANDOFF.md` 或 `TASKS.md` 中明确未完成的任务。
- 不重新规划项目，不改变癌种、数据来源、研究目标或技术路线。
- 不跳到机器学习、生存分析、SHAP 或 Streamlit 等后期任务。
- 不大范围重构，不移动或删除已有文件。
- 不删除 Codex 已完成的代码，除非存在明确且已记录的 bug。
- 修改前必须说明计划。
- 修改后必须记录改动文件、运行命令、实际输出、未完成事项和风险。
- 不覆盖项目记忆文件，只做保守补充。

## 交付要求

接力结束前更新 `HANDOFF.md` 和 `CHANGELOG.md`，并保留清晰的 Git diff，供 Codex 回来后审查。未经明确要求，不自动提交或推送。

