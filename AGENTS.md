# 项目协作指南

本文档记录当前仓库与《生物AI项目冲刺路线图 - 第一周.pdf》中可以确认的项目信息，供后续开发、分析和 AI 代理协作使用。

## 1. 项目定位

- 项目名称：**弥漫性脑胶质瘤进化风险分层预测器**（Glioma Evolutionary Risk Predictor）。
- 研究对象：成人弥漫性低级别脑胶质瘤（LGG，主要为 WHO Grade II/III）。
- 临床问题：LGG 患者的演化轨迹差异很大，需要识别较快复发、进展或恶化的高风险患者。
- 数据来源：cBioPortal 的 **Brain Lower Grade Glioma (TCGA, PanCancer Atlas)** 队列。
- 研究对标：香港科技大学王吉光教授团队的胶质瘤演化研究，如 CELLO/CELLO2 和免疫微环境分型工作。
- 当前仓库的直接目标：完成临床数据与 mRNA 表达数据的读取、清洗、患者级对齐、合并和探索性分析。
- 路线图的最终目标：以患者两年内是否进展/恶化为风险终点，构建 XGBoost 风险模型，使用生存分析和 SHAP 验证并解释结果，最后制作 Streamlit Web 应用和研究报告。

> 重要边界：当前仓库只有临床/样本元数据和 mRNA 表达 Z-score，尚未包含 DNA 突变、拷贝数变异等其他组学文件。因此当前所谓“多组学合并表”严格来说是“临床 + 样本病理 + 转录组表达”合并表。

## 2. 当前完成度

仓库已基本完成路线图第 1 周的数据工程任务，并完成了第 2 周的一部分 EDA：

- 已读取并检查患者表、样本表和 mRNA 表达矩阵。
- 已按 TCGA 条码前 12 位统一到患者级 `PATIENT_ID`。
- 已将原始“基因为行、样本为列”的 mRNA 表转置为“患者为行、基因为列”。
- 已通过两次内连接生成合并表 `data_multiomics_merged.csv`。
- 已完成年龄分布、分级占比、TP53 表达箱线图和 PCA。
- 已定义 UMAP 分析函数，并存在生成图 `umap_visualization.png`。
- 尚未构建正式训练标签、训练分类/生存模型、执行 SHAP、开发 Web 应用或撰写最终报告。

## 3. 数据文件与已核验规模

| 文件 | 角色 | 已核验规模/说明 |
| --- | --- | --- |
| `data_clinical_patient.txt` | 患者级临床表 | `514 × 38`；含 `AGE`、`SEX`、`SUBTYPE`、`OS_*`、`PFS_*` 等 |
| `data_clinical_sample.txt` | 样本级病理表 | `514 × 19`；含 `SAMPLE_ID`、`GRADE`、肿瘤类型等；全部为 Primary 样本 |
| `data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt` | mRNA 表达 Z-score | `20531 × 516`；前两列为基因标识，后 514 列为样本 |
| `data_clinical_cleaned.csv` | 患者表清洗结果 | 生成文件；删除 OS 标签缺失行并填补少量 AGE/SEX 缺失 |
| `data_multiomics_merged.csv` | 临床、病理、mRNA 合并表 | 实际为 `514 × 20574`；含 56 个临床/样本列和 20518 个表达特征列 |
| `umap_visualization.png` | UMAP 输出图 | 生成文件 |

数据仓库约定：

- 原始 TSV 文件使用制表符分隔，头部带 `#` 注释；读取时必须使用：

  ```python
  pd.read_csv(path, sep="\t", comment="#")
  ```

- mRNA 原始文件由 Git LFS 管理。
- `data_clinical_cleaned.csv`、`data_multiomics_merged.csv` 和 `umap_visualization.png` 已被 `.gitignore` 忽略，不应作为源码提交。
- 仓库当前没有 `requirements.txt`、环境锁文件或正式自动化测试。

## 4. 关键数据事实

### 4.1 临床与样本分布

- 患者数：514；患者 ID 无重复。
- 样本数：514；样本 ID 无重复；全部为原发样本。
- 分级：G3 为 264 例，G2 为 248 例，缺失 2 例。
- OS 状态：存活 388 例，死亡 125 例，缺失 1 例。
- OS 标签完整患者：513 例。
- PFS 状态：未观察到进展/删失 321 例，进展 192 例，缺失 1 例；`PFS_MONTHS` 缺失 2 例。
- 亚型：`LGG_IDHmut-non-codel` 248 例，`LGG_IDHmut-codel` 167 例，`LGG_IDHwt` 92 例，缺失 7 例。
- 路线图示例中的“年龄大于 50 岁且已死亡”亚群实际为 57 例。

### 4.2 mRNA 数据质量

- 原始 mRNA 表有 13 行缺失 `Hugo_Symbol`，当前流程会删除这些行。
- 原始 mRNA 表有 7 个重复基因符号：`PALM2AKAP2`、`ELMOD1`、`FGF13`、`QSOX1`、`SNAP47`、`NKAIN3`、`TMEM8B`。
- 合并表中的基因表达列均被 Pandas 读取为 `float64`，但仍存在约 18.8 万个表达缺失值。
- 建模前必须明确重复基因的聚合策略，并处理表达缺失值；不能假设转置后矩阵已经完全干净。

### 4.3 当前 EDA 结果

- PCA 使用 Top 1000 高方差基因。
- PC1 解释约 `20.86%` 的整体差异。
- PC2 解释约 `4.12%` 的整体差异。

## 5. 文件职责

- `01_Data_Prep_and_Merging.ipynb`
  - 项目的数据工程主 Notebook。
  - 记录科学背景、临床清洗、数据接入、ID 对齐、mRNA 转置、双重内连接和 NumPy 特征提取。
- `02_EDA_and_Visualization.ipynb`
  - EDA 与降维 Notebook。
  - 包含年龄直方图、分级饼图、TP53 箱线图、Top 1000 高方差基因 PCA 和 UMAP 函数。
- `data_analysis.py`
  - 临床患者表的初步读取、缺失值处理、高风险亚群筛选和清洗结果保存。
- `data_test.py`
  - 三张原始表的读取冒烟测试，只验证文件可读和基础字段存在，不是正式测试套件。
- `merge_omics.py`
  - 三表读取、ID 对齐、mRNA 转置、两次内连接、关键列检查和合并表保存。

## 6. 当前数据处理流程

1. 读取患者表、样本表和 mRNA 表，跳过 `#` 注释行。
2. 从 `SAMPLE_ID` 前 12 个字符构造患者级 `PATIENT_ID`。
3. 删除缺失 `Hugo_Symbol` 的 mRNA 行。
4. 将 `Hugo_Symbol` 设为索引并删除 `Entrez_Gene_Id`。
5. 转置 mRNA 表，使行表示患者/样本，列表示基因。
6. 从转置后索引前 12 个字符构造 `PATIENT_ID`。
7. 先合并患者表和样本表，再合并转置后的 mRNA 表，均使用 `how="inner"`。
8. 保存 `data_multiomics_merged.csv`，用于后续 EDA 和建模。

TCGA ID 规则：

- 患者级 ID 示例：`TCGA-DU-5872`，长度 12。
- 样本级 ID 示例：`TCGA-DU-5872-01`，长度 15。
- 生存标签挂在患者级，病理和表达数据挂在样本级；合并前必须统一到患者级 ID。

## 7. 必须遵守的建模与统计规则

### 7.1 先确定正式研究终点

当前材料中存在两个方向：

- Notebook 偏向使用 OS/PFS 开展生存预测。
- 56 天路线图的核心模型偏向构建“诊断后两年内是否进展/恶化”的二分类标签。

训练模型前必须明确并记录最终终点、纳入标准和评估指标。不要在同一实验中混用 OS、PFS、复发、恶化和 GBM 转化等不同概念。

若采用“两年内 PFS 进展”二分类：

- 当前数据中，两年内明确进展约 133 例。
- 随访或进展时间超过两年的患者约 187 例，可用于判断“两年内未进展”。
- 在两年内即被删失的患者约 192 例，终点不确定，不能直接标记为稳定组。
- PFS 标签/时间缺失的患者必须剔除。
- “PFS 进展”不必然等于“恶性转化为 GBM”，报告中必须准确描述终点。

### 7.2 严禁数据泄露

- 不要使用 `df.iloc[:, 6:]` 提取基因特征。当前合并表有 56 个临床/样本列，第 7 列仍是 `GRADE`，这种切片会把标签和元数据放入特征矩阵。
- 应通过患者表与样本表的列名集合识别并剥离全部临床/样本元数据，再取得基因列。
- 训练/测试划分必须发生在插补、标准化、特征选择和 SMOTE 之前。
- 插补器、标准化器、特征选择器和 SMOTE 只能在训练集上拟合。
- 测试集必须保持隐藏，不能参与特征筛选、调参或阈值选择。

### 7.3 保持患者级独立性

- 当前每个患者恰有一个原发样本，但未来加入复发或多样本数据后，必须按患者分组划分训练集与测试集。
- 不允许同一患者的不同样本出现在训练集和测试集两侧。

### 7.4 特征工程要求

- 先处理重复 `Hugo_Symbol`，建议明确采用均值、最大方差探针或其他可解释聚合规则。
- 处理 mRNA 缺失值，并记录每个过滤阈值。
- mRNA 已是 Z-score；若再次标准化，必须说明原因，并只在训练集拟合。
- 保留基因名与矩阵列的对应关系，供特征重要性和 SHAP 生物学解释使用。
- 当前仓库没有突变矩阵。不能把 `IDH1` 表达量当作 IDH1 突变状态；若需要 IDH 状态，可谨慎使用已有 `SUBTYPE` 派生标签，或补充真实突变数据。

### 7.5 评估要求

- 分类任务至少报告 ROC-AUC、PR-AUC、混淆矩阵、Precision、Recall 和 F1，并使用交叉验证。
- 类别不平衡时优先关注 PR-AUC、召回率和校准情况，不能只看 Accuracy。
- 生存任务应使用 Kaplan-Meier、log-rank、Cox 或适当的生存模型指标；不要只用普通分类指标替代删失数据建模。
- 固定并记录 `random_state`，保证结果可复现。

## 8. 路线图摘要

上传的 PDF 虽名为“第一周”，实际包含完整的 **8 周、56 天、约 250 小时**冲刺路线。

### 阶段一：Python 与数据科学基础（第 1-2 周）

- 第 1 周：Python/Pandas、临床缺失值处理、cBioPortal 数据下载、三表对齐合并、NumPy 向量化、整理学术 Notebook。
- 第 2 周：Matplotlib、Seaborn、PCA、t-SNE/UMAP、胶质瘤领域文献阅读、形成 EDA 报告。

当前仓库已覆盖第 1 周大部分任务，以及第 2 周的可视化、PCA 和部分 UMAP 工作。

### 阶段二：机器学习算法库实战（第 3-4 周）

- 第 3 周：训练/测试集、逻辑回归、随机森林、特征重要性、ROC/AUC、交叉验证和 XGBoost。
- 第 4 周：Kaplan-Meier、生存曲线、Cox 回归，并初步了解 PyTorch/MLP。

### 阶段三：核心项目实战（第 5-7 周）

- 第 5 周：定义两年 PFS 风险标签、构建生物学特征集、处理不平衡、规范切分和建立 Baseline/XGBoost。
- 第 6 周：超参数调优、防过拟合、隐藏测试集评估和生存分析验证。
- 第 7 周：SHAP 解释、连接基因功能与生物学机制、重构为数据准备/模型训练/解释性分析三个 Notebook。

### 阶段四：部署与申请材料（第 8 周）

- 使用 Streamlit 构建可交互风险预测应用。
- 整理 GitHub 仓库与 README。
- 撰写约 4 页英文研究报告。
- 准备简历、申请材料和联系课题组的邮件。

预期最终作品包括：可复现代码仓库、带 ROC/KM/SHAP 结果的研究报告，以及可交互的 Streamlit 风险预测 Demo。

## 9. 开发与运行约定

从仓库根目录运行命令。当前 Notebook 元数据使用 Python `3.13.9` 的 `base` 环境，但仓库没有锁定依赖版本。

基础检查：

```powershell
python -m py_compile data_analysis.py data_test.py merge_omics.py
python data_test.py
```

重建数据：

```powershell
python data_analysis.py
python merge_omics.py
```

当前直接依赖包括：

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `umap-learn`
- Jupyter Notebook

路线图后续可能需要：

- `xgboost`
- `imbalanced-learn`
- `lifelines`
- `shap`
- `optuna`
- `torch`
- `streamlit`

协作规则：

- 不要打印完整高维表达矩阵，优先使用 `.shape`、`.info()`、`.head()` 和统计摘要。
- 不要提交生成的大型 CSV、图片、模型文件或临时文件，除非项目明确改变版本管理策略。
- 修改数据管道时添加形状、唯一性、关键列、缺失率和标签分布断言。
- 新实验应保留配置、随机种子、特征列表和评估结果。
- 重要结论必须区分“已由数据验证”“路线图计划”和“生物学推断”。

## 10. 当前技术债与优先事项

1. **正式确定终点**：明确做 OS/PFS 生存分析，还是两年 PFS 进展二分类；写出严格的删失处理规则。
2. **修复特征提取**：彻底移除基于“前 6 列”的位置切片，按列名集合提取基因特征。
3. **统一清洗管道**：`data_analysis.py` 清洗了患者表，但 `merge_omics.py` 仍直接使用未清洗患者表，因此合并表仍含缺失标签。
4. **处理重复基因与表达缺失**：在建模前形成可复现、可解释的规则。
5. **补充可复现工程配置**：增加依赖清单、正式测试、统一入口和结果目录。
6. **完成 EDA 报告**：整理当前图表、PCA/UMAP 结果和数据质量结论。
7. **再进入模型训练**：先建立无泄露的 Baseline，再逐步引入 XGBoost、调参、SHAP 和生存验证。

## 11. AI 协作执行规则

- Codex 是主力 AI 编程助手，必须先读取并遵守 `prompts/CODEX_INIT.md`、`PROJECT_STATE.md`、`ROADMAP.md`、`TASKS.md` 和 `CHANGELOG.md`。
- Claude Code / DeepSeek V4 Pro 仅在 Codex 额度不足时作为备用执行者，只能继续 `HANDOFF.md` 或 `TASKS.md` 中明确未完成的任务。
- 网页 GPT 负责项目计划、原理解释、每日任务拆解和生成 Codex 执行提示词。
- VSCode、Git 和仓库项目文档是项目中枢；项目状态和重要决策不能只存在于聊天记录中。
- 每次只推进一个小任务，修改前说明计划，修改后记录文件、运行命令、实际输出、风险和下一步。
- 不大范围重构，不删除已有代码，不擅自移动当前根目录中的数据、脚本或 Notebook。
- 优先保证代码能在 VSCode 本地运行。
- 技术路线优先使用 Python、pandas、numpy、scikit-learn、lifelines、shap、streamlit 和 matplotlib。

未来推荐但尚未实施的目录包括 `data/raw/`、`data/processed/`、`src/data/`、`src/features/`、`src/models/`、`src/survival/`、`src/explain/`、`app/`、`reports/`、`notebooks/` 和 `tests/`。不得仅为满足推荐结构而移动现有文件；目录迁移必须作为独立任务进行规划、验证和记录。
