import json
from pathlib import Path

from graph.graph_builder import build_graph, get_impacted_components

ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "outputs" / "llm_recommendations.json"
MAPPINGS = ROOT / "sample_legacy" / "table_mappings.json"
OUTPUT = ROOT / "outputs" / "validated_llm_recommendations.json"

ALLOWED = {
    "SOURCE_ONLY_TABLE": "REVIEW_MIGRATION_MAPPING",
    "COLUMN_TYPE_DRIFT": "REVIEW_SCHEMA_TRANSFORMATION",
    "SOURCE_COLUMN_UNMAPPED": "REVIEW_COLUMN_MAPPING",
    "CROSS_TENANT_ID_OVERLAP": "REVIEW_ID_NAMESPACE_POLICY"
}


def validate(item, graph, mappings):
    finding = item["source_finding"]
    recommendation = item.get("llm_recommendation")

    if not isinstance(recommendation, dict):
        return {
            **item,
            "guardian_status": "REVIEW_REQUIRED",
            "guardian_issues": ["LLM_RESPONSE_MISSING_OR_INVALID"],
            "human_approval_required": True,
            "execution_authorized": False
        }

    finding_type = finding["type"]
    table = finding.get("source_table") or finding.get("table")

    issues = []

    if recommendation["disposition"] != ALLOWED.get(finding_type):
        issues.append("DISPOSITION_NOT_ALLOWED")

    if recommendation.get("human_approval_required") is not True:
        issues.append("HUMAN_APPROVAL_NOT_REQUIRED_BY_LLM")

    if table and table in graph:
        actual_impacts = set(get_impacted_components(graph, table))
        claimed_impacts = set(
            finding["graph_evidence"]["impacted_components"]
        )

        if actual_impacts != claimed_impacts:
            issues.append("GRAPH_DEPENDENCY_MISMATCH")

    elif finding_type == "CROSS_TENANT_ID_OVERLAP":
        issues.append("TARGET_ID_POLICY_NOT_VERIFIED")

    if finding_type == "SOURCE_ONLY_TABLE" and table in mappings:
        issues.append(
            "SOURCE_ONLY_FINDING_CONFLICTS_WITH_EXPLICIT_TABLE_MAPPING"
        )

    return {
        **item,
        "guardian_status": (
            "REVIEW_REQUIRED" if issues else "BASIC_CHECKS_PASSED"
        ),
        "guardian_issues": issues,
        "human_approval_required": True,
        "execution_authorized": False
    }


def main():
    items = json.loads(INPUT.read_text())
    mappings = json.loads(MAPPINGS.read_text())
    graph = build_graph()

    results = [
        validate(item, graph, mappings)
        for item in items
    ]

    OUTPUT.write_text(json.dumps(results, indent=2))

    for item in results:
        print("Finding:", item["source_finding"]["type"])
        print("Guardian:", item["guardian_status"])
        print("Issues:", item["guardian_issues"])
        print("Execution authorized:", item["execution_authorized"])

    print("\nSaved:", OUTPUT)


if __name__ == "__main__":
    main()
