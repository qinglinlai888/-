# Patient Data Quality Report

## Run Summary

- Source: `data_clinical_patient.txt`
- Cleaned output: `data/processed/patient_cleaned.csv`
- Shape before cleaning: `514 × 38`
- Shape after cleaning: `514 × 38`
- Patient IDs changed by normalization: `0`
- Missing patient IDs: `0`
- Duplicate patient rows after normalization: `0`
- Invalid TCGA patient IDs after normalization: `0`

## Cleaning Rules

- The original patient table was read without modification.
- String values were stripped; whitespace-only strings were converted to missing values.
- `PATIENT_ID` values were stripped and converted to uppercase.
- No patient rows were removed.
- No clinical missing values were imputed because the formal research endpoint is not yet fixed.

## Requested Key Fields

| Field | Status | Missing | Missing rate |
| --- | --- | ---: | ---: |
| `PATIENT_ID` | present | 0 | 0.00% |
| `OS_STATUS` | present | 1 | 0.19% |
| `OS_MONTHS` | present | 1 | 0.19% |
| `AGE` | present | 1 | 0.19% |
| `SEX` | present | 1 | 0.19% |
| `GENDER` | absent | N/A | N/A |
| `GRADE` | absent | N/A | N/A |
| `HISTOLOGY` | absent | N/A | N/A |
| `IDH_STATUS` | absent | N/A | N/A |
| `1P19Q_STATUS` | absent | N/A | N/A |

## Interpretation

- `SEX` is present; `GENDER` is absent, so `SEX` remains the available demographic field.
- Fields marked absent are not created or inferred from other columns.
- Patient-level output is safe for merging only while missing, duplicate, and invalid `PATIENT_ID` counts remain zero.
