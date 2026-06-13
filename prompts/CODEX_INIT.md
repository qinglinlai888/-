# CODEX_INIT

## 项目性质

这是一个已经推进一周的生物AI项目，不是从零开始的新项目。当前目标是无损接管现有 Git 仓库、固化 AI 协作工作流、保证项目后续稳定推进。

项目固定主线为：基于 TCGA/cBioPortal Brain Lower Grade Glioma (TCGA, PanCancer Atlas) 队列，开展胶质瘤恶化风险预测与可解释分析。不得改变癌种、数据来源、研究目标或既定技术路线。

## 当前阶段

仓库实际已基本完成第一周数据工程，并完成第二周的一部分 EDA：

* 已读取 patient 表、sample 表和 mRNA 表达矩阵
* 已完成 PATIENT_ID 与 SAMPLE_ID 对齐
* 已完成三表内连接并生成合并数据
* 已完成年龄、分级、TP53、PCA 和部分 UMAP 分析

当前仍冻结建模任务，优先处理数据质量、清洗管道一致性和工程可复现性。当前数据和代码继续保留在仓库根目录，不移动、不删除、不重构。

当前重点是：

* Python / Pandas 基础
* TCGA/cBioPortal 数据理解
* patient 表读取与质量检查
* sample 表读取与质量检查
* mRNA 表达矩阵读取与质量检查
* PATIENT_ID 与 SAMPLE_ID 对齐验证
* 三表合并结果验证
* 输出和核验 clean dataset

暂不进入：

* 机器学习
* 生存分析
* SHAP
* Streamlit
* 大规模重构

## 最终工作流

* 网页 GPT 负责计划、原理解释、每日任务拆解和生成 Codex 提示词
* Codex 是主力代码执行者
* Claude Code / DeepSeek V4 Pro 只在 Codex 额度不足时备用接力
* VSCode + Git + 项目文档是项目中枢
* 所有项目状态、决策和接力信息必须写入仓库文件，不能只存在于聊天记录

## 最高优先级原则

* 不要重建项目
* 不要删除已有代码
* 不要擅自改变项目方向
* 不要改变癌种、数据源、研究目标或技术路线
* 不要大范围重构
* 每次只推进一个小任务
* 修改前先说明计划
* 修改后说明修改文件、运行命令、预期输出和下一步
* 如果不确定某个文件用途，保留它，不要删除
* 不在未完成数据质量检查前进入建模
* 不移动当前根目录中的数据、脚本或 Notebook，除非项目文档明确批准迁移

## 需要创建或完善的项目记忆文件

请创建或完善：

* `PROJECT_STATE.md`
* `ROADMAP.md`
* `TASKS.md`
* `AGENTS.md`
* `CLAUDE.md`
* `CHANGELOG.md`
* `HANDOFF.md`
* `README.md`

如果文件不存在，请创建。如果文件已存在，请保守补充，不要覆盖。

## PROJECT_STATE.md 应包含

* 项目名称：生物AI项目：基于 TCGA/cBioPortal 数据的胶质瘤恶化风险预测与可解释分析系统
* 当前阶段：项目已推进一周，数据准备与三表合并基本完成，正在进行数据质量检查和第二周 EDA
* 总体目标：TCGA/cBioPortal 数据整理、多表合并、特征工程、机器学习、生存分析、SHAP 可解释性分析、Streamlit 展示、项目总结和汇报材料
* 当前优先任务：验证 patient/sample/mRNA 数据质量、统一清洗规则、核验三表合并结果、明确未来输出目录迁移方案
* 禁止事项：不跳过数据清洗直接建模，不更换主线，不大范围重构，不把聊天记录当作唯一项目记忆

## ROADMAP.md 应包含

8周路线：

1. Python、Pandas、TCGA/cBioPortal 数据理解与三表读取
2. 数据清洗、多表合并、质量检查与 EDA
3. 特征工程与标签构建
4. 机器学习建模
5. 生存分析
6. SHAP 可解释性分析
7. Streamlit 应用
8. 项目整理与展示

## TASKS.md 应包含

当前阶段：第一周数据工程基本完成 / 第二周 EDA 与质量检查阶段。

已完成：

* 检查并读取 patient 表、sample 表、mRNA 表达矩阵
* 输出并核验三张表的 shape 和关键字段
* 确认 PATIENT_ID 与 SAMPLE_ID 的关系
* 完成三表合并并生成 `data_multiomics_merged.csv`

下一最小任务：

* 为现有合并流程补充患者 ID 唯一性、合并形状、关键列、重复基因和表达缺失率检查
* 明确未来输出目录迁移方案
* 暂不进入机器学习

## AGENTS.md 应包含

Codex 是主力 AI 编程助手，必须遵守 `PROJECT_STATE.md`、`ROADMAP.md`、`TASKS.md`、`CHANGELOG.md`。

规则：

* 每次只推进一个小任务
* 修改前先说明计划
* 修改后说明文件、运行命令、预期输出
* 不大范围重构
* 不删除已有代码
* 优先保证代码能在 VSCode 本地运行
* 技术路线优先使用 Python、pandas、numpy、scikit-learn、lifelines、shap、streamlit、matplotlib

推荐但尚未实施的目录：

* `data/raw/`
* `data/processed/`
* `src/data/`
* `src/features/`
* `src/models/`
* `src/survival/`
* `src/explain/`
* `app/`
* `reports/`
* `notebooks/`
* `tests/`

不得仅为满足推荐结构而移动现有文件；目录迁移必须单独规划和验证。

## CLAUDE.md 应包含

Claude Code / DeepSeek V4 Pro 是备用执行者，不是主项目经理。

规则：

* 只继续 `HANDOFF.md` 或 `TASKS.md` 中明确未完成的任务
* 不重新规划项目
* 不改变技术路线
* 不大范围重构
* 不删除 Codex 已完成代码，除非存在明确 bug
* 修改前必须说明计划
* 修改后必须说明改动文件、运行命令和预期输出

## HANDOFF.md 应包含

* 当前主力执行者是 Codex
* Claude Code / DeepSeek V4 Pro 仅作为备用执行者
* 当前阶段是 TCGA/cBioPortal 数据质量检查、Pandas 清洗、三表合并验证与 EDA
* 接力者不得改变方向、不得重构整个项目、不得跳到后期任务
* Codex 回来后必须审查 Claude Code / DeepSeek 的改动

## CHANGELOG.md 应记录

* 建立网页 GPT + Codex + Claude Code/DeepSeek 的稳定协作模式
* Codex 作为主力代码执行者
* Claude Code / DeepSeek V4 Pro 作为 Codex 额度不足时的备用执行者
* 项目方向由 `PROJECT_STATE.md`、`ROADMAP.md`、`TASKS.md`、`AGENTS.md` 控制
* 当前项目状态：已推进一周，三表读取与合并基本完成，处于质量检查和部分 EDA 阶段

## requirements.txt

初始化时只加入：

```text
pandas
numpy
scikit-learn
matplotlib
lifelines
shap
streamlit
```

该最小清单不完整覆盖现有 Notebook；`seaborn`、`umap-learn` 和 Jupyter 依赖将在后续依赖审计任务中处理。

## 业务代码限制

本次任务主要目标是工作流迁移与项目接管，不是大量业务开发。

* 不修改现有业务代码或 Notebook
* 不创建 `src/data/inspect_raw_data.py`，因为当前没有 `data/raw/`，且 `data_test.py` 已具备最基本的读取检查能力
* 不做机器学习
* 不做复杂清洗
* 不覆盖原始数据
