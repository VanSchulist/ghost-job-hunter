"""
Ghost Job Hunter v2.0
Autonomous Anti-Ghost Job Hunting & Direct Outreach Agent powered by mcp-mesh.
Detects phantom job postings, audits company GitHub stacks, and synthesizes executive bypass pitches.
Curated & Vibe-Coded by Van Schulist (@VanSchulist) / Existential Cloud.
"""

from .core import (
    DiagnosticReport, HeuristicSignal, JobPosting, CompanyAudit,
    CandidateProfile, ProjectShowcase, SkillMatchResult, HuntResult
)
from .analyzer import JobAnalyzer
from .agent import JobHunterAgent
from .mesh_client import MeshClient
from .github_auditor import CompanyGitHubAuditor
from .matcher import CandidateMatcher
from .candidate import get_default_candidate, load_candidate_from_file
from .generator import (
    generate_executive_bypass, generate_targeted_pitch,
    generate_comprehensive_report, generate_executive_bypass_from_params
)

__version__ = "2.0.0"
__author__ = "Van Schulist (Existential Cloud)"
__license__ = "MIT"

__all__ = [
    "DiagnosticReport",
    "HeuristicSignal",
    "JobPosting",
    "CompanyAudit",
    "CandidateProfile",
    "ProjectShowcase",
    "SkillMatchResult",
    "HuntResult",
    "JobAnalyzer",
    "JobHunterAgent",
    "MeshClient",
    "CompanyGitHubAuditor",
    "CandidateMatcher",
    "get_default_candidate",
    "load_candidate_from_file",
    "generate_executive_bypass",
    "generate_targeted_pitch",
    "generate_comprehensive_report",
    "generate_executive_bypass_from_params",
    "__version__",
]
