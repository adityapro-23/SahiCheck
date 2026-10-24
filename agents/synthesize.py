# TODO: Agent 3 - Deterministic Scorer & Synthesizer (Score calculation in code + Gemma explanation)

"""Agent 3: Deterministic Scorer & Synthesizer (agents/synthesize.py).
- Verdict and legitimacy_score (3..97) are computed deterministically in Python code.
- Hard caps are enforced for any payment/fee demand, OTP request, ID-document request (cap 29),
  or lookalike/blocklisted domain (cap 35). Verified official domain does NOT lift hard caps.
- Gemma 4 receives the fixed score, verdict, flags, and checks, and writes ONLY the
  plain-language summary, per-flag explanation refinements, and next steps.
- Includes Pydantic validation, 1 retry, and a deterministic template fallback in code.
"""

import json
import os
from typing import Any, Dict, List, Literal, Tuple

from llm import call_gemma
from schemas import (
    CheckResult,
    ExtractionResult,
    FinalReport,
    GemmaSynthesisOutput,
    RedFlag,
    VerificationBundle,
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

MANDATORY_NEXT_STEPS = [
    "Do NOT pay any registration, training, laptop/kit, or refundable security deposit fee.",
    "Do NOT share any OTP, UPI PIN, bank passbook, Aadhaar, or PAN card details over chat or unverified email.",
    "Verify the job opening directly on the company's official website and official careers portal.",
    "Contact the company's HR department only through phone numbers or emails listed on its official website.",
    "If money or sensitive data was requested, report the fraud immediately at https://cybercrime.gov.in or call India's National Cyber Crime Helpline at 1930.",
]

SYNTHESIS_PROMPT_TEMPLATE = """You are Agent 3 (Explainer) in SahiCheck, an open-source job offer fraud detector for students and job seekers in India.
The deterministic scoring engine has ALREADY decided the fixed score and verdict below. You MUST NOT change the verdict or score.

FIXED VERDICT: {verdict}
FIXED LEGITIMACY SCORE: {score}/100 (Evidence coverage: {coverage})
CLAIMED COMPANY: {company}
CLAIMED ROLE: {role}

RED FLAGS FOUND:
{flags_json}

VERIFICATION CHECKS:
{checks_json}

Write a clear, empathetic explanation in simple English for a student/job seeker.
Return ONLY a valid JSON object matching this exact schema:
{{
  "summary": "One or two plain-English sentences explaining why this offer is marked {verdict} (Score {score}/100).",
  "flag_explanations": [
    {{"id": "flag_id_from_input", "why_it_matters": "1 short plain-English sentence explaining the risk"}}
  ],
  "next_steps": [
    "3 to 5 practical next steps (must include not paying any fee, not sharing OTP/ID documents, verifying on official careers page, and reporting scams at cybercrime.gov.in or 1930)"
  ]
}}
"""


def _load_scoring_config() -> Dict[str, Any]:
    path = os.path.join(DATA_DIR, "rules.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["scoring"]


def compute_deterministic_score_and_verdict(
    red_flags: List[RedFlag],
    checks: List[CheckResult],
) -> Tuple[int, Literal["SAFE", "SUSPICIOUS", "SCAM"], Literal["low", "medium", "high"], List[str]]:
    """Computes legitimacy_score (3..97), verdict, evidence_coverage, and active hard-cap reasons."""
    cfg = _load_scoring_config()
    score = int(cfg.get("base_score", 50))
    penalties = cfg["flag_penalties"]
    deltas = cfg["check_deltas"]

    # 1. Subtract Red Flags
    for flag in red_flags:
        score += int(penalties.get(flag.severity, -5))

    # 2. Add/Subtract Verification Check Deltas
    ran_checks = 0
    for chk in checks:
        tier_map = deltas.get(chk.tier, {"passed": 0, "failed": 0, "unavailable": 0})
        delta = int(tier_map.get(chk.status, 0))
        chk.score_delta = delta
        score += delta
        if chk.status in ("passed", "failed"):
            ran_checks += 1

    # 3. Apply Hard Caps (official domain NEVER lifts these caps)
    hard_cap_reasons: List[str] = []
    fee_otp_id_categories = {"hard_cap_fee", "hard_cap_otp", "hard_cap_id"}
    has_fee_otp_id = any(f.category in fee_otp_id_categories for f in red_flags)
    has_domain_spoof = any(
        f.category == "hard_cap_domain" and f.severity == "high" for f in red_flags
    )

    if has_fee_otp_id:
        cap_29 = int(cfg["hard_caps"]["fee_otp_id_cap"])
        if score > cap_29:
            score = cap_29
        hard_cap_reasons.append("Score capped at 29 due to upfront payment/UPI, OTP, or ID document demand.")

    if has_domain_spoof:
        cap_35 = int(cfg["hard_caps"]["domain_spoof_cap"])
        if score > cap_35:
            score = cap_35
        hard_cap_reasons.append("Score capped at 35 due to high-severity lookalike or blocklisted domain.")

    # 4. Clamp to 3..97 (never claim 0% or 100% certainty)
    score = max(int(cfg.get("clamp_min", 3)), min(int(cfg.get("clamp_max", 97)), score))

    # 5. Evidence coverage
    total_checks = max(1, len(checks))
    ratio = ran_checks / float(total_checks)
    if ratio >= 0.75:
        coverage: Literal["low", "medium", "high"] = "high"
    elif ratio >= 0.5:
        coverage = "medium"
    else:
        coverage = "low"

    # 6. Verdict bands (prefer SUSPICIOUS over SCAM when evidence is weak/mixed and no hard cap applies)
    high_flags_count = sum(1 for f in red_flags if f.severity == "high")
    if score >= int(cfg["verdict_thresholds"]["safe_min"]):
        verdict: Literal["SAFE", "SUSPICIOUS", "SCAM"] = "SAFE"
    elif score >= int(cfg["verdict_thresholds"]["suspicious_min"]):
        verdict = "SUSPICIOUS"
    else:
        if not hard_cap_reasons and high_flags_count == 0 and coverage == "low":
            verdict = "SUSPICIOUS"
            score = max(score, 40)
        else:
            verdict = "SCAM"

    return score, verdict, coverage, hard_cap_reasons


def _build_template_fallback_summary(
    verdict: str,
    score: int,
    company: str,
    red_flags: List[RedFlag],
    checks: List[CheckResult],
    hard_cap_reasons: List[str],
) -> str:
    """Deterministic plain-language summary fallback if LLM explanation fails."""
    comp_label = f"claimed to be from {company}" if company else "submitted"
    if verdict == "SCAM":
        top_reasons = [f.id.replace("_", " ") for f in red_flags[:2]]
        reason_str = ", ".join(top_reasons) if top_reasons else "critical fraud indicators"
        cap_note = f" {hard_cap_reasons[0]}" if hard_cap_reasons else ""
        return (
            f"High-risk scam indicators detected in the offer {comp_label} (Legitimacy Score: {score}/100) "
            f"due to {reason_str}.{cap_note}"
        )
    if verdict == "SUSPICIOUS":
        return (
            f"This job offer {comp_label} shows mixed or incomplete evidence (Legitimacy Score: {score}/100) "
            f"with {len(red_flags)} warning flag(s). Verify independently before responding."
        )
    passed_names = [c.name for c in checks if c.status == "passed"]
    passed_str = ", ".join(passed_names[:2]) if passed_names else "standard checks"
    return (
        f"This offer {comp_label} passed key legitimacy checks including {passed_str} "
        f"(Legitimacy Score: {score}/100), with no high-risk scam demands detected."
    )


def run_synthesis(
    extraction: ExtractionResult,
    red_flags: List[RedFlag],
    verification: VerificationBundle,
) -> FinalReport:
    """Computes final score and verdict in code, then asks Gemma 4 for plain-English explanations."""
    score, verdict, coverage, hard_cap_reasons = compute_deterministic_score_and_verdict(
        red_flags=red_flags,
        checks=verification.checks,
    )

    summary = _build_template_fallback_summary(
        verdict=verdict,
        score=score,
        company=extraction.extracted.company,
        red_flags=red_flags,
        checks=verification.checks,
        hard_cap_reasons=hard_cap_reasons,
    )
    next_steps = list(MANDATORY_NEXT_STEPS)

    # Prepare prompt for Gemma 4 explanation
    prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        verdict=verdict,
        score=score,
        coverage=coverage,
        company=extraction.extracted.company or "Unspecified",
        role=extraction.extracted.role or "Unspecified",
        flags_json=json.dumps([f.model_dump() for f in red_flags], indent=2),
        checks_json=json.dumps([c.model_dump() for c in verification.checks], indent=2),
    )

    # Try Gemma 4 with 1 retry, validated by Pydantic
    for _attempt in range(2):
        try:
            raw_dict, _model_id = call_gemma(prompt=prompt, images=None, expect_json=True)
            parsed = GemmaSynthesisOutput.model_validate(raw_dict)
            if parsed.summary.strip():
                summary = parsed.summary.strip()

            # Map refined per-flag explanations back without losing any flags
            exp_map = {item.id: item.why_it_matters.strip() for item in parsed.flag_explanations if item.why_it_matters.strip()}
            for flag in red_flags:
                if flag.id in exp_map:
                    suffix = (
                        " (Severity lowered because extracted field was unverified)."
                        if flag.unverified_downgraded and "unverified" not in exp_map[flag.id].lower()
                        else ""
                    )
                    flag.why_it_matters = exp_map[flag.id] + suffix

            # Merge model's next steps with mandatory safety steps
            merged_steps: List[str] = []
            for step in parsed.next_steps + MANDATORY_NEXT_STEPS:
                clean_s = step.strip()
                if clean_s and clean_s not in merged_steps:
                    merged_steps.append(clean_s)
            next_steps = merged_steps[:6]
            break
        except Exception:
            continue

    return FinalReport(
        verdict=verdict,
        legitimacy_score=score,
        evidence_coverage=coverage,
        summary=summary,
        red_flags=red_flags,
        checks=verification.checks,
        positive_signs=verification.positive_signs,
        next_steps=next_steps,
        verify_links=verification.verify_links,
        extracted=extraction.extracted,
    )