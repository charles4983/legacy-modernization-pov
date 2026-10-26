import json
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "sample_legacy" / "dependencies.json"


def build_graph():
    metadata = json.loads(DATA.read_text())
    graph = nx.DiGraph()

    for node in metadata["nodes"]:
        graph.add_node(node["id"], type=node["type"])

    for edge in metadata["edges"]:
        graph.add_edge(
            edge["from"],
            edge["to"],
            relationship=edge["relationship"]
        )

    return graph


def get_impacted_components(graph, table_name):
    if table_name not in graph:
        return []

    return sorted(nx.ancestors(graph, table_name))


if __name__ == "__main__":
    graph = build_graph()

    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())

    impacted = get_impacted_components(
        graph, "CustomerAccounts"
    )

    print("\nComponents impacted by CustomerAccounts:")
    for component in impacted:
        print("-", component)
