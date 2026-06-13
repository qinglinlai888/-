"""Clean the raw mRNA expression matrix for safe downstream merging."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "expression_cleaned.csv"
REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality" / "expression_cleaning_report.md"

EXPRESSION_INPUT_CANDIDATES = (
    PROJECT_ROOT / "data" / "raw" / "data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt",
    PROJECT_ROOT / "data_mrna_seq_v2_rsem_zscores_ref_all_samples.txt",
    PROJECT_ROOT / "data" / "raw" / "data_mrna_seq_v2_rsem_zscores_ref_all_samples.tsv",
    PROJECT_ROOT / "data" / "raw" / "data_mrna_seq_v2_rsem_zscores_ref_all_samples.csv",
)

GENE_SYMBOL_CANDIDATES = (
    "Hugo_Symbol",
    "HUGO_SYMBOL",
    "gene_symbol",
    "GENE_SYMBOL",
    "Gene",
    "GENE",
    "gene",
)

KNOWN_GENE_IDENTIFIER_COLUMNS = {
    *GENE_SYMBOL_CANDIDATES,
    "Entrez_Gene_Id",
    "ENTREZ_GENE_ID",
    "Entrez_Gene_ID",
}


def locate_expression_matrix() -> Path:
    """Return the first supported raw expression matrix that exists."""
    for path in EXPRESSION_INPUT_CANDIDATES:
        if path.is_file():
            return path
    checked = "\n".join(f"- {path}" for path in EXPRESSION_INPUT_CANDIDATES)
    raise FileNotFoundError(f"Expression matrix not found. Checked:\n{checked}")


def read_expression_matrix(path: Path) -> pd.DataFrame:
    """Read a supported expression matrix without modifying the source."""
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_csv(path, sep="\t", comment="#")


def find_gene_symbol_location(df: pd.DataFrame) -> tuple[str, str]:
    """Return whether gene symbols are stored in a column or named index."""
    for column in GENE_SYMBOL_CANDIDATES:
        if column in df.columns:
            return "column", column
    if df.index.name in GENE_SYMBOL_CANDIDATES:
        return "index", str(df.index.name)
    raise ValueError("Could not identify a gene symbol column or named index.")


def expression_components(
    raw_df: pd.DataFrame, gene_location: str, gene_name: str
) -> tuple[pd.Series, pd.DataFrame]:
    """Return normalized gene symbols and numeric sample expression values."""
    if gene_location == "column":
        gene_symbols = raw_df[gene_name]
    else:
        gene_symbols = raw_df.index.to_series()

    gene_symbols = gene_symbols.astype("string").str.strip().replace("", pd.NA)
    candidate_df = raw_df.drop(
        columns=[
            column for column in KNOWN_GENE_IDENTIFIER_COLUMNS if column in raw_df.columns
        ],
        errors="ignore",
    )
    sample_columns = candidate_df.select_dtypes(include="number").columns.tolist()
    if not sample_columns:
        raise ValueError("No numeric sample expression columns were identified.")

    return gene_symbols.reset_index(drop=True), candidate_df[sample_columns].reset_index(
        drop=True
    )


def clean_expression_matrix(
    gene_symbols: pd.Series, expression_df: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, object], list[str]]:
    """Filter fully missing genes and aggregate duplicate symbols by mean."""
    fully_missing_mask = expression_df.isna().all(axis=1)
    filtered_symbols = gene_symbols.loc[~fully_missing_mask].reset_index(drop=True)
    filtered_expression = expression_df.loc[~fully_missing_mask].reset_index(drop=True)

    missing_symbol_mask = filtered_symbols.isna()
    named_symbols = filtered_symbols.loc[~missing_symbol_mask].reset_index(drop=True)
    named_expression = filtered_expression.loc[~missing_symbol_mask].reset_index(drop=True)

    duplicate_mask = named_symbols.duplicated(keep=False)
    duplicate_symbols = sorted(named_symbols.loc[duplicate_mask].unique().tolist())

    expression_with_symbols = named_expression.copy()
    expression_with_symbols.insert(0, "Hugo_Symbol", named_symbols)
    cleaned_df = (
        expression_with_symbols.groupby("Hugo_Symbol", sort=False, as_index=False)
        .mean(numeric_only=True)
    )

    remaining_missing = int(cleaned_df.drop(columns=["Hugo_Symbol"]).isna().sum().sum())
    metrics = {
        "expression_shape_before": expression_df.shape,
        "fully_missing_rows_removed": int(fully_missing_mask.sum()),
        "missing_symbol_rows_before": int(gene_symbols.isna().sum()),
        "missing_symbol_rows_removed_after_full_filter": int(missing_symbol_mask.sum()),
        "duplicate_symbol_count": len(duplicate_symbols),
        "duplicate_rows_aggregated": int(duplicate_mask.sum()),
        "duplicate_extra_rows_removed": int(named_symbols.duplicated().sum()),
        "expression_shape_after": (cleaned_df.shape[0], cleaned_df.shape[1] - 1),
        "output_shape": cleaned_df.shape,
        "remaining_missing_values": remaining_missing,
    }
    return cleaned_df, metrics, duplicate_symbols


def write_report(
    source_path: Path,
    raw_shape: tuple[int, int],
    gene_location: str,
    gene_name: str,
    metrics: dict[str, object],
    duplicate_symbols: list[str],
) -> None:
    """Write a Markdown audit report for expression cleaning."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    source_display = source_path.relative_to(PROJECT_ROOT).as_posix()
    output_display = OUTPUT_PATH.relative_to(PROJECT_ROOT).as_posix()
    duplicate_display = ", ".join(f"`{symbol}`" for symbol in duplicate_symbols)
    before_rows, before_samples = metrics["expression_shape_before"]
    after_rows, after_samples = metrics["expression_shape_after"]
    output_rows, output_columns = metrics["output_shape"]

    report = f"""# Expression Cleaning Report

## Inputs And Outputs

- Source: `{source_display}`
- Raw table shape: `{raw_shape[0]} × {raw_shape[1]}`
- Numeric expression shape before cleaning: `{before_rows} genes/rows × {before_samples} samples`
- Gene symbol location: `{gene_location}` named `{gene_name}`
- Cleaned output: `{output_display}`
- Numeric expression shape after cleaning: `{after_rows} genes × {after_samples} samples`
- Saved table shape including `Hugo_Symbol`: `{output_rows} × {output_columns}`

## Cleaning Rules And Results

- Fully missing gene rows removed: `{metrics["fully_missing_rows_removed"]}`
- Missing gene-symbol rows in raw data: `{metrics["missing_symbol_rows_before"]}`
- Missing gene-symbol rows removed after fully missing filtering: `{metrics["missing_symbol_rows_removed_after_full_filter"]}`
- Duplicate gene symbols aggregated by: `mean`
- Unique duplicated gene symbols aggregated: `{metrics["duplicate_symbol_count"]}`
- Rows involved in duplicate aggregation: `{metrics["duplicate_rows_aggregated"]}`
- Extra duplicate rows removed by aggregation: `{metrics["duplicate_extra_rows_removed"]}`
- Duplicated symbols: {duplicate_display}
- Remaining missing expression values: `{metrics["remaining_missing_values"]}`

## Missing-Value Policy

- No `fillna(0)` or global median imputation was performed.
- Any remaining missing values are intentionally preserved.
- If imputation is needed during modeling, it must be performed inside a training-only Pipeline after the train/test split.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    source_path = locate_expression_matrix()
    raw_df = read_expression_matrix(source_path)
    gene_location, gene_name = find_gene_symbol_location(raw_df)
    gene_symbols, expression_df = expression_components(raw_df, gene_location, gene_name)
    cleaned_df, metrics, duplicate_symbols = clean_expression_matrix(
        gene_symbols, expression_df
    )

    if cleaned_df["Hugo_Symbol"].isna().any() or cleaned_df["Hugo_Symbol"].duplicated().any():
        raise ValueError("Cleaned expression matrix still has missing or duplicate gene symbols.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(OUTPUT_PATH, index=False)
    write_report(
        source_path,
        raw_df.shape,
        gene_location,
        gene_name,
        metrics,
        duplicate_symbols,
    )

    print(f"Source expression matrix: {source_path.relative_to(PROJECT_ROOT)}")
    print(f"Expression shape before cleaning: {metrics['expression_shape_before']}")
    print(f"Expression shape after cleaning: {metrics['expression_shape_after']}")
    print(f"Fully missing gene rows removed: {metrics['fully_missing_rows_removed']}")
    print(
        "Missing gene-symbol rows removed after fully missing filtering: "
        f"{metrics['missing_symbol_rows_removed_after_full_filter']}"
    )
    print(f"Duplicate gene symbols aggregated by mean: {metrics['duplicate_symbol_count']}")
    print(f"Genes after aggregation: {metrics['expression_shape_after'][0]}")
    print(f"Remaining missing expression values: {metrics['remaining_missing_values']}")
    print(f"Cleaned expression matrix: {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Cleaning report: {REPORT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
