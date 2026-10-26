import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "outputs" / "validated_llm_recommendations.json"
OUTPUT = ROOT / "reports" / "modernization_assessment.md"


def clean(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def main():
    results = json.loads(INPUT.read_text())
    counts = Counter(
        item["guardian_status"] for item in results
    )

    lines = [
        "# Legacy Modernization Assessment",
        "",
        "**Environment:** Synthetic local proof of value",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "**Execution status:** Not authorized",
        "",
        "## Executive Summary",
        "",
        f"- Total findings: {len(results)}",
        f"- Basic checks passed: {counts.get('BASIC_CHECKS_PASSED', 0)}",
        f"- Review required: {counts.get('REVIEW_REQUIRED', 0)}",
        "- All migration changes require human authorization.",
        "",
        "## Finding Summary",
        "",
        "| # | Finding | Disposition | Guardian |",
        "|---|---|---|---|",
    ]

    for i, item in enumerate(results, 1):
        finding = item["source_finding"]
        recommendation = item.get("llm_recommendation") or {}

        lines.append(
            f"| {i} | {clean(finding.get('type', 'Unknown'))} "
            f"| {clean(recommendation.get('disposition', 'N/A'))} "
            f"| {clean(item['guardian_status'])} |"
        )

    lines.extend(["", "## Detailed Findings", ""])

    for i, item in enumerate(results, 1):
        finding = item["source_finding"]
        recommendation = item.get("llm_recommendation") or {}
        evidence = finding.get("graph_evidence") or {}

        lines.extend([
            f"### Finding {i}: {finding.get('type', 'Unknown')}",
            "",
            f"**Object:** {finding.get('table') or finding.get('source_table') or finding.get('account_id') or 'See evidence'}",
            "",
            f"**Disposition:** {recommendation.get('disposition', 'N/A')}",
            "",
            f"**Guardian:** {item['guardian_status']}",
            "",
            f"**Reason:** {recommendation.get('reason', 'Not available')}",
            "",
            "**Dependency evidence:**",
            "",
        ])

        for component in evidence.get("impacted_components", []):
            lines.append(f"- {component}")

        if not evidence.get("impacted_components"):
            lines.append("- No dependency impact confirmed")

        lines.extend(["", "**Risks:**", ""])

        for risk in recommendation.get("risks", []):
            lines.append(f"- {risk}")

        lines.extend(["", "**Recommended next steps:**", ""])

        for step in recommendation.get("next_steps", []):
            lines.append(f"- {step}")

        lines.extend(["", "**Guardian issues:**", ""])

        for issue in item.get("guardian_issues", []):
            lines.append(f"- {issue}")

        if not item.get("guardian_issues"):
            lines.append("- No issues detected by implemented checks")

        lines.extend([
            "",
            "**Execution authorized:** No",
            "",
            "---",
            "",
        ])

    lines.extend([
        "## Limitations",
        "",
        "- This report uses synthetic project data.",
        "- LLM explanations have not been independently verified in full.",
        "- Basic Guardian checks do not establish migration readiness.",
        "- Target-system policies and actual deployment dependencies require verification.",
        "- Human approval is required before execution.",
        "",
    ])

    OUTPUT.write_text("\n".join(lines))
    print("Report generated:", OUTPUT)
    print("Total findings:", len(results))


if __name__ == "__main__":
    main()
