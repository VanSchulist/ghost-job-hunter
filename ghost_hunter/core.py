"""
Core Heuristic Definitions and Risk Scoring Engine for Ghost Job Hunter.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import re

@dataclass
class HeuristicSignal:
    id: str
    name: str
    weight: float  # Importance weight (0.0 to 1.0)
    score: float   # Triggered score (0.0 to 100.0)
    triggered: bool
    evidence: List[str]
    description: str

@dataclass
class DiagnosticReport:
    """Diagnostic assessment produced by heuristic signal analyzers.

    NOTE: 'ghost_probability_index' is an empirical heuristic risk indicator (0.0 to 100.0)
    evaluating linguistic and structural patterns typical of low-intent requisitions.
    It represents a heuristic risk score rather than a formally calibrated Bayesian posterior probability.
    """
    job_title: str
    company_name: str
    ghost_probability_index: float  # 0.0 to 100.0% heuristic risk score
    risk_level: str  # ACTIVE | LOW_CONFIDENCE | SUSPECTED_HARVEST | CRITICAL_GHOST
    verdict_summary: str
    signals: List[HeuristicSignal]
    salary_analysis: Dict[str, Optional[float]]
    key_responsibilities: List[str]
    detected_tech_stack: List[str]
    actionable_recommendation: str

# ----------------------------------------------------------------------
# Heuristic Dictionaries & Pattern Definitions
# ----------------------------------------------------------------------

EVERGREEN_PATTERNS = [
    r"\bevergreen\s+requisition\b",
    r"\bcontinuous\s+pipeline\b",
    r"\btalent\s+pipeline\b",
    r"\btalent\s+community\b",
    r"\bfuture\s+consideration\b",
    r"\bgeneral\s+application\b",
    r"\bexpressions?\s+of\s+interest\b",
    r"\balways\s+looking\s+for\s+talented\b",
    r"\bongoing\s+(need|recruitment|search)\b",
    r"\banticipated\s+(opening|need|vacancy)\b",
    r"\bbench\s+building\b",
    r"\bproactive\s+sourcing\b",
    r"\bnot\s+an\s+active\s+opening\b",
    r"\bthis\s+is\s+a\s+pipeline\s+posting\b",
]

COMPLIANCE_THEATER_PATTERNS = [
    r"\bmay\s+be\s+subject\s+to\s+internal\s+transfer\b",
    r"\binternal\s+candidates?\s+being\s+considered\b",
    r"\bposted\s+to\s+satisfy\s+immigration\b",
    r"\blabor\s+certification\b",
    r"\bperm\s+filing\b",
    r"\bfor\s+compliance\s+purposes\s+only\b",
]

FLUFF_TERMS = [
    "rockstar", "ninja", "guru", "wizard", "superhero", "evangelist",
    "fast-paced", "wear many hats", "dynamic environment", "hit the ground running",
    "self-starter", "synergy", "synergistic", "paradigm", "disruptor", "game-changer",
    "hyper-growth", "crush it", "work hard play hard", "family atmosphere",
    "bleeding edge", "passion-driven", "culture fit", "radical transparency",
    "high-octane", "unlimited potential"
]

DELIVERABLE_VERBS = [
    "architect", "build", "deploy", "design", "refactor", "reduce", "increase",
    "optimize", "lead", "manage", "monitor", "maintain", "integrate", "scale",
    "automate", "ship", "benchmark", "audit", "migrate", "spearhead", "budget"
]

TECH_DOMAINS = {
    "Frontend": ["react", "vue", "angular", "next.js", "tailwind", "typescript", "css3", "svelte"],
    "Backend / Systems": ["golang", "rust", "c++", "java", "spring boot", "python", "fastapi", "django", "node.js"],
    "DevOps / Infrastructure": ["kubernetes", "docker", "terraform", "ansible", "aws", "gcp", "azure", "ci/cd", "prometheus", "helm"],
    "Data / ML": ["pytorch", "tensorflow", "spark", "kafka", "snowflake", "databricks", "hadoop", "pandas", "airflow"],
    "Sales / GTM": ["salesforce", "hubspot", "cold calling", "prospecting", "lead generation", "quota", "bdr", "outreach"],
    "Compliance / Finance": ["sox", "hipaa", "gdpr", "pci-dss", "audit", "balance sheet", "gaap", "ifrs"]
}


# ----------------------------------------------------------------------
# Agentic & Multi-Tool Data Models (Ghost Hunter v2.0)
# ----------------------------------------------------------------------

@dataclass
class JobPosting:
    title: str
    company: str
    description: str
    location: str = "Remote / Unspecified"
    salary_raw: str = ""
    url: str = ""
    posted_date: str = ""
    requirements: List[str] = field(default_factory=list)
    detected_tech_stack: List[str] = field(default_factory=list)


@dataclass
class CompanyAudit:
    company_name: str
    github_org: str = ""
    public_repos_count: int = 0
    top_languages: Dict[str, int] = field(default_factory=dict)
    active_repos: List[str] = field(default_factory=list)
    last_commit_date: str = ""
    verified_tech_stack: List[str] = field(default_factory=list)
    discrepancy_flags: List[str] = field(default_factory=list)
    engineering_health_score: float = 100.0  # 0 to 100


@dataclass
class ProjectShowcase:
    name: str
    description: str
    github_url: str = ""
    tech_stack: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)


@dataclass
class CandidateProfile:
    name: str
    title: str
    bio: str
    github_username: str = ""
    skills: List[str] = field(default_factory=list)
    featured_projects: List[ProjectShowcase] = field(default_factory=list)
    contact_email: str = ""
    linkedin_url: str = ""


@dataclass
class SkillMatchResult:
    match_score: float  # 0.0 to 100.0%
    matched_skills: List[str]
    missing_skills: List[str]
    superfluous_job_demands: List[str]
    aligned_projects: List[ProjectShowcase]
    key_selling_points: List[str]


@dataclass
class HuntResult:
    job: JobPosting
    diagnostic_report: DiagnosticReport
    company_audit: Optional[CompanyAudit]
    match_result: Optional[SkillMatchResult]
    recommended_strategy: str  # "EXECUTIVE_BYPASS" | "TARGETED_ATS" | "AVOID_GHOST"
    generated_pitch: str
    tailored_bullets: List[str] = field(default_factory=list)
    token_economy: Dict[str, Any] = field(default_factory=dict)

