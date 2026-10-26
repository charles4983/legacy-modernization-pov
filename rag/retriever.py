import json
from pathlib import Path

import networkx as nx

from graph.graph_builder import build_graph

ROOT = Path(__file__).resolve().parent.parent
FINDINGS = ROOT / "outputs" / "findings.json"
RESULTS = ROOT / "outputs" / "enriched_findings.json"


def retrieve_dependencies(graph, table):
    """Retrieve all components depending on a table."""
    if table not in graph:
        return {
            "status": "NO_GRAPH_EVIDENCE",
            "impacted_components": [],
            "dependency_paths": []
        }

    impacted = sorted(nx.ancestors(graph, table))
    paths = []

    for component in impacted:
        path = nx.shortest_path(graph, component, table)

        relationships = [
            {
                "from": source,
                "to": target,
                "relationship": graph.edges[source, target]["relationship"]
            }
            for source, target in zip(path, path[1:])
        ]

        paths.append({
            "component": component,
            "component_type": graph.nodes[component]["type"],
            "relationships": relationships
        })

    return {
        "status": "EVIDENCE_FOUND" if paths else "NO_DEPENDENTS_FOUND",
        "impacted_components": impacted,
        "dependency_paths": paths
    }


def enrich_findings():
    if not FINDINGS.exists():
        raise FileNotFoundError(
            "Run 'python -m src.main' first."
        )

    findings = json.loads(FINDINGS.read_text())
    graph = build_graph()

    enriched = []

    for finding in findings:
        # Schema findings identify their source table in
        # either 'source_table' or 'table'.
        table = finding.get("source_table") or finding.get("table")

        result = dict(finding)

        if table:
            result["graph_evidence"] = retrieve_dependencies(
                graph, table
            )
        else:
            # Account-level overlaps cannot be assigned to a
            # specific table without additional source metadata.
            result["graph_evidence"] = {
                "status": "TABLE_CONTEXT_REQUIRED",
                "impacted_components": [],
                "dependency_paths": []
            }

        enriched.append(result)

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(enriched, indent=2))

    return enriched


if __name__ == "__main__":
    results = enrich_findings()

    for finding in results:
        evidence = finding["graph_evidence"]

        print("\nFinding:", finding["type"])
        print(
            "Object:",
            finding.get("source_table")
            or finding.get("table")
            or finding.get("account_id")
        )
        print("Graph status:", evidence["status"])
        print(
            "Impacted components:",
            evidence["impacted_components"]
        )

    print(f"\nSaved {len(results)} enriched findings")
    print(f"Output: {RESULTS}")
