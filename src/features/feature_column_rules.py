"""Column-name rules for selecting candidate features without outcome leakage."""

import re
from collections.abc import Iterable

import pandas as pd


EXACT_EXCLUDED_COLUMNS = {
    "PATIENT_ID",
    "SAMPLE_ID",
    "OS_STATUS",
    "OS_MONTHS",
    "DFS_STATUS",
    "DFS_MONTHS",
    "DSS_STATUS",
    "DSS_MONTHS",
    "PFS_STATUS",
    "PFS_MONTHS",
}

LEAKAGE_TOKENS = {
    "DAYS",
    "FOLLOWUP",
    "LABEL",
    "MONTHS",
    "RISK_GROUP",
    "SURVIVAL",
    "DEATH",
    "STATUS",
    "OUTCOME",
    "TARGET",
    "EVENT",
    "TIME",
}


def _normalized_column_name(column: object) -> str:
    normalized = re.sub(r"[^A-Z0-9]+", "_", str(column).strip().upper())
    return normalized.strip("_")


def leakage_reason(column: object) -> str | None:
    """Return the rule that marks a column as a possible leakage source."""
    normalized = _normalized_column_name(column)
    if normalized in EXACT_EXCLUDED_COLUMNS:
        return f"exact excluded column: {normalized}"

    if normalized.endswith("_PATIENT_ID") or normalized.endswith("_SAMPLE_ID"):
        return "identifier column"

    padded = f"_{normalized}_"
    for token in sorted(LEAKAGE_TOKENS):
        if f"_{token}_" in padded:
            return f"contains leakage token: {token}"
    return None


def find_suspected_leakage_columns(columns: Iterable[object]) -> dict[str, str]:
    """Return suspected leakage columns and the matching rule."""
    risks = {}
    for column in columns:
        reason = leakage_reason(column)
        if reason:
            risks[str(column)] = reason
    return risks


def validate_no_leakage_columns(feature_columns: Iterable[object]) -> None:
    """Raise ValueError when a proposed feature list contains leakage risks."""
    risks = find_suspected_leakage_columns(feature_columns)
    if risks:
        details = "; ".join(f"{column} ({reason})" for column, reason in risks.items())
        raise ValueError(f"Suspected leakage columns detected: {details}")


def get_candidate_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return columns that pass name-based leakage checks.

    The returned columns are only candidates. They still require explicit
    metadata review, dtype checks, and a documented feature definition.
    """
    risks = find_suspected_leakage_columns(df.columns)
    candidates = [str(column) for column in df.columns if str(column) not in risks]
    validate_no_leakage_columns(candidates)
    return candidates
