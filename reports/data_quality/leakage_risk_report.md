# Feature Leakage Risk Report

## Search Scope

The repository was searched for fixed-position `iloc` column slices and code that creates modeling feature matrices. This review does not train a model or modify any Notebook.

## Confirmed Risk

| Location | Pattern | Risk |
| --- | --- | --- |
| `01_Data_Prep_and_Merging.ipynb:198` | `df_genes_only = df_super.iloc[:, 6:]` | High: the merged table has 56 clinical/sample metadata columns, so slicing from column 6 includes `GRADE`, outcome fields, and other metadata before converting the result to `X`. |
| `01_Data_Prep_and_Merging.ipynb:184` | Markdown recommends `df.iloc[:, 6:]` | High: the explanation documents the unsafe positional rule and could lead future work to repeat it. |

## Other Positional Slices Reviewed

| Location | Pattern | Assessment |
| --- | --- | --- |
| `01_Data_Prep_and_Merging.ipynb:66` | `df.iloc[0:10, 0:5]` | Low risk: used only to preview a small table subset, not to define model features. |
| `data_analysis.py:16` | `df.iloc[0:10, 0:5]` | Low risk: used only to print a preview, not to define model features. |

No other fixed-position feature-selection slice was found in the current Python scripts or Notebooks.

## Added Safeguard

`src/features/feature_column_rules.py` provides:

- `get_candidate_feature_columns(df)` to remove columns whose names match known identifier or outcome-related leakage rules.
- `validate_no_leakage_columns(feature_columns)` to raise `ValueError` if a proposed feature list contains suspected leakage columns.
- `find_suspected_leakage_columns(columns)` to return the risk reasons for review.

The rules explicitly exclude patient/sample identifiers; OS, DFS, DSS, and PFS status/month fields; plus names containing `label`, `risk_group`, `survival`, `death`, `status`, `outcome`, `target`, `event`, `time`, `months`, `days`, or `followup`.

## Remaining Limitation

Name-based rules cannot prove that candidate columns are biologically appropriate or leakage-free. Candidate features still require explicit metadata review. The unsafe Notebook cell remains unchanged in this task and must not be executed for feature extraction.
