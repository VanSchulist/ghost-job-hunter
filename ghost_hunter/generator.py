"""
Executive Bypass Pitch & Targeted Application Generator.
Synthesizes high-converting cold outreach letters, bypass pitches,
and comprehensive strategic dossiers.
"""

from typing import Dict, Optional, List, Any
from .core import DiagnosticReport, CompanyAudit, SkillMatchResult, CandidateProfile, JobPosting, HuntResult


def generate_executive_bypass(
    report: DiagnosticReport,
    sender_name: str = "[Your Full Name]",
    sender_title: str = "[Your Senior Professional Title]",
    key_achievement: str = "[e.g., Reduced cloud infrastructure spend by 32% while maintaining 99.99% uptime]",
    department_head_title: str = "VP of Engineering / Operations"
) -> str:
    """
    Generates a battle-tested Executive Value Pitch letter based on Chapter 6
    tactics from The Career Reboot Armor. (Backward-compatible).
    """
    company = report.company_name if report.company_name != "Unknown Company" else "[Target Company]"
    title = report.job_title if report.job_title != "Unknown Title" else "[Target Role]"

    letter = f"""================================================================================
EXECUTIVE BYPASS VALUE PITCH
Target: {department_head_title} at {company}
Re: Direct Operational Value & {title} Objectives
Framework: Existential Cloud / Career Reboot Protocol
================================================================================

SUBJECT: Question regarding {company}'s {title} roadmap & operational scaling

Dear {department_head_title},

I noticed {company}'s public requisition for the {title} position. Given typical corporate recruiting cycles and automated portal backlogs, I am reaching out directly to focus on the operational challenges your team is actively addressing.

Over the past decade leading high-stakes initiatives, my focus has been executing measurable business outcomes rather than bureaucratic process:

- Core Value Delivery: {key_achievement}
- Systems Architecture: Engineered scalable, resilient operational frameworks that eliminated single points of failure across cross-functional teams.
- Execution Discipline: Experienced in stabilizing ambiguous environments, driving rapid execution sprints, and delivering tangible deliverables from day one.

I understand that public requisitions often attract high volumes of generic ATS submissions. If you are currently evaluating senior leaders who can step in, diagnose core bottlenecks, and execute with zero onboarding friction, I would welcome a brief 10-minute introductory conversation.

Even if your immediate headcount is currently allocated, I would be glad to share a 1-page tear-sheet on how we addressed comparable architecture bottlenecks in similar environments.

Best regards,

{sender_name}
{sender_title}
[Phone Number] | [LinkedIn Profile URL] | [Email Address]
================================================================================
"""
    return letter


def generate_executive_bypass_from_params(
    company: str,
    title: str,
    key_selling_points: Optional[List[str]] = None,
    sender_name: str = "Van Schulist",
    sender_title: str = "Systems & Autonomous Agent Engineer",
    department_head_title: str = "VP of Engineering"
) -> str:
    """
    Synthesizes an Executive Bypass Pitch directly using dynamic candidate selling points.
    """
    points = key_selling_points or [
        "Architected zero-dependency MCP tool gateway cutting Turn-0 context bloat by 90%.",
        "Engineered autonomous heuristic and scraping pipelines with sub-5ms latency."
    ]
    points_str = "\n".join(f"- {p}" for p in points[:3])

    return f"""================================================================================
EXECUTIVE BYPASS VALUE PITCH (ATS PORTAL BYPASS)
Target: {department_head_title} at {company}
Re: {title} Architectural Bottlenecks & Operational Deliverables
Framework: Existential Cloud Career Protocol
================================================================================

SUBJECT: Engineering note on {company}'s {title} roadmap & system performance

Dear {department_head_title},

I came across {company}'s opening for {title}. Public recruiting portals often get swamped by hundreds of generic LLM resumes; I wanted to bypass the noise and share concrete evidence of work directly addressing your operational layer:

{points_str}

I build production-grade, zero-dependency tools with extreme reliability. Rather than going through a 6-week automated ATS pipeline, I'd welcome a brief 10-minute technical exchange to discuss your team's immediate Q3/Q4 engineering roadmap.

If immediate headcount is locked, feel free to inspect my open-source implementations on GitHub (https://github.com/VanSchulist).

Best regards,

{sender_name}
{sender_title} | Existential Cloud
GitHub: https://github.com/VanSchulist | Email: van@existentialcloud.ccwu.cc
================================================================================
"""


def generate_targeted_pitch(
    company: str,
    title: str,
    selling_points: Optional[List[str]] = None,
    sender_name: str = "Van Schulist",
    sender_title: str = "Distributed Systems & Agent Engineer"
) -> str:
    """
    Synthesizes a targeted, ATS-optimized cover pitch for legitimate, active requisitions.
    """
    pts = selling_points or ["Direct hands-on production mastery in Python, Asyncio, and Systems."]
    pts_str = "\n".join(f"- {p}" for p in pts[:3])

    return f"""================================================================================
TARGETED HIGH-CONVERSION APPLICATION PITCH
Role: {title} at {company}
Classification: ACTIVE REQUISITION (Verified Legitimacy)
================================================================================

SUBJECT: Application for {title} - {sender_name} (Open-Source Proof of Work)

Dear {company} Hiring Team,

I am writing to express my strong enthusiasm for the {title} role at {company}. Having reviewed your tech stack and public engineering footprint, I recognize the technical challenges your team is solving and have built directly relevant open-source systems:

Key Alignment & Proof of Work:
{pts_str}

My engineering philosophy centers on zero-dependency architectures, relentless token and latency efficiency, and shipping resilient, test-verified software. I would be thrilled to bring this execution discipline to {company}.

Thank you for your consideration, and I look forward to speaking with the team!

Warm regards,

{sender_name}
{sender_title}
GitHub: https://github.com/VanSchulist | Email: van@existentialcloud.ccwu.cc
================================================================================
"""


def generate_comprehensive_report(hunt: HuntResult) -> str:
    """
    Renders a complete, formatted tactical dossier combining:
    - Requisition & Ghost Probability Index (GPI)
    - Company GitHub Footprint & Tech Stack Reality Check
    - Candidate Match & Proof-of-Work Evidence
    - Strategic Tactical Recommendation
    - Token Economy Ledger (mcp-mesh impact)
    """
    rep = hunt.diagnostic_report
    audit = hunt.company_audit
    match = hunt.match_result
    tok = hunt.token_economy

    lines = []
    lines.append("=" * 80)
    lines.append(f"GHOST JOB HUNTER v2.0 - AUTONOMOUS TACTICAL DOSSIER")
    lines.append(f"Target Role   : {hunt.job.title}")
    lines.append(f"Target Company: {hunt.job.company}")
    lines.append(f"Strategy      : {hunt.recommended_strategy}")
    lines.append("=" * 80)

    # Section 1: Ghost Probability Index
    lines.append(f"\n[1] GHOST PROBABILITY AUDIT:")
    lines.append(f"  Ghost Probability Index (GPI): {rep.ghost_probability_index}%")
    lines.append(f"  Classification : [{rep.risk_level}]")
    lines.append(f"  Verdict        : {rep.verdict_summary}")
    lines.append(f"  Recommendation : {rep.actionable_recommendation}")

    # Section 2: GitHub Stack Reality Check
    if audit:
        lines.append(f"\n[2] COMPANY GITHUB & ENGINEERING FOOTPRINT AUDIT:")
        lines.append(f"  GitHub Org Slug     : {audit.github_org}")
        lines.append(f"  Public Repositories : {audit.public_repos_count}")
        lines.append(f"  Engineering Health  : {audit.engineering_health_score}/100")
        lines.append(f"  Top Languages       : {', '.join([f'{k} ({v})' for k, v in list(audit.top_languages.items())[:3]]) or 'None identified'}")
        lines.append(f"  Verified Tech Stack : {', '.join(audit.verified_tech_stack[:6]) or 'Closed Source'}")
        if audit.discrepancy_flags:
            lines.append("  Discrepancy Alerts  :")
            for flag in audit.discrepancy_flags:
                lines.append(f"    ! {flag}")

    # Section 3: Candidate Match & Proof-of-Work
    if match:
        lines.append(f"\n[3] CANDIDATE FIT & PROOF OF WORK:")
        lines.append(f"  Candidate Fit Score : {match.match_score}%")
        lines.append(f"  Matched Skills      : {', '.join(match.matched_skills) or 'None'}")
        lines.append(f"  Missing Skills      : {', '.join(match.missing_skills) or 'None'}")
        if match.superfluous_job_demands:
            lines.append(f"  Recruiter Fluff     : {', '.join(match.superfluous_job_demands)}")
        if match.aligned_projects:
            lines.append("  Aligned Repositories:")
            for proj in match.aligned_projects:
                lines.append(f"    * {proj.name} ({proj.github_url}): {proj.description[:75]}...")

    # Section 4: Tailored Resume Bullets
    if hunt.tailored_bullets:
        lines.append(f"\n[4] TAILORED ATS RESUME BULLET POINTS:")
        for b in hunt.tailored_bullets:
            lines.append(f"  {b}")

    # Section 5: Token Economy Stats
    if tok:
        lines.append(f"\n[5] MCP-MESH TOKEN ECONOMY TELEMETRY:")
        lines.append(f"  Turn-0 Baseline Context : {tok.get('baseline_turn0_tokens', 0)} tokens")
        lines.append(f"  mcp-mesh Gateway Footprint: {tok.get('mesh_turn0_tokens', 0)} tokens")
        lines.append(f"  Static Token Reduction  : {tok.get('static_savings_ratio', '0%')} ({tok.get('static_token_savings', 0)} tokens)")
        lines.append(f"  Runtime Tokens Saved    : {tok.get('runtime_tokens_saved', 0)} tokens across {tok.get('tool_invocations_count', 0)} tool calls")

    lines.append("\n" + "=" * 80)
    lines.append("GENERATED OUTREACH ARTIFACT:")
    lines.append("=" * 80)
    lines.append(hunt.generated_pitch)

    return "\n".join(lines)
