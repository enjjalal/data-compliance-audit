import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import yaml


@dataclass
class Violation:
    policy_id: str
    table: str
    column: str
    pii_tags: str
    reason: str


def load_policies(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_metadata_registry(path: Path) -> pd.DataFrame:
    # Reuse outputs from step 3 as a simple metadata source
    # columns: table,column,pii_tags,reason
    return pd.read_csv(path)


def evaluate_policies(policies: Dict, registry: pd.DataFrame) -> List[Violation]:
    violations: List[Violation] = []

    for policy in policies.get("policies", []):
        pid = policy.get("id")
        forbidden = set(policy.get("forbidden_tags", []))
        applies_tables = set(policy.get("applies_to_tables", [])) if policy.get("applies_to_tables") else None
        name_prefix: Optional[str] = policy.get("table_name_prefix")
        require_tag_for_detected = policy.get("require_tag_for_detected", False)

        for _, row in registry.iterrows():
            table = str(row["table"])  # type: ignore[index]
            column = str(row["column"])  # type: ignore[index]
            tags = set(str(row["pii_tags"]).split(",")) if pd.notna(row["pii_tags"]) else set()

            # Filter by table scope
            if applies_tables and table not in applies_tables:
                continue
            if name_prefix and not table.startswith(name_prefix):
                continue

            # Policy: forbidden tags present
            if forbidden and (tags & forbidden):
                violations.append(
                    Violation(
                        policy_id=pid,
                        table=table,
                        column=column,
                        pii_tags=",".join(sorted(tags)),
                        reason=f"forbidden tags present: {','.join(sorted(tags & forbidden))}",
                    )
                )

            # Policy: detected PII must be tagged (placeholder uses presence in registry as detection)
            if require_tag_for_detected and not tags:
                # if registry row exists but has empty tags, treat as detection missing tag
                violations.append(
                    Violation(
                        policy_id=pid,
                        table=table,
                        column=column,
                        pii_tags="",
                        reason="detected PII missing tag",
                    )
                )

    return violations


def write_violations(violations: List[Violation], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([
        {
            "policy_id": v.policy_id,
            "table": v.table,
            "column": v.column,
            "pii_tags": v.pii_tags,
            "reason": v.reason,
        }
        for v in violations
    ]).to_csv(out_path, index=False)


def main() -> None:
    policies_path = Path("conf/policies.yaml")
    registry_path = Path("outputs/pii_scan.csv")
    out_path = Path("outputs/violations.csv")

    policies = load_policies(policies_path)
    registry = load_metadata_registry(registry_path)
    violations = evaluate_policies(policies, registry)
    write_violations(violations, out_path)
    print(f"Wrote violations to {out_path.as_posix()} ({len(violations)} rows)")


if __name__ == "__main__":
    main()


