"""
Unit tests for JobPipelineStore (SQLite Opportunity Pipeline).
Verifies schema initialization, lead insertion, conflict handling, status transitions, and metrics.
"""

import unittest
import tempfile
import os
from pathlib import Path
from ghost_hunter.pipeline import JobPipelineStore, LeadRecord


class TestJobPipelineStore(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test_pipeline.db"
        self.store = JobPipelineStore(db_path=self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_schema_creation(self):
        self.assertTrue(self.db_path.exists())

    def test_save_and_retrieve_lead(self):
        lead_id = self.store.save_lead(
            company="DuckDuckGo",
            title="Senior Backend Engineer",
            source="wwr",
            url="https://weworkremotely.com/jobs/duckduckgo",
            salary="$160,000 - $210,000",
            location="Remote",
            gpi_score=12.5,
            risk_level="ACTIVE",
            fit_score=92.0,
            status="AUDITED",
            notes="Strong distributed systems match."
        )
        self.assertGreater(lead_id, 0)

        record = self.store.get_lead(lead_id)
        self.assertIsNotNone(record)
        self.assertEqual(record.company, "DuckDuckGo")
        self.assertEqual(record.title, "Senior Backend Engineer")
        self.assertEqual(record.gpi_score, 12.5)
        self.assertEqual(record.status, "AUDITED")

    def test_status_update(self):
        lead_id = self.store.save_lead(
            company="NeuralFrame",
            title="Senior Backend Engineer",
            source="hn",
            status="AUDITED"
        )
        ok = self.store.update_status(lead_id, "APPLIED", notes="Sent cold email to hiring lead")
        self.assertTrue(ok)

        record = self.store.get_lead(lead_id)
        self.assertEqual(record.status, "APPLIED")
        self.assertIn("Sent cold email", record.notes)

    def test_invalid_status_raises(self):
        with self.assertRaises(ValueError):
            self.store.update_status(1, "NON_EXISTENT_STATUS")

    def test_list_leads_filtering(self):
        self.store.save_lead(company="AlphaCorp", title="Dev", status="DISCOVERED", gpi_score=20.0)
        self.store.save_lead(company="BetaCorp", title="Architect", status="AUDITED", gpi_score=80.0)

        all_leads = self.store.list_leads()
        self.assertEqual(len(all_leads), 2)

        audited = self.store.list_leads(status="AUDITED")
        self.assertEqual(len(audited), 1)
        self.assertEqual(audited[0].company, "BetaCorp")

        low_gpi = self.store.list_leads(max_gpi=30.0)
        self.assertEqual(len(low_gpi), 1)
        self.assertEqual(low_gpi[0].company, "AlphaCorp")

    def test_summary_stats(self):
        self.store.save_lead(company="C1", title="T1", status="DISCOVERED")
        self.store.save_lead(company="C2", title="T2", status="AUDITED")
        self.store.save_lead(company="C3", title="T3", status="APPLIED")

        stats = self.store.get_summary_stats()
        self.assertEqual(stats["total_leads"], 3)
        self.assertEqual(stats["applied_count"], 1)
        self.assertEqual(stats["active_prospects"], 1)


if __name__ == "__main__":
    unittest.main()
