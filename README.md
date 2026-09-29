# 👻 Ghost Job Hunter
### *An open-source heuristic engine & CLI for detecting phantom job postings, resume harvesting traps, and corporate hiring theater.*

[![Vibe Coded with Pride](https://img.shields.io/badge/Methodology-Vibe%20Coding-8A2BE2?style=flat-square&logo=openai)](https://github.com/VanSchulist)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-success?style=flat-square)](https://github.com/VanSchulist/ghost-job-hunter)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=flat-square)](https://github.com/VanSchulist/ghost-job-hunter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

```text
   ____ _   _  ___  ____ _____      _  ___  ____  
  / ___| | | |/ _ \/ ___|_   _|    | |/ _ \| __ ) 
 | |  _| |_| | | | \___ \ | |   _  | | | | |  _ \ 
 | |_| |  _  | |_| |___) || |  | |_| | |_| | |_) |
  \____|_| |_|\___/|____/ |_|   \___/ \___/|____/ 
  >> GHOST JOB HUNTER v1.0.0 | Existential Cloud <<
  Curated & Vibe-Coded by Van Schulist (@VanSchulist)
```

> *"According to labor disclosures and recruiter whistleblowers on X, over 40% of tech job listings are 'Ghost Jobs'—postings kept perpetually open to pacify overworked staff, build passive resume banks, or project illusory growth to investors. Applying to them via web portals is an algorithmic trap. This tool is the countermeasure."*

---

## 🌩️ Origin & The Existential Cloud Story

Hi, I'm **Van Schulist** (`@VanSchulist`). I'm an American undergraduate student and an unapologetic **vibe coder** running **Existential Cloud**.

Following the release of [**The Career Reboot Armor**](https://github.com/VanSchulist/career-reboot-armor), job seekers on X kept asking the same desperate question: *"How do I know if an opening is real before I burn 3 hours tailoring my resume?"*

I dug through dozens of recruiter confession threads, pay transparency evasion loopholes, and compliance filings. Then, I vibe-coded **Ghost Job Hunter**—a zero-dependency, lightning-fast Python CLI that runs heuristic pattern recognition against any job description, calculates a **Ghost Probability Index (GPI)**, and synthesizes a direct **1-Page Executive Bypass Pitch** to the department head if the portal is flagged as a phantom.

---

## ⚡ The 5 Diagnostic Heuristic Engines

| Heuristic Engine | Weight | What It Detects |
| :--- | :---: | :--- |
| **Talent Pipeline / Evergreen Disclosure** | **30%** | Catches fine-print language admitting the post is a *"continuous talent community"*, *"future consideration"*, or *"bench building"* requisition with zero committed headcount. |
| **Regulatory / Compliance Theater** | **25%** | Flags boilerplate disclosures required by federal PERM immigration filings or internal transfer laws where a candidate has already been selected. |
| **Pay Transparency Evasion Index** | **15%** | Calculates the salary band spread ratio (e.g. `$90,000 - $265,000`). Ratios exceeding 120% indicate corporate legal hedging to skirt state laws without real budget approval. |
| **The Unicorn Paradox (Scope Creep)** | **15%** | Flags requisitions demanding deep mastery across 3 or more incompatible disciplines (e.g. React frontend + Rust systems + Kubernetes SRE + Sales prospecting). |
| **Fluff & Buzzword Overload Density** | **15%** | Measures the statistical ratio of empty corporate adjectives (*"rockstar"*, *"ninja"*, *"synergy"*, *"wear many hats"*) against verifiable functional KPIs. |

---

## 🚀 Quickstart & Installation

**Ghost Job Hunter requires ZERO external libraries.** It runs out of the box with standard Python 3.8+.

```bash
# 1. Clone the repository
git clone https://github.com/VanSchulist/ghost-job-hunter.git
cd ghost-job-hunter

# 2. Run diagnostic against built-in benchmarks
python main.py samples ghost
python main.py samples legit
python main.py samples compliance

# 3. Analyze any job description file or text
python main.py analyze "path/to/job_posting.txt" --title "Senior Backend Engineer" --company "Acme Corp"

# 4. Analyze and automatically generate a 1-page Executive Bypass Pitch Letter if GPI >= 40%
python main.py analyze "path/to/job_posting.txt" --bypass
```

---

## 📊 Sample Output

```text
============================================================================
DIAGNOSTIC REPORT: Principal Solutions Architect @ Apex Global Tech
============================================================================

Ghost Probability Index (GPI):
  [#############-------] 68.2%

Classification: [ CRITICAL GHOST JOB / PIPELINE THEATER ]
Verdict: HIGH PROBABILITY GHOST JOB (Applying via portal is an algorithmic black hole)

----------------------------------------------------------------------------
SIGNAL EVALUATED                         WEIGHT   SCORE    STATUS
----------------------------------------------------------------------------
Talent Pipeline / Evergreen Disclosure   0.30     95.0     TRIGGERED
  -> Detected pipeline keyword matching pattern '\bcontinuous\s+pipeline\b'
  -> Detected pipeline keyword matching pattern '\btalent\s+community\b'
Pay Transparency Evasion / Absurd Spread 0.15     80.0     TRIGGERED
  -> Salary spread is 179% ($95,000 - $265,000). Used to obscure actual compensation.
Unicorn Paradox & Multi-Domain Scope Creep 0.15     85.0     TRIGGERED
  -> Demands mastery across 4 conflicting disciplines: Frontend, Systems, DevOps, Data
Corporate Fluff & Buzzword Overload      0.15     100.0    TRIGGERED
  -> 'rockstar' (x1), 'ninja' (x1), 'wear many hats' (x1), 'radical transparency' (x1)

============================================================================
ACTIONABLE TACTICAL RECOMMENDATION:
  DO NOT submit through the web portal. Bypass directly to the functional VP/Director with an Executive Pitch Letter.
============================================================================
```

---

## 🛠️ CLI Subcommands & Options

* `python main.py analyze <target>`: Evaluates a raw string or file path.
  * `--title <str>`: Specify target job title.
  * `--company <str>`: Specify target company.
  * `--bypass`: Automatically output a tailored 1-page Executive Pitch Letter if the role is flagged as high-risk.
  * `--json`: Output machine-readable JSON for integration into custom scrapers and agentic pipelines.
* `python main.py bypass --title <title> --company <company> --head <title>`: Generate an on-demand Executive Bypass Pitch Letter.
* `python main.py samples <ghost|legit|compliance>`: Run instant verification against calibrated benchmarks.

---

## 🧪 Running the Test Suite

```bash
python -m unittest discover -s tests
```

---

## 💭 The Vibe Coder's Note

```
____________________________________________________________________
"I don't write syntax from scratch; I curate reality, vibe with 
frontier models, and ship production-grade systems."
                                            — Van Schulist
____________________________________________________________________
```

Engineered 100% via vibe coding and agentic prompt chains under **Existential Cloud**. Free, open source, and dedicated to every job seeker tired of screaming into the corporate recruitment void.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
