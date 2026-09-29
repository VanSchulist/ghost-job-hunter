"""
Automated Test Suite for Ghost Job Hunter.
Verifies scoring models, salary spread math, and heuristic detections.
"""

import unittest
from ghost_hunter.analyzer import JobAnalyzer
from ghost_hunter.sample_data import GHOST_SAMPLE, LEGIT_SAMPLE, COMPLIANCE_SAMPLE
from ghost_hunter.generator import generate_executive_bypass

class TestGhostJobHunter(unittest.TestCase):

    def setUp(self):
        self.analyzer = JobAnalyzer()

    def test_ghost_sample_triggers_high_gpi(self):
        report = self.analyzer.analyze(GHOST_SAMPLE, title="Architect", company="Apex")
        self.assertGreaterEqual(report.ghost_probability_index, 65.0)
        self.assertEqual(report.risk_level, "CRITICAL_GHOST")

        # Check signals
        evergreen_sig = next(s for s in report.signals if s.id == "EVERGREEN_PIPELINE")
        self.assertTrue(evergreen_sig.triggered)

        salary_sig = next(s for s in report.signals if s.id == "SALARY_SPREAD")
        self.assertTrue(salary_sig.triggered)

    def test_legit_sample_produces_active_verdict(self):
        report = self.analyzer.analyze(LEGIT_SAMPLE, title="Staff Engineer", company="ScaleScale")
        self.assertLessEqual(report.ghost_probability_index, 35.0)
        self.assertIn(report.risk_level, ["ACTIVE", "LOW_CONFIDENCE"])

    def test_compliance_theater_detection(self):
        report = self.analyzer.analyze(COMPLIANCE_SAMPLE, title="Auditor", company="Legacy")
        compliance_sig = next(s for s in report.signals if s.id == "COMPLIANCE_THEATER")
        self.assertTrue(compliance_sig.triggered)

    def test_salary_spread_calculation(self):
        sample = "Base salary is $100,000 - $300,000 commensurate with experience."
        sal = self.analyzer.extract_salary_range(sample)
        self.assertEqual(sal["min"], 100000.0)
        self.assertEqual(sal["max"], 300000.0)
        self.assertEqual(sal["spread_ratio"], 2.0)  # 200% spread

    def test_executive_bypass_generation(self):
        report = self.analyzer.analyze(GHOST_SAMPLE, title="Solutions Architect", company="Apex Corp")
        letter = generate_executive_bypass(report, sender_name="Jane Doe", sender_title="Lead Architect")
        self.assertIn("EXECUTIVE BYPASS VALUE PITCH", letter)
        self.assertIn("Apex Corp", letter)
        self.assertIn("Jane Doe", letter)

if __name__ == "__main__":
    unittest.main()
