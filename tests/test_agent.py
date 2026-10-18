"""
Tests for Autonomous JobHunterAgent.
Verifies end-to-end hunting across ghost, legit, compliance samples, and custom input.
"""

import unittest
from ghost_hunter.agent import JobHunterAgent
from ghost_hunter.core import HuntResult


class TestJobHunterAgent(unittest.TestCase):

    def setUp(self):
        self.agent = JobHunterAgent()

    def test_hunt_ghost_benchmark(self):
        # Run autonomous hunt on built-in ghost benchmark
        result = self.agent.hunt("ghost")
        self.assertIsInstance(result, HuntResult)
        self.assertGreaterEqual(result.diagnostic_report.ghost_probability_index, 65.0)
        self.assertEqual(result.diagnostic_report.risk_level, "CRITICAL_GHOST")
        self.assertIn(result.recommended_strategy, ["AVOID_GHOST", "EXECUTIVE_BYPASS"])
        self.assertIn("EXECUTIVE BYPASS", result.generated_pitch)
        self.assertGreater(result.token_economy["static_token_savings"], 0)

    def test_hunt_legit_benchmark(self):
        # Run autonomous hunt on built-in legit benchmark
        result = self.agent.hunt("legit")
        self.assertIsInstance(result, HuntResult)
        self.assertLessEqual(result.diagnostic_report.ghost_probability_index, 35.0)
        self.assertEqual(result.recommended_strategy, "TARGETED_ATS")
        self.assertIn("TARGETED HIGH-CONVERSION APPLICATION PITCH", result.generated_pitch)
        self.assertGreaterEqual(len(result.tailored_bullets), 1)

    def test_hunt_custom_text(self):
        custom_text = """
        About Us: Fast growing Series A startup building developer tooling.
        Role: Python Systems Engineer
        Requirements: 3+ years experience with Python, asyncio, and API protocols.
        Salary: $140,000 - $175,000 per year.
        Responsibilities: Architect low-latency JSON-RPC gateways and maintain open source client libraries.
        """
        result = self.agent.hunt(custom_text, title="Python Systems Engineer", company="DevToolCorp")
        self.assertEqual(result.job.company, "DevToolCorp")
        self.assertEqual(result.job.title, "Python Systems Engineer")
        self.assertLess(result.diagnostic_report.ghost_probability_index, 40.0)
        self.assertEqual(result.recommended_strategy, "TARGETED_ATS")


if __name__ == "__main__":
    unittest.main()
