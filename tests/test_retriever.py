import unittest

from graph.graph_builder import build_graph
from rag.retriever import retrieve_dependencies


class TestGraphRetrieval(unittest.TestCase):

    def test_customer_account_dependencies(self):
        graph = build_graph()
        result = retrieve_dependencies(
            graph, "CustomerAccounts"
        )

        self.assertEqual(
            result["status"], "EVIDENCE_FOUND"
        )

        self.assertIn(
            "AccountService",
            result["impacted_components"]
        )

        self.assertIn(
            "AccountLoadJob",
            result["impacted_components"]
        )

    def test_unknown_table(self):
        graph = build_graph()
        result = retrieve_dependencies(
            graph, "UnknownTable"
        )

        self.assertEqual(
            result["status"], "NO_GRAPH_EVIDENCE"
        )


if __name__ == "__main__":
    unittest.main()
