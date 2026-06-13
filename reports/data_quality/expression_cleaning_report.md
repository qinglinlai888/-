# Expression Cleaning Report

## Inputs And Outputs

- Source: `data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt`
- Raw table shape: `20531 × 516`
- Numeric expression shape before cleaning: `20531 genes/rows × 514 samples`
- Gene symbol location: `column` named `Hugo_Symbol`
- Cleaned output: `data/processed/expression_cleaned.csv`
- Numeric expression shape after cleaning: `20145 genes × 514 samples`
- Saved table shape including `Hugo_Symbol`: `20145 × 515`

## Cleaning Rules And Results

- Fully missing gene rows removed: `368`
- Missing gene-symbol rows in raw data: `13`
- Missing gene-symbol rows removed after fully missing filtering: `11`
- Duplicate gene symbols aggregated by: `mean`
- Unique duplicated gene symbols aggregated: `7`
- Rows involved in duplicate aggregation: `14`
- Extra duplicate rows removed by aggregation: `7`
- Duplicated symbols: `ELMOD1`, `FGF13`, `NKAIN3`, `PALM2AKAP2`, `QSOX1`, `SNAP47`, `TMEM8B`
- Remaining missing expression values: `0`

## Missing-Value Policy

- No `fillna(0)` or global median imputation was performed.
- Any remaining missing values are intentionally preserved.
- If imputation is needed during modeling, it must be performed inside a training-only Pipeline after the train/test split.
