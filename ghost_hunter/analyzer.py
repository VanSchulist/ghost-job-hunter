"""
Text Ingestion, Signal Evaluation, and Score Calculation Engine.
"""

import re
import math
from typing import List, Dict, Optional, Tuple
from .core import (
    HeuristicSignal, DiagnosticReport,
    EVERGREEN_PATTERNS, COMPLIANCE_THEATER_PATTERNS,
    FLUFF_TERMS, DELIVERABLE_VERBS, TECH_DOMAINS
)

class JobAnalyzer:
    """
    Evaluates job postings against known corporate ghost-job heuristics.
    """

    def __init__(self):
        pass

    def extract_salary_range(self, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts annual salary or hourly rate numbers to evaluate pay spread absurdity.
        """
        # Matches patterns like $120,000 - $280,000 or $120k - $280k or $120k-$280k
        range_pattern = r"\$\s*(\d{2,3}(?:,\d{3})*k?)\s*(?:-|to|–|—)\s*\$?\s*(\d{2,3}(?:,\d{3})*k?)"
        match = re.search(range_pattern, text, re.IGNORECASE)
        
        if not match:
            return {"min": None, "max": None, "spread_ratio": None}
        
        def parse_val(s: str) -> float:
            s = s.lower().replace(",", "").strip()
            if s.endswith("k"):
                return float(s[:-1]) * 1000.0
            return float(s)

        try:
            min_val = parse_val(match.group(1))
            max_val = parse_val(match.group(2))
            if min_val <= 0:
                return {"min": None, "max": None, "spread_ratio": None}
            spread_ratio = (max_val - min_val) / min_val
            return {
                "min": min_val,
                "max": max_val,
                "spread_ratio": round(spread_ratio, 2)
            }
        except Exception:
            return {"min": None, "max": None, "spread_ratio": None}

    def detect_evergreen_signals(self, text: str) -> Tuple[bool, List[str]]:
        evidence = []
        for pat in EVERGREEN_PATTERNS:
            matches = re.findall(pat, text, re.IGNORECASE)
            if matches:
                evidence.append(f"Detected pipeline keyword matching pattern '{pat}'")
        return len(evidence) > 0, evidence

    def detect_compliance_theater(self, text: str) -> Tuple[bool, List[str]]:
        evidence = []
        for pat in COMPLIANCE_THEATER_PATTERNS:
            matches = re.findall(pat, text, re.IGNORECASE)
            if matches:
                evidence.append(f"Detected legal compliance pattern '{pat}'")
        return len(evidence) > 0, evidence

    def calculate_fluff_density(self, text: str) -> Tuple[float, List[str]]:
        lower_text = text.lower()
        words = re.findall(r"\b[a-z]{3,}\b", lower_text)
        total_words = max(len(words), 1)
        
        detected_fluff = []
        for term in FLUFF_TERMS:
            count = lower_text.count(term)
            if count > 0:
                detected_fluff.append(f"'{term}' (x{count})")
        
        fluff_ratio = (len(detected_fluff) * 15.0) / (total_words / 100.0)
        return min(fluff_ratio, 100.0), detected_fluff

    def evaluate_unicorn_paradox(self, text: str) -> Tuple[float, List[str]]:
        lower_text = text.lower()
        domains_detected = {}
        
        for domain, keywords in TECH_DOMAINS.items():
            matched_kw = [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", lower_text)]
            if matched_kw:
                domains_detected[domain] = matched_kw

        evidence = []
        # If demanding 4 or more completely distinct disciplines in one job (e.g. Frontend + Backend + Data + Sales)
        if len(domains_detected) >= 4:
            evidence.append(
                f"Demands mastery across {len(domains_detected)} conflicting disciplines: " +
                ", ".join([f"{k} ({', '.join(v[:2])})" for k, v in domains_detected.items()])
            )
            score = 85.0
        elif len(domains_detected) == 3:
            evidence.append(
                f"Spans 3 wide disciplines: " +
                ", ".join([f"{k} ({', '.join(v[:2])})" for k, v in domains_detected.items()])
            )
            score = 45.0
        else:
            score = 0.0

        return score, evidence

    def evaluate_deliverables_presence(self, text: str) -> Tuple[float, List[str]]:
        lower_text = text.lower()
        detected_verbs = [v for v in DELIVERABLE_VERBS if re.search(r"\b" + re.escape(v) + r"\b", lower_text)]
        
        evidence = []
        if len(detected_verbs) < 3:
            evidence.append(f"Only {len(detected_verbs)} concrete action verbs found. Role is heavily abstract.")
            score = 75.0
        else:
            score = 15.0
        return score, evidence

    def analyze(self, raw_text: str, title: str = "Unknown Title", company: str = "Unknown Company") -> DiagnosticReport:
        clean_text = raw_text.strip()
        
        # 1. Evergreen Pipeline Check
        is_evergreen, ev_evidence = self.detect_evergreen_signals(clean_text)
        sig_evergreen = HeuristicSignal(
            id="EVERGREEN_PIPELINE",
            name="Talent Pipeline / Evergreen Disclosure",
            weight=0.30,
            score=95.0 if is_evergreen else 5.0,
            triggered=is_evergreen,
            evidence=ev_evidence,
            description="Posting explicitly or implicitly states it is a talent pipeline rather than an active immediate requisition."
        )

        # 2. Compliance Theater Check
        is_compliance, comp_evidence = self.detect_compliance_theater(clean_text)
        sig_compliance = HeuristicSignal(
            id="COMPLIANCE_THEATER",
            name="Regulatory / Internal Transfer Theater",
            weight=0.25,
            score=90.0 if is_compliance else 0.0,
            triggered=is_compliance,
            evidence=comp_evidence,
            description="Posting exhibits hallmarks of mandated public advertising for an already pre-selected internal candidate."
        )

        # 3. Salary Spread Absurdity
        salary_info = self.extract_salary_range(clean_text)
        spread_ratio = salary_info.get("spread_ratio")
        sig_salary_triggered = False
        sig_salary_score = 0.0
        sal_evidence = []

        if spread_ratio is not None:
            if spread_ratio > 1.20:  # e.g., $100k to $230k+
                sig_salary_triggered = True
                sig_salary_score = 80.0
                sal_evidence.append(
                    f"Salary spread is {int(spread_ratio * 100)}% (${salary_info['min']:,.0f} - ${salary_info['max']:,.0f}). "
                    "Used to obscure actual compensation while legally satisfying pay transparency statutes."
                )
            elif spread_ratio > 0.60:
                sig_salary_score = 35.0
                sal_evidence.append(f"Moderate salary spread: {int(spread_ratio * 100)}%.")
        else:
            sal_evidence.append("No salary or compensation range disclosed.")

        sig_salary = HeuristicSignal(
            id="SALARY_SPREAD",
            name="Pay Transparency Evasion / Absurd Spread",
            weight=0.15,
            score=sig_salary_score,
            triggered=sig_salary_triggered,
            evidence=sal_evidence,
            description="Wide salary bands indicate corporate compensation hedge with no committed budget line."
        )

        # 4. Unicorn Paradox (Scope Creep)
        unicorn_score, unicorn_ev = self.evaluate_unicorn_paradox(clean_text)
        sig_unicorn = HeuristicSignal(
            id="UNICORN_PARADOX",
            name="Unicorn Paradox & Multi-Domain Scope Creep",
            weight=0.15,
            score=unicorn_score,
            triggered=unicorn_score >= 50.0,
            evidence=unicorn_ev,
            description="Demanding multi-disciplinary mastery usually reflects a phantom committee wish-list without a real hiring manager."
        )

        # 5. Fluff Ratio vs Concrete Deliverables
        fluff_score, fluff_ev = self.calculate_fluff_density(clean_text)
        sig_fluff = HeuristicSignal(
            id="FLUFF_DENSITY",
            name="Corporate Fluff & Buzzword Overload",
            weight=0.15,
            score=fluff_score,
            triggered=fluff_score >= 50.0,
            evidence=fluff_ev,
            description="Disproportionate density of corporate buzzwords relative to functional deliverables."
        )

        signals = [sig_evergreen, sig_compliance, sig_salary, sig_unicorn, sig_fluff]

        # Calculate Weighted Ghost Probability Index (GPI)
        total_weighted_score = sum(s.score * s.weight for s in signals)
        total_weight = sum(s.weight for s in signals)
        gpi = round(total_weighted_score / total_weight, 1)

        # Classify Risk Level
        if gpi >= 65.0:
            risk_level = "CRITICAL_GHOST"
            verdict = "HIGH PROBABILITY GHOST JOB (Applying via portal is an algorithmic black hole)"
            rec = "DO NOT submit through the web portal. Bypass directly to the functional VP/Director with an Executive Pitch Letter."
        elif gpi >= 40.0:
            risk_level = "SUSPECTED_HARVEST"
            verdict = "SUSPECTED RESUME HARVEST / LOW-PRIORITY REQUISITION"
            rec = "Apply only if quick (<2 mins). Do not tailor custom cover letters for this portal; use warm outreach to verify urgency."
        elif gpi >= 20.0:
            risk_level = "LOW_CONFIDENCE"
            verdict = "LOW-CONFIDENCE REQUISITION (Moderate Fluff Detected)"
            rec = "Requisition appears active but contains corporate hedging. Submit standard ATS-proof resume."
        else:
            risk_level = "ACTIVE"
            verdict = "ACTIVE REQUISITION (Legitimate Hiring Intent)"
            rec = "High-confidence active opening. Ensure targeted keyword alignment and apply promptly."

        return DiagnosticReport(
            job_title=title,
            company_name=company,
            ghost_probability_index=gpi,
            risk_level=risk_level,
            verdict_summary=verdict,
            signals=signals,
            salary_analysis=salary_info,
            key_responsibilities=[],
            detected_tech_stack=[],
            actionable_recommendation=rec
        )
