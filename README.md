# 👻 `ghost-job-hunter`

> **Deterministic Heuristic Scoring Engine & Opportunity Pipeline Ledger for Technical Hiring Auditing**  
> Evaluates job postings for phantom requisitions using 5 weighted heuristic engines, scrapes live developer hiring feeds, cross-references corporate GitHub footprints, persists pipeline stages to local SQLite, and generates standard RFC 822 email outreach packages with pure Python standard library.

[![Curated by Van Schulist](https://img.shields.io/badge/Author-Van%20Schulist-8A2BE2?style=flat-square)](https://github.com/VanSchulist)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Pure%20Stdlib%20(Zero%20External)-success?style=flat-square)](https://github.com/VanSchulist/ghost-job-hunter)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat-square)](https://github.com/VanSchulist/ghost-job-hunter)
[![Protocol: MCP](https://img.shields.io/badge/Protocol-MCP%202024--11--05-orange.svg?style=flat-square)](https://modelcontextprotocol.io/)
[![Powered by: mcp-mesh](https://img.shields.io/badge/Powered%20By-mcp--mesh%20Gateway-f59e0b?style=flat-square)](https://github.com/VanSchulist/mcp-mesh)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

---

## ⚡ 10-Second Zero-Install Quickstart

Audit a calibrated phantom job listing and view deterministic scoring breakdown in under 0.1 seconds:

```bash
# Instant zero-config demonstration (evaluates benchmark requisition & logs to SQLite pipeline)
uvx --from git+https://github.com/VanSchulist/ghost-job-hunter ghost-job-hunter --demo

# Analyze any local job description text file directly
uvx --from git+https://github.com/VanSchulist/ghost-job-hunter ghost-job-hunter analyze "path/to/job.txt"
```

---

## 🔬 Systems Engineering Problem & Methodological Foundation

Industry analyses report that 30% to 45% of active tech postings are "Ghost Jobs"—unfunded talent-pipeline traps, PERM immigration compliance placeholders, or corporate signals meant to project phantom growth without committed hiring intent.

`ghost-job-hunter` replaces manual screening with a deterministic 5-dimension weighted heuristic scoring model:

$$GPI = \sum_{i=1}^{5} w_i \cdot s_i$$

Where $w_i$ represents the empirically calibrated signal weight and $s_i \in [0, 100]$ represents the sub-engine score:

| Heuristic Engine | Weight ($w_i$) | Detection Mechanism & Logic |
| :--- | :---: | :--- |
| **Talent Pipeline / Evergreen Disclosure** | **0.30** | Regex pattern matching for non-requisition phrases (`"continuous pipeline"`, `"talent community"`, `"future consideration"`, `"proactive sourcing"`). |
| **Regulatory / Compliance Theater** | **0.25** | Identifies boilerplate language characteristic of US PERM immigration labor certification filings or legal transfer requirements where a hire has already been predetermined. |
| **Pay Transparency Evasion Spread** | **0.15** | Parses minimum ($M_{\min}$) and maximum ($M_{\max}$) compensation. If the spread ratio $(M_{\max} - M_{\min}) / M_{\min} > 1.20$ (120%), flags legal hedging designed to satisfy state disclosure laws without disclosing actionable compensation. |
| **The Unicorn Paradox (Scope Creep)** | **0.15** | Evaluates required domain boundaries. Flags requisitions demanding deep specialization across $\ge 4$ conflicting engineering silos (e.g. React frontend + Rust systems + Kubernetes SRE + Sales prospecting). |
| **Corporate Fluff & Buzzword Density** | **0.15** | Measures the statistical ratio of non-functional corporate clichés (`"rockstar"`, `"ninja"`, `"wear many hats"`, `"synergy"`) relative to concrete technical deliverables. |

### Classification Tiers

- **`CRITICAL_GHOST`** ($GPI \ge 65.0\%$): High-confidence phantom requisition. Submitting via web ATS portal is an algorithmic dead end. Direct bypass pitch recommended.
- **`SUSPECTED_HARVEST`** ($40.0\% \le GPI < 65.0\%$): Evergreen talent harvesting or compliance placeholder.
- **`ACTIVE_REQUISITION`** ($GPI < 40.0\%$): Legitimate hiring requisition with committed headcount and concrete deliverables.

---

## 🏛️ System Architecture

```text
 ┌────────────────────────────────────────────────────────┐
 │            Developer CLI / AI Agent Driver             │
 │         uvx ghost-job-hunter hunt "job_posting.txt"    │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │                JobHunterAgent (Pipeline)               │
 └──────┬────────────────────┬────────────────────┬───────┘
        │ 1. Ingestion       │ 2. Heuristics      │ 3. Match
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

## ⚙️ Core Technical Capabilities

* **100% Zero External Dependencies**: Engineered strictly with Python 3.8+ standard library (`urllib.request`, `json`, `sqlite3`, `email`, `re`, `argparse`). Instant, frictionless deployment.
* **Live Developer Hiring Feeds (`live`)**: Scrapes active engineering postings directly from Hacker News (*"Ask HN: Who is hiring?"*), RemoteOK, and WeWorkRemotely without third-party web scrapers.
* **Local SQLite Pipeline Ledger (`pipeline`)**: Automatically persists tracked opportunities to `~/.ghost-hunter/pipeline.db` using SQLite with WAL mode. Tracks lifecycle states: `DISCOVERED` ➔ `AUDITED` ➔ `PITCH_READY` ➔ `APPLIED` ➔ `INTERVIEWING` ➔ `OFFER` ➔ `REJECTED`.
* **RFC 822 Email Package Exporter (`--export`)**: Compiles tailored outreach into standard `.eml` MIME files compatible with Apple Mail, Thunderbird, and Microsoft Outlook, paired with markdown dossiers and direct `mailto:` links.
* **Corporate GitHub Footprint Auditing (`inspect`)**: Cross-references job requisition tech claims against target company public GitHub organizations to verify actual commit recency and language distribution.
* **Native Model Context Protocol (MCP) Server (`serve-mcp`)**: Can be integrated directly as an MCP server for Claude Desktop, Cursor, or `mcp-mesh`.

---

## 💻 CLI Subcommand Reference

```bash
# 1. Run zero-config demonstration on calibrated benchmark
ghost-job-hunter --demo

# 2. Autonomous end-to-end audit and pipeline ingestion
ghost-job-hunter hunt "path/to/job_posting.txt" --company "Stripe" --title "Staff Infrastructure Engineer" --export

# 3. Scrape live remote developer positions and save to local pipeline
ghost-job-hunter live --source hn --remote --limit 10 --save

# 4. Query and export local pipeline opportunities (Table, JSON, CSV)
ghost-job-hunter pipeline list --status AUDITED --max-gpi 40.0
ghost-job-hunter pipeline list --format json
ghost-job-hunter pipeline export --format csv --output leads.csv

# 5. Inspect corporate GitHub engineering reality
ghost-job-hunter inspect "CompanySlug" --claimed rust kubernetes python

# 6. Run as an MCP stdio server
ghost-job-hunter serve-mcp
```

---

## 🧪 Automated Test Suite

```bash
python -m unittest discover -s tests -v
```

All 38 test cases execute in ~9 seconds using Python's standard library test runner.

---

## 📄 License

Released under the **MIT License**. Maintained by **Van Schulist (@VanSchulist)** at **Existential Cloud AI Studio**.
