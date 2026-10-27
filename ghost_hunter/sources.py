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


class GreenhouseSource:
    """
    Direct public API consumer for companies hosting job boards on Greenhouse.
    Queries https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true
    Zero external dependencies, 100% standard library (urllib.request, json, re).
    """

    def __init__(self):
        self.headers = {"User-Agent": "GhostJobHunter/2.2 (+https://github.com/VanSchulist/ghost-job-hunter)"}

    def fetch_jobs(
        self,
        company: str,
        query: Optional[str] = None,
        limit: int = 10,
        content: bool = True,
    ) -> List[JobPosting]:
        """
        Fetches live postings directly from a company's Greenhouse job board.
        `company`: the Greenhouse board token (e.g. 'stripe', 'canonical', 'github', 'airbnb')
        """
        company_slug = re.sub(r"[^a-zA-Z0-9_\-]", "", company.strip().lower())
        if not company_slug:
            return []

        url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content={'true' if content else 'false'}"
        req = urllib.request.Request(url, headers=self.headers)

        try:
            with urllib.request.urlopen(req, timeout=12) as res:
                if res.status != 200:
                    return []
                data = json.loads(res.read().decode("utf-8"))
        except Exception:
            return []

        jobs_list = data.get("jobs", [])
        if not isinstance(jobs_list, list):
            return []

        results: List[JobPosting] = []

        for item in jobs_list:
            if not isinstance(item, dict):
                continue

            title = item.get("title", "").strip()
            raw_content = item.get("content", "")
            clean_desc = _clean_html(raw_content) if raw_content else title

            # Keyword filtering if specified
            if query:
                q_lower = query.lower().strip()
                if q_lower not in title.lower() and q_lower not in clean_desc.lower():
                    continue

            # Extract location
            loc_info = item.get("location", {})
            location = loc_info.get("name", "Remote / Unspecified") if isinstance(loc_info, dict) else str(loc_info)

            # Extract departments / metadata
            dept_names = [d.get("name") for d in item.get("departments", []) if isinstance(d, dict) and d.get("name")]
            if dept_names:
                clean_desc = f"[Department: {', '.join(dept_names)}] {clean_desc}"

            # Salary extraction
            salary_match = re.search(r"\$\d{2,3}[kK0-9,\s–—\-\$to]+", clean_desc)
            salary_raw = salary_match.group(0) if salary_match else ""

            updated_at = item.get("updated_at", "")
            url_link = item.get("absolute_url", f"https://boards.greenhouse.io/{company_slug}/jobs/{item.get('id', '')}")

            posting = JobPosting(
                title=title,
                company=company_slug.capitalize(),
                description=clean_desc,
                location=location,
                salary_raw=salary_raw,
                url=url_link,
                posted_date=updated_at,
                requirements=[],
            )
            results.append(posting)
            if len(results) >= limit:
                break

        return results


class LeverSource:
    """
    Direct public API consumer for companies hosting job boards on Lever.co.
    Queries https://api.lever.co/v0/postings/{company}?mode=json
    Zero external dependencies, 100% standard library (urllib.request, json, re, datetime).
    """

    def __init__(self):
        self.headers = {"User-Agent": "GhostJobHunter/2.2 (+https://github.com/VanSchulist/ghost-job-hunter)"}

    def fetch_jobs(
        self,
        company: str,
        query: Optional[str] = None,
        limit: int = 10,
    ) -> List[JobPosting]:
        """
        Fetches live postings directly from a company's Lever job board.
        `company`: the Lever board token (e.g. 'figma', 'netflix', 'palantir')
        """
        company_slug = re.sub(r"[^a-zA-Z0-9_\-]", "", company.strip().lower())
        if not company_slug:
            return []

        url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
        req = urllib.request.Request(url, headers=self.headers)

        try:
            with urllib.request.urlopen(req, timeout=12) as res:
                if res.status != 200:
                    return []
                data = json.loads(res.read().decode("utf-8"))
        except Exception:
            return []

        if not isinstance(data, list):
            return []

        results: List[JobPosting] = []

        for item in data:
            if not isinstance(item, dict):
                continue

            title = item.get("text", "").strip()
            plain_desc = item.get("descriptionPlain", "")
            raw_desc = item.get("description", "")
            clean_desc = plain_desc if plain_desc else _clean_html(raw_desc)
            if not clean_desc:
                clean_desc = title

            # Keyword filtering
            if query:
                q_lower = query.lower().strip()
                if q_lower not in title.lower() and q_lower not in clean_desc.lower():
                    continue

            # Categories (team, department, location)
            categories = item.get("categories", {})
            location = "Remote / Unspecified"
            if isinstance(categories, dict):
                location = categories.get("location") or categories.get("workplaceType") or location
                team = categories.get("team")
                department = categories.get("department")
                dept_str = " / ".join(filter(None, [department, team]))
                if dept_str:
                    clean_desc = f"[{dept_str}] {clean_desc}"

            # Salary extraction
            salary_match = re.search(r"\$\d{2,3}[kK0-9,\s–—\-\$to]+", clean_desc)
            salary_raw = salary_match.group(0) if salary_match else ""

            # Posted date from epoch milliseconds
            created_at_ms = item.get("createdAt")
            posted_date = ""
            if isinstance(created_at_ms, (int, float)) and created_at_ms > 0:
                import datetime
                try:
                    dt = datetime.datetime.fromtimestamp(created_at_ms / 1000.0, tz=datetime.timezone.utc)
                    posted_date = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                except Exception:
                    pass

            hosted_url = item.get("hostedUrl", f"https://jobs.lever.co/{company_slug}/{item.get('id', '')}")

            posting = JobPosting(
                title=title,
                company=company_slug.capitalize(),
                description=clean_desc,
                location=str(location),
                salary_raw=salary_raw,
                url=hosted_url,
                posted_date=posted_date,
                requirements=[],
            )
            results.append(posting)
            if len(results) >= limit:
                break

        return results


class UnifiedJobSource:
    """
    Unified aggregator routing across all live developer hiring feeds.
    Provides single-point query interface and targeted company lookup.
    """

    def __init__(self):
        self.hn = HNHiringSource()
        self.remoteok = RemoteOKSource()
        self.wwr = WeWorkRemotelySource()
        self.greenhouse = GreenhouseSource()
        self.lever = LeverSource()

    def fetch_live_jobs(
        self,
        source: str = "all",
        query: Optional[str] = None,
        remote_only: bool = False,
        company: Optional[str] = None,
        limit: int = 10
    ) -> List[JobPosting]:
        """
        Fetches live developer postings across selected real-world feeds.
        `source`: 'all' | 'hn' | 'remoteok' | 'wwr' | 'greenhouse' | 'lever'
        """
        source = source.lower().strip()
        jobs: List[JobPosting] = []

        if source in ["greenhouse"]:
            comp_target = company or query or "stripe"
            return self.greenhouse.fetch_jobs(company=comp_target, query=query if company else None, limit=limit)

        if source in ["lever"]:
            comp_target = company or query or "figma"
            return self.lever.fetch_jobs(company=comp_target, query=query if company else None, limit=limit)

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
          - 'greenhouse:<Company>' (or 'greenhouse:<Company>:<Role>')
          - 'lever:<Company>' (or 'lever:<Company>:<Role>')
          - 'hn:<Company>'
          - 'remoteok:<Company>'
          - 'wwr:<Company>'
          - Direct Greenhouse or Lever board URLs
          - '<Company>' (searches across all)
        """
        target = target.strip()

        # Check for direct Greenhouse job board URLs
        if "boards.greenhouse.io" in target:
            match = re.search(r"boards\.greenhouse\.io/([^/]+)(?:/jobs/(\d+))?", target)
            if match:
                comp_slug = match.group(1)
                job_id = match.group(2)
                results = self.greenhouse.fetch_jobs(company=comp_slug, limit=30)
                if job_id:
                    for r in results:
                        if f"/jobs/{job_id}" in r.url:
                            return r
                return results[0] if results else None

        # Check for direct Lever job board URLs
        if "jobs.lever.co" in target:
            match = re.search(r"jobs\.lever\.co/([^/]+)(?:/([a-zA-Z0-9\-]+))?", target)
            if match:
                comp_slug = match.group(1)
                job_id = match.group(2)
                results = self.lever.fetch_jobs(company=comp_slug, limit=30)
                if job_id:
                    for r in results:
                        if f"/{job_id}" in r.url:
                            return r
                return results[0] if results else None

        prefix = ""
        comp_query = target

        if ":" in target:
            prefix, comp_query = target.split(":", 1)
            prefix = prefix.lower().strip()
            comp_query = comp_query.strip()

        if prefix == "greenhouse":
            parts = comp_query.split(":", 1)
            comp_name = parts[0].strip()
            role_filter = parts[1].strip() if len(parts) > 1 else None
            results = self.greenhouse.fetch_jobs(company=comp_name, query=role_filter, limit=3)
            return results[0] if results else None
        elif prefix == "lever":
            parts = comp_query.split(":", 1)
            comp_name = parts[0].strip()
            role_filter = parts[1].strip() if len(parts) > 1 else None
            results = self.lever.fetch_jobs(company=comp_name, query=role_filter, limit=3)
            return results[0] if results else None
        elif prefix == "hn":
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
