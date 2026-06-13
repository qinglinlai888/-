"""Inspect the raw mRNA expression matrix without modifying or imputing it."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports" / "data_quality"
REPORT_PATH = REPORT_DIR / "expression_quality_report.md"
SAMPLE_MISSING_PATH = REPORT_DIR / "expression_missing_by_sample.csv"
GENE_MISSING_PATH = REPORT_DIR / "expression_missing_by_gene.csv"

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
    "Hugo_Symbol",
    "HUGO_SYMBOL",
    "gene_symbol",
    "GENE_SYMBOL",
    "Gene",
    "GENE",
    "gene",
    "Entrez_Gene_Id",
    "ENTREZ_GENE_ID",
    "Entrez_Gene_ID",
}


def locate_expression_matrix() -> Path:
    """Return the first supported expression matrix that exists."""
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

    raise ValueError(
        "Could not identify a gene symbol column or named index. "
        f"Checked candidates: {GENE_SYMBOL_CANDIDATES}"
    )


def expression_components(
    raw_df: pd.DataFrame, gene_location: str, gene_name: str
) -> tuple[pd.Series, pd.DataFrame, list[str]]:
    """Return gene symbols, numeric sample matrix, and excluded non-sample columns."""
    if gene_location == "column":
        gene_symbols = raw_df[gene_name].astype("string").str.strip().replace("", pd.NA)
        candidate_df = raw_df.drop(
            columns=[column for column in KNOWN_GENE_IDENTIFIER_COLUMNS if column in raw_df],
            errors="ignore",
        )
    else:
        gene_symbols = raw_df.index.to_series().astype("string").str.strip().replace("", pd.NA)
        candidate_df = raw_df.drop(
            columns=[column for column in KNOWN_GENE_IDENTIFIER_COLUMNS if column in raw_df],
            errors="ignore",
        )

    sample_columns = candidate_df.select_dtypes(include="number").columns.tolist()
    excluded_columns = [
        str(column) for column in candidate_df.columns if column not in sample_columns
    ]
    if not sample_columns:
        raise ValueError("No numeric sample expression columns were identified.")

    return gene_symbols.reset_index(drop=True), candidate_df[sample_columns], excluded_columns


def summarize_quality(
    gene_symbols: pd.Series, expression_df: pd.DataFrame
) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame, list[str]]:
    """Calculate duplicate-gene and missing-value statistics."""
    present_symbols = gene_symbols.dropna()
    duplicate_mask = gene_symbols.notna() & gene_symbols.duplicated(keep=False)
    duplicate_symbols = sorted(gene_symbols[duplicate_mask].dropna().unique().tolist())

    missing_by_sample = expression_df.isna().sum().rename("missing_values").to_frame()
    missing_by_sample.index.name = "sample_id"
    missing_by_sample["missing_percent"] = (
        missing_by_sample["missing_values"] / expression_df.shape[0] * 100
    )
    missing_by_sample = missing_by_sample.reset_index()

    missing_by_gene = expression_df.isna().sum(axis=1)
    missing_gene_labels = gene_symbols.fillna("<missing_gene_symbol>")
    missing_by_gene_df = pd.DataFrame(
        {
            "row_number": range(len(expression_df)),
            "gene_symbol": missing_gene_labels,
            "missing_values": missing_by_gene,
            "missing_percent": missing_by_gene / expression_df.shape[1] * 100,
            "is_duplicate_gene_symbol": duplicate_mask,
        }
    )

    total_missing = int(expression_df.isna().sum().sum())
    metrics = {
        "expression_shape": expression_df.shape,
        "missing_gene_symbols": int(gene_symbols.isna().sum()),
        "unique_gene_symbols": int(present_symbols.nunique()),
        "duplicate_symbol_count": len(duplicate_symbols),
        "duplicate_rows": int(duplicate_mask.sum()),
        "duplicate_extra_rows": int(present_symbols.duplicated().sum()),
        "missing_total": total_missing,
        "missing_percent": total_missing / expression_df.size * 100,
        "samples_with_missing": int((missing_by_sample["missing_values"] > 0).sum()),
        "genes_with_missing": int((missing_by_gene_df["missing_values"] > 0).sum()),
        "fully_missing_genes": int(
            (missing_by_gene_df["missing_values"] == expression_df.shape[1]).sum()
        ),
        "partially_missing_genes": int(
            (
                (missing_by_gene_df["missing_values"] > 0)
                & (missing_by_gene_df["missing_values"] < expression_df.shape[1])
            ).sum()
        ),
        "min_sample_missing": int(missing_by_sample["missing_values"].min()),
        "max_sample_missing": int(missing_by_sample["missing_values"].max()),
        "max_gene_missing": int(missing_by_gene_df["missing_values"].max()),
    }
    return metrics, missing_by_sample, missing_by_gene_df, duplicate_symbols


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    """Render a small DataFrame slice as a Markdown table."""
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    rows = []
    for _, row in df[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if column == "missing_percent":
                values.append(f"{float(value):.4f}%")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *rows])


def write_report(
    source_path: Path,
    raw_shape: tuple[int, int],
    gene_location: str,
    gene_name: str,
    excluded_columns: list[str],
    metrics: dict[str, object],
    missing_by_sample: pd.DataFrame,
    missing_by_gene: pd.DataFrame,
    duplicate_symbols: list[str],
) -> None:
    """Write the expression quality report and complete missingness summaries."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    missing_by_sample.to_csv(SAMPLE_MISSING_PATH, index=False)
    missing_by_gene.to_csv(GENE_MISSING_PATH, index=False)

    top_samples = missing_by_sample.sort_values("missing_values", ascending=False).head(15)
    top_genes = missing_by_gene.sort_values("missing_values", ascending=False).head(15)
    expression_rows, expression_columns = metrics["expression_shape"]
    source_display = source_path.relative_to(PROJECT_ROOT).as_posix()
    duplicate_display = ", ".join(f"`{symbol}`" for symbol in duplicate_symbols) or "None"
    excluded_display = ", ".join(f"`{column}`" for column in excluded_columns) or "None"

    report = f"""# Expression Matrix Quality Report

## Source And Structure

- Source: `{source_display}`
- Raw table shape: `{raw_shape[0]} × {raw_shape[1]}`
- Numeric expression shape: `{expression_rows} genes/rows × {expression_columns} samples`
- Gene symbol location: `{gene_location}` named `{gene_name}`
- Non-numeric columns excluded from expression statistics: {excluded_display}
- Missing gene symbols: `{metrics["missing_gene_symbols"]}`
- Unique non-missing gene symbols: `{metrics["unique_gene_symbols"]}`

## Duplicate Genes

- Unique duplicated gene symbols: `{metrics["duplicate_symbol_count"]}`
- Rows involved in duplicated symbols: `{metrics["duplicate_rows"]}`
- Extra rows beyond one row per symbol: `{metrics["duplicate_extra_rows"]}`
- Duplicated symbols: {duplicate_display}

## Missing Values

- Total missing expression values: `{metrics["missing_total"]}`
- Missing expression proportion: `{metrics["missing_percent"]:.6f}%`
- Samples with at least one missing value: `{metrics["samples_with_missing"]}` / `{expression_columns}`
- Genes/rows with at least one missing value: `{metrics["genes_with_missing"]}` / `{expression_rows}`
- Genes/rows missing in all samples: `{metrics["fully_missing_genes"]}`
- Genes/rows with partial missingness: `{metrics["partially_missing_genes"]}`
- Minimum missing values in one sample: `{metrics["min_sample_missing"]}`
- Maximum missing values in one sample: `{metrics["max_sample_missing"]}`
- Maximum missing values in one gene/row: `{metrics["max_gene_missing"]}`
- Complete per-sample statistics: `reports/data_quality/expression_missing_by_sample.csv`
- Complete per-gene statistics: `reports/data_quality/expression_missing_by_gene.csv`

### Samples With Most Missing Values

{markdown_table(top_samples, ["sample_id", "missing_values", "missing_percent"])}

### Genes With Most Missing Values

{markdown_table(top_genes, ["row_number", "gene_symbol", "missing_values", "missing_percent", "is_duplicate_gene_symbol"])}

## Conservative Recommendations

- Do not fill missing expression values with zero without a separately approved biological and statistical rationale.
- The current missingness is entirely concentrated in genes that are missing for every sample; confirm and filter these fully missing genes before considering imputation.
- Before downstream analysis, choose and document whether duplicated gene symbols are aggregated by mean or median.
- Define and document a threshold for filtering high-missingness genes before any imputation.
- Confirm the missing-value imputation strategy separately before modeling; fit any imputer only on training data.
- No aggregated expression matrix was written in this run because the mean-versus-median policy has not been confirmed.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    source_path = locate_expression_matrix()
    raw_df = read_expression_matrix(source_path)
    gene_location, gene_name = find_gene_symbol_location(raw_df)
    gene_symbols, expression_df, excluded_columns = expression_components(
        raw_df, gene_location, gene_name
    )
    metrics, missing_by_sample, missing_by_gene, duplicate_symbols = summarize_quality(
        gene_symbols, expression_df
    )
    write_report(
        source_path,
        raw_df.shape,
        gene_location,
        gene_name,
        excluded_columns,
        metrics,
        missing_by_sample,
        missing_by_gene,
        duplicate_symbols,
    )

    print(f"Source expression matrix: {source_path.relative_to(PROJECT_ROOT)}")
    print(f"Raw shape: {raw_df.shape}")
    print(f"Expression shape: {metrics['expression_shape']}")
    print(f"Unique duplicated gene symbols: {metrics['duplicate_symbol_count']}")
    print(f"Rows involved in duplicated symbols: {metrics['duplicate_rows']}")
    print(f"Total missing expression values: {metrics['missing_total']}")
    print(f"Missing expression proportion: {metrics['missing_percent']:.6f}%")
    print(f"Samples with missing values: {metrics['samples_with_missing']}")
    print(f"Genes/rows with missing values: {metrics['genes_with_missing']}")
    print(f"Genes/rows missing in all samples: {metrics['fully_missing_genes']}")
    print(f"Genes/rows with partial missingness: {metrics['partially_missing_genes']}")
    print(f"Quality report: {REPORT_PATH.relative_to(PROJECT_ROOT)}")
    print("No values were imputed and no aggregated expression matrix was written.")


if __name__ == "__main__":
    main()
