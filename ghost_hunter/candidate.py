"""
Candidate Profile Management & Built-in Van Schulist Profile.
Supports loading custom profiles from JSON files or utilizing default persona.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict, Any

from .core import CandidateProfile, ProjectShowcase


def get_default_candidate() -> CandidateProfile:
    """
    Returns the battle-tested profile for Van Schulist (Existential Cloud founder).
    """
    return CandidateProfile(
        name="Van Schulist",
        title="Distributed Systems & Autonomous Agent Engineer",
        bio="Undergraduate student & founder of Existential Cloud. Author of mcp-mesh and career-reboot-armor.",
        github_username="VanSchulist",
        skills=[
            "python", "asyncio", "mcp", "json-rpc", "distributed systems",
            "token optimization", "sqlite", "git", "api design",
            "cli tooling", "linux", "subprocesses", "heuristics"
        ],
        featured_projects=[
            ProjectShowcase(
                name="mcp-mesh",
                description="Dynamic Model Context Protocol gateway and lazy tool router cutting Turn-0 token consumption by 90% via BM25 indexing.",
                github_url="https://github.com/VanSchulist/mcp-mesh",
                tech_stack=["python", "mcp", "json-rpc", "sqlite", "sse", "cli"],
                highlights=[
                    "Engineered zero-dependency JSON-RPC stdio router supervising 50+ upstream MCP servers.",
                    "Implemented inverted index BM25 search reducing schema context from 25,000 to ~380 tokens.",
                    "Achieved 100% test pass rate with Simon Willison style SQLite telemetry."
                ]
            ),
            ProjectShowcase(
                name="ghost-job-hunter",
                description="Autonomous heuristic and multi-agent system detecting phantom job listings and generating direct executive bypass pitches.",
                github_url="https://github.com/VanSchulist/ghost-job-hunter",
                tech_stack=["python", "heuristics", "mcp", "nlp", "automation"],
                highlights=[
                    "Built 5 diagnostic heuristic engines detecting evergreen requisitions and compliance theater.",
                    "Integrated company GitHub stack auditing to verify actual codebase vs recruiter claims.",
                    "Designed automated executive cold pitch generator with high conversion rate."
                ]
            ),
            ProjectShowcase(
                name="mcp-registry-cli",
                description="Unified cross-client CLI tool and registry synchronizer for Model Context Protocol servers.",
                github_url="https://github.com/VanSchulist/mcp-registry-cli",
                tech_stack=["python", "json", "cli", "antigravity", "claude-desktop"],
                highlights=[
                    "Supports multi-client synchronization across Claude Desktop, Cursor, and Antigravity.",
                    "Built semantic search and verification for upstream open-source MCP repositories."
                ]
            )
        ],
        contact_email="van@existentialcloud.ccwu.cc",
        linkedin_url="https://github.com/VanSchulist"
    )


def load_candidate_from_file(file_path: str | Path) -> CandidateProfile:
    """Loads a CandidateProfile from a JSON configuration file."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Candidate profile file not found: {file_path}")
    
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    projects = []
    for proj in data.get("featured_projects", []):
        projects.append(
            ProjectShowcase(
                name=proj.get("name", "Project"),
                description=proj.get("description", ""),
                github_url=proj.get("github_url", ""),
                tech_stack=proj.get("tech_stack", []),
                highlights=proj.get("highlights", [])
            )
        )
        
    return CandidateProfile(
        name=data.get("name", "Candidate"),
        title=data.get("title", "Software Engineer"),
        bio=data.get("bio", ""),
        github_username=data.get("github_username", ""),
        skills=data.get("skills", []),
        featured_projects=projects,
        contact_email=data.get("contact_email", ""),
        linkedin_url=data.get("linkedin_url", "")
    )


def save_candidate_to_file(profile: CandidateProfile, file_path: str | Path) -> None:
    """Saves a CandidateProfile to a JSON configuration file."""
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "name": profile.name,
        "title": profile.title,
        "bio": profile.bio,
        "github_username": profile.github_username,
        "skills": profile.skills,
        "featured_projects": [
            {
                "name": proj.name,
                "description": proj.description,
                "github_url": proj.github_url,
                "tech_stack": proj.tech_stack,
                "highlights": proj.highlights
            }
            for proj in profile.featured_projects
        ],
        "contact_email": profile.contact_email,
        "linkedin_url": profile.linkedin_url
    }
    
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
