"""Inspect candidate label fields without creating labels or training models."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MERGED_PATH = PROJECT_ROOT / "data" / "processed" / "data_multiomics_merged.csv"
PATIENT_PATH = PROJECT_ROOT / "data" / "processed" / "patient_cleaned.csv"
SAMPLE_PATH = PROJECT_ROOT / "data_clinical_sample.txt"
EXPRESSION_PATH = PROJECT_ROOT / "data" / "processed" / "expression_cleaned.csv"
REPORT_PATH = (
    PROJECT_ROOT / "reports" / "feature_engineering" / "label_candidate_field_report.md"
)

CANDIDATE_FIELDS = (
    "OS_STATUS",
    "OS_MONTHS",
    "DFS_STATUS",
    "DFS_MONTHS",
    "GRADE",
    "WHO_GRADE",
    "HISTOLOGY",
    "IDH_STATUS",
    "1P19Q_STATUS",
    "AGE",
    "SEX",
    "GENDER",
)

EXPLICIT_ID_FIELDS = {"PATIENT_ID", "SAMPLE_ID", "OTHER_PATIENT_ID"}
CONTINUOUS_VALUE_COUNT_LIMIT = 30


def require_input(path: Path, instruction: str) -> None:
    """Raise a clear error when a required generated input is absent."""
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}. {instruction}")


def read_headers() -> tuple[list[str], list[str], list[str]]:
    """Read source fields used to classify merged-table columns."""
    require_input(PATIENT_PATH, "Run: python src/data/clean_patient.py")
    require_input(EXPRESSION_PATH, "Run: python src/data/clean_expression.py")

    patient_columns = pd.read_csv(PATIENT_PATH, nrows=0).columns.tolist()
    sample_columns = pd.read_csv(
        SAMPLE_PATH, sep="\t", comment="#", nrows=0
    ).columns.tolist()
    expression_genes = (
        pd.read_csv(EXPRESSION_PATH, usecols=["Hugo_Symbol"])["Hugo_Symbol"]
        .dropna()
        .astype(str)
        .tolist()
    )
    return patient_columns, sample_columns, expression_genes


def classify_columns(
    merged_columns: list[str],
    patient_columns: list[str],
    sample_columns: list[str],
    expression_genes: list[str],
) -> dict[str, list[str]]:
    """Classify merged columns by source names rather than column position."""
    merged_set = set(merged_columns)
    expression_set = set(expression_genes)

    id_fields = [
        column
        for column in merged_columns
        if column in EXPLICIT_ID_FIELDS
        or column.endswith("_PATIENT_ID")
        or column.endswith("_SAMPLE_ID")
    ]
    id_set = set(id_fields)

    sample_fields = [
        column
        for column in sample_columns
        if column in merged_set and column not in id_set
    ]
    sample_set = set(sample_fields)

    clinical_fields = [
        column
        for column in patient_columns
        if column in merged_set and column not in id_set and column not in sample_set
    ]
    classified_metadata = id_set | sample_set | set(clinical_fields)

    expression_fields = [
        column for column in merged_columns if column in expression_set
    ]
    unclassified_fields = [
        column
        for column in merged_columns
        if column not in classified_metadata and column not in expression_set
    ]
    categories = {
        "id_fields": id_fields,
        "clinical_fields": clinical_fields,
        "sample_fields": sample_fields,
        "expression_fields": expression_fields,
        "unclassified_fields": unclassified_fields,
    }
    classified_columns = [
        column for fields in categories.values() for column in fields
    ]
    if len(classified_columns) != len(merged_columns):
        raise ValueError(
            "Column classification did not cover the merged table exactly once."
        )
    if len(set(classified_columns)) != len(classified_columns):
        raise ValueError("Column classification assigned at least one column twice.")
    return categories


def summarize_field(series: pd.Series) -> dict[str, object]:
    """Return missingness, uniqueness, counts, and numeric summaries."""
    missing_count = int(series.isna().sum())
    non_missing = series.dropna()
    unique_count = int(non_missing.nunique())
    is_numeric = pd.api.types.is_numeric_dtype(series)

    summary: dict[str, object] = {
        "dtype": str(series.dtype),
        "missing_count": missing_count,
        "missing_percent": missing_count / len(series) * 100 if len(series) else 0.0,
        "unique_count": unique_count,
        "is_numeric": is_numeric,
        "value_counts": non_missing.value_counts(dropna=False),
    }
    if is_numeric and not non_missing.empty:
        summary["minimum"] = float(non_missing.min())
        summary["median"] = float(non_missing.median())
        summary["maximum"] = float(non_missing.max())
    return summary


def markdown_field_list(title: str, fields: list[str]) -> str:
    """Render a named field category."""
    field_text = ", ".join(f"`{field}`" for field in fields) if fields else "None"
    return f"### {title}\n\n- Count: `{len(fields)}`\n- Fields: {field_text}\n"


def markdown_value_counts(summary: dict[str, object]) -> str:
    """Render categorical counts fully and continuous counts conservatively."""
    counts = summary["value_counts"]
    unique_count = int(summary["unique_count"])
    is_numeric = bool(summary["is_numeric"])

    if is_numeric and unique_count > CONTINUOUS_VALUE_COUNT_LIMIT:
        counts = counts.head(10)
        note = (
            f"Continuous/high-cardinality numeric field; showing the 10 most frequent "
            f"values from {unique_count} unique non-missing values."
        )
    else:
        note = "Complete non-missing value counts."

    rows = ["| Value | Count |", "| --- | ---: |"]
    for value, count in counts.items():
        rows.append(f"| `{value}` | {int(count)} |")
    if counts.empty:
        rows.append("| No non-missing values | 0 |")
    return f"{note}\n\n" + "\n".join(rows)


def markdown_candidate_section(field: str, summary: dict[str, object]) -> str:
    """Render one available candidate field summary."""
    numeric_summary = ""
    if summary["is_numeric"] and "minimum" in summary:
        numeric_summary = (
            f"- Numeric min / median / max: `{summary['minimum']}` / "
            f"`{summary['median']}` / `{summary['maximum']}`\n"
        )

    return f"""### `{field}`

- dtype: `{summary["dtype"]}`
- Missing: `{summary["missing_count"]}` / `{summary["missing_percent"]:.2f}%`
- Unique non-missing values: `{summary["unique_count"]}`
{numeric_summary}
{markdown_value_counts(summary)}
"""


def write_report(
    merged_shape: tuple[int, int],
    categories: dict[str, list[str]],
    available_fields: list[str],
    missing_fields: list[str],
    summaries: dict[str, dict[str, object]],
) -> None:
    """Write the label-candidate inspection report."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    available_text = ", ".join(f"`{field}`" for field in available_fields) or "None"
    missing_text = ", ".join(f"`{field}`" for field in missing_fields) or "None"
    candidate_sections = "\n\n".join(
        markdown_candidate_section(field, summaries[field]) for field in available_fields
    )

    report = f"""# Label Candidate Field Report

## Dataset Structure

- Source: `data/processed/data_multiomics_merged.csv`
- Shape: `{merged_shape[0]} × {merged_shape[1]}`
- Non-expression fields: `{len(categories["id_fields"]) + len(categories["clinical_fields"]) + len(categories["sample_fields"]) + len(categories["unclassified_fields"])}`
- Expression gene fields: `{len(categories["expression_fields"])}`

Column categories were derived from the source patient, sample, and cleaned expression headers. No positional slicing was used.

## Non-Expression Fields

{markdown_field_list("ID Fields", categories["id_fields"])}
{markdown_field_list("Clinical Fields", categories["clinical_fields"])}
{markdown_field_list("Sample Fields", categories["sample_fields"])}
{markdown_field_list("Unclassified Non-Expression Fields", categories["unclassified_fields"])}

## Candidate Label Field Availability

- Detected candidate fields: {available_text}
- Missing candidate fields: {missing_text}

## Available Field Summaries

{candidate_sections}

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
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    require_input(MERGED_PATH, "Run: python merge_omics.py")
    merged_df = pd.read_csv(MERGED_PATH, low_memory=False)
    patient_columns, sample_columns, expression_genes = read_headers()
    categories = classify_columns(
        merged_df.columns.tolist(),
        patient_columns,
        sample_columns,
        expression_genes,
    )

    available_fields = [field for field in CANDIDATE_FIELDS if field in merged_df.columns]
    missing_fields = [field for field in CANDIDATE_FIELDS if field not in merged_df.columns]
    summaries = {
        field: summarize_field(merged_df[field]) for field in available_fields
    }
    write_report(
        merged_df.shape,
        categories,
        available_fields,
        missing_fields,
        summaries,
    )

    non_expression_count = sum(
        len(categories[name])
        for name in (
            "id_fields",
            "clinical_fields",
            "sample_fields",
            "unclassified_fields",
        )
    )
    print(f"Merged dataset shape: {merged_df.shape}")
    print(f"ID fields: {len(categories['id_fields'])}")
    print(f"Clinical fields: {len(categories['clinical_fields'])}")
    print(f"Sample fields: {len(categories['sample_fields'])}")
    print(f"Non-expression fields: {non_expression_count}")
    print(f"Expression gene fields: {len(categories['expression_fields'])}")
    print(f"Detected candidate fields: {available_fields}")
    print(f"Missing candidate fields: {missing_fields}")
    print(f"Report: {REPORT_PATH.relative_to(PROJECT_ROOT)}")
    print("No label was created and no model was trained.")


if __name__ == "__main__":
    main()
