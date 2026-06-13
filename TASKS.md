# 当前任务

## 当前阶段

数据清洗与安全合并阶段。暂不进入机器学习、生存分析、SHAP 或 Streamlit。

## 已完成

- [x] 检查并读取 patient 表、sample 表和 mRNA 表达矩阵。
- [x] 核验三张原始表的 shape 和关键字段。
- [x] 确认 `PATIENT_ID` 与 `SAMPLE_ID` 前 12 位的关系。
- [x] 确认 514 名患者在三张表中均可对齐。
- [x] 完成 mRNA 转置和三表内连接。
- [x] 生成并核验 `data_multiomics_merged.csv`。
- [x] 完成年龄、分级、TP53、PCA 和部分 UMAP 分析。
- [x] 初始化网页 GPT + Codex + Claude Code/DeepSeek 备用协作模式。
- [x] 新增 patient 表清洗脚本并生成 patient 数据质量报告。
- [x] 将合并流程的 patient 输入切换为 `data/processed/patient_cleaned.csv`。
- [x] 输出并记录重复 `Hugo_Symbol` 和表达缺失率摘要。
- [x] 生成完整的按样本和按基因表达缺失统计。
- [x] 搜索并记录固定位置特征切片的数据泄露风险。
- [x] 新增基于列名的候选特征筛选和泄露列校验规则。
- [x] 将主线三表合并结果输出到 `data/processed/data_multiomics_merged.csv`。
- [x] 在安全合并前输出输入 shape，并检查 patient ID 完整性与唯一性。
- [x] 核验安全合并结果为 `514 × 20574`，包含 514 个唯一患者和所需关键列。

## 下一最小任务

- [ ] 确认 7 个重复 gene symbol 使用均值还是中位数聚合。
- [ ] 确认并实施 368 个全缺失基因行的过滤规则。

## 后续任务

- [ ] 决定旧 `data_analysis.py` 的后续职责，避免与新 patient 清洗入口产生歧义。
- [ ] 明确重复基因聚合和表达缺失值处理策略。
- [ ] 在不大改 Notebook 的前提下，后续替换基于 `df.iloc[:, 6:]` 的特征提取方式。
- [ ] 完成 EDA 报告。
- [ ] 审计并补全可复现依赖清单。
- [ ] 在数据质量检查完成后确定正式研究终点和标签规则。

## 本阶段验收标准

- 三张输入表、患者 ID 对齐和合并结果具有明确断言与摘要。
- 重复基因和表达缺失问题已量化并形成处理决策。
- 生成数据继续被 `.gitignore` 忽略。
- 未开始模型训练。
