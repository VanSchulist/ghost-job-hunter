"""
Unit tests for OutreachExporter.
Verifies RFC 822 email (.eml) synthesis, MIME structure, subject headers, and markdown dossier generation.
"""

import unittest
import tempfile
import email
from pathlib import Path

from ghost_hunter.core import (
    JobPosting, DiagnosticReport, CompanyAudit, SkillMatchResult,
    HuntResult, CandidateProfile, ProjectShowcase
)
from ghost_hunter.outreach import OutreachExporter, sanitize_filename


class TestOutreachExporter(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.output_base = Path(self.tmp_dir.name)
        self.exporter = OutreachExporter(output_base_dir=self.output_base)

        self.candidate = CandidateProfile(
            name="Van Schulist",
            title="Systems Engineer",
            bio="Indie hacker and systems builder.",
            github_username="VanSchulist",
            skills=["Python", "Rust", "Distributed Systems"],
            featured_projects=[
                ProjectShowcase(
                    name="mcp-mesh",
                    description="Dynamic Tool Routing Mesh",
                    github_url="https://github.com/VanSchulist/mcp-mesh",
                    tech_stack=["Python"]
                )
            ],
            contact_email="van@existentialcloud.ccwu.cc"
        )

        self.hunt_result = HuntResult(
            job=JobPosting(
                title="Staff Backend Engineer",
                company="DuckDuckGo",
                description="We are hiring a backend engineer to scale tracker-radar. Contact jobs@duckduckgo.com",
                salary_raw="$180,000 - $220,000",
                url="https://weworkremotely.com/jobs/duckduckgo"
            ),
            diagnostic_report=DiagnosticReport(
                job_title="Staff Backend Engineer",
                company_name="DuckDuckGo",
                ghost_probability_index=8.5,
                risk_level="ACTIVE",
                verdict_summary="Highly authentic opening",
                signals=[],
                salary_analysis={"min": 180000, "max": 220000},
                key_responsibilities=[],
                detected_tech_stack=["Python", "Go"],
                actionable_recommendation="Apply immediately."
            ),
            company_audit=CompanyAudit(
                company_name="DuckDuckGo",
                github_org="duckduckgo",
                public_repos_count=20,
                engineering_health_score=95.0
            ),
            match_result=SkillMatchResult(
                match_score=94.0,
                matched_skills=["Python", "Distributed Systems"],
                missing_skills=[],
                superfluous_job_demands=[],
                aligned_projects=self.candidate.featured_projects,
                key_selling_points=["Built mcp-mesh standard library distributed gateway"]
            ),
            recommended_strategy="TARGETED_ATS",
            generated_pitch="I built mcp-mesh and scaled high-throughput systems.",
            tailored_bullets=["Architected mcp-mesh zero-dependency dynamic tool routing gateway."]
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename("DuckDuckGo / Scale"), "duckduckgo_scale")
        self.assertEqual(sanitize_filename("Stripe, Inc."), "stripe_inc")

    def test_export_package_files(self):
        pkg = self.exporter.export(self.hunt_result, candidate=self.candidate)
        
        self.assertTrue(Path(pkg["eml_path"]).exists())
        self.assertTrue(Path(pkg["dossier_path"]).exists())
        self.assertEqual(pkg["recipient"], "jobs@duckduckgo.com")
        self.assertIn("DuckDuckGo", pkg["subject"])
        self.assertTrue(pkg["mailto_uri"].startswith("mailto:jobs@duckduckgo.com"))

    def test_eml_rfc822_validity(self):
        pkg = self.exporter.export(self.hunt_result, candidate=self.candidate)
        eml_file = Path(pkg["eml_path"])
        
        with open(eml_file, "rb") as f:
            msg = email.message_from_bytes(f.read(), policy=email.policy.default)
            
        self.assertEqual(msg["To"], "jobs@duckduckgo.com")
        self.assertIn("Van Schulist", msg["From"])
        self.assertIn("Staff Backend Engineer", msg["Subject"])
        
        body = msg.get_content()
        self.assertIn("DuckDuckGo Engineering Team", body)
        self.assertIn("mcp-mesh", body)
        self.assertIn("https://github.com/VanSchulist", body)


if __name__ == "__main__":
    unittest.main()
