import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "outputs" / "enriched_findings.json"
OUTPUT = ROOT / "outputs" / "dispositions.json"


def generate_disposition(finding):
    finding_type = finding["type"]
    evidence = finding["graph_evidence"]

    impacted = evidence.get("impacted_components", [])

    result = {
        "finding_type": finding_type,
        "object": (
            finding.get("source_table")
            or finding.get("table")
            or finding.get("account_id")
        ),
        "impacted_components": impacted,
        "evidence_status": evidence["status"],
        "human_approval_required": True
    }

    if finding_type == "SOURCE_ONLY_TABLE":
        result["disposition"] = "REVIEW_MIGRATION_MAPPING"
        result["reason"] = (
            "Source table has no same-named target table. "
            "Migration mapping and dependency impact require review."
        )

    elif finding_type == "COLUMN_TYPE_DRIFT":
        result["disposition"] = "REVIEW_SCHEMA_TRANSFORMATION"
        result["reason"] = (
            f"Column {finding['column']} changes from "
            f"{finding['source_type']} to "
            f"{finding['target_type']}."
        )

    elif finding_type == "SOURCE_COLUMN_UNMAPPED":
        result["disposition"] = "REVIEW_COLUMN_MAPPING"
        result["reason"] = (
            f"Column {finding['column']} has no matching "
            "target column name."
        )

    elif finding_type == "CROSS_TENANT_ID_OVERLAP":
        result["disposition"] = "REVIEW_ID_NAMESPACE_POLICY"
        result["reason"] = (
            "The same account ID occurs across multiple tenants. "
            "Target uniqueness and re-keying policy must be confirmed."
        )

    else:
        result["disposition"] = "MANUAL_REVIEW"
        result["reason"] = "No deterministic rule available."

    if evidence["status"] in (
        "NO_GRAPH_EVIDENCE",
        "TABLE_CONTEXT_REQUIRED"
    ):
        result["limitations"] = [
            "Insufficient graph context for full impact analysis."
        ]

    return result


def run():
    if not INPUT.exists():
        raise FileNotFoundError(
            "Run 'python -m rag.retriever' first."
        )

    findings = json.loads(INPUT.read_text())
    dispositions = [
        generate_disposition(finding)
        for finding in findings
    ]

    OUTPUT.write_text(json.dumps(dispositions, indent=2))
    return dispositions


if __name__ == "__main__":
    dispositions = run()

    for item in dispositions:
        print(
            f"{item['object']} | "
            f"{item['finding_type']} | "
            f"{item['disposition']}"
        )

    print(f"\nSaved {len(dispositions)} dispositions")
    print(f"Output: {OUTPUT}")
