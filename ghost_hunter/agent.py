"""
Autonomous Multi-Role Job Hunter Agent.
Orchestrates job scouting, ghost requisition auditing, GitHub tech stack verification,
and candidate matching dynamically through the mcp-mesh tool gateway.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import urllib.request

from .core import (
    JobPosting, DiagnosticReport, CompanyAudit, CandidateProfile,
    SkillMatchResult, HuntResult, HeuristicSignal
)
from .candidate import get_default_candidate, load_candidate_from_file
from .mesh_client import MeshClient
from .generator import generate_comprehensive_report


class JobHunterAgent:
    """
    Autonomous Job Hunter Agent powered by the mcp-mesh dynamic gateway.
    Coordinates specialized roles without Turn-0 schema bloat:
    - Scout: Ingests job requisitions
    - Ghost Auditor: Calculates Ghost Probability Index (GPI)
    - Tech Auditor: Verifies company GitHub engineering footprint
    - Tailor: Matches candidate proof-of-work and synthesizes outreach
    """

    def __init__(
        self,
        mesh_client: Optional[MeshClient] = None,
        candidate_profile: Optional[CandidateProfile] = None
    ):
        self.mesh = mesh_client or MeshClient()
        self.candidate = candidate_profile or get_default_candidate()

    def _resolve_target_input(
        self,
        target: str,
        title: Optional[str] = None,
        company: Optional[str] = None
    ) -> JobPosting:
        """
        Parses raw text, file path, URL, or sample benchmark into a JobPosting.
        """
        # 1. Check if target is a sample shortcut
        from .sample_data import GHOST_SAMPLE, LEGIT_SAMPLE, COMPLIANCE_SAMPLE
        lower_t = target.lower().strip()
        if lower_t in ["ghost", "sample_ghost"]:
            return JobPosting(
                title=title or "Principal Solutions Architect",
                company=company or "Apex Global Tech",
                description=GHOST_SAMPLE
            )
        elif lower_t in ["legit", "sample_legit"]:
            return JobPosting(
                title=title or "Staff Backend Infrastructure Engineer",
                company=company or "ScaleScale Systems",
                description=LEGIT_SAMPLE
            )
        elif lower_t in ["compliance", "sample_compliance"]:
            return JobPosting(
                title=title or "Senior Compliance Systems Analyst",
                company=company or "Legacy Financial Group",
                description=COMPLIANCE_SAMPLE
            )

        # 2. Check if target is a live query, e.g. "hn:neuralframe", "remoteok:onebrief", "wwr:duckduckgo"
        prefixes = ("hn:", "remoteok:", "wwr:", "live:", "online:")
        if lower_t.startswith(prefixes) or lower_t in ["hn", "remoteok", "wwr", "live"]:
            from .sources import UnifiedJobSource
            source = UnifiedJobSource()
            job = source.resolve_target(target)
            if job:
                if title:
                    job.title = title
                if company:
                    job.company = company
                return job

        # 2. Check if target is a URL
        if target.startswith("http://") or target.startswith("https://"):
            try:
                req = urllib.request.Request(
                    target,
                    headers={"User-Agent": "GhostJobHunter/2.0 (+https://github.com/VanSchulist)"}
                )
                with urllib.request.urlopen(req, timeout=8) as res:
                    content = res.read().decode("utf-8", errors="ignore")
                return JobPosting(
                    title=title or "Scouted Requisition",
                    company=company or "Target Company",
                    description=content,
                    url=target
                )
            except Exception as e:
                # If network fails, treat target as raw text
                pass

        # 3. Check if target is a local file path
        p = Path(target)
        if p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8", errors="ignore")
            derived_title = title or p.stem.replace("_", " ").title()
            derived_company = company or "Target Company"
            return JobPosting(
                title=derived_title,
                company=derived_company,
                description=content
            )

        # 4. Check if target is a company name or short query (e.g. "NeuralFrame", "DuckDuckGo", "Onebrief")
        if len(target.strip()) < 120 and "\n" not in target:
            try:
                from .sources import UnifiedJobSource
                source = UnifiedJobSource()
                job = source.resolve_target(target)
                if job:
                    if title:
                        job.title = title
                    if company:
                        job.company = company
                    return job
            except Exception:
                pass

        # 5. Fallback: target is raw text description
        return JobPosting(
            title=title or "Software Engineer",
            company=company or "Target Company",
            description=target
        )

    def hunt(
        self,
        target_input: str,
        title: Optional[str] = None,
        company: Optional[str] = None,
        candidate_profile: Optional[CandidateProfile] = None,
        mock_github_data: Optional[List[Dict[str, Any]]] = None
    ) -> HuntResult:
        """
        Executes the autonomous end-to-end hunting workflow via mcp-mesh tool calls.
        """
        profile = candidate_profile or self.candidate
        job = self._resolve_target_input(target_input, title=title, company=company)

        # -------------------------------------------------------------
        # Phase 1: Dynamic Discovery & Ghost Heuristic Audit
        # -------------------------------------------------------------
        # In a standard static setup, all 10+ tool schemas would be injected into context.
        # With mcp-mesh, the agent dynamically searches for the audit tool:
        discovered_audit = self.mesh.search_tools("audit ghost job posting heuristics", limit=1)
        audit_tool_name = discovered_audit[0]["name"] if discovered_audit else "ghost_hunter::audit_posting"

        # Invoke audit tool
        audit_res = self.mesh.invoke_tool(audit_tool_name, {
            "text": job.description,
            "title": job.title,
            "company": job.company
        })

        signals = [
            HeuristicSignal(
                id=s["id"],
                name=s["name"],
                weight=s.get("weight", 0.2),
                score=s["score"],
                triggered=s["triggered"],
                evidence=s["evidence"],
                description=s.get("description", "")
            )
            for s in audit_res.get("signals", [])
        ]

        diagnostic_report = DiagnosticReport(
            job_title=audit_res.get("job_title", job.title),
            company_name=audit_res.get("company_name", job.company),
            ghost_probability_index=audit_res.get("ghost_probability_index", 50.0),
            risk_level=audit_res.get("risk_level", "LOW_CONFIDENCE"),
            verdict_summary=audit_res.get("verdict_summary", ""),
            signals=signals,
            salary_analysis=audit_res.get("salary_analysis", {}),
            key_responsibilities=[],
            detected_tech_stack=[],
            actionable_recommendation=audit_res.get("recommendation", "")
        )

        # -------------------------------------------------------------
        # Phase 2: Dynamic Company GitHub Stack Audit
        # -------------------------------------------------------------
        discovered_github = self.mesh.search_tools("audit company github tech stack", limit=1)
        github_tool_name = discovered_github[0]["name"] if discovered_github else "ghost_hunter::audit_company_github"

        # Pass detected domains as claimed tech stack
        claimed_tech = []
        for s in diagnostic_report.signals:
            if s.id == "UNICORN_PARADOX":
                for ev in s.evidence:
                    claimed_tech.append(ev)

        github_res = self.mesh.invoke_tool(github_tool_name, {
            "company_name": job.company,
            "claimed_tech_stack": claimed_tech,
            "mock_data": mock_github_data
        })

        company_audit = CompanyAudit(
            company_name=github_res.get("company_name", job.company),
            github_org=github_res.get("github_org", ""),
            public_repos_count=github_res.get("public_repos_count", 0),
            top_languages=github_res.get("top_languages", {}),
            active_repos=github_res.get("active_repos", []),
            last_commit_date=github_res.get("last_commit_date", "Unknown"),
            verified_tech_stack=github_res.get("verified_tech_stack", []),
            discrepancy_flags=github_res.get("discrepancy_flags", []),
            engineering_health_score=github_res.get("engineering_health_score", 70.0)
        )

        # -------------------------------------------------------------
        # Phase 3: Dynamic Candidate Proof-of-Work Alignment
        # -------------------------------------------------------------
        discovered_match = self.mesh.search_tools("match candidate skills resume", limit=1)
        match_tool_name = discovered_match[0]["name"] if discovered_match else "ghost_hunter::match_candidate"

        match_res = self.mesh.invoke_tool(match_tool_name, {
            "job_posting": {
                "title": job.title,
                "company": job.company,
                "description": job.description,
                "requirements": job.requirements
            },
            "candidate_profile": {
                "name": profile.name,
                "title": profile.title,
                "bio": profile.bio,
                "github_username": profile.github_username,
                "skills": profile.skills,
                "featured_projects": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "github_url": p.github_url,
                        "tech_stack": p.tech_stack,
                        "highlights": p.highlights
                    }
                    for p in profile.featured_projects
                ]
            }
        })

        skill_match = SkillMatchResult(
            match_score=match_res.get("match_score", 80.0),
            matched_skills=match_res.get("matched_skills", []),
            missing_skills=match_res.get("missing_skills", []),
            superfluous_job_demands=[],
            aligned_projects=profile.featured_projects,
            key_selling_points=match_res.get("key_selling_points", [])
        )
        tailored_bullets = match_res.get("tailored_bullets", [])

        # -------------------------------------------------------------
        # Phase 4: Tactical Strategy & Outreach Synthesis
        # -------------------------------------------------------------
        gpi = diagnostic_report.ghost_probability_index
        if gpi >= 65.0:
            strategy = "AVOID_GHOST"
        elif gpi >= 40.0:
            strategy = "EXECUTIVE_BYPASS"
        else:
            strategy = "TARGETED_ATS"

        pitch_tool_name = "ghost_hunter::generate_pitch"
        pitch_res = self.mesh.invoke_tool(pitch_tool_name, {
            "strategy": "EXECUTIVE_BYPASS" if strategy != "TARGETED_ATS" else "TARGETED_ATS",
            "job_title": job.title,
            "company_name": job.company,
            "selling_points": skill_match.key_selling_points
        })
        generated_pitch = pitch_res.get("pitch", "")

        # Token Economy Telemetry
        tok_stats = self.mesh.get_token_economy_stats()

        return HuntResult(
            job=job,
            diagnostic_report=diagnostic_report,
            company_audit=company_audit,
            match_result=skill_match,
            recommended_strategy=strategy,
            generated_pitch=generated_pitch,
            tailored_bullets=tailored_bullets,
            token_economy=tok_stats
        )
