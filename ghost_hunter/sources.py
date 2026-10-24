"""
Live Job Posting Feed Ingestion (Hacker News "Who is hiring?", etc.).
Zero external dependencies (uses standard library urllib.request, json, re).
Pulls 100% authentic, real-time developer job postings directly from hiring founders.
"""

from __future__ import annotations

import re
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Optional, Any, Tuple

from .core import JobPosting


class HNHiringSource:
    """
    Scrapes authentic, live job postings directly from the Hacker News "Who is hiring?" thread.
    No API keys required, zero rate limits for public reads.
    """

    def __init__(self):
        self.headers = {"User-Agent": "GhostJobHunter/2.0 (+https://github.com/VanSchulist/ghost-job-hunter)"}

    def get_latest_thread_id(self) -> Tuple[str, str]:
        """Finds the most recent 'Ask HN: Who is hiring?' thread ID and title."""
        url = "https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&query=Who%20is%20hiring&hitsPerPage=3"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            for hit in data.get("hits", []):
                title = hit.get("title", "")
                if "who is hiring?" in title.lower():
                    return str(hit.get("objectID")), title
        raise RuntimeError("Could not locate latest 'Ask HN: Who is hiring?' thread.")

    def parse_comment_to_job(self, comment_text: str, author: str = "") -> Optional[JobPosting]:
        """
        Parses standard HN Who is hiring comment syntax:
        Company | Role | Location | Remote/ONSITE | Tech Stack | Comp | Link
        """
        clean = re.sub(r"<[^>]+>", "\n", comment_text)
        clean = clean.replace("&amp;", "&").replace("&quot;", '"').replace("&#x27;", "'").replace("&#x2F;", "/")
        clean = clean.strip()
        lines = [line.strip() for line in clean.split("\n") if line.strip()]
        if not lines:
            return None

        header = lines[0]
        parts = [p.strip() for p in header.split("|")]
        
        # In HN hiring, first pipe component is company name
        company = parts[0] if parts else "Unknown Company"
        title = parts[1] if len(parts) > 1 else "Software Engineer"
        location = parts[2] if len(parts) > 2 else "Remote / Unspecified"
        
        # Look for salary or compensation
        salary_match = re.search(r"\$\d{2,3}[kK0-9,\s–—\-\$to]+", clean)
        salary_raw = salary_match.group(0) if salary_match else ""

        # Look for application URL
        url_match = re.search(r"https?://[^\s<>]+", clean)
        url = url_match.group(0) if url_match else ""

        return JobPosting(
            title=title,
            company=company,
            description=clean,
            location=location,
            salary_raw=salary_raw,
            url=url
        )

    def fetch_live_jobs(
        self,
        query: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 10
    ) -> List[JobPosting]:
        """
        Pulls real, live job postings from the latest active monthly thread.
        """
        thread_id, thread_title = self.get_latest_thread_id()
        
        # Build Algolia query
        algolia_url = f"https://hn.algolia.com/api/v1/search?tags=comment,story_{thread_id}&numericFilters=parent_id={thread_id}"
        if query:
            algolia_url += f"&query={urllib.parse.quote(query)}"
        algolia_url += f"&hitsPerPage={min(limit * 3, 50)}"

        req = urllib.request.Request(algolia_url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))

        jobs: List[JobPosting] = []
        for hit in data.get("hits", []):
            raw_text = hit.get("comment_text", "")
            if not raw_text:
                continue

            job = self.parse_comment_to_job(raw_text, author=hit.get("author", ""))
            if not job:
                continue

            if remote_only and "remote" not in job.description.lower():
                continue

            jobs.append(job)
            if len(jobs) >= limit:
                break

        return jobs
