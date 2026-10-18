"""
Standard Model Context Protocol (MCP) Server for Ghost Job Hunter.
Exposes Ghost Job Hunter capabilities over standard stdio JSON-RPC 2.0.
Can be plugged directly into mcp-mesh, Antigravity, Claude Desktop, or Cursor.
"""

from __future__ import annotations

import sys
import os
import json
from typing import Dict, Any, Optional

from .agent import JobHunterAgent
from .analyzer import JobAnalyzer
from .github_auditor import CompanyGitHubAuditor
from .generator import generate_comprehensive_report


TOOLS_MANIFEST = [
    {
        "name": "ghost_hunter_audit_posting",
        "description": "Evaluates job description against 5 diagnostic heuristic engines to compute Ghost Probability Index (GPI).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Raw job posting text"},
                "title": {"type": "string", "description": "Target job title", "default": "Software Engineer"},
                "company": {"type": "string", "description": "Target company name", "default": "Target Company"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "ghost_hunter_audit_company",
        "description": "Audits target company's public GitHub repositories, active languages, commit velocity, and tech stack discrepancies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "Target company name"},
                "claimed_tech_stack": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tech stack claimed in the job posting"
                }
            },
            "required": ["company_name"]
        }
    },
    {
        "name": "ghost_hunter_hunt",
        "description": "Runs the full autonomous end-to-end job hunting workflow: scout -> ghost audit -> GitHub inspection -> candidate matching -> outreach pitch.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Job description text, file path, URL, or sample ('ghost', 'legit', 'compliance')"},
                "title": {"type": "string", "description": "Job title"},
                "company": {"type": "string", "description": "Company name"}
            },
            "required": ["target"]
        }
    }
]


def handle_request(agent: JobHunterAgent, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params", {}) or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False}
                },
                "serverInfo": {
                    "name": "ghost-job-hunter-mcp",
                    "version": "2.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS_MANIFEST
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        try:
            if tool_name == "ghost_hunter_audit_posting":
                analyzer = JobAnalyzer()
                report = analyzer.analyze(
                    args.get("text", ""),
                    title=args.get("title", "Software Engineer"),
                    company=args.get("company", "Target Company")
                )
                output = {
                    "job_title": report.job_title,
                    "company_name": report.company_name,
                    "gpi": report.ghost_probability_index,
                    "risk_level": report.risk_level,
                    "verdict": report.verdict_summary,
                    "recommendation": report.actionable_recommendation,
                    "salary_spread": report.salary_analysis
                }
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(output, indent=2)}]
                    }
                }

            elif tool_name == "ghost_hunter_audit_company":
                auditor = CompanyGitHubAuditor()
                audit = auditor.audit_company(
                    args.get("company_name", "Unknown"),
                    args.get("claimed_tech_stack", [])
                )
                output = {
                    "company": audit.company_name,
                    "github_org": audit.github_org,
                    "public_repos": audit.public_repos_count,
                    "top_languages": audit.top_languages,
                    "engineering_health_score": audit.engineering_health_score,
                    "discrepancies": audit.discrepancy_flags
                }
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(output, indent=2)}]
                    }
                }

            elif tool_name == "ghost_hunter_hunt":
                hunt_res = agent.hunt(
                    args.get("target", ""),
                    title=args.get("title"),
                    company=args.get("company")
                )
                dossier = generate_comprehensive_report(hunt_res)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": dossier}]
                    }
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method or tool not found: {tool_name}"}
                }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": f"Internal error executing {tool_name}: {str(e)}"}
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not supported: {method}"}
    }


def run_mcp_server() -> None:
    """Runs the MCP server over stdio."""
    agent = JobHunterAgent()
    sys.stderr.write("[ghost-hunter] MCP Stdio Server v2.0 initialized.\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(agent, req)
            if resp:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
