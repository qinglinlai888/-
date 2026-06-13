# Label Candidate Field Report

## Dataset Structure

- Source: `data/processed/data_multiomics_merged.csv`
- Shape: `514 × 20201`
- Non-expression fields: `56`
- Expression gene fields: `20145`

Column categories were derived from the source patient, sample, and cleaned expression headers. No positional slicing was used.

## Non-Expression Fields

### ID Fields

- Count: `3`
- Fields: `PATIENT_ID`, `SAMPLE_ID`, `OTHER_PATIENT_ID`

### Clinical Fields

- Count: `36`
- Fields: `SUBTYPE`, `CANCER_TYPE_ACRONYM`, `AGE`, `SEX`, `AJCC_PATHOLOGIC_TUMOR_STAGE`, `AJCC_STAGING_EDITION`, `DAYS_LAST_FOLLOWUP`, `DAYS_TO_BIRTH`, `DAYS_TO_INITIAL_PATHOLOGIC_DIAGNOSIS`, `ETHNICITY`, `FORM_COMPLETION_DATE`, `HISTORY_NEOADJUVANT_TRTYN`, `ICD_10`, `ICD_O_3_HISTOLOGY`, `ICD_O_3_SITE`, `INFORMED_CONSENT_VERIFIED`, `NEW_TUMOR_EVENT_AFTER_INITIAL_TREATMENT`, `PATH_M_STAGE`, `PATH_N_STAGE`, `PATH_T_STAGE`, `PERSON_NEOPLASM_CANCER_STATUS`, `PRIMARY_LYMPH_NODE_PRESENTATION_ASSESSMENT`, `PRIOR_DX`, `RACE`, `RADIATION_THERAPY`, `WEIGHT`, `IN_PANCANPATHWAYS_FREEZE`, `OS_STATUS`, `OS_MONTHS`, `DSS_STATUS`, `DSS_MONTHS`, `DFS_STATUS`, `DFS_MONTHS`, `PFS_STATUS`, `PFS_MONTHS`, `GENETIC_ANCESTRY_LABEL`

### Sample Fields

- Count: `17`
- Fields: `ONCOTREE_CODE`, `CANCER_TYPE`, `CANCER_TYPE_DETAILED`, `TUMOR_TYPE`, `GRADE`, `TISSUE_PROSPECTIVE_COLLECTION_INDICATOR`, `TISSUE_RETROSPECTIVE_COLLECTION_INDICATOR`, `TISSUE_SOURCE_SITE_CODE`, `TUMOR_TISSUE_SITE`, `ANEUPLOIDY_SCORE`, `SAMPLE_TYPE`, `MSI_SCORE_MANTIS`, `MSI_SENSOR_SCORE`, `SOMATIC_STATUS`, `TMB_NONSYNONYMOUS`, `TISSUE_SOURCE_SITE`, `TBL_SCORE`

### Unclassified Non-Expression Fields

- Count: `0`
- Fields: None


## Candidate Label Field Availability

- Detected candidate fields: `OS_STATUS`, `OS_MONTHS`, `DFS_STATUS`, `DFS_MONTHS`, `GRADE`, `AGE`, `SEX`
- Missing candidate fields: `WHO_GRADE`, `HISTOLOGY`, `IDH_STATUS`, `1P19Q_STATUS`, `GENDER`

## Available Field Summaries

### `OS_STATUS`

- dtype: `str`
- Missing: `1` / `0.19%`
- Unique non-missing values: `2`

Complete non-missing value counts.

| Value | Count |
| --- | ---: |
| `0:LIVING` | 388 |
| `1:DECEASED` | 125 |


### `OS_MONTHS`

- dtype: `float64`
- Missing: `1` / `0.19%`
- Unique non-missing values: `432`
- Numeric min / median / max: `0.0` / `22.25729033` / `211.1648092`

Continuous/high-cardinality numeric field; showing the 10 most frequent values from 432 unique non-missing values.

| Value | Count |
| --- | ---: |
| `0.098629056` | 9 |
| `0.230134464` | 7 |
| `6.378012296` | 3 |
| `14.39984219` | 3 |
| `16.1751652` | 3 |
| `18.60801526` | 3 |
| `7.956077194` | 3 |
| `29.85172765` | 3 |
| `36.82151429` | 3 |
| `0.131505408` | 3 |


### `DFS_STATUS`

- dtype: `str`
- Missing: `381` / `74.12%`
- Unique non-missing values: `2`

Complete non-missing value counts.

| Value | Count |
| --- | ---: |
| `0:DiseaseFree` | 113 |
| `1:Recurred/Progressed` | 20 |


### `DFS_MONTHS`

- dtype: `float64`
- Missing: `382` / `74.32%`
- Unique non-missing values: `125`
- Numeric min / median / max: `0.0` / `19.66005852` / `172.76523`

Continuous/high-cardinality numeric field; showing the 10 most frequent values from 125 unique non-missing values.

| Value | Count |
| --- | ---: |
| `17.88473551` | 2 |
| `0.230134464` | 2 |
| `0.098629056` | 2 |
| `6.378012296` | 2 |
| `23.17782819` | 2 |
| `14.95874018` | 2 |
| `14.5313476` | 2 |
| `40.17490219` | 1 |
| `122.7274222` | 1 |
| `81.96074564` | 1 |


### `GRADE`

- dtype: `str`
- Missing: `2` / `0.39%`
- Unique non-missing values: `2`

Complete non-missing value counts.

| Value | Count |
| --- | ---: |
| `G3` | 264 |
| `G2` | 248 |


### `AGE`

- dtype: `float64`
- Missing: `1` / `0.19%`
- Unique non-missing values: `60`
- Numeric min / median / max: `14.0` / `41.0` / `87.0`

Continuous/high-cardinality numeric field; showing the 10 most frequent values from 60 unique non-missing values.

| Value | Count |
| --- | ---: |
| `38.0` | 21 |
| `30.0` | 19 |
| `33.0` | 18 |
| `31.0` | 17 |
| `32.0` | 15 |
| `34.0` | 15 |
| `29.0` | 15 |
| `35.0` | 15 |
| `37.0` | 14 |
| `39.0` | 14 |


### `SEX`

- dtype: `str`
- Missing: `1` / `0.19%`
- Unique non-missing values: `2`

Complete non-missing value counts.

| Value | Count |
| --- | ---: |
| `Male` | 285 |
| `Female` | 228 |


## Interpretation

### Fields Worth Further Endpoint Consideration

- `OS_STATUS` together with `OS_MONTHS` can define an overall-survival endpoint, subject to a documented censoring policy.
- `DFS_STATUS` together with `DFS_MONTHS` can define a disease-free-survival endpoint, but its missingness and clinical meaning must be reviewed before selection.
- `GRADE` can be considered only as an ordinal pathology classification target; it is not interchangeable with progression, recurrence, or malignant transformation.
- The merged table also contains `PFS_STATUS` and `PFS_MONTHS`, which are not in the requested candidate list but remain important for the planned two-year PFS endpoint review.

No final label is created by this inspection.

### Covariates Or Descriptive Features

- `AGE` and `SEX` are candidate demographic covariates, not outcome labels.
- `GRADE` may be a covariate only when it is not selected as the prediction target and when its timing is compatible with the intended prediction setting.
- Exact fields `HISTOLOGY`, `IDH_STATUS`, and `1P19Q_STATUS` are absent. Existing related fields such as `ICD_O_3_HISTOLOGY` and `SUBTYPE` require separate semantic review before use.
- Missing molecular-status fields must not be inferred from gene expression.

### Leakage Exclusions

- Any selected target field and its paired time/status field must be excluded from ordinary features.
- `OS_STATUS`, `OS_MONTHS`, `DFS_STATUS`, and `DFS_MONTHS` must be excluded from ordinary feature matrices.
- `PFS_STATUS`, `PFS_MONTHS`, DSS fields, patient/sample IDs, follow-up durations, event fields, and outcome/status/time-derived columns must also be excluded.
- Use `src/features/feature_column_rules.py` for name-based screening, followed by explicit metadata review.

## Next Step

Choose and document one formal endpoint before label construction. For the roadmap's two-year PFS direction, separately audit `PFS_STATUS` and `PFS_MONTHS`, define censoring and inclusion rules, and verify class counts without creating a model.
