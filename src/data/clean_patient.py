"""Clean the patient-level clinical table and write a data quality report."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "patient_cleaned.csv"
REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality" / "patient_quality_report.md"

PATIENT_INPUT_CANDIDATES = (
    PROJECT_ROOT / "data" / "raw" / "data_clinical_patient.txt",
    PROJECT_ROOT / "data_clinical_patient.txt",
    PROJECT_ROOT / "data" / "raw" / "data_clinical_patient.tsv",
    PROJECT_ROOT / "data" / "raw" / "data_clinical_patient.csv",
)

KEY_FIELDS = (
    "PATIENT_ID",
    "OS_STATUS",
    "OS_MONTHS",
    "AGE",
    "SEX",
    "GENDER",
    "GRADE",
    "HISTOLOGY",
    "IDH_STATUS",
    "1P19Q_STATUS",
)


def locate_patient_table() -> Path:
    """Return the first supported patient table that exists."""
    for path in PATIENT_INPUT_CANDIDATES:
        if path.is_file():
            return path
    checked = "\n".join(f"- {path}" for path in PATIENT_INPUT_CANDIDATES)
    raise FileNotFoundError(f"Patient table not found. Checked:\n{checked}")


def read_patient_table(path: Path) -> pd.DataFrame:
    """Read a supported patient table without modifying the source file."""
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_csv(path, sep="\t", comment="#")


def normalize_patient_ids(patient_ids: pd.Series) -> pd.Series:
    """Normalize patient identifiers while preserving missing values."""
    normalized = patient_ids.astype("string").str.strip().str.upper()
    return normalized.replace({"": pd.NA, "NAN": pd.NA, "NONE": pd.NA})


def clean_patient_table(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Apply conservative patient-level cleaning and return audit metrics."""
    if "PATIENT_ID" not in raw_df.columns:
        raise KeyError("Required column PATIENT_ID is missing from the patient table.")

    cleaned_df = raw_df.copy()
    before_ids = cleaned_df["PATIENT_ID"].astype("string")

    string_columns = cleaned_df.select_dtypes(include=["object", "string"]).columns
    for column in string_columns:
        cleaned_df[column] = cleaned_df[column].astype("string").str.strip()
        cleaned_df[column] = cleaned_df[column].replace("", pd.NA)

    cleaned_df["PATIENT_ID"] = normalize_patient_ids(cleaned_df["PATIENT_ID"])

    missing_patient_ids = int(cleaned_df["PATIENT_ID"].isna().sum())
    duplicate_patients = int(cleaned_df["PATIENT_ID"].duplicated(keep=False).sum())
    invalid_patient_ids = int(
        (
            cleaned_df["PATIENT_ID"].notna()
            & ~cleaned_df["PATIENT_ID"].str.fullmatch(
                r"TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}", na=False
            )
        ).sum()
    )
    normalized_patient_ids = int(
        before_ids.fillna("<NA>").ne(cleaned_df["PATIENT_ID"].fillna("<NA>")).sum()
    )

    metrics = {
        "missing_patient_ids": missing_patient_ids,
        "duplicate_patients": duplicate_patients,
        "invalid_patient_ids": invalid_patient_ids,
        "normalized_patient_ids": normalized_patient_ids,
    }
    return cleaned_df, metrics


def key_field_quality(df: pd.DataFrame) -> list[dict[str, object]]:
    """Summarize presence and missingness for requested patient fields."""
    quality = []
    for field in KEY_FIELDS:
        if field in df.columns:
            missing = int(df[field].isna().sum())
            quality.append(
                {
                    "field": field,
                    "status": "present",
                    "missing": missing,
                    "missing_percent": missing / len(df) * 100 if len(df) else 0.0,
                }
            )
        else:
            quality.append(
                {
                    "field": field,
                    "status": "absent",
                    "missing": None,
                    "missing_percent": None,
                }
            )
    return quality


def write_quality_report(
    source_path: Path,
    before_shape: tuple[int, int],
    cleaned_df: pd.DataFrame,
    metrics: dict[str, int],
    field_quality: list[dict[str, object]],
) -> None:
    """Write a Markdown report describing the conservative cleaning run."""
    rows = []
    for item in field_quality:
        if item["status"] == "present":
            missing = str(item["missing"])
            missing_percent = f"{item['missing_percent']:.2f}%"
        else:
            missing = "N/A"
            missing_percent = "N/A"
        rows.append(
            f"| `{item['field']}` | {item['status']} | {missing} | {missing_percent} |"
        )

    source_display = source_path.relative_to(PROJECT_ROOT).as_posix()
    output_display = OUTPUT_PATH.relative_to(PROJECT_ROOT).as_posix()
    report = f"""# Patient Data Quality Report

## Run Summary

- Source: `{source_display}`
- Cleaned output: `{output_display}`
- Shape before cleaning: `{before_shape[0]} × {before_shape[1]}`
- Shape after cleaning: `{cleaned_df.shape[0]} × {cleaned_df.shape[1]}`
- Patient IDs changed by normalization: `{metrics["normalized_patient_ids"]}`
- Missing patient IDs: `{metrics["missing_patient_ids"]}`
- Duplicate patient rows after normalization: `{metrics["duplicate_patients"]}`
- Invalid TCGA patient IDs after normalization: `{metrics["invalid_patient_ids"]}`

## Cleaning Rules

- The original patient table was read without modification.
- String values were stripped; whitespace-only strings were converted to missing values.
- `PATIENT_ID` values were stripped and converted to uppercase.
- No patient rows were removed.
- No clinical missing values were imputed because the formal research endpoint is not yet fixed.

## Requested Key Fields

| Field | Status | Missing | Missing rate |
| --- | --- | ---: | ---: |
{chr(10).join(rows)}

## Interpretation

- `SEX` is present; `GENDER` is absent, so `SEX` remains the available demographic field.
- Fields marked absent are not created or inferred from other columns.
- Patient-level output is safe for merging only while missing, duplicate, and invalid `PATIENT_ID` counts remain zero.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    source_path = locate_patient_table()
    raw_df = read_patient_table(source_path)
    cleaned_df, metrics = clean_patient_table(raw_df)
    field_quality = key_field_quality(cleaned_df)

    if metrics["missing_patient_ids"] or metrics["duplicate_patients"] or metrics["invalid_patient_ids"]:
        raise ValueError(
            "Patient ID quality checks failed; cleaned patient data was not written. "
            f"Metrics: {metrics}"
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(OUTPUT_PATH, index=False)
    write_quality_report(source_path, raw_df.shape, cleaned_df, metrics, field_quality)

    print(f"Source patient table: {source_path.relative_to(PROJECT_ROOT)}")
    print(f"Shape before cleaning: {raw_df.shape}")
    print(f"Shape after cleaning: {cleaned_df.shape}")
    print(f"Duplicate patients after normalization: {metrics['duplicate_patients']}")
    print("Requested key field quality:")
    for item in field_quality:
        if item["status"] == "present":
            print(
                f"  {item['field']}: present, missing={item['missing']} "
                f"({item['missing_percent']:.2f}%)"
            )
        else:
            print(f"  {item['field']}: absent")
    print(f"Cleaned patient table: {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Quality report: {REPORT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
