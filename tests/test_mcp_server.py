"""
Tests for Standard Model Context Protocol (MCP) Server.
Verifies JSON-RPC 2.0 handshake, tools listing, and tool invocation.
"""

import unittest
import json
from ghost_hunter.server import handle_request
from ghost_hunter.agent import JobHunterAgent


class TestMCPServer(unittest.TestCase):

    def setUp(self):
        self.agent = JobHunterAgent()

    def test_initialize_handshake(self):
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            }
        }
        res = handle_request(self.agent, req)
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], 1)
        self.assertIn("serverInfo", res["result"])
        self.assertEqual(res["result"]["serverInfo"]["name"], "ghost-job-hunter-mcp")

    def test_tools_list(self):
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        res = handle_request(self.agent, req)
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], 2)
        tools = res["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        self.assertIn("ghost_hunter_audit_posting", tool_names)
        self.assertIn("ghost_hunter_audit_company", tool_names)
        self.assertIn("ghost_hunter_hunt", tool_names)

    def test_tools_call_audit_posting(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "ghost_hunter_audit_posting",
                "arguments": {
                    "text": "Seeking an evergreen talent community submission. Salary $100k-$350k.",
                    "title": "Software Architect",
                    "company": "Apex Corp"
                }
            }
        }
        res = handle_request(self.agent, req)
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], 3)
        self.assertIn("content", res["result"])
        text_content = res["result"]["content"][0]["text"]
        data = json.loads(text_content)
        self.assertIn("gpi", data)
        self.assertGreater(data["gpi"], 40.0)

    def test_tools_call_hunt(self):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "ghost_hunter_hunt",
                "arguments": {
                    "target": "ghost",
                    "title": "Principal Architect",
                    "company": "Apex Corp"
                }
            }
        }
        res = handle_request(self.agent, req)
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], 4)
        text_content = res["result"]["content"][0]["text"]
        self.assertIn("AUTONOMOUS TACTICAL DOSSIER", text_content)
        self.assertIn("GHOST PROBABILITY AUDIT", text_content)


if __name__ == "__main__":
    unittest.main()
