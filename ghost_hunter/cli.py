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
from .sources import UnifiedJobSource, HNHiringSource, RemoteOKSource, WeWorkRemotelySource
from .pipeline import JobPipelineStore
from .outreach import OutreachExporter

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
  {MAGENTA}>> GHOST JOB HUNTER v2.2 | Deterministic Heuristic Engine <<{RESET}
  {DIM}Engineered by Van Schulist (@VanSchulist) | Existential Cloud{RESET}
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
    print(f"  {render_meter(report.ghost_probability_index)} {DIM}(Empirical Heuristic Risk Score){RESET}")
    
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
        "description": "Ghost Job Hunter v2.1 - Autonomous anti-ghost job hunting & ATS bypass agent"
    }

    data.setdefault("mcpServers", {})["ghost-job-hunter"] = server_entry

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"{GREEN}[+]{RESET} Successfully registered 'ghost-job-hunter' in {config_path}")
    print(f"{CYAN}[*]{RESET} mcp-mesh and Antigravity can now route tools to ghost-job-hunter via stdio.")



def cmd_demo(args: argparse.Namespace) -> None:
    """Instant zero-config heuristic audit demonstration."""
    print(BANNER)
    print(f"{CYAN}[*] Running Instant Anti-Ghost Job Heuristic Audit Demonstration...{RESET}")
    print(f"{DIM}[*] Evaluating calibrated benchmark: 'Principal Cloud Solutions Architect (Evergreen Pipeline)' @ Apex Global Tech{RESET}\n")

    from .sample_data import GHOST_SAMPLE
    from .analyzer import JobAnalyzer
    from .pipeline import JobPipelineStore
    from .mesh_client import MeshClient

    analyzer = JobAnalyzer()
    report = analyzer.analyze(
        GHOST_SAMPLE,
        title="Principal Cloud Solutions Architect (Evergreen Pipeline)",
        company="Apex Global Tech"
    )

    print_report(report)

    # Pipeline record
    pipe = JobPipelineStore()
    lead_id = pipe.save_lead(
        company="Apex Global Tech",
        title="Principal Cloud Solutions Architect (Evergreen Pipeline)",
        source="demo-audit",
        salary="$95,000 - $265,000",
        location="Remote, US",
        gpi_score=report.ghost_probability_index,
        risk_level=report.risk_level,
        fit_score=78.5,
        status="REJECTED",
        notes="Calibrated demo audit. Phantom listing detected via deterministic heuristics."
    )
    print(f"{GREEN}[+] Tracked in local pipeline as Lead #{lead_id} [REJECTED]{RESET}")

    # Token economy
    mesh = MeshClient()
    stats = mesh.get_token_economy_stats()
    print(f"\n{BOLD}{CYAN}=== mcp-mesh DYNAMIC TOOL ROUTING ECONOMY ==={RESET}")
    print(f"  Turn-0 Baseline Footprint : {stats['baseline_turn0_tokens']} tokens (un-routed static tool schemas)")
    print(f"  mcp-mesh Lazy Routing     : {stats['mesh_turn0_tokens']} tokens")
    print(f"  Context Token Reduction   : {GREEN}{BOLD}{stats['static_savings_ratio']}{RESET} ({stats['static_token_savings']} tokens saved)")
    print(f"\n{GREEN}[+] Demo completed successfully. Zero external dependencies required.{RESET}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Ghost Job Hunter v2.2 - Deterministic heuristic job audit engine powered by mcp-mesh."
    )
    parser.add_argument("--demo", "-d", action="store_true", help="Run instant zero-config heuristic audit demonstration")
    parser.add_argument("--version", "-v", action="version", version="ghost-job-hunter 2.2.0")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: demo
    subparsers.add_parser("demo", help="Run instant zero-config heuristic audit demonstration")

    # Command: hunt (Autonomous Agent Pipeline)
    p_hunt = subparsers.add_parser("hunt", help="Autonomous end-to-end job hunting workflow via mcp-mesh")
    p_hunt.add_argument("target", help="Job description text, file path, URL, sample ('ghost', 'legit', 'compliance'), or live query ('greenhouse:co', 'lever:co', 'hn:co', 'remoteok:co', 'wwr:co')")
    p_hunt.add_argument("--title", default=None, help="Target Job Title")
    p_hunt.add_argument("--company", default=None, help="Target Company Name")
    p_hunt.add_argument("--profile", default=None, help="Path to custom candidate profile JSON")
    p_hunt.add_argument("--output", default=None, help="Write comprehensive tactical dossier to file")
    p_hunt.add_argument("--export", action="store_true", help="Export ready-to-send RFC 822 .eml and markdown package to outreach/")
    p_hunt.add_argument("--recipient", default=None, help="Recipient email address for cold application outreach")
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

    # Command: live (Multi-Source Real-World Feeds)
    p_live = subparsers.add_parser("live", help="Browse real, live developer job postings across Greenhouse, Lever, HN, RemoteOK, and WeWorkRemotely")
    p_live.add_argument("--source", choices=["all", "hn", "remoteok", "wwr", "greenhouse", "lever"], default="all", help="Job source (default: all)")
    p_live.add_argument("--company", default=None, help="Company board token for Greenhouse or Lever (e.g. 'stripe', 'figma')")
    p_live.add_argument("--query", default=None, help="Search filter (e.g. 'python', 'rust', 'backend')")
    p_live.add_argument("--remote", action="store_true", help="Filter only remote-friendly postings")
    p_live.add_argument("--limit", type=int, default=5, help="Number of postings to display (default: 5)")
    p_live.add_argument("--save", action="store_true", help="Automatically save all fetched leads into ~/.ghost-hunter/pipeline.db")

    # Command: pipeline (Local Opportunity Tracking Ledger)
    p_pipe = subparsers.add_parser("pipeline", help="Manage and query local job hunting pipeline (~/.ghost-hunter/pipeline.db)")
    p_pipe_sub = p_pipe.add_subparsers(dest="pipe_action", help="Pipeline action: list, status, stats, inspect")
    
    p_pl_list = p_pipe_sub.add_parser("list", help="List tracked opportunities")
    p_pl_list.add_argument("--status", choices=JobPipelineStore.VALID_STATUSES, default=None, help="Filter by pipeline status")
    p_pl_list.add_argument("--query", default=None, help="Filter by company or role keyword")
    p_pl_list.add_argument("--max-gpi", type=float, default=None, help="Maximum Ghost Probability Index (GPI)")
    p_pl_list.add_argument("--limit", type=int, default=20, help="Max entries to return")
    p_pl_list.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Output format: table, json, csv (default: table)")
    p_pl_list.add_argument("--output", "-o", default=None, help="Write output directly to file path")

    p_pl_export = p_pipe_sub.add_parser("export", help="Export pipeline audit leads to structured JSON or CSV")
    p_pl_export.add_argument("--format", choices=["json", "csv"], default="json", help="Export format: json, csv (default: json)")
    p_pl_export.add_argument("--status", choices=JobPipelineStore.VALID_STATUSES, default=None, help="Filter by pipeline status")
    p_pl_export.add_argument("--query", default=None, help="Filter by company or role keyword")
    p_pl_export.add_argument("--max-gpi", type=float, default=None, help="Maximum Ghost Probability Index (GPI)")
    p_pl_export.add_argument("--limit", type=int, default=100, help="Max entries to export (default: 100)")
    p_pl_export.add_argument("--output", "-o", default=None, help="Write output directly to file path")

    p_pl_status = p_pipe_sub.add_parser("status", help="Update the status of a lead")
    p_pl_status.add_argument("id", type=int, help="Lead ID in pipeline")
    p_pl_status.add_argument("new_status", choices=JobPipelineStore.VALID_STATUSES, help="Target status")
    p_pl_status.add_argument("--notes", default=None, help="Add or update notes")

    p_pipe_sub.add_parser("stats", help="Show pipeline funnel metrics and statistics")

    p_pl_insp = p_pipe_sub.add_parser("inspect", help="Inspect detailed lead record")
    p_pl_insp.add_argument("id", type=int, help="Lead ID in pipeline")

    # Command: bypass (Direct Cold Outreach Generator)
    p_bypass = subparsers.add_parser("bypass", help="Generate a 1-page direct executive pitch letter")
    p_bypass.add_argument("--title", required=True, help="Target Job Title")
    p_bypass.add_argument("--company", required=True, help="Target Company Name")
    p_bypass.add_argument("--head", default="VP of Engineering / Operations", help="Target Department Head Title")

    args = parser.parse_args()

    if getattr(args, "demo", False) or args.command == "demo":
        cmd_demo(args)
        return

    if not args.command:
        cmd_demo(args)
        return

    # Dispatch subcommands
    if args.command == "hunt":
        profile = load_candidate_from_file(args.profile) if args.profile else get_default_candidate()
        agent = JobHunterAgent(candidate_profile=profile)
        
        print(BANNER)
        print(f"{CYAN}[*] Autonomous Agent Hunt initiated for:{RESET} {args.target}")
        print(f"{DIM}[*] Routing tools through mcp-mesh dynamic gateway...{RESET}\n")

        hunt_result = agent.hunt(args.target, title=args.title, company=args.company)

        # Automatically record to pipeline
        pipe = JobPipelineStore()
        fit_score = hunt_result.match_result.match_score if hunt_result.match_result else 0.0
        gpi = hunt_result.diagnostic_report.ghost_probability_index
        risk = hunt_result.diagnostic_report.risk_level
        init_status = "AUDITED" if gpi < 65.0 else "REJECTED"

        lead_id = pipe.save_lead(
            company=hunt_result.job.company,
            title=hunt_result.job.title,
            source="hunt",
            url=hunt_result.job.url,
            salary=hunt_result.job.salary_raw,
            location=hunt_result.job.location,
            gpi_score=gpi,
            risk_level=risk,
            fit_score=fit_score,
            status=init_status,
            notes=f"Audited via mcp-mesh. Strategy: {hunt_result.recommended_strategy}"
        )

        if args.json:
            data = {
                "lead_id": lead_id,
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
            print(f"{GREEN}[+] Tracked in local pipeline as Lead #{lead_id} [{init_status}]{RESET}")

        # Export outreach package if requested
        if args.export:
            exporter = OutreachExporter()
            pkg = exporter.export(hunt_result, candidate=profile, recipient_email=args.recipient)
            pipe.update_status(lead_id, "PITCH_READY", notes=f"Exported to {pkg['eml_path']}")
            print(f"\n{BOLD}{CYAN}=== ACTIONABLE OUTREACH PACKAGE READY ==={RESET}")
            print(f"  {GREEN}✔ RFC 822 Email File : {WHITE}{pkg['eml_path']}{RESET}")
            print(f"  {GREEN}✔ Tactical Dossier   : {WHITE}{pkg['dossier_path']}{RESET}")
            print(f"  {GREEN}✔ Target Recipient   : {WHITE}{pkg['recipient']}{RESET}")
            print(f"  {GREEN}✔ Quick Mailto Link  : {CYAN}{pkg['mailto_uri']}{RESET}")
            print(f"\n{DIM}Tip: On Windows, run 'start \"\" \"{pkg['eml_path']}\"' to open draft in Outlook / Mail!{RESET}\n")

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

    elif args.command == "live":
        print(BANNER)
        print(f"{CYAN}[*] Fetching live engineering jobs from {args.source.upper()} feeds...{RESET}\n")
        unified = UnifiedJobSource()
        pipe = JobPipelineStore() if args.save else None

        try:
            jobs = unified.fetch_live_jobs(
                source=args.source,
                query=args.query,
                remote_only=args.remote,
                company=getattr(args, "company", None),
                limit=args.limit
            )
            if not jobs:
                print(f"{YELLOW}[!] No matching live job postings found.{RESET}")
            else:
                for i, j in enumerate(jobs, 1):
                    print(f"{BOLD}[{i}] {j.company}{RESET} - {WHITE}{j.title}{RESET}")
                    if j.salary_raw:
                        print(f"    Compensation: {GREEN}{j.salary_raw}{RESET}")
                    if j.location:
                        print(f"    Location    : {DIM}{j.location}{RESET}")
                    if j.url:
                        print(f"    Link        : {CYAN}{j.url}{RESET}")
                    first_p = j.description.split("\n")[0] if "\n" in j.description else j.description[:180]
                    print(f"    Details     : {first_p[:200]}...")
                    
                    if pipe:
                        lid = pipe.save_lead(
                            company=j.company,
                            title=j.title,
                            source=args.source,
                            url=j.url,
                            salary=j.salary_raw,
                            location=j.location,
                            status="DISCOVERED",
                            notes="Imported via live scan"
                        )
                        print(f"    Pipeline    : {MAGENTA}Saved as Lead #{lid} [DISCOVERED]{RESET}")
                    print()

                sample_comp = jobs[0].company
                print(f"{DIM}Tip: Run 'python main.py hunt \"{sample_comp}\" --export' to audit, match, and generate cold email!{RESET}\n")
        except Exception as e:
            print(f"{RED}[!] Error fetching live postings: {str(e)}{RESET}")

    elif args.command == "pipeline":
        pipe = JobPipelineStore()
        if not args.pipe_action or args.pipe_action in ("list", "export"):
            fmt = getattr(args, "format", "table" if args.pipe_action != "export" else "json").lower()
            out_path = getattr(args, "output", None)
            limit_val = getattr(args, "limit", 20 if args.pipe_action != "export" else 100)

            if fmt in ("json", "csv"):
                content = pipe.export_leads(
                    format=fmt,
                    status=getattr(args, "status", None),
                    query=getattr(args, "query", None),
                    max_gpi=getattr(args, "max_gpi", None),
                    limit=limit_val,
                    output_path=out_path
                )
                if out_path:
                    print(f"{GREEN}[+]{RESET} Successfully exported pipeline leads to {BOLD}{out_path}{RESET} ({fmt.upper()} format).")
                else:
                    sys.stdout.write(content + "\n")
            else:
                leads = pipe.list_leads(
                    status=getattr(args, "status", None),
                    query=getattr(args, "query", None),
                    max_gpi=getattr(args, "max_gpi", None),
                    limit=limit_val
                )
                table_lines = [
                    BANNER,
                    f"{BOLD}Active Opportunities Pipeline ({len(leads)} leads):{RESET}\n"
                ]
                if not leads:
                    table_lines.append(f"{YELLOW}[!] No opportunities currently match your filter.{RESET}")
                    table_lines.append(f"{DIM}Tip: Run 'python main.py live --save' to automatically populate your pipeline!{RESET}\n")
                else:
                    table_lines.append(f"{BOLD}{'ID':<4} {'COMPANY':<22} {'ROLE':<28} {'STATUS':<14} {'GPI':<8} {'FIT':<6} {'COMPENSATION'}{RESET}")
                    table_lines.append("-" * 95)
                    for ld in leads:
                        st_color = GREEN if ld.status == "PITCH_READY" else CYAN if ld.status == "AUDITED" else YELLOW if ld.status == "DISCOVERED" else MAGENTA
                        gpi_color = GREEN if ld.gpi_score < 40 else YELLOW if ld.gpi_score < 65 else RED
                        table_lines.append(f"{ld.id:<4} {ld.company[:20]:<22} {ld.title[:26]:<28} {st_color}{ld.status:<14}{RESET} {gpi_color}{ld.gpi_score:>4.1f}%{RESET}   {ld.fit_score:>4.1f}% {WHITE}{ld.salary[:15]}{RESET}")
                    table_lines.append("")

                table_output = "\n".join(table_lines)
                if out_path:
                    # Strip ANSI codes for plain text file output
                    import re
                    plain_output = re.sub(r'\x1b\[[0-9;]*m', '', table_output)
                    with open(out_path, "w", encoding="utf-8") as f_out:
                        f_out.write(plain_output)
                    print(f"{GREEN}[+]{RESET} Successfully saved pipeline table to {BOLD}{out_path}{RESET}.")
                else:
                    print(table_output)

        elif args.pipe_action == "status":
            ok = pipe.update_status(args.id, args.new_status, notes=args.notes)
            if ok:
                print(f"{GREEN}[+]{RESET} Lead #{args.id} status updated to {BOLD}{args.new_status.upper()}{RESET}")
            else:
                print(f"{RED}[!] Lead #{args.id} not found in pipeline.{RESET}")

        elif args.pipe_action == "stats":
            stats = pipe.get_summary_stats()
            print(BANNER)
            print(f"{BOLD}Opportunity Funnel & Conversion Stats:{RESET}")
            print(f"  Total Tracked Leads : {stats['total_leads']}")
            print(f"  Active Prospects    : {stats['active_prospects']}")
            print(f"  Applications Sent   : {stats['applied_count']}")
            print(f"  Interviews Active   : {stats['interviewing_count']}")
            print(f"  Offers Received     : {stats['offers_count']}\n")
            print("Status Breakdown:")
            for st, cnt in stats["by_status"].items():
                print(f"  • {st:<16}: {cnt}")
            print()

        elif args.pipe_action == "inspect":
            ld = pipe.get_lead(args.id)
            if not ld:
                print(f"{RED}[!] Lead #{args.id} not found.{RESET}")
            else:
                print(BANNER)
                print(f"{BOLD}Lead Dossier #{ld.id}:{RESET} {WHITE}{ld.title}{RESET} @ {CYAN}{ld.company}{RESET}")
                print(f"  Source     : {ld.source}")
                print(f"  URL        : {ld.url or 'N/A'}")
                print(f"  Salary     : {ld.salary or 'N/A'}")
                print(f"  Location   : {ld.location}")
                print(f"  Status     : {BOLD}{ld.status}{RESET}")
                print(f"  GPI Score  : {ld.gpi_score}% ({ld.risk_level})")
                print(f"  Fit Score  : {ld.fit_score}%")
                print(f"  Created At : {ld.created_at}")
                print(f"  Updated At : {ld.updated_at}")
                print(f"  Notes      : {ld.notes or 'None'}\n")

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
