"""
Tests for Company GitHub Stack & Engineering Footprint Auditor.
Verifies tech stack extraction, discrepancy alerts, and health scores using deterministic mock data.
"""

import unittest
from ghost_hunter.github_auditor import CompanyGitHubAuditor


class TestGitHubAuditor(unittest.TestCase):

    def setUp(self):
        self.auditor = CompanyGitHubAuditor()

    def test_audit_with_mock_repos(self):
        mock_repos = [
            {
                "name": "core-engine",
                "language": "Python",
                "updated_at": "2026-09-15T12:00:00Z",
                "archived": False,
                "description": "High performance async networking with asyncio and fastapi",
                "topics": ["python", "asyncio", "fastapi"]
            },
            {
                "name": "data-pipeline",
                "language": "Python",
                "updated_at": "2026-08-10T10:00:00Z",
                "archived": False,
                "description": "Data processing with kafka and spark",
                "topics": ["kafka", "spark"]
            },
            {
                "name": "legacy-ui",
                "language": "TypeScript",
                "updated_at": "2026-01-05T08:00:00Z",
                "archived": True,
                "description": "Frontend React portal",
                "topics": ["react"]
            }
        ]

        audit = self.auditor.audit_company(
            "TechInnovate Corp",
            claimed_tech_stack=["python", "fastapi", "kafka"],
            mock_data=mock_repos
        )

        self.assertEqual(audit.company_name, "TechInnovate Corp")
        self.assertEqual(audit.public_repos_count, 3)
        self.assertIn("Python", audit.top_languages)
        self.assertEqual(audit.top_languages["Python"], 2)
        self.assertIn("fastapi", audit.verified_tech_stack)
        self.assertIn("kafka", audit.verified_tech_stack)
        self.assertEqual(len(audit.discrepancy_flags), 0)
        self.assertGreaterEqual(audit.engineering_health_score, 60.0)

    def test_discrepancy_detection_when_claimed_tech_missing(self):
        # Company claims high-level Rust & Kubernetes systems engineering,
        # but only has a single inactive PHP repo.
        mock_repos = [
            {
                "name": "simple-wordpress",
                "language": "PHP",
                "updated_at": "2023-01-01T00:00:00Z",
                "archived": True,
                "description": "Old company blog",
                "topics": []
            }
        ]

        audit = self.auditor.audit_company(
            "GhostScale Inc",
            claimed_tech_stack=["rust", "kubernetes"],
            mock_data=mock_repos
        )

        self.assertGreaterEqual(len(audit.discrepancy_flags), 1)
        discrepancy_str = " ".join(audit.discrepancy_flags).lower()
        self.assertIn("rust", discrepancy_str)

    def test_org_slug_sanitization(self):
        self.assertEqual(self.auditor._sanitize_org_name("Acme Corp"), "acme")
        self.assertEqual(self.auditor._sanitize_org_name("NextGen AI LLC"), "nextgen")
        self.assertEqual(self.auditor._sanitize_org_name("ScaleScale Systems"), "scalescale")


if __name__ == "__main__":
    unittest.main()
