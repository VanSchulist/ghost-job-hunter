"""
Tests for mcp-mesh Dynamic Gateway Client & Tool Router.
Verifies keyword tool discovery, lazy schema inspection, tool invocation, and token tracking.
"""

import unittest
from ghost_hunter.mesh_client import MeshClient


class TestMeshClient(unittest.TestCase):

    def setUp(self):
        self.mesh = MeshClient()

    def test_search_tools_keyword_matching(self):
        # Query for audit tools
        results = self.mesh.search_tools("audit ghost posting")
        self.assertGreaterEqual(len(results), 1)
        tool_names = [r["name"] for r in results]
        self.assertIn("ghost_hunter::audit_posting", tool_names)

        # Query for github tools
        results_gh = self.mesh.search_tools("github company repository")
        self.assertGreaterEqual(len(results_gh), 1)
        self.assertEqual(results_gh[0]["name"], "ghost_hunter::audit_company_github")

    def test_describe_tool_lazy_schema(self):
        schema = self.mesh.describe_tool("ghost_hunter::audit_posting")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["name"], "ghost_hunter::audit_posting")
        self.assertIn("inputSchema", schema)
        self.assertIn("properties", schema["inputSchema"])

        # Nonexistent tool returns None
        self.assertIsNone(self.mesh.describe_tool("nonexistent::tool"))

    def test_invoke_audit_posting_tool(self):
        sample = "We are seeking a rockstar ninja to join our talent pipeline for future consideration."
        res = self.mesh.invoke_tool("ghost_hunter::audit_posting", {
            "text": sample,
            "title": "Software Ninja",
            "company": "GhostCorp"
        })
        self.assertIn("ghost_probability_index", res)
        self.assertGreater(res["ghost_probability_index"], 40.0)
        self.assertEqual(res["company_name"], "GhostCorp")

    def test_token_economy_accounting(self):
        initial_stats = self.mesh.get_token_economy_stats()
        self.assertEqual(initial_stats["tool_invocations_count"], 0)
        self.assertGreater(initial_stats["static_token_savings"], 500)

        # Invoke tool and check runtime savings increment
        self.mesh.invoke_tool("ghost_hunter::audit_posting", {"text": "Simple job text"})
        updated_stats = self.mesh.get_token_economy_stats()
        self.assertEqual(updated_stats["tool_invocations_count"], 1)
        self.assertGreater(updated_stats["runtime_tokens_saved"], 0)


if __name__ == "__main__":
    unittest.main()
