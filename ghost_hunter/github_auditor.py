"""
Company GitHub Stack & Engineering Footprint Auditor.
Audits public repositories to verify actual engineering activity against job requisition claims.
Zero external dependencies (uses standard library urllib.request).
"""

from __future__ import annotations

import json
import re
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

from .core import CompanyAudit, TECH_DOMAINS


class CompanyGitHubAuditor:
    """
    Audits a company's open-source engineering footprint via the GitHub REST API.
    Identifies tech stack discrepancies, dormant codebases, and recruiter buzzword inflation.
    """

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token

    def _sanitize_org_name(self, company_name: str) -> str:
        """Derives a plausible GitHub organization slug from a company name."""
        clean = re.sub(r"\b(inc|corp|corporation|llc|ltd|technologies|tech|solutions|systems|ai|io)\b", "", company_name, flags=re.IGNORECASE)
        clean = re.sub(r"[^a-zA-Z0-9_-]", "", clean.strip())
        return clean.lower() if clean else company_name.lower().replace(" ", "")

    def _make_request(self, url: str) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """Makes an authenticated or anonymous request to the GitHub API."""
        headers = {
            "User-Agent": "GhostJobHunter/2.0 (+https://github.com/VanSchulist/ghost-job-hunter)",
            "Accept": "application/vnd.github.v3+json"
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data, None
                return None, f"HTTP {response.status}"
        except urllib.error.HTTPError as e:
            msg = f"HTTP {e.code}: {e.reason}"
            try:
                e.close()
            except Exception:
                pass
            return None, msg
        except Exception as e:
            return None, str(e)

    def audit_company(
        self,
        company_name: str,
        claimed_tech_stack: Optional[List[str]] = None,
        mock_data: Optional[List[Dict[str, Any]]] = None
    ) -> CompanyAudit:
        """
        Audits a target company. If mock_data is provided, uses it for offline deterministic evaluation.
        """
        claimed_tech = [t.lower() for t in (claimed_tech_stack or [])]
        org_slug = self._sanitize_org_name(company_name)

        repos: List[Dict[str, Any]] = []
        error_note = None

        if mock_data is not None:
            repos = mock_data
        else:
            # Attempt org lookup first, fallback to user lookup
            data, err = self._make_request(f"https://api.github.com/orgs/{org_slug}/repos?per_page=30&sort=updated")
            if data is not None:
                repos = data
            else:
                data_user, err_user = self._make_request(f"https://api.github.com/users/{org_slug}/repos?per_page=30&sort=updated")
                if data_user is not None:
                    repos = data_user
                else:
                    error_note = err or err_user

        # If API failed or was rate-limited, provide an informative baseline audit
        if not repos:
            flags = []
            if error_note and "404" in error_note:
                flags.append(f"No public GitHub organization found for slug '{org_slug}'. Company may operate 100% closed-source.")
            elif error_note:
                flags.append(f"GitHub API notice: {error_note}")
            
            return CompanyAudit(
                company_name=company_name,
                github_org=org_slug,
                public_repos_count=0,
                top_languages={},
                active_repos=[],
                last_commit_date="Unknown / Closed Source",
                verified_tech_stack=[],
                discrepancy_flags=flags,
                engineering_health_score=50.0  # neutral uncertainty
            )

        # Analyze repositories
        languages_count: Dict[str, int] = {}
        active_repos_list: List[str] = []
        verified_tech: set[str] = set()
        latest_update: Optional[str] = None
        has_recent_activity = False

        for r in repos:
            name = r.get("name", "")
            lang = r.get("language")
            updated_at = r.get("updated_at", "")
            archived = r.get("archived", False)

            if updated_at and (latest_update is None or updated_at > latest_update):
                latest_update = updated_at

            if lang:
                clean_lang = lang.lower()
                languages_count[lang] = languages_count.get(lang, 0) + 1
                verified_tech.add(clean_lang)

            # Check description and topics for technologies
            desc = (r.get("description") or "").lower()
            topics = [t.lower() for t in r.get("topics", [])]
            for domain_keywords in TECH_DOMAINS.values():
                for kw in domain_keywords:
                    if kw in desc or kw in topics:
                        verified_tech.add(kw)

            if not archived and len(active_repos_list) < 5:
                active_repos_list.append(name)

        # Check for discrepancy flags
        discrepancies: List[str] = []
        if claimed_tech:
            for tech in claimed_tech:
                # Check if claimed core tech exists in verified open-source languages
                matched = any(
                    tech in v_tech or v_tech in tech
                    for v_tech in verified_tech
                )
                if not matched and tech in ["rust", "golang", "c++", "kubernetes", "pytorch"]:
                    discrepancies.append(
                        f"Requisition requires high-priority '{tech}', but zero public repos or topics reflect '{tech}'."
                    )

        # Compute engineering health score
        health = 80.0
        if len(repos) >= 10:
            health += 15.0
        elif len(repos) < 3:
            health -= 15.0

        if discrepancies:
            health -= min(len(discrepancies) * 15.0, 35.0)

        return CompanyAudit(
            company_name=company_name,
            github_org=org_slug,
            public_repos_count=len(repos),
            top_languages=dict(sorted(languages_count.items(), key=lambda item: item[1], reverse=True)[:5]),
            active_repos=active_repos_list,
            last_commit_date=latest_update or "Unknown",
            verified_tech_stack=sorted(list(verified_tech)),
            discrepancy_flags=discrepancies,
            engineering_health_score=round(max(min(health, 100.0), 0.0), 1)
        )
