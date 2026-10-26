"""
Local SQLite Pipeline Ledger for Real-World Job Opportunities.
Tracks audited positions from discovery through application and interview stages.
Zero external dependencies (uses standard library sqlite3, json, datetime, contextlib).
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import os
from pathlib import Path
import sqlite3
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class LeadRecord:
    id: int
    company: str
    title: str
    source: str
    url: str
    salary: str
    location: str
    gpi_score: float
    risk_level: str
    fit_score: float
    status: str
    notes: str
    created_at: str
    updated_at: str


class JobPipelineStore:
    """
    Manages user's local pipeline of genuine job opportunities.
    Default ledger location: ~/.ghost-hunter/pipeline.db
    """

    VALID_STATUSES = [
        "DISCOVERED",
        "AUDITED",
        "PITCH_READY",
        "APPLIED",
        "INTERVIEWING",
        "OFFER",
        "REJECTED",
        "ARCHIVED"
    ]

    def __init__(self, db_path: Optional[str | Path] = None):
        if db_path is None:
            self.db_path = Path.home() / ".ghost-hunter" / "pipeline.db"
        else:
            self.db_path = Path(db_path)

        self._ensure_schema()

    @contextlib.contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT NOT NULL,
                    title TEXT NOT NULL,
                    source TEXT DEFAULT 'manual',
                    url TEXT DEFAULT '',
                    salary TEXT DEFAULT '',
                    location TEXT DEFAULT 'Remote',
                    gpi_score REAL DEFAULT 0.0,
                    risk_level TEXT DEFAULT 'ACTIVE',
                    fit_score REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'DISCOVERED',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(company, title)
                );
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company);
                """
            )

    def save_lead(
        self,
        company: str,
        title: str,
        source: str = "manual",
        url: str = "",
        salary: str = "",
        location: str = "Remote",
        gpi_score: float = 0.0,
        risk_level: str = "ACTIVE",
        fit_score: float = 0.0,
        status: str = "DISCOVERED",
        notes: str = ""
    ) -> int:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO leads (
                    company, title, source, url, salary, location,
                    gpi_score, risk_level, fit_score, status, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company, title) DO UPDATE SET
                    source=excluded.source,
                    url=CASE WHEN excluded.url != '' THEN excluded.url ELSE leads.url END,
                    salary=CASE WHEN excluded.salary != '' THEN excluded.salary ELSE leads.salary END,
                    location=excluded.location,
                    gpi_score=CASE WHEN excluded.gpi_score > 0 THEN excluded.gpi_score ELSE leads.gpi_score END,
                    risk_level=CASE WHEN excluded.risk_level != '' THEN excluded.risk_level ELSE leads.risk_level END,
                    fit_score=CASE WHEN excluded.fit_score > 0 THEN excluded.fit_score ELSE leads.fit_score END,
                    status=CASE WHEN leads.status = 'DISCOVERED' THEN excluded.status ELSE leads.status END,
                    notes=CASE WHEN excluded.notes != '' THEN excluded.notes ELSE leads.notes END,
                    updated_at=excluded.updated_at
                RETURNING id;
                """,
                (
                    company.strip(),
                    title.strip(),
                    source.strip(),
                    url.strip(),
                    salary.strip(),
                    location.strip(),
                    round(gpi_score, 1),
                    risk_level.strip(),
                    round(fit_score, 1),
                    status.strip(),
                    notes.strip(),
                    now,
                    now,
                ),
            )
            row = cur.fetchone()
            return int(row[0]) if row else -1

    def update_status(self, lead_id: int, status: str, notes: Optional[str] = None) -> bool:
        status_upper = status.upper().strip()
        if status_upper not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {self.VALID_STATUSES}")

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._connect() as conn:
            if notes is not None:
                cur = conn.execute(
                    "UPDATE leads SET status=?, notes=?, updated_at=? WHERE id=?",
                    (status_upper, notes, now, lead_id)
                )
            else:
                cur = conn.execute(
                    "UPDATE leads SET status=?, updated_at=? WHERE id=?",
                    (status_upper, now, lead_id)
                )
            return cur.rowcount > 0

    def get_lead(self, lead_id: int) -> Optional[LeadRecord]:
        with self._connect() as conn:
            cur = conn.execute("SELECT * FROM leads WHERE id=?", (lead_id,))
            row = cur.fetchone()
            if not row:
                return None
            return LeadRecord(**dict(row))

    def list_leads(
        self,
        status: Optional[str] = None,
        query: Optional[str] = None,
        max_gpi: Optional[float] = None,
        limit: int = 50
    ) -> List[LeadRecord]:
        sql = "SELECT * FROM leads WHERE 1=1"
        params: List[Any] = []

        if status:
            sql += " AND UPPER(status) = ?"
            params.append(status.upper().strip())

        if query:
            sql += " AND (company LIKE ? OR title LIKE ? OR notes LIKE ?)"
            q_pat = f"%{query}%"
            params.extend([q_pat, q_pat, q_pat])

        if max_gpi is not None:
            sql += " AND gpi_score <= ?"
            params.append(max_gpi)

        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            cur = conn.execute(sql, params)
            return [LeadRecord(**dict(row)) for row in cur.fetchall()]

    def get_summary_stats(self) -> Dict[str, Any]:
        with self._connect() as conn:
            cur = conn.execute(
                """
                SELECT status, COUNT(*) as cnt FROM leads GROUP BY status
                """
            )
            by_status = {row["status"]: row["cnt"] for row in cur.fetchall()}
            
            total = sum(by_status.values())
            active_prospects = by_status.get("AUDITED", 0) + by_status.get("PITCH_READY", 0)
            applied = by_status.get("APPLIED", 0)
            interviewing = by_status.get("INTERVIEWING", 0)
            offers = by_status.get("OFFER", 0)

            return {
                "total_leads": total,
                "by_status": by_status,
                "active_prospects": active_prospects,
                "applied_count": applied,
                "interviewing_count": interviewing,
                "offers_count": offers,
            }

    def export_leads(
        self,
        format: str = "json",
        status: Optional[str] = None,
        query: Optional[str] = None,
        max_gpi: Optional[float] = None,
        limit: int = 50,
        output_path: Optional[str | Path] = None,
    ) -> str:
        """Exports tracked pipeline opportunities to structured JSON or CSV format.

        Optionally writes output to file when output_path is provided.
        Returns the formatted string.
        """
        fmt = format.strip().lower()
        if fmt not in ("json", "csv"):
            raise ValueError(f"Unsupported export format: {format!r}. Must be 'json' or 'csv'.")

        leads = self.list_leads(status=status, query=query, max_gpi=max_gpi, limit=limit)
        lead_dicts = [asdict(ld) for ld in leads]

        if fmt == "json":
            result_str = json.dumps(lead_dicts, indent=2, ensure_ascii=False)
        else:
            buffer = io.StringIO()
            fields = [
                "id",
                "company",
                "title",
                "source",
                "url",
                "salary",
                "location",
                "gpi_score",
                "risk_level",
                "fit_score",
                "status",
                "notes",
                "created_at",
                "updated_at",
            ]
            writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            for row in lead_dicts:
                writer.writerow(row)
            result_str = buffer.getvalue()

        if output_path:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w", encoding="utf-8", newline="") as f:
                f.write(result_str)

        return result_str
