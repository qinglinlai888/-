# 项目状态

## 项目名称

生物AI项目：基于 TCGA/cBioPortal 数据的胶质瘤恶化风险预测与可解释分析系统

具体研究对象为成人弥漫性低级别脑胶质瘤（LGG），数据来源固定为 cBioPortal 的 Brain Lower Grade Glioma (TCGA, PanCancer Atlas) 队列。

## 当前阶段

数据清洗与安全合并阶段。第一周的数据准备、Pandas 读取和 TCGA/cBioPortal 三表对齐已完成，当前重点是使用清洗数据安全合并、核验表达质量和固化泄露防护规则。

已由仓库和数据验证：

- patient 表为 `514 × 38`
- sample 表为 `514 × 19`
- mRNA 表达矩阵为 `20531 × 516`
- 514 名患者在 patient、sample 和 mRNA 数据中均可对齐
- 安全合并结果输出到 `data/processed/data_multiomics_merged.csv`
- 已验证安全合并结果为 `514 × 20574`，包含 514 个唯一患者且无重复患者
- 已完成年龄、分级、TP53、PCA 和部分 UMAP 分析
- 已新增 patient 表清洗入口，输出 `data/processed/patient_cleaned.csv` 和质量报告
- `merge_omics.py` 已改为使用清洗后的 patient 表，不再直接读取原始 patient 表
- 已新增表达矩阵质量检查，量化重复基因和按样本/按基因缺失情况
- 已生成 `data/processed/expression_cleaned.csv`：过滤 368 个全缺失基因行，并按 mean 聚合 7 个重复 gene symbol
- 已新增基于列名的泄露防护规则，并记录 Notebook 固定位置切片风险
- `merge_omics.py` 已强制使用清洗后的 patient 与 expression 数据
- 已验证重新安全合并结果为 `514 × 20201`

当前正在完成数据清洗与安全合并验证。尚未进入正式建模。

## 总体目标

完成 TCGA/cBioPortal 数据整理、多表合并、特征工程、机器学习、生存分析、SHAP 可解释性分析、Streamlit 展示、项目总结和汇报材料。

## 当前优先任务

已完成 `expression_cleaned.csv` 生成与重新安全三表合并。下一优先任务是核验清洗后合并表的元数据列与表达特征列边界；暂不进入机器学习。

## 当前文件布局

原始数据、旧脚本和两个 Notebook 仍位于仓库根目录。清洗数据写入 `data/processed/`，质量检查代码位于 `src/`，报告位于 `reports/data_quality/`。

该布局暂时保留。未经单独规划、验证和记录，不得移动或删除现有文件。

## 禁止事项

- 不跳过数据清洗和质量检查直接建模。
- 不更换癌种、数据来源、研究目标或技术路线。
- 不把 PFS 进展、复发、恶化和 GBM 转化混为同一终点。
- 不大范围重构或删除已有代码。
- 不把聊天记录当作唯一项目记忆。
- 不提交生成的大型 CSV、图片、模型文件或临时文件。

## 已知风险

- patient 清洗会保留全部患者及临床缺失值；正式终点确定前不得擅自删除或插补缺失标签。
- mRNA 清洗规则已确定为过滤 368 个全缺失基因行，并对 7 个重复 gene symbol 使用 mean 聚合；未执行任何缺失值填补。
- `01_Data_Prep_and_Merging.ipynb` 中的 `df.iloc[:, 6:]` 会混入临床元数据并造成数据泄露。
- 当前最小 `requirements.txt` 尚不包含现有 Notebook 使用的 `seaborn`、`umap-learn` 和 Jupyter。
