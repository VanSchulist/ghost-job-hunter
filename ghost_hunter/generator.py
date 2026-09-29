"""
Executive Bypass Pitch Generator.
Synthesizes a 1-page high-converting cold outreach letter to the department head
when an ATS portal posting is flagged as a Ghost Job or Resume Harvest.
"""

from typing import Dict, Optional
from .core import DiagnosticReport

def generate_executive_bypass(
    report: DiagnosticReport,
    sender_name: str = "[Your Full Name]",
    sender_title: str = "[Your Senior Professional Title]",
    key_achievement: str = "[e.g., Reduced cloud infrastructure spend by 32% while maintaining 99.99% uptime]",
    department_head_title: str = "VP of Engineering / Operations"
) -> str:
    """
    Generates a battle-tested Executive Value Pitch letter based on Chapter 6
    tactics from The Career Reboot Armor.
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
