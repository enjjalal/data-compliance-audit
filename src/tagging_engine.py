import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd


PII_COLUMN_NAME_PATTERNS: Dict[str, str] = {
    "email": r"\bemail\b|e[-_]?mail",
    "phone": r"\bphone\b|contact[-_]?number|mobile",
    "ip": r"ip([-_]?address)?|^ip$",
    "dob": r"date[-_]?of[-_]?birth|\bdob\b|birth[_-]?date",
    "name": r"\bname\b|full[-_]?name|first[_-]?name|last[_-]?name",
    "national_id": r"\b(ssn|nin|passport|national[_-]?id|aadhar|aadhaar)\b",
}


PII_VALUE_REGEXES: Dict[str, re.Pattern] = {
    "email": re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"),
    "phone": re.compile(r"^(\+?\d[\d\s().-]{7,})$"),
    "ip": re.compile(r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"),
    "dob": re.compile(r"^(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})$"),
    "national_id": re.compile(r"^(?:\d{3}-?\d{2}-?\d{4})$"),  # simple SSN-like
}


@dataclass
class ColumnPIIResult:
    table: str
    column: str
    detected_tags: List[str]
    detection_reason: str


def detect_by_name(column_name: str) -> Optional[str]:
    lower = column_name.lower()
    for tag, pattern in PII_COLUMN_NAME_PATTERNS.items():
        if re.search(pattern, lower):
            return tag
    return None


def detect_by_values(series: pd.Series) -> Optional[str]:
    sample = series.dropna().astype(str).head(50)
    if sample.empty:
        return None
    # try each value regex; require at least 3 matches in sample to be confident
    for tag, pattern in PII_VALUE_REGEXES.items():
        matches = sum(1 for v in sample if pattern.match(v))
        if matches >= 3:
            return tag
    return None


def scan_dataframe(df: pd.DataFrame, table_name: str) -> List[ColumnPIIResult]:
    results: List[ColumnPIIResult] = []
    for col in df.columns:
        tags: List[str] = []
        reason_parts: List[str] = []

        name_tag = detect_by_name(col)
        if name_tag:
            tags.append(name_tag)
            reason_parts.append(f"name:{name_tag}")

        value_tag = detect_by_values(df[col])
        if value_tag and value_tag not in tags:
            tags.append(value_tag)
            reason_parts.append(f"value:{value_tag}")

        # heuristic: names typically human readable strings with spaces
        if not tags and df[col].dtype == object:
            sampled = df[col].dropna().astype(str).head(20)
            if not sampled.empty and sum(1 for v in sampled if " " in v) >= 5:
                tags.append("name")
                reason_parts.append("heuristic:name_with_spaces")

        if tags:
            results.append(
                ColumnPIIResult(
                    table=table_name,
                    column=col,
                    detected_tags=sorted(tags),
                    detection_reason=",".join(reason_parts) or "n/a",
                )
            )
    return results


def results_to_dataframe(results: List[ColumnPIIResult]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "table": r.table,
                "column": r.column,
                "pii_tags": ",".join(r.detected_tags),
                "reason": r.detection_reason,
            }
            for r in results
        ]
    )


