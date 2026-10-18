"""
Candidate Skill & Project Matcher Engine.
Aligns candidate credentials and proof-of-work repositories against job requisitions.
"""

from __future__ import annotations

import re
from typing import List, Dict, Set, Tuple

from .core import CandidateProfile, JobPosting, ProjectShowcase, SkillMatchResult, TECH_DOMAINS


class CandidateMatcher:
    """
    Evaluates candidate fit against job requirements, filtering out
    recruiter fluff while highlighting proof-of-work achievements.
    """

    def __init__(self, profile: CandidateProfile):
        self.profile = profile

    def _normalize(self, text: str) -> str:
        return text.lower().strip()

    def match(self, job: JobPosting) -> SkillMatchResult:
        candidate_skills = {self._normalize(s) for s in self.profile.skills}
        
        # Add tech stack from candidate's featured projects
        for proj in self.profile.featured_projects:
            for t in proj.tech_stack:
                candidate_skills.add(self._normalize(t))

        # Detect job required skills
        job_text = self._normalize(job.description + " " + " ".join(job.requirements))
        job_skills: Set[str] = set()

        for domain, keywords in TECH_DOMAINS.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", job_text):
                    job_skills.add(kw)

        # Detect candidate's known skills mentioned in job text
        for s in candidate_skills:
            if re.search(r"\b" + re.escape(s) + r"\b", job_text):
                job_skills.add(s)

        # Match skills
        matched = sorted(list(job_skills.intersection(candidate_skills)))
        missing = sorted(list(job_skills.difference(candidate_skills)))

        # Identify superfluous/buzzword requirements
        superfluous: List[str] = []
        if len(job_skills) > 10:
            superfluous.append(f"Demanding {len(job_skills)} disparate technologies simultaneously (Unicorn Requisition)")

        # Match candidate projects to job requirements
        aligned_projects: List[ProjectShowcase] = []
        for proj in self.profile.featured_projects:
            proj_tech = {self._normalize(t) for t in proj.tech_stack}
            if proj_tech.intersection(job_skills) or any(self._normalize(w) in job_text for w in proj.name.split("-")):
                aligned_projects.append(proj)

        # If no project directly matched, include all featured projects as proof of work
        if not aligned_projects and self.profile.featured_projects:
            aligned_projects = self.profile.featured_projects[:2]

        # Calculate match score
        if not job_skills:
            score = 75.0
        else:
            base_ratio = len(matched) / max(len(job_skills), 1)
            # Bonus for strong open-source project alignment
            proj_bonus = min(len(aligned_projects) * 10.0, 25.0)
            score = min(round((base_ratio * 75.0) + proj_bonus, 1), 100.0)

        # Generate key selling points
        selling_points: List[str] = []
        if matched:
            selling_points.append(f"Direct hands-on production mastery in {', '.join(matched[:4])}.")
        for proj in aligned_projects[:2]:
            selling_points.append(f"Proven open-source implementation: '{proj.name}' ({proj.description[:70]}...).")

        return SkillMatchResult(
            match_score=score,
            matched_skills=matched,
            missing_skills=missing,
            superfluous_job_demands=superfluous,
            aligned_projects=aligned_projects,
            key_selling_points=selling_points
        )

    def generate_tailored_bullets(self, job: JobPosting, match_result: SkillMatchResult) -> List[str]:
        """
        Synthesizes 3-4 tailored resume bullet points highlighting candidate proof-of-work
        targeted directly at the company's tech stack.
        """
        bullets: List[str] = []
        target_company = job.company if job.company != "Unknown Company" else "high-scale architectures"
        
        for proj in match_result.aligned_projects:
            for hl in proj.highlights[:2]:
                bullet = f"• Built and maintained {proj.name} ({proj.github_url}): {hl}"
                bullets.append(bullet)

        if not bullets:
            bullets.append(
                f"• Architected resilient, high-throughput backend services using {', '.join(self.profile.skills[:3])}, driving zero-friction reliability."
            )
            bullets.append(
                f"• Automated cross-system integrations and tool pipelines for {target_company}, reducing manual overhead and latency."
            )

        return bullets[:4]
