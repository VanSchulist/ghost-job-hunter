"""
Real-World Outreach Package and RFC 822 Email (.eml) Exporter.
Zero external dependencies (uses standard library email.message, urllib.parse, pathlib).
"""

from __future__ import annotations

import os
import re
import urllib.parse
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Any, Optional

from .core import HuntResult, CandidateProfile
from .candidate import get_default_candidate


def sanitize_filename(name: str) -> str:
    """Sanitizes a string for safe use in file paths."""
    clean = re.sub(r"[^\w\-]", "_", name.strip().lower())
    return re.sub(r"_+", "_", clean).strip("_")


class OutreachExporter:
    """
    Exports comprehensive, ready-to-dispatch job application materials.
    """

    def __init__(self, output_base_dir: Optional[str | Path] = None):
        if output_base_dir is None:
            self.output_base = Path("outreach")
        else:
            self.output_base = Path(output_base_dir)

    def export(
        self,
        hunt_result: HuntResult,
        candidate: Optional[CandidateProfile] = None,
        recipient_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates:
          1. <output_dir>/<company>/application.eml (Standard RFC 822 email file)
          2. <output_dir>/<company>/dossier.md (Full strategic analysis & pitch)
          3. Clickable mailto: link
        """
        if candidate is None:
            candidate = get_default_candidate()

        company = hunt_result.job.company
        title = hunt_result.job.title
        comp_slug = sanitize_filename(company)

        target_dir = self.output_base / comp_slug
        target_dir.mkdir(parents=True, exist_ok=True)

        # 1. Determine recipient email
        if not recipient_email:
            # Check if email is embedded in description or url
            email_match = re.search(r"[\w.-]+@[\w.-]+\.\w+", hunt_result.job.description)
            if email_match:
                to_addr = email_match.group(0)
            else:
                domain = re.sub(r"[^\w]", "", company.lower()) + ".com"
                to_addr = f"hiring@{domain}"
        else:
            to_addr = recipient_email

        # 2. Craft subject line
        subject = f"Application: {title} - {company} ({candidate.name} - Systems/Backend)"

        # 3. Build email plain text body
        body_lines = [
            f"Hi {company} Engineering Team,",
            "",
            f"I came across your opening for {title} and wanted to reach out directly with my engineering background.",
            "",
            "--- Why My Background Aligns ---",
        ]

        if hunt_result.tailored_bullets:
            for b in hunt_result.tailored_bullets:
                body_lines.append(f"• {b}")
        else:
            for proj in candidate.featured_projects[:2]:
                body_lines.append(f"• {proj.name}: {proj.description} ({proj.github_url})")

        body_lines.extend([
            "",
            "--- Proof of Work & Repositories ---",
            f"• GitHub Profile: https://github.com/{candidate.github_username}",
        ])
        for p in candidate.featured_projects:
            if p.github_url:
                body_lines.append(f"• {p.name}: {p.github_url}")

        if hunt_result.job.url:
            body_lines.extend([
                "",
                f"Referenced Posting: {hunt_result.job.url}",
            ])

        body_lines.extend([
            "",
            "I'd welcome 15 minutes to discuss how my systems engineering experience can directly benefit your roadmap.",
            "",
            f"Best regards,",
            f"{candidate.name}",
            f"{candidate.contact_email}",
            f"https://github.com/{candidate.github_username}",
        ])

        email_body = "\n".join(body_lines)

        # 4. Generate RFC 822 .eml file
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{candidate.name} <{candidate.contact_email}>"
        msg["To"] = to_addr
        msg["User-Agent"] = "GhostJobHunter/2.1 Autonomous Outreach"
        msg.set_content(email_body, charset="utf-8")

        eml_path = target_dir / "application.eml"
        with open(eml_path, "wb") as f:
            f.write(msg.as_bytes())

        # 5. Generate Markdown strategic dossier
        dossier_lines = [
            f"# Tactical Application Dossier: {company} - {title}",
            "",
            f"- **Target Role**: {title}",
            f"- **Company**: {company}",
            f"- **Salary Tier**: {hunt_result.job.salary_raw or 'Not disclosed'}",
            f"- **Ghost Probability Index (GPI)**: {hunt_result.diagnostic_report.ghost_probability_index:.1f}% ({hunt_result.diagnostic_report.risk_level})",
            f"- **Recommended Strategy**: `{hunt_result.recommended_strategy}`",
            "",
            "## 1. Candidate Fit & Proof-of-Work Alignment",
        ]
        if hunt_result.match_result:
            dossier_lines.extend([
                f"- **Overall Match Score**: {hunt_result.match_result.match_score:.1f}%",
                f"- **Matched Skills**: {', '.join(hunt_result.match_result.matched_skills) or 'None'}",
                f"- **Missing Skills**: {', '.join(hunt_result.match_result.missing_skills) or 'None'}",
                f"- **Aligned Portfolio**: {', '.join(p.name for p in hunt_result.match_result.aligned_projects)}",
            ])

        if hunt_result.company_audit:
            dossier_lines.extend([
                "",
                "## 2. Public GitHub Footprint Audit",
                f"- **GitHub Org**: `{hunt_result.company_audit.github_org}`",
                f"- **Public Repositories**: {hunt_result.company_audit.public_repos_count}",
                f"- **Engineering Health**: {hunt_result.company_audit.engineering_health_score}/100",
                f"- **Top Languages**: {', '.join(hunt_result.company_audit.top_languages.keys())}",
                f"- **Active Repos**: {', '.join(hunt_result.company_audit.active_repos)}",
            ])
            if hunt_result.company_audit.discrepancy_flags:
                dossier_lines.append("\n**Discrepancy Flags**:")
                for fl in hunt_result.company_audit.discrepancy_flags:
                    dossier_lines.append(f"- ⚠️ {fl}")

        dossier_lines.extend([
            "",
            "## 3. Executive Pitch & Outreach Draft",
            "```text",
            email_body,
            "```",
            "",
            "## 4. Next Actions",
            f"1. Double click `{eml_path.name}` to open pre-filled draft in your mail client.",
            f"2. Or apply directly at: {hunt_result.job.url or to_addr}",
        ])

        dossier_path = target_dir / "dossier.md"
        dossier_path.write_text("\n".join(dossier_lines), encoding="utf-8")

        # 6. Build mailto URL
        mailto_params = {
            "subject": subject,
            "body": email_body,
        }
        mailto_uri = f"mailto:{to_addr}?" + urllib.parse.urlencode(mailto_params, quote_via=urllib.parse.quote)

        return {
            "eml_path": str(eml_path.resolve()),
            "dossier_path": str(dossier_path.resolve()),
            "recipient": to_addr,
            "subject": subject,
            "mailto_uri": mailto_uri,
        }
