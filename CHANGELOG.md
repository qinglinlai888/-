# 变更记录

所有重要流程、代码和项目状态变化都应记录在此。最新记录置于顶部。

## 2026-06-13

### 表达矩阵清洗与重新安全合并

- 新增 `src/data/clean_expression.py`，自动定位并读取原始 mRNA 表达矩阵。
- 过滤 368 个在所有样本中完全缺失的基因行。
- 排除全缺失过滤后仍无法命名的 11 个缺失 gene symbol 行。
- 对 7 个重复 gene symbol 使用 mean 聚合，生成 `data/processed/expression_cleaned.csv`。
- 生成 `reports/data_quality/expression_cleaning_report.md`。
- 未执行 `fillna(0)`、全局中位数填补或其他缺失值插补；清洗后实际剩余表达缺失值为 0。
- 修改 `merge_omics.py`，强制使用 `data/processed/expression_cleaned.csv`。
- 重新安全合并结果为 `514 × 20201`。

### 安全三表合并与项目文档更新

- 最小修改主线合并脚本 `merge_omics.py`，未修改包含旧流程的 Notebook。
- 合并流程优先且强制使用 `data/processed/patient_cleaned.csv`；文件不存在时提示先运行 patient 清洗脚本。
- 合并前输出 patient、sample、expression shape，并检查 patient ID 完整性与唯一性。
- 安全合并结果改为输出到 `data/processed/data_multiomics_merged.csv`，并加入 `.gitignore`。
- 已验证安全合并输出为 `514 × 20574`，包含 514 个唯一患者且关键列齐全。
- 更新 `PROJECT_STATE.md`、`TASKS.md` 和 `README.md`，将当前阶段明确为数据清洗与安全合并阶段。
- 保持 `requirements.txt` 不变；本轮脚本不需要 seaborn、umap-learn 或 Jupyter。

### 表达矩阵质量检查与泄露防护规则

- 新增 `src/data/check_expression_quality.py`，自动定位并检查原始 mRNA 表达矩阵。
- 生成表达质量报告，以及完整的按样本和按基因缺失统计。
- 确认原始数值表达区域存在 7 个重复基因符号、189,152 个缺失值；缺失值全部来自 368 个全缺失基因行，未执行填补、过滤或聚合。
- 新增 `src/features/feature_column_rules.py`，按列名排除标识符、结果字段和疑似泄露字段。
- 生成泄露风险报告，记录 `01_Data_Prep_and_Merging.ipynb` 中的 `df.iloc[:, 6:]` 高风险写法。
- 本轮未修改 Notebook，未训练模型。

### Patient 表清洗与合并输入修正

- 新增 `src/data/clean_patient.py`，自动定位并读取 patient 表。
- 标准化 `PATIENT_ID`，检查缺失、重复和非法 TCGA patient ID。
- 保守清洗字符串字段，不删除患者、不插补临床缺失值。
- 生成 `data/processed/patient_cleaned.csv` 和 `reports/data_quality/patient_quality_report.md`。
- 修改 `merge_omics.py`，使其只读取清洗后的 patient 表，不再直接读取原始 patient 表。
- 将生成的 patient 清洗 CSV 加入 `.gitignore`。
- 重新暂存最新完整版本的 `AGENTS.md`，未执行提交。

### 项目接管与协作工作流初始化

- 建立网页 GPT + Codex + Claude Code/DeepSeek 的稳定协作模式。
- 明确 Codex 是主力代码执行者。
- 明确 Claude Code / DeepSeek V4 Pro 仅在 Codex 额度不足时作为备用执行者。
- 使用 `PROJECT_STATE.md`、`ROADMAP.md`、`TASKS.md`、`AGENTS.md`、`HANDOFF.md` 控制项目方向与接力状态。
- 创建 `prompts/CODEX_INIT.md`，固化无损接管和禁止大范围重构等规则。
- 确认当前项目已推进一周，三表读取与合并基本完成，处于数据质量检查和部分 EDA 阶段。
- 保留现有根目录文件布局，未移动数据、脚本或 Notebook。
- 本次初始化未修改业务代码。
