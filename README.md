# 胶质瘤恶化风险预测与可解释分析系统

本项目基于 cBioPortal 的 Brain Lower Grade Glioma (TCGA, PanCancer Atlas) 队列，研究成人弥漫性低级别脑胶质瘤患者的进展风险，并逐步构建机器学习、生存分析、SHAP 解释和 Streamlit 展示流程。

## 当前状态

项目不是从零开始的新工程。当前已经：

- 读取 patient、sample 和 mRNA 表达数据
- 按 TCGA 条码前 12 位完成患者级对齐
- 转置 mRNA 表达矩阵并完成三表内连接
- 使用清洗后的 patient 表生成 `data/processed/data_multiomics_merged.csv`
- 完成年龄、分级、TP53、PCA 和部分 UMAP EDA

当前处于数据清洗与安全合并阶段。尚未进入正式模型训练。

## 数据与主要文件

| 文件 | 用途 |
| --- | --- |
| `data_clinical_patient.txt` | 患者级临床数据 |
| `data_clinical_sample.txt` | 样本级病理数据 |
| `data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt` | mRNA 表达 Z-score，使用 Git LFS 管理 |
| `data_analysis.py` | 临床患者表初步清洗 |
| `data_test.py` | 三张原始表读取冒烟检查 |
| `src/data/clean_patient.py` | patient 表保守清洗与质量报告 |
| `src/data/check_expression_quality.py` | 表达矩阵重复基因和缺失值质量检查 |
| `src/features/feature_column_rules.py` | 基于列名的泄露风险防护规则 |
| `merge_omics.py` | 使用清洗 patient 表执行安全三表合并 |
| `01_Data_Prep_and_Merging.ipynb` | 数据准备与合并 Notebook |
| `02_EDA_and_Visualization.ipynb` | EDA 与降维 Notebook |

生成的 `data/processed/patient_cleaned.csv`、`data/processed/data_multiomics_merged.csv`、旧根目录生成 CSV 和 `umap_visualization.png` 已被 `.gitignore` 忽略。

## 基础运行

从仓库根目录运行：

```powershell
python -m py_compile data_analysis.py data_test.py merge_omics.py
python data_test.py
```

按顺序执行当前安全数据流程：

```powershell
python src/data/clean_patient.py
python src/data/check_expression_quality.py
python merge_omics.py
```

`merge_omics.py` 强制读取 `data/processed/patient_cleaned.csv`。若清洗结果不存在，脚本会停止并提示先运行 patient 清洗。

## 特征选择安全规则

正式建模前必须通过 `src/features/feature_column_rules.py` 显式选择和校验候选特征列：

- 使用 `get_candidate_feature_columns(df)` 获取通过列名泄露检查的候选列。
- 使用 `validate_no_leakage_columns(feature_columns)` 校验最终特征列表。
- 禁止使用 `df.iloc[:, 6:]` 或其他固定位置切片粗暴选择建模特征。
- 候选列仍需人工核验其数据来源和生物学含义。

## 协作入口

- 首先阅读 `prompts/CODEX_INIT.md`
- 当前状态见 `PROJECT_STATE.md`
- 当前任务见 `TASKS.md`
- 8 周路线见 `ROADMAP.md`
- AI 执行规则见 `AGENTS.md`、`CLAUDE.md` 和 `HANDOFF.md`
- 重要变化见 `CHANGELOG.md`

## 目录策略

未来推荐使用 `data/raw/`、`data/processed/`、`src/`、`notebooks/`、`reports/` 和 `tests/`。当前文件仍保留在根目录；未经单独规划和验证，不得为了目录整洁而移动或删除现有文件。
