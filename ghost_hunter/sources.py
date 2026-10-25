"""
Live Job Posting Feed Ingestion (Hacker News, RemoteOK, WeWorkRemotely).
Zero external dependencies (uses standard library urllib.request, json, re, xml.etree.ElementTree).
Pulls 100% authentic, real-time developer job postings directly from hiring founders and live platforms.
"""

from __future__ import annotations

import re
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Any, Tuple

from .core import JobPosting


def _clean_html(text: str) -> str:
    """Removes HTML tags and decodes common HTML entities."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = (
        clean.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#x27;", "'")
        .replace("&#39;", "'")
        .replace("&apos;", "'")
        .replace("&#x2F;", "/")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&nbsp;", " ")
    )
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


class HNHiringSource:
    """
    Scrapes authentic, live job postings directly from the Hacker News "Who is hiring?" thread.
    No API keys required, zero rate limits for public reads.
    """

    def __init__(self):
        self.headers = {"User-Agent": "GhostJobHunter/2.1 (+https://github.com/VanSchulist/ghost-job-hunter)"}

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
        raw_clean = re.sub(r"<[^>]+>", "\n", comment_text)
        raw_clean = (
            raw_clean.replace("&amp;", "&")
            .replace("&quot;", '"')
            .replace("&#x27;", "'")
            .replace("&#39;", "'")
            .replace("&#x2F;", "/")
        )
        lines = [line.strip() for line in raw_clean.split("\n") if line.strip()]
        if not lines:
            return None

        header = lines[0]
        parts = [p.strip() for p in header.split("|")]

        company = parts[0] if parts else "Unknown Company"
        title = parts[1] if len(parts) > 1 else "Software Engineer"
        location = parts[2] if len(parts) > 2 else "Remote / Unspecified"

        salary_match = re.search(r"\$\d{2,3}[kK0-9,\s–—\-\$to]+", raw_clean)
        salary_raw = salary_match.group(0) if salary_match else ""

        url_match = re.search(r"https?://[^\s<>]+", raw_clean)
        url = url_match.group(0) if url_match else ""

        return JobPosting(
            title=title,
            company=company,
            description=_clean_html(comment_text),
            location=location,
            salary_raw=salary_raw,
            url=url,
            requirements=[]
        )

    def fetch_live_jobs(
        self,
        query: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 10
    ) -> List[JobPosting]:
        thread_id, _ = self.get_latest_thread_id()
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

            if remote_only and "remote" not in job.description.lower() and "remote" not in job.location.lower():
                continue

            jobs.append(job)
            if len(jobs) >= limit:
                break

        return jobs


class RemoteOKSource:
    """
    Direct ingestion from RemoteOK Public API (https://remoteok.com/api).
    Fetches real-time remote developer jobs with verified compensation tiers.
    """

    API_URL = "https://remoteok.com/api"

    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GhostJobHunter/2.1"}

    def fetch_live_jobs(
        self,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[JobPosting]:
        req = urllib.request.Request(self.API_URL, headers=self.headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))

        jobs: List[JobPosting] = []
        # Item 0 is metadata/legal banner in RemoteOK API
        items = data[1:] if len(data) > 1 else []

        q_lower = query.lower() if query else None

        for item in items:
            if not isinstance(item, dict) or "company" not in item:
                continue

            company = item.get("company", "").strip()
            title = item.get("position", "").strip()
            tags = item.get("tags", [])
            raw_desc = item.get("description", "")
            clean_desc = _clean_html(raw_desc)
            location = item.get("location") or "Remote (Worldwide)"

            # Filter by query if supplied
            if q_lower:
                combined_text = f"{company} {title} {' '.join(tags)} {clean_desc}".lower()
                if q_lower not in combined_text:
                    continue

            # Salary extraction
            s_min = item.get("salary_min", 0)
            s_max = item.get("salary_max", 0)
            salary_raw = ""
            if s_min and s_max and s_min > 0 and s_max > 0:
                salary_raw = f"${s_min:,} - ${s_max:,}"
            elif s_min and s_min > 0:
                salary_raw = f"${s_min:,}+"

            apply_url = item.get("apply_url") or item.get("url", "")

            posting = JobPosting(
                title=title,
                company=company,
                description=clean_desc,
                location=location,
                salary_raw=salary_raw,
                url=apply_url,
                requirements=tags[:8] if isinstance(tags, list) else []
            )
            jobs.append(posting)
            if len(jobs) >= limit:
                break

        return jobs


class WeWorkRemotelySource:
    """
    Ingestion from WeWorkRemotely RSS feeds.
    Pulls authentic engineering positions from established tech firms.
    """

    FEEDS = [
        "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
    ]

    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GhostJobHunter/2.1"}

    def fetch_live_jobs(
        self,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[JobPosting]:
        jobs: List[JobPosting] = []
        q_lower = query.lower() if query else None

        for feed_url in self.FEEDS:
            try:
                req = urllib.request.Request(feed_url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=10) as res:
                    tree = ET.fromstring(res.read())

                for item in tree.findall(".//item"):
                    raw_title = item.findtext("title") or ""
                    link = item.findtext("link") or ""
                    raw_desc = item.findtext("description") or ""
                    clean_desc = _clean_html(raw_desc)

                    # Extract company and position from title (Format: "Company: Position")
                    if ":" in raw_title:
                        comp_part, title_part = raw_title.split(":", 1)
                        company = comp_part.strip()
                        title = title_part.strip()
                    else:
                        company = "Remote Tech Co"
                        title = raw_title.strip()

                    if q_lower:
                        search_target = f"{company} {title} {clean_desc}".lower()
                        if q_lower not in search_target:
                            continue

                    # Look for salary in description
                    salary_match = re.search(r"\$\d{2,3}[kK0-9,\s–—\-\$to]+", clean_desc)
                    salary_raw = salary_match.group(0) if salary_match else ""

                    posting = JobPosting(
                        title=title,
                        company=company,
                        description=clean_desc,
                        location="Remote",
                        salary_raw=salary_raw,
                        url=link,
                        requirements=[]
                    )
                    jobs.append(posting)
                    if len(jobs) >= limit:
                        return jobs
            except Exception:
                continue

        return jobs


class UnifiedJobSource:
    """
    Unified aggregator routing across all live developer hiring feeds.
    Provides single-point query interface and targeted company lookup.
    """

    def __init__(self):
        self.hn = HNHiringSource()
        self.remoteok = RemoteOKSource()
        self.wwr = WeWorkRemotelySource()

    def fetch_live_jobs(
        self,
        source: str = "all",
        query: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 10
    ) -> List[JobPosting]:
        """
        Fetches live developer postings across selected real-world feeds.
        `source`: 'all' | 'hn' | 'remoteok' | 'wwr'
        """
        source = source.lower().strip()
        jobs: List[JobPosting] = []

        if source in ["hn", "all"]:
            try:
                hn_limit = limit if source == "hn" else max(3, limit // 2)
                jobs.extend(self.hn.fetch_live_jobs(query=query, remote_only=remote_only, limit=hn_limit))
            except Exception:
                pass

        if source in ["remoteok", "all"]:
            try:
                rok_limit = limit if source == "remoteok" else max(3, limit // 2)
                jobs.extend(self.remoteok.fetch_live_jobs(query=query, limit=rok_limit))
            except Exception:
                pass

        if source in ["wwr", "all"]:
            try:
                wwr_limit = limit if source == "wwr" else max(2, limit // 3)
                jobs.extend(self.wwr.fetch_live_jobs(query=query, limit=wwr_limit))
            except Exception:
                pass

        # Deduplicate by (company, title)
        seen = set()
        deduped: List[JobPosting] = []
        for j in jobs:
            key = (j.company.lower().strip(), j.title.lower().strip())
            if key not in seen:
                seen.add(key)
                deduped.append(j)
                if len(deduped) >= limit:
                    break

        return deduped

    def resolve_target(self, target: str) -> Optional[JobPosting]:
        """
        Resolves a company or role query into a live JobPosting.
        Supports prefixes:
          - 'hn:<Company>'
          - 'remoteok:<Company>'
          - 'wwr:<Company>'
          - '<Company>' (searches across all)
        """
        target = target.strip()
        prefix = ""
        comp_query = target

        if ":" in target:
            prefix, comp_query = target.split(":", 1)
            prefix = prefix.lower().strip()
            comp_query = comp_query.strip()

        if prefix == "hn":
            results = self.hn.fetch_live_jobs(query=comp_query, limit=3)
            return results[0] if results else None
        elif prefix == "remoteok":
            results = self.remoteok.fetch_live_jobs(query=comp_query, limit=3)
            return results[0] if results else None
        elif prefix == "wwr":
            results = self.wwr.fetch_live_jobs(query=comp_query, limit=3)
            return results[0] if results else None
        else:
            # Search all
            results = self.fetch_live_jobs(source="all", query=comp_query, limit=5)
            if results:
                # Match closest company name
                for r in results:
                    if comp_query.lower() in r.company.lower() or comp_query.lower() in r.title.lower():
                        return r
                return results[0]
            return None
