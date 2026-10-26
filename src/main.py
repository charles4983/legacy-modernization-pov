from src.schema_scanner import detect_schema_drift

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "sample_legacy"
OUTPUT = ROOT / "outputs" / "findings.json"


def parse_tables(path):
    sql = path.read_text()
    pattern = r"CREATE\s+TABLE\s+(\w+)\s*\("
    return re.findall(pattern, sql, flags=re.IGNORECASE)


def detect_source_only_tables():
    source = parse_tables(DATA / "legacy_schema.sql")
    target = parse_tables(DATA / "target_schema.sql")

    with open(DATA / "table_mappings.json") as file:
        mappings = json.load(file)

    target_names = {name.lower() for name in target}

    mapped_sources = {
        name.lower()
        for name in mappings
    }

    return [
        {
            "type": "SOURCE_ONLY_TABLE",
            "table": name,
            "status": "REQUIRES_REVIEW"
        }
        for name in source
        if name.lower() not in target_names
        and name.lower() not in mapped_sources
    ]


def detect_id_overlaps():
    accounts = defaultdict(set)

    with open(DATA / "accounts.csv", newline="") as file:
        for row in csv.DictReader(file):
            accounts[row["AccountID"]].add(row["TenantID"])

    return [
        {
            "type": "CROSS_TENANT_ID_OVERLAP",
            "account_id": account_id,
            "tenants": sorted(tenants),
            "status": "TARGET_KEY_POLICY_UNKNOWN"
        }
        for account_id, tenants in sorted(accounts.items())
        if len(tenants) > 1
    ]


def main():
    findings = (
        detect_source_only_tables()
        + detect_id_overlaps()
        + detect_schema_drift()
    )

    OUTPUT.parent.mkdir(exist_ok=True, parents=True)
    OUTPUT.write_text(json.dumps(findings, indent=2))

    print(json.dumps(findings, indent=2))
    print(f"\nSaved {len(findings)} findings to {OUTPUT}")


if __name__ == "__main__":
    main()
