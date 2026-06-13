# Expression Matrix Quality Report

## Source And Structure

- Source: `data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt`
- Raw table shape: `20531 × 516`
- Numeric expression shape: `20531 genes/rows × 514 samples`
- Gene symbol location: `column` named `Hugo_Symbol`
- Non-numeric columns excluded from expression statistics: None
- Missing gene symbols: `13`
- Unique non-missing gene symbols: `20511`

## Duplicate Genes

- Unique duplicated gene symbols: `7`
- Rows involved in duplicated symbols: `14`
- Extra rows beyond one row per symbol: `7`
- Duplicated symbols: `ELMOD1`, `FGF13`, `NKAIN3`, `PALM2AKAP2`, `QSOX1`, `SNAP47`, `TMEM8B`

## Missing Values

- Total missing expression values: `189152`
- Missing expression proportion: `1.792411%`
- Samples with at least one missing value: `514` / `514`
- Genes/rows with at least one missing value: `368` / `20531`
- Genes/rows missing in all samples: `368`
- Genes/rows with partial missingness: `0`
- Minimum missing values in one sample: `368`
- Maximum missing values in one sample: `368`
- Maximum missing values in one gene/row: `514`
- Complete per-sample statistics: `reports/data_quality/expression_missing_by_sample.csv`
- Complete per-gene statistics: `reports/data_quality/expression_missing_by_gene.csv`

### Samples With Most Missing Values

| sample_id | missing_values | missing_percent |
| --- | --- | --- |
| TCGA-CS-4938-01 | 368 | 1.7924% |
| TCGA-CS-4941-01 | 368 | 1.7924% |
| TCGA-CS-4942-01 | 368 | 1.7924% |
| TCGA-CS-4943-01 | 368 | 1.7924% |
| TCGA-CS-4944-01 | 368 | 1.7924% |
| TCGA-CS-5390-01 | 368 | 1.7924% |
| TCGA-CS-5393-01 | 368 | 1.7924% |
| TCGA-CS-5394-01 | 368 | 1.7924% |
| TCGA-CS-5395-01 | 368 | 1.7924% |
| TCGA-CS-5396-01 | 368 | 1.7924% |
| TCGA-CS-5397-01 | 368 | 1.7924% |
| TCGA-CS-6186-01 | 368 | 1.7924% |
| TCGA-CS-6188-01 | 368 | 1.7924% |
| TCGA-CS-6290-01 | 368 | 1.7924% |
| TCGA-CS-6665-01 | 368 | 1.7924% |

### Genes With Most Missing Values

| row_number | gene_symbol | missing_values | missing_percent | is_duplicate_gene_symbol |
| --- | --- | --- | --- | --- |
| 7870 | HIST1H4G | 514 | 100.0000% | False |
| 6805 | GAGE12F | 514 | 100.0000% | False |
| 9308 | KRTAP19-6 | 514 | 100.0000% | False |
| 6807 | GAGE13 | 514 | 100.0000% | False |
| 4808 | DEFB105A | 514 | 100.0000% | False |
| 4655 | DAZ4 | 514 | 100.0000% | False |
| 4809 | DEFB106A | 514 | 100.0000% | False |
| 4810 | DEFB107A | 514 | 100.0000% | False |
| 3526 | CDY1 | 514 | 100.0000% | False |
| 9309 | KRTAP19-7 | 514 | 100.0000% | False |
| 6809 | GAGE2B | 514 | 100.0000% | False |
| 6810 | GAGE2C | 514 | 100.0000% | False |
| 4814 | DEFB110 | 514 | 100.0000% | False |
| 9744 | TEX36-AS1 | 514 | 100.0000% | False |
| 4816 | DEFB113 | 514 | 100.0000% | False |

## Conservative Recommendations

- Do not fill missing expression values with zero without a separately approved biological and statistical rationale.
- The current missingness is entirely concentrated in genes that are missing for every sample; confirm and filter these fully missing genes before considering imputation.
- Before downstream analysis, choose and document whether duplicated gene symbols are aggregated by mean or median.
- Define and document a threshold for filtering high-missingness genes before any imputation.
- Confirm the missing-value imputation strategy separately before modeling; fit any imputer only on training data.
- No aggregated expression matrix was written in this run because the mean-versus-median policy has not been confirmed.
