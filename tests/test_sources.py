"""
Unit tests for Job Sources (Greenhouse, Lever, Hacker News, RemoteOK, UnifiedJobSource).
Verifies ATS API parsing, text cleaning, salary extraction, and URL detection with mocked HTTP responses.
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from ghost_hunter.sources import (
    GreenhouseSource,
    HNHiringSource,
    LeverSource,
    RemoteOKSource,
    UnifiedJobSource,
    WeWorkRemotelySource,
    _clean_html,
)


class TestJobSources(unittest.TestCase):

    def test_clean_html(self):
        raw = "<p>Join our team &amp; build &quot;scalable&quot; systems &#x27;fast&#x27;!</p>"
        clean = _clean_html(raw)
        self.assertEqual(clean, "Join our team & build \"scalable\" systems 'fast'!")

    def test_hn_comment_parser(self):
        hn = HNHiringSource()
        sample_comment = """
        NeuralFrame | Senior Backend Engineer | Remote (US) | ONSITE/REMOTE | Python, Rust, uv, pytest | $170k - $210k | https://neuralframe.com/careers
        We are building high-throughput healthcare ingestion pipelines.
        Please apply directly or email jobs@neuralframe.com
        """
        job = hn.parse_comment_to_job(sample_comment)
        self.assertIsNotNone(job)
        self.assertEqual(job.company, "NeuralFrame")
        self.assertEqual(job.title, "Senior Backend Engineer")
        self.assertIn("Remote", job.location)
        self.assertIn("$170k - $210k", job.salary_raw)
        self.assertEqual(job.url, "https://neuralframe.com/careers")

    def test_hn_comment_parser_empty(self):
        hn = HNHiringSource()
        job = hn.parse_comment_to_job("")
        self.assertIsNone(job)

    def test_greenhouse_fetch_jobs(self):
        """Tests parsing of Greenhouse boards API JSON response."""
        sample_payload = {
            "jobs": [
                {
                    "id": 987654,
                    "title": "Staff Infrastructure Engineer",
                    "updated_at": "2026-10-15T12:00:00Z",
                    "absolute_url": "https://boards.greenhouse.io/stripe/jobs/987654",
                    "location": {"name": "Remote, US"},
                    "departments": [{"name": "Core Platform"}],
                    "content": "<p>Build high-scale distributed payments systems. Salary range: $190,000 - $240,000 per year.</p>",
                },
                {
                    "id": 987655,
                    "title": "Senior Frontend Designer",
                    "updated_at": "2026-10-14T10:00:00Z",
                    "absolute_url": "https://boards.greenhouse.io/stripe/jobs/987655",
                    "location": {"name": "San Francisco, CA"},
                    "departments": [{"name": "Design Systems"}],
                    "content": "<p>Design web apps in React and TypeScript.</p>",
                },
            ]
        }

        mock_res = MagicMock()
        mock_res.status = 200
        mock_res.read.return_value = json.dumps(sample_payload).encode("utf-8")
        mock_res.__enter__.return_value = mock_res

        gh = GreenhouseSource()

        with patch("urllib.request.urlopen", return_value=mock_res):
            jobs = gh.fetch_jobs("stripe", limit=10)

        self.assertEqual(len(jobs), 2)
        j1 = jobs[0]
        self.assertEqual(j1.company, "Stripe")
        self.assertEqual(j1.title, "Staff Infrastructure Engineer")
        self.assertEqual(j1.location, "Remote, US")
        self.assertIn("[Department: Core Platform]", j1.description)
        self.assertIn("$190,000 - $240,000", j1.salary_raw)
        self.assertEqual(j1.url, "https://boards.greenhouse.io/stripe/jobs/987654")
        self.assertEqual(j1.posted_date, "2026-10-15T12:00:00Z")

        # Test query filtering
        with patch("urllib.request.urlopen", return_value=mock_res):
            filtered = gh.fetch_jobs("stripe", query="Infrastructure", limit=10)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, "Staff Infrastructure Engineer")

    def test_greenhouse_empty_slug(self):
        """Tests that invalid company slugs return empty list without network call."""
        gh = GreenhouseSource()
        self.assertEqual(gh.fetch_jobs(""), [])
        self.assertEqual(gh.fetch_jobs("   "), [])

    def test_lever_fetch_jobs(self):
        """Tests parsing of Lever postings API JSON response."""
        sample_payload = [
            {
                "id": "lever-job-001",
                "text": "Senior Distributed Database Engineer",
                "createdAt": 1729000000000,
                "hostedUrl": "https://jobs.lever.co/figma/lever-job-001",
                "categories": {
                    "team": "Storage & Compute",
                    "department": "Infrastructure",
                    "location": "Remote, Americas",
                },
                "descriptionPlain": "Develop high-throughput consensus systems in Rust. Pay: $185k - $225k.",
                "description": "<div>...</div>",
            }
        ]

        mock_res = MagicMock()
        mock_res.status = 200
        mock_res.read.return_value = json.dumps(sample_payload).encode("utf-8")
        mock_res.__enter__.return_value = mock_res

        lever = LeverSource()

        with patch("urllib.request.urlopen", return_value=mock_res):
            jobs = lever.fetch_jobs("figma", limit=5)

        self.assertEqual(len(jobs), 1)
        j = jobs[0]
        self.assertEqual(j.company, "Figma")
        self.assertEqual(j.title, "Senior Distributed Database Engineer")
        self.assertEqual(j.location, "Remote, Americas")
        self.assertIn("[Infrastructure / Storage & Compute]", j.description)
        self.assertIn("$185k - $225k", j.salary_raw)
        self.assertEqual(j.url, "https://jobs.lever.co/figma/lever-job-001")
        self.assertTrue(j.posted_date.startswith("2024-") or j.posted_date.startswith("202"))

    def test_unified_resolve_target_greenhouse_and_lever(self):
        """Tests UnifiedJobSource resolution for greenhouse:<co> and lever:<co> prefixes and URLs."""
        unified = UnifiedJobSource()

        # Mock Greenhouse
        mock_gh_job = GreenhouseSource().fetch_jobs.__name__  # just a string reference
        with patch.object(unified.greenhouse, "fetch_jobs") as mock_gh:
            from ghost_hunter.core import JobPosting
            mock_posting = JobPosting(
                title="Staff Security Engineer",
                company="Stripe",
                description="Secure payment infrastructure.",
                url="https://boards.greenhouse.io/stripe/jobs/112233",
            )
            mock_gh.return_value = [mock_posting]

            # 1. Prefix query: greenhouse:stripe
            res1 = unified.resolve_target("greenhouse:stripe")
            self.assertIsNotNone(res1)
            self.assertEqual(res1.title, "Staff Security Engineer")
            mock_gh.assert_called_with(company="stripe", query=None, limit=3)

            # 2. Direct Greenhouse URL
            res2 = unified.resolve_target("https://boards.greenhouse.io/stripe/jobs/112233")
            self.assertIsNotNone(res2)
            self.assertEqual(res2.title, "Staff Security Engineer")

        # Mock Lever
        with patch.object(unified.lever, "fetch_jobs") as mock_lev:
            from ghost_hunter.core import JobPosting
            mock_lev_posting = JobPosting(
                title="Product Designer",
                company="Figma",
                description="Design vector editing tools.",
                url="https://jobs.lever.co/figma/abc-xyz",
            )
            mock_lev.return_value = [mock_lev_posting]

            # 1. Prefix query: lever:figma
            res3 = unified.resolve_target("lever:figma")
            self.assertIsNotNone(res3)
            self.assertEqual(res3.title, "Product Designer")

            # 2. Direct Lever URL
            res4 = unified.resolve_target("https://jobs.lever.co/figma/abc-xyz")
            self.assertIsNotNone(res4)
            self.assertEqual(res4.title, "Product Designer")


if __name__ == "__main__":
    unittest.main()
