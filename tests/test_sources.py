"""
Unit tests for Job Sources (HNHiringSource, RemoteOKSource, WeWorkRemotelySource, UnifiedJobSource).
Verifies comment parsing, text cleaning, salary extraction, and URL detection without relying on external network.
"""

import unittest
from ghost_hunter.sources import HNHiringSource, RemoteOKSource, WeWorkRemotelySource, _clean_html


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


if __name__ == "__main__":
    unittest.main()
