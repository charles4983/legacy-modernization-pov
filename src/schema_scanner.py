import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "sample_legacy"


def parse_schema(path):
    sql = path.read_text()
    tables = {}

    table_pattern = r"CREATE\s+TABLE\s+(\w+)\s*\((.*?)\)\s*;"

    for table_name, body in re.findall(
        table_pattern, sql, flags=re.IGNORECASE | re.DOTALL
    ):
        columns = {}

        for line in body.splitlines():
            line = line.strip().rstrip(",")

            match = re.match(
                r"(\w+)\s+(\w+(?:\(\d+(?:,\d+)?\))?)",
                line,
                flags=re.IGNORECASE
            )

            if match:
                columns[match.group(1)] = match.group(2).upper()

        tables[table_name] = columns

    return tables


def detect_schema_drift():
    source = parse_schema(DATA / "legacy_schema.sql")
    target = parse_schema(DATA / "target_schema.sql")

    mappings = json.loads(
        (DATA / "table_mappings.json").read_text()
    )

    findings = []

    for source_table, target_table in mappings.items():
        if source_table not in source or target_table not in target:
            findings.append({
                "type": "MAPPING_TABLE_MISSING",
                "source_table": source_table,
                "target_table": target_table
            })
            continue

        source_columns = source[source_table]
        target_columns = target[target_table]

        for column, source_type in source_columns.items():
            if column not in target_columns:
                findings.append({
                    "type": "SOURCE_COLUMN_UNMAPPED",
                    "table": source_table,
                    "column": column
                })
            elif source_type != target_columns[column]:
                findings.append({
                    "type": "COLUMN_TYPE_DRIFT",
                    "source_table": source_table,
                    "target_table": target_table,
                    "column": column,
                    "source_type": source_type,
                    "target_type": target_columns[column]
                })

    return findings


if __name__ == "__main__":
    print(json.dumps(detect_schema_drift(), indent=2))
