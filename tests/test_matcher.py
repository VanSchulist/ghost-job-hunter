"""
Tests for Candidate Matcher & Resume Bullet Tailoring Engine.
Verifies skill matching, project alignment, and proof-of-work bullet point generation.
"""

import unittest
from ghost_hunter.candidate import get_default_candidate
from ghost_hunter.matcher import CandidateMatcher
from ghost_hunter.core import JobPosting


class TestCandidateMatcher(unittest.TestCase):

    def setUp(self):
        self.candidate = get_default_candidate()
        self.matcher = CandidateMatcher(self.candidate)

    def test_skill_match_and_project_alignment(self):
        job = JobPosting(
            title="Senior Python Backend Engineer",
            company="CloudMesh Inc",
            description="We are building high-throughput distributed systems in Python using asyncio, sqlite, and microservice APIs."
        )

        match_res = self.matcher.match(job)
        self.assertGreaterEqual(match_res.match_score, 60.0)
        self.assertIn("python", match_res.matched_skills)
        self.assertIn("asyncio", match_res.matched_skills)
        self.assertIn("sqlite", match_res.matched_skills)
        
        # Check that aligned projects include mcp-mesh
        proj_names = [p.name for p in match_res.aligned_projects]
        self.assertIn("mcp-mesh", proj_names)

    def test_tailored_bullets_generation(self):
        job = JobPosting(
            title="Staff Infrastructure Engineer",
            company="ScaleApex",
            description="Seeking an engineer experienced in Python and distributed tool routing."
        )
        match_res = self.matcher.match(job)
        bullets = self.matcher.generate_tailored_bullets(job, match_res)

        self.assertGreaterEqual(len(bullets), 2)
        # Verify bullets reference candidate's real proof of work
        all_bullets_text = " ".join(bullets)
        self.assertIn("mcp-mesh", all_bullets_text)


if __name__ == "__main__":
    unittest.main()
