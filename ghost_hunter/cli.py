"""
Command Line Interface with Rich Visuals and mcp-mesh Tool Routing.
Zero external dependencies.
"""

from __future__ import annotations

import sys
import os
import argparse
import json
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from .core import DiagnosticReport, JobPosting
from .analyzer import JobAnalyzer
from .generator import generate_executive_bypass, generate_comprehensive_report
from .agent import JobHunterAgent
from .candidate import get_default_candidate, load_candidate_from_file, save_candidate_to_file
from .github_auditor import CompanyGitHubAuditor
from .matcher import CandidateMatcher
from .mesh_client import MeshClient
from .server import run_mcp_server

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

BANNER = rf"""{CYAN}{BOLD}
   ____ _   _  ___  ____ _____      _  ___  ____  
  / ___| | | |/ _ \/ ___|_   _|    | |/ _ \| __ ) 
 | |  _| |_| | | | \___ \ | |   _  | | | | |  _ \ 
 | |_| |  _  | |_| |___) || |  | |_| | |_| | |_) |
  \____|_| |_|\___/|____/ |_|   \___/ \___/|____/ 
  {MAGENTA}>> GHOST JOB HUNTER v2.0 | Autonomous mcp-mesh Agent <<{RESET}
  {DIM}Curated & Vibe-Coded by Van Schulist (@VanSchulist) | Existential Cloud{RESET}
"""

def render_meter(score: float) -> str:
    total_bars = 20
    filled = int((score / 100.0) * total_bars)
    empty = total_bars - filled
    
    if score >= 65:
        color = RED
    elif score >= 40:
        color = YELLOW
    elif score >= 20:
        color = BLUE
    else:
        color = GREEN
        
    bar = f"{color}[" + ("#" * filled) + ("-" * empty) + f"] {score:.1f}%{RESET}"
    return bar

def print_report(report: DiagnosticReport, json_output: bool = False):
    if json_output:
        data = {
            "job_title": report.job_title,
            "company_name": report.company_name,
            "ghost_probability_index": report.ghost_probability_index,
            "risk_level": report.risk_level,
            "verdict": report.verdict_summary,
            "recommendation": report.actionable_recommendation,
            "salary": report.salary_analysis,
            "signals": [
                {
                    "id": s.id,
                    "name": s.name,
                    "triggered": s.triggered,
                    "score": s.score,
                    "weight": s.weight,
                    "evidence": s.evidence
                } for s in report.signals
            ]
        }
        print(json.dumps(data, indent=2))
        return

    print("\n" + "=" * 76)
    print(f"{BOLD}DIAGNOSTIC REPORT:{RESET} {WHITE}{report.job_title}{RESET} @ {CYAN}{report.company_name}{RESET}")
    print("=" * 76)
    
    print(f"\n{BOLD}Ghost Probability Index (GPI):{RESET}")
    print(f"  {render_meter(report.ghost_probability_index)}")
    
    if report.risk_level == "CRITICAL_GHOST":
        badge = f"{RED}{BOLD}[ CRITICAL GHOST JOB / PIPELINE THEATER ]{RESET}"
    elif report.risk_level == "SUSPECTED_HARVEST":
        badge = f"{YELLOW}{BOLD}[ SUSPECTED RESUME HARVEST ]{RESET}"
    elif report.risk_level == "LOW_CONFIDENCE":
        badge = f"{BLUE}{BOLD}[ LOW-CONFIDENCE / AMBIGUOUS REQUISITION ]{RESET}"
    else:
        badge = f"{GREEN}{BOLD}[ ACTIVE REQUISITION ]{RESET}"
        
    print(f"\n{BOLD}Classification:{RESET} {badge}")
    print(f"{BOLD}Verdict:{RESET} {report.verdict_summary}")

    print("\n" + "-" * 76)
    print(f"{BOLD}{'SIGNAL EVALUATED':<40} {'WEIGHT':<8} {'SCORE':<8} {'STATUS'}{RESET}")
    print("-" * 76)
    
    for s in report.signals:
        status = f"{RED}TRIGGERED{RESET}" if s.triggered else f"{GREEN}CLEAR{RESET}"
        print(f"{s.name:<40} {s.weight:<8.2f} {s.score:<8.1f} {status}")
        if s.evidence:
            for ev in s.evidence:
                print(f"  {DIM}-> {ev}{RESET}")

    if report.salary_analysis.get("min"):
        sal = report.salary_analysis
        print("\n" + "-" * 76)
        print(f"{BOLD}COMPENSATION TRANSPARENCY AUDIT:{RESET}")
        print(f"  Disclosed Range: ${sal['min']:,.0f} - ${sal['max']:,.0f}")
        print(f"  Spread Ratio:    {int(sal['spread_ratio'] * 100)}% " + 
              (f"{RED}(Extreme - likely pay transparency evasion){RESET}" if sal['spread_ratio'] > 1.2 else f"{GREEN}(Normal){RESET}"))

    print("\n" + "=" * 76)
    print(f"{BOLD}ACTIONABLE TACTICAL RECOMMENDATION:{RESET}")
    print(f"  {report.actionable_recommendation}")
    print("=" * 76 + "\n")


def register_with_mcp_mesh() -> None:
    """
    Registers ghost-job-hunter into mcp_config.json for Antigravity and mcp-mesh.
    """
    config_path = Path.home() / ".gemini" / "config" / "mcp_config.json"
    if not config_path.parent.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)

    data = {"mcpServers": {}}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    server_entry = {
        "command": sys.executable,
        "args": ["-m", "ghost_hunter.server"],
        "env": {},
        "description": "Ghost Job Hunter v2.0 - Autonomous anti-ghost job hunting & ATS bypass agent"
    }

    data.setdefault("mcpServers", {})["ghost-job-hunter"] = server_entry

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"{GREEN}[+]{RESET} Successfully registered 'ghost-job-hunter' in {config_path}")
    print(f"{CYAN}[*]{RESET} mcp-mesh and Antigravity can now route tools to ghost-job-hunter via stdio.")


def main():
    parser = argparse.ArgumentParser(
        description="Ghost Job Hunter v2.0 - Autonomous anti-ghost job hunting agent powered by mcp-mesh."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: hunt (Autonomous Agent Pipeline)
    p_hunt = subparsers.add_parser("hunt", help="Autonomous end-to-end job hunting workflow via mcp-mesh")
    p_hunt.add_argument("target", help="Job description text, file path, URL, or sample ('ghost', 'legit', 'compliance')")
    p_hunt.add_argument("--title", default=None, help="Target Job Title")
    p_hunt.add_argument("--company", default=None, help="Target Company Name")
    p_hunt.add_argument("--profile", default=None, help="Path to custom candidate profile JSON")
    p_hunt.add_argument("--output", default=None, help="Write comprehensive tactical dossier to file")
    p_hunt.add_argument("--json", action="store_true", help="Output machine-readable JSON format")

    # Command: analyze (Classic Heuristic Analysis)
    p_analyze = subparsers.add_parser("analyze", help="Analyze a job description text or file for ghost signals")
    p_analyze.add_argument("target", nargs="?", help="Path to job description text file or raw string")
    p_analyze.add_argument("--title", default="Target Professional", help="Job Title")
    p_analyze.add_argument("--company", default="Target Enterprise", help="Company Name")
    p_analyze.add_argument("--json", action="store_true", help="Output machine-readable JSON format")
    p_analyze.add_argument("--bypass", action="store_true", help="Automatically generate an Executive Bypass pitch if GPI >= 40 percent")

    # Command: inspect (Company GitHub Tech Stack Audit)
    p_inspect = subparsers.add_parser("inspect", help="Audit company open-source GitHub footprint and engineering activity")
    p_inspect.add_argument("company", help="Target company name or GitHub organization")
    p_inspect.add_argument("--claimed", nargs="*", help="Claimed tech stack from job posting")

    # Command: tailor (Candidate Skill Alignment & Resume Bullets)
    p_tailor = subparsers.add_parser("tailor", help="Match candidate profile to job and generate tailored resume bullets")
    p_tailor.add_argument("target", help="Job description text or file")
    p_tailor.add_argument("--profile", default=None, help="Path to candidate profile JSON")
    p_tailor.add_argument("--company", default="Target Company", help="Company name")

    # Command: profile (View or create candidate profile)
    p_profile = subparsers.add_parser("profile", help="View active candidate profile or export template")
    p_profile.add_argument("--export", default=None, help="Export default profile to JSON file")

    # Command: mesh-status (Token economy & mcp-mesh connectivity)
    subparsers.add_parser("mesh-status", help="Inspect mcp-mesh dynamic gateway connection and token economy stats")

    # Command: register-mesh (Auto-register in Antigravity / mcp-mesh)
    subparsers.add_parser("register-mesh", help="Register ghost-job-hunter in mcp_config.json")

    # Command: serve-mcp (Standard MCP Stdio Server)
    subparsers.add_parser("serve-mcp", help="Run Ghost Job Hunter as a standard Model Context Protocol server over stdio")

    # Command: samples (Calibrated Benchmarks)
    p_samples = subparsers.add_parser("samples", help="Run diagnostic on built-in test case samples")
    p_samples.add_argument("sample_type", choices=["ghost", "legit", "compliance"], help="Sample type to evaluate")

    # Command: bypass (Direct Cold Outreach Generator)
    p_bypass = subparsers.add_parser("bypass", help="Generate a 1-page direct executive pitch letter")
    p_bypass.add_argument("--title", required=True, help="Target Job Title")
    p_bypass.add_argument("--company", required=True, help="Target Company Name")
    p_bypass.add_argument("--head", default="VP of Engineering / Operations", help="Target Department Head Title")

    args = parser.parse_args()

    if not args.command:
        print(BANNER)
        parser.print_help()
        sys.exit(0)

    # Dispatch subcommands
    if args.command == "hunt":
        profile = load_candidate_from_file(args.profile) if args.profile else get_default_candidate()
        agent = JobHunterAgent(candidate_profile=profile)
        
        print(BANNER)
        print(f"{CYAN}[*] Autonomous Agent Hunt initiated for:{RESET} {args.target}")
        print(f"{DIM}[*] Routing tools through mcp-mesh dynamic gateway...{RESET}\n")

        hunt_result = agent.hunt(args.target, title=args.title, company=args.company)

        if args.json:
            data = {
                "job": {
                    "title": hunt_result.job.title,
                    "company": hunt_result.job.company,
                    "url": hunt_result.job.url
                },
                "strategy": hunt_result.recommended_strategy,
                "gpi": hunt_result.diagnostic_report.ghost_probability_index,
                "risk_level": hunt_result.diagnostic_report.risk_level,
                "verdict": hunt_result.diagnostic_report.verdict_summary,
                "company_audit": {
                    "github_org": hunt_result.company_audit.github_org if hunt_result.company_audit else None,
                    "public_repos": hunt_result.company_audit.public_repos_count if hunt_result.company_audit else 0,
                    "top_languages": hunt_result.company_audit.top_languages if hunt_result.company_audit else {}
                },
                "match": {
                    "score": hunt_result.match_result.match_score if hunt_result.match_result else 0,
                    "matched_skills": hunt_result.match_result.matched_skills if hunt_result.match_result else [],
                    "missing_skills": hunt_result.match_result.missing_skills if hunt_result.match_result else []
                },
                "tailored_bullets": hunt_result.tailored_bullets,
                "pitch": hunt_result.generated_pitch,
                "token_economy": hunt_result.token_economy
            }
            print(json.dumps(data, indent=2))
        else:
            dossier = generate_comprehensive_report(hunt_result)
            print(dossier)

        if args.output:
            out_p = Path(args.output)
            dossier = generate_comprehensive_report(hunt_result)
            out_p.write_text(dossier, encoding="utf-8")
            print(f"\n{GREEN}[+] Full Tactical Dossier written to:{RESET} {out_p.resolve()}")

    elif args.command == "analyze":
        analyzer = JobAnalyzer()
        text = ""
        if args.target and os.path.exists(args.target):
            with open(args.target, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            text = args.target or ""

        report = analyzer.analyze(text, title=args.title, company=args.company)
        print_report(report, json_output=args.json)

        if args.bypass and report.ghost_probability_index >= 40.0:
            print(f"\n{BOLD}{CYAN}GENERATING EXECUTIVE BYPASS LETTER (Chapter 6 Protocol):{RESET}\n")
            letter = generate_executive_bypass(report, department_head_title="VP of Department")
            print(letter)

    elif args.command == "inspect":
        auditor = CompanyGitHubAuditor()
        print(BANNER)
        print(f"{CYAN}[*] Auditing company GitHub engineering footprint for:{RESET} {WHITE}{BOLD}{args.company}{RESET}\n")
        audit = auditor.audit_company(args.company, claimed_tech_stack=args.claimed)
        print(f"Company Name       : {audit.company_name}")
        print(f"GitHub Org Slug    : {audit.github_org}")
        print(f"Public Repositories: {audit.public_repos_count}")
        print(f"Engineering Health : {audit.engineering_health_score} / 100")
        print(f"Last Commit Date   : {audit.last_commit_date}")
        print(f"Top Languages      : {json.dumps(audit.top_languages)}")
        print(f"Active Repos       : {', '.join(audit.active_repos) if audit.active_repos else 'None'}")
        if audit.discrepancy_flags:
            print(f"\n{RED}[!] Discrepancy & Risk Flags:{RESET}")
            for d in audit.discrepancy_flags:
                print(f"  {RED}!{RESET} {d}")
        else:
            print(f"\n{GREEN}[+] No obvious tech stack discrepancies detected.{RESET}")

    elif args.command == "tailor":
        profile = load_candidate_from_file(args.profile) if args.profile else get_default_candidate()
        matcher = CandidateMatcher(profile)
        
        target_text = args.target
        if os.path.exists(args.target):
            with open(args.target, "r", encoding="utf-8", errors="ignore") as f:
                target_text = f.read()
                
        job = JobPosting(title="Target Role", company=args.company, description=target_text)
        res = matcher.match(job)
        bullets = matcher.generate_tailored_bullets(job, res)

        print(BANNER)
        print(f"{CYAN}CANDIDATE FIT & PROOF-OF-WORK ALIGNMENT:{RESET}")
        print(f"  Candidate : {profile.name} ({profile.title})")
        print(f"  Fit Score : {res.match_score}%")
        print(f"  Matched   : {', '.join(res.matched_skills) or 'None'}")
        print(f"  Missing   : {', '.join(res.missing_skills) or 'None'}")
        print(f"\n{CYAN}TAILORED RESUME ACTION BULLETS:{RESET}")
        for b in bullets:
            print(f"  {b}")

    elif args.command == "profile":
        if args.export:
            p = get_default_candidate()
            save_candidate_to_file(p, args.export)
            print(f"{GREEN}[+]{RESET} Default profile template exported to {args.export}")
        else:
            p = get_default_candidate()
            print(BANNER)
            print(f"{BOLD}Active Candidate Profile:{RESET}")
            print(f"  Name    : {p.name}")
            print(f"  Title   : {p.title}")
            print(f"  GitHub  : https://github.com/{p.github_username}")
            print(f"  Skills  : {', '.join(p.skills)}")
            print(f"  Projects: {', '.join(pr.name for pr in p.featured_projects)}")

    elif args.command == "mesh-status":
        mesh = MeshClient()
        stats = mesh.get_token_economy_stats()
        print(BANNER)
        print(f"{BOLD}mcp-mesh Tool Gateway Status & Token Economy:{RESET}")
        print(f"  Registered Mesh Tools   : {len(mesh.tools_registry)}")
        print(f"  Turn-0 Baseline Footprint: {stats['baseline_turn0_tokens']} tokens (un-routed static dump)")
        print(f"  mcp-mesh Lazy Footprint  : {stats['mesh_turn0_tokens']} tokens")
        print(f"  Context Token Reduction  : {stats['static_savings_ratio']} ({stats['static_token_savings']} tokens saved)")
        print("\nRegistered Tools in Gateway Index:")
        for name, meta in mesh.tools_registry.items():
            print(f"  • {CYAN}{name:<32}{RESET} [{meta.get('category', 'general')}] ({meta.get('raw_tokens', 0)} tokens)")

    elif args.command == "register-mesh":
        register_with_mcp_mesh()

    elif args.command == "serve-mcp":
        run_mcp_server()

    elif args.command == "samples":
        from .sample_data import GHOST_SAMPLE, LEGIT_SAMPLE, COMPLIANCE_SAMPLE
        analyzer = JobAnalyzer()
        sample_map = {
            "ghost": ("Evergreen Talent Pipeline (Phantom Listing)", "Apex Global Tech", GHOST_SAMPLE),
            "legit": ("Staff Backend Distributed Systems Engineer", "Stripe / ScaleScale", LEGIT_SAMPLE),
            "compliance": ("Senior Regulatory Financial Auditor", "Legacy Capital Corp", COMPLIANCE_SAMPLE)
        }
        title, comp, text = sample_map[args.sample_type]
        print(BANNER)
        print(f"{DIM}Running Heuristic Engine against verified benchmark: [{args.sample_type.upper()}]{RESET}")
        report = analyzer.analyze(text, title=title, company=comp)
        print_report(report)

    elif args.command == "bypass":
        mock_report = DiagnosticReport(
            job_title=args.title,
            company_name=args.company,
            ghost_probability_index=85.0,
            risk_level="CRITICAL_GHOST",
            verdict_summary="Bypass Protocol Triggered",
            signals=[],
            salary_analysis={},
            key_responsibilities=[],
            detected_tech_stack=[],
            actionable_recommendation=""
        )
        print(BANNER)
        letter = generate_executive_bypass(mock_report, department_head_title=args.head)
        print(letter)


if __name__ == "__main__":
    main()
