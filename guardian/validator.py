import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "outputs" / "dispositions.json"
OUTPUT = ROOT / "outputs" / "validated_dispositions.json"

ALLOWED = {
    "SOURCE_ONLY_TABLE": "REVIEW_MIGRATION_MAPPING",
    "COLUMN_TYPE_DRIFT": "REVIEW_SCHEMA_TRANSFORMATION",
    "SOURCE_COLUMN_UNMAPPED": "REVIEW_COLUMN_MAPPING",
    "CROSS_TENANT_ID_OVERLAP": "REVIEW_ID_NAMESPACE_POLICY",
}


def validate(disposition):
    errors = []

    finding_type = disposition.get("finding_type")
    proposed = disposition.get("disposition")

    if finding_type not in ALLOWED:
        errors.append("UNKNOWN_FINDING_TYPE")
    elif proposed != ALLOWED[finding_type]:
        errors.append("UNSUPPORTED_DISPOSITION")

    if not disposition.get("reason"):
        errors.append("MISSING_REASON")

    if disposition.get("human_approval_required") is not True:
        errors.append("HUMAN_APPROVAL_REQUIRED")

    evidence_status = disposition.get("evidence_status")

    if evidence_status != "EVIDENCE_FOUND":
        errors.append("INSUFFICIENT_GRAPH_EVIDENCE")

    return {
        **disposition,
        "guardian_status": (
            "PASS" if not errors else "REVIEW_REQUIRED"
        ),
        "guardian_errors": errors,
    }


def run():
    if not INPUT.exists():
        raise FileNotFoundError(
            "Run 'python -m reasoning.disposition_engine' first."
        )

    dispositions = json.loads(INPUT.read_text())
    validated = [validate(item) for item in dispositions]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(validated, indent=2))

    return validated


if __name__ == "__main__":
    results = run()

    for item in results:
        print(
            f"{item['object']} | "
            f"{item['disposition']} | "
            f"{item['guardian_status']}"
        )
        if item["guardian_errors"]:
            print("  Reasons:", item["guardian_errors"])

    print(f"\nValidated {len(results)} dispositions")
    print(f"Output: {OUTPUT}")
