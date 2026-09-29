"""
Command Line Interface with Rich ANSI Visuals and Terminal Risk Meters.
Zero external dependencies.
"""

import sys
import os
import argparse
import json
from .core import DiagnosticReport
from .analyzer import JobAnalyzer
from .generator import generate_executive_bypass

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
  {MAGENTA}>> GHOST JOB HUNTER v1.0.0 | Existential Cloud <<{RESET}
  {DIM}Curated & Vibe-Coded by Van Schulist (@VanSchulist){RESET}
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
    
    # Meter & Verdict
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

    # Signals Breakdown Table
    print("\n" + "-" * 76)
    print(f"{BOLD}{'SIGNAL EVALUATED':<40} {'WEIGHT':<8} {'SCORE':<8} {'STATUS'}{RESET}")
    print("-" * 76)
    
    for s in report.signals:
        status = f"{RED}TRIGGERED{RESET}" if s.triggered else f"{GREEN}CLEAR{RESET}"
        print(f"{s.name:<40} {s.weight:<8.2f} {s.score:<8.1f} {status}")
        if s.evidence:
            for ev in s.evidence:
                print(f"  {DIM}-> {ev}{RESET}")

    # Salary Analysis
    if report.salary_analysis.get("min"):
        sal = report.salary_analysis
        print("\n" + "-" * 76)
        print(f"{BOLD}COMPENSATION TRANSPARENCY AUDIT:{RESET}")
        print(f"  Disclosed Range: ${sal['min']:,.0f} - ${sal['max']:,.0f}")
        print(f"  Spread Ratio:    {int(sal['spread_ratio'] * 100)}% " + 
              (f"{RED}(Extreme - likely pay transparency evasion){RESET}" if sal['spread_ratio'] > 1.2 else f"{GREEN}(Normal){RESET}"))

    # Tactical Recommendation
    print("\n" + "=" * 76)
    print(f"{BOLD}ACTIONABLE TACTICAL RECOMMENDATION:{RESET}")
    print(f"  {report.actionable_recommendation}")
    print("=" * 76 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="Ghost Job Hunter - Uncover phantom job postings and hiring theater."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: analyze
    p_analyze = subparsers.add_parser("analyze", help="Analyze a job description text or file")
    p_analyze.add_argument("target", nargs="?", help="Path to job description text file or raw string")
    p_analyze.add_argument("--title", default="Target Professional", help="Job Title")
    p_analyze.add_argument("--company", default="Target Enterprise", help="Company Name")
    p_analyze.add_argument("--json", action="store_true", help="Output machine-readable JSON format")
    p_analyze.add_argument("--bypass", action="store_true", help="Automatically generate an Executive Bypass pitch if GPI >= 45 percent")

    # Command: samples
    p_samples = subparsers.add_parser("samples", help="Run diagnostic on built-in test case samples")
    p_samples.add_argument("sample_type", choices=["ghost", "legit", "compliance"], help="Sample type to evaluate")

    # Command: bypass
    p_bypass = subparsers.add_parser("bypass", help="Generate a 1-page direct executive pitch letter")
    p_bypass.add_argument("--title", required=True, help="Target Job Title")
    p_bypass.add_argument("--company", required=True, help="Target Company Name")
    p_bypass.add_argument("--head", default="VP of Engineering / Operations", help="Target Department Head Title")

    args = parser.parse_args()

    if not args.command or args.command == "analyze" and not args.target:
        print(BANNER)
        parser.print_help()
        sys.exit(0)

    analyzer = JobAnalyzer()

    if args.command == "analyze":
        text = ""
        if os.path.exists(args.target):
            with open(args.target, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            text = args.target

        report = analyzer.analyze(text, title=args.title, company=args.company)
        print_report(report, json_output=args.json)

        if args.bypass and report.ghost_probability_index >= 45.0:
            print(f"\n{BOLD}{CYAN}GENERATING EXECUTIVE BYPASS LETTER (Chapter 6 Protocol):{RESET}\n")
            letter = generate_executive_bypass(report, department_head_title="VP of Department")
            print(letter)

    elif args.command == "samples":
        from .sample_data import GHOST_SAMPLE, LEGIT_SAMPLE, COMPLIANCE_SAMPLE
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
