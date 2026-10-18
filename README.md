# 👻 Ghost Job Hunter v2.0

> **The Autonomous Anti-Ghost Job Hunting & Direct Outreach Agent powered by `mcp-mesh`**  
> Uncover phantom job postings, verify real company GitHub codebases, eliminate ATS black holes, and generate high-converting executive bypass pitches with zero external dependencies.

[![Curated by Van Schulist](https://img.shields.io/badge/Curated%20by-Van%20Schulist-8A2BE2?style=flat-square&logo=openai)](https://github.com/VanSchulist)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-success?style=flat-square)](https://github.com/VanSchulist/ghost-job-hunter)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat-square)](https://github.com/VanSchulist/ghost-job-hunter)
[![Protocol: MCP](https://img.shields.io/badge/Protocol-MCP%202024--11--05-orange.svg?style=flat-square)](https://modelcontextprotocol.io/)
[![Powered by: mcp-mesh](https://img.shields.io/badge/Powered%20By-mcp--mesh%20Gateway-f59e0b?style=flat-square)](https://github.com/VanSchulist/mcp-mesh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

```text
   ____ _   _  ___  ____ _____      _  ___  ____  
  / ___| | | |/ _ \/ ___|_   _|    | |/ _ \| __ ) 
 | |  _| |_| | | | \___ \ | |   _  | | | | |  _ \ 
 | |_| |  _  | |_| |___) || |  | |_| | |_| | |_) |
  \____|_| |_|\___/|____/ |_|   \___/ \___/|____/ 
  >> GHOST JOB HUNTER v2.0 | Autonomous mcp-mesh Agent <<
  Curated & Vibe-Coded by Van Schulist (@VanSchulist) | Existential Cloud
```

> *"Over 40% of tech job listings are 'Ghost Jobs'—postings kept open indefinitely to pacify overworked teams, build passive resume banks, or project phantom growth to investors. Applying to them via automated ATS portals is an algorithmic trap. Ghost Job Hunter v2.0 turns the tables by deploying an autonomous multi-role agent that audits the hiring reality, inspects the company's real GitHub footprint, and bypasses broken portals directly to engineering leadership."*

---

## 💡 What's New in v2.0

* 🌐 **Dynamic Tool Routing via `mcp-mesh`**: Eliminates Turn-0 schema bloat. Tools (`audit_posting`, `audit_company_github`, `match_candidate`, `generate_pitch`) are discovered and loaded lazily on demand, slashing context token usage by **77.6% to 90%**.
* 🤖 **Autonomous Multi-Role Agent Pipeline (`hunt`)**: Single command executes end-to-end job scouting, ghost heuristic auditing, GitHub codebase verification, candidate matching, and outreach synthesis.
* 🔍 **Company GitHub Stack & Reality Audit (`inspect`)**: Cross-references job descriptions against public GitHub repositories. Detects dormant codebases and discrepancies (e.g. asking for "10 years of Rust & K8s" when the company repo is 100% PHP with zero commits).
* 🎯 **Proof-of-Work Candidate Alignment (`tailor`)**: Matches candidate GitHub repositories and credentials (defaulting to Van Schulist / Existential Cloud portfolio), producing targeted ATS action bullets.
* 📨 **Bifurcated Strategic Outreach Engine**:
  * **If Ghost Job / Trap (GPI >= 40%)**: Generates an **Executive Bypass Value Pitch** targeting the VP of Engineering to skip the broken portal.
  * **If Active Requisition (GPI < 40%)**: Generates a **Targeted High-Conversion Application** with tailored resume bullets highlighting proven open-source implementations.
* 🔌 **Bidirectional MCP Support (`serve-mcp`)**: Runs as a standard Model Context Protocol (MCP) stdio server. Auto-registers with Antigravity, Claude Desktop, Cursor, and `mcp-mesh`.
* ⚡ **100% Zero External Dependencies**: Engineered with pure Python standard library (`urllib.request`, `json`, `dataclasses`, `re`, `argparse`). Instant execution with zero `pip install` friction.

---

## 🏛️ Autonomous Agent Architecture

```text
 ┌────────────────────────────────────────────────────────┐
 │            Candidate / Terminal User CLI               │
 │        python main.py hunt "path/to/job_posting.txt"   │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                JobHunterAgent (Pipeline)               │
 └──────┬────────────────────┬────────────────────┬───────┘
        │ 1. Scout           │ 2. Audit           │ 3. Match
        ▼                    ▼                    ▼
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │ Job Ingestion│     │ Heuristic    │     │ Proof-of-Work│
 │ & URL Parser │     │ Risk Engine  │     │ Matcher      │
 └──────────────┘     └──────┬───────┘     └──────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │           mcp-mesh Dynamic Gateway & Tool Bus          │
 │   • mesh_search_tools  • describe_tool  • invoke_tool  │
 └──────┬────────────────────┬────────────────────┬───────┘
        │                    │                    │
        ▼                    ▼                    ▼
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │ Ghost Audit  │     │ GitHub Org   │     │ Bypass Pitch │
 │ (5 Engines)  │     │ Tech Stack   │     │ Generator    │
 └──────────────┘     └──────────────┘     └──────────────┘
```

---

## ⚡ The 5 Diagnostic Heuristic Engines

| Heuristic Engine | Weight | What It Detects |
| :--- | :---: | :--- |
| **Talent Pipeline / Evergreen Disclosure** | **30%** | Catches fine-print language admitting the post is a *"continuous talent community"*, *"future consideration"*, or *"bench building"* requisition with zero committed headcount. |
| **Regulatory / Compliance Theater** | **25%** | Flags boilerplate disclosures required by federal PERM immigration filings or internal transfer laws where a candidate has already been selected. |
| **Pay Transparency Evasion Index** | **15%** | Calculates salary band spread ratios (e.g. `$90k - $280k`). Spreads exceeding 120% indicate corporate legal hedging to skirt state disclosure laws. |
| **The Unicorn Paradox (Scope Creep)** | **15%** | Flags requisitions demanding deep mastery across 4 or more incompatible disciplines (e.g. React frontend + Rust systems + Kubernetes SRE + Sales prospecting). |
| **Fluff & Buzzword Overload Density** | **15%** | Measures the statistical ratio of empty corporate adjectives (*"rockstar"*, *"ninja"*, *"synergy"*, *"wear many hats"*) against verifiable functional KPIs. |

---

## 🚀 Quickstart & Installation

**Ghost Job Hunter requires ZERO external libraries.** It runs out of the box with standard Python 3.8+.

```bash
# 1. Clone the repository
git clone https://github.com/VanSchulist/ghost-job-hunter.git
cd ghost-job-hunter

# 2. Run an autonomous hunt on calibrated benchmark cases
python main.py hunt ghost
python main.py hunt legit
python main.py hunt compliance

# 3. Autonomous hunt on any real job posting (file, text, or URL)
python main.py hunt "path/to/job_posting.txt" --company "Stripe" --title "Staff Infrastructure Engineer"

# 4. Audit target company's public GitHub engineering footprint
python main.py inspect "Netflix" --claimed rust kubernetes python

# 5. Check mcp-mesh gateway connectivity & token savings
python main.py mesh-status

# 6. One-click registration in Antigravity & mcp-mesh
python main.py register-mesh
```

---

## 📊 Sample Output (Autonomous Hunt)

```text
================================================================================
GHOST JOB HUNTER v2.0 - AUTONOMOUS TACTICAL DOSSIER
Target Role   : Principal Cloud Solutions Architect
Target Company: Apex Global Tech
Strategy      : AVOID_GHOST
================================================================================

[1] GHOST PROBABILITY AUDIT:
  Ghost Probability Index (GPI): 68.2%
  Classification : [CRITICAL_GHOST]
  Verdict        : HIGH PROBABILITY GHOST JOB (Applying via portal is an algorithmic black hole)
  Recommendation : DO NOT submit through the web portal. Bypass directly to the functional VP/Director with an Executive Pitch Letter.

[2] COMPANY GITHUB & ENGINEERING FOOTPRINT AUDIT:
  GitHub Org Slug     : apexglobal
  Public Repositories : 1
  Engineering Health  : 45.0/100
  Top Languages       : PHP (1)
  Discrepancy Alerts  :
    ! Requisition requires high-priority 'rust', but zero public repos reflect 'rust'.

[3] CANDIDATE FIT & PROOF OF WORK:
  Candidate Fit Score : 75.0%
  Matched Skills      : python, asyncio, mcp, distributed systems
  Aligned Repositories:
    * mcp-mesh (https://github.com/VanSchulist/mcp-mesh): Dynamic MCP tool router...
    * ghost-job-hunter (https://github.com/VanSchulist/ghost-job-hunter): Autonomous agent...

[4] TAILORED ATS RESUME BULLET POINTS:
  • Built and maintained mcp-mesh: Engineered zero-dependency JSON-RPC stdio router supervising 50+ upstream MCP servers.
  • Built and maintained mcp-mesh: Implemented inverted index BM25 search reducing schema context from 25,000 to ~380 tokens.
  • Built and maintained ghost-job-hunter: Integrated company GitHub stack auditing to verify actual codebase vs recruiter claims.

[5] MCP-MESH TOKEN ECONOMY TELEMETRY:
  Turn-0 Baseline Context   : 1,700 tokens
  mcp-mesh Gateway Footprint: 380 tokens
  Static Token Reduction    : 77.6% (1,320 tokens saved)
  Runtime Tokens Saved      : 1,360 tokens across 4 tool calls

================================================================================
EXECUTIVE BYPASS VALUE PITCH (ATS PORTAL BYPASS)
Target: VP of Engineering at Apex Global Tech
Re: Principal Cloud Solutions Architect Architectural Bottlenecks & Operational Deliverables
================================================================================

SUBJECT: Engineering note on Apex Global Tech's Principal Solutions Architect roadmap

Dear VP of Engineering,

I came across Apex Global Tech's opening for Principal Solutions Architect. Public recruiting portals often get swamped by hundreds of generic LLM resumes; I wanted to bypass the noise and share concrete evidence of work directly addressing your operational layer:

- Proven open-source implementation: 'mcp-mesh' (Dynamic Model Context Protocol gateway cutting Turn-0 context bloat by 90%).
- Proven open-source implementation: 'ghost-job-hunter' (Autonomous heuristic and multi-agent system detecting phantom job listings).

I build production-grade, zero-dependency tools with extreme reliability. Rather than going through a 6-week automated ATS pipeline, I'd welcome a brief 10-minute technical exchange to discuss your team's immediate engineering roadmap.

Best regards,

Van Schulist
Systems & Autonomous Agent Engineer | Existential Cloud
GitHub: https://github.com/VanSchulist | Email: van@existentialcloud.ccwu.cc
================================================================================
```

---

## 🛠️ CLI Subcommands & Reference

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `python main.py hunt <target>` | `--title`, `--company`, `--output`, `--json` | **Flagship command**: End-to-end autonomous agent workflow. |
| `python main.py analyze <target>` | `--title`, `--company`, `--bypass`, `--json` | Heuristic evaluation with Ghost Probability Index (GPI) calculation. |
| `python main.py inspect <company>` | `--claimed <tech...>` | Audits public GitHub repositories, active languages, and commit recency. |
| `python main.py tailor <target>` | `--profile <path>`, `--company <name>` | Matches candidate profile to requirements and produces tailored bullet points. |
| `python main.py profile` | `--export <path>` | Displays active candidate persona or exports JSON template for customization. |
| `python main.py mesh-status` | None | Displays `mcp-mesh` gateway health, tool signatures, and token economy stats. |
| `python main.py register-mesh` | None | Automatically registers `ghost-job-hunter` into `mcp_config.json`. |
| `python main.py serve-mcp` | None | Runs standard MCP JSON-RPC 2.0 stdio server for AI clients and gateways. |
| `python main.py samples <type>` | `<ghost\|legit\|compliance>` | Evaluates calibrated benchmark postings. |
| `python main.py bypass` | `--title`, `--company`, `--head` | Generates a 1-page executive cold outreach letter on demand. |

---

## 🔌 Using as an MCP Server

`ghost-job-hunter` is a native Model Context Protocol (MCP) server. You can integrate it directly into `mcp-mesh`, Claude Desktop, Cursor, or Antigravity:

```json
{
  "mcpServers": {
    "ghost-job-hunter": {
      "command": "python",
      "args": ["-m", "ghost_hunter.server"]
    }
  }
}
```

Exposed MCP Tools:
* `ghost_hunter_audit_posting`: Evaluates job text and returns Ghost Probability Index (GPI).
* `ghost_hunter_audit_company`: Audits target company GitHub repos and tech stack reality.
* `ghost_hunter_hunt`: Runs full autonomous agent pipeline and returns formatted tactical dossier.

---

## 🧪 Automated Test Suite

Run the complete 21-test test suite across heuristics, GitHub auditing, candidate matching, agent loop, and MCP protocol:

```bash
python -m unittest discover -s tests
```

---

## 💭 The Vibe Coder's Note

```text
____________________________________________________________________
"I don't write syntax from scratch; I curate reality, vibe with 
frontier models, and ship production-grade systems."
                                            — Van Schulist
____________________________________________________________________
```

Curated, designed, and vibe-coded under **Existential Cloud**. Dedicated to every job seeker who refuses to let automated corporate hiring algorithms waste their time.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
