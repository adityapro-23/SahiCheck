"""Deterministic scoring and report synthesis for SahiCheck."""

import json
import os
from typing import Dict, List, Literal, Tuple

from checks_registry import get_checks
from schemas import CheckResult, ExtractionResult, FinalReport, RedFlag, VerificationBundle

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

MANDATORY_NEXT_STEPS = [
    "Do NOT pay any registration, training, laptop/kit, or refundable security deposit fee.",
    "Do NOT share any OTP, UPI PIN, bank passbook, Aadhaar, or PAN card details over chat or unverified email.",
    "Verify the job opening directly on the company's official website and official careers portal.",
    "Contact the company's HR department only through phone numbers or emails listed on its official website.",
    "If money or sensitive data was requested, report the fraud immediately at https://cybercrime.gov.in or call India's National Cyber Crime Helpline at 1930.",
]


def _load_scoring_config() -> Dict:
    path = os.path.join(DATA_DIR, "rules.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["scoring"]


def compute_deterministic_score_and_verdict(
    red_flags: List[RedFlag],
    checks: List[CheckResult],
) -> Tuple[int, Literal["SAFE", "SUSPICIOUS", "SCAM"], Literal["low", "medium", "high"], List[str]]:
    """Scores passed registry checks, applies the lowest hard cap, and determines a verdict."""
    config = _load_scoring_config()
    flags_by_id = {flag.id for flag in red_flags}
    verification_by_id = {check.id: check for check in checks}
    verification_by_id["pay_plausibility"] = verification_by_id.get(
        "salary_plausibility"
    )

    check_statuses: Dict[str, str] = {}
    raw_score = 0
    eligible_checks = 0

    for meta in get_checks():
        check_id = meta["id"]
        if meta["flag_ids"]:
            status = "failed" if flags_by_id.intersection(meta["flag_ids"]) else "passed"
        elif (
            check_id == "pay_plausibility"
            and "unrealistic_daily_or_part_time_pay" in flags_by_id
        ):
            status = "failed"
        elif check_id == "verify_links":
            status = "info"
        else:
            verification_result = verification_by_id.get(check_id)
            status = verification_result.status if verification_result else "unavailable"

        check_statuses[check_id] = status
        if status in ("passed", "failed"):
            eligible_checks += 1
        if status == "passed":
            raw_score += meta["max_points"]

    if check_statuses.get("lookalike_domain") == "failed":
        if check_statuses.get("official_domain") == "passed":
            raw_score -= next(
                meta["max_points"] for meta in get_checks()
                if meta["id"] == "official_domain"
            )
        check_statuses["official_domain"] = "failed"
        official = verification_by_id.get("official_domain")
        if official:
            official.status = "failed"
            official.detail = "Forced failed because a lookalike/spoof domain was detected."

    caps: List[Tuple[int, str]] = []
    for check_id in ("payment_demand", "otp_request", "id_doc_request"):
        if check_statuses.get(check_id) == "failed":
            labels = {
                "payment_demand": "a payment demand",
                "otp_request": "an OTP/PIN request",
                "id_doc_request": "an ID document request",
            }
            caps.append((29, f"Limited to 29 because {labels[check_id]} was found."))
    for check_id in ("blocklisted_domain", "lookalike_domain"):
        if check_statuses.get(check_id) == "failed":
            label = "a blocklisted domain" if check_id == "blocklisted_domain" else "a lookalike domain"
            caps.append((35, f"Limited to 35 because {label} was found."))

    cap = min(caps, key=lambda item: item[0]) if caps else None
    score = raw_score if cap is None else min(raw_score, cap[0])
    score = max(1, min(99, score))
    hard_cap_reasons = [cap[1]] if cap else []

    ratio = eligible_checks / max(1, len(get_checks()) - 1)
    if ratio >= 0.75:
        coverage: Literal["low", "medium", "high"] = "high"
    elif ratio >= 0.5:
        coverage = "medium"
    else:
        coverage = "low"

    thresholds = _load_scoring_config()["verdict_thresholds"]
    if score >= int(thresholds["safe_min"]):
        verdict: Literal["SAFE", "SUSPICIOUS", "SCAM"] = "SAFE"
    elif score >= int(thresholds["suspicious_min"]):
        verdict = "SUSPICIOUS"
    else:
        verdict = "SCAM"

    return score, verdict, coverage, hard_cap_reasons


def _build_summary(
    verdict: str,
    score: int,
    company: str,
    red_flags: List[RedFlag],
    checks: List[CheckResult],
    cap_reasons: List[str],
) -> str:
    company_label = f"claimed to be from {company}" if company else "submitted"
    if verdict == "SCAM":
        reasons = ", ".join(flag.id.replace("_", " ") for flag in red_flags[:2])
        reason_text = reasons or "critical fraud indicators"
        cap_note = f" {cap_reasons[0]}" if cap_reasons else ""
        return (
            f"High-risk scam indicators detected in the offer {company_label} "
            f"(Legitimacy Score: {score}/100) due to {reason_text}.{cap_note}"
        )
    if verdict == "SUSPICIOUS":
        return (
            f"This job offer {company_label} shows mixed or incomplete evidence "
            f"(Legitimacy Score: {score}/100) with {len(red_flags)} warning flag(s). "
            "Verify independently before responding."
        )
    passed_names = [check.name for check in checks if check.status == "passed"]
    passed_text = ", ".join(passed_names[:2]) if passed_names else "standard checks"
    return (
        f"This offer {company_label} passed key legitimacy checks including {passed_text} "
        f"(Legitimacy Score: {score}/100), with no high-risk scam demands detected."
    )


def run_synthesis(
    extraction: ExtractionResult,
    red_flags: List[RedFlag],
    verification: VerificationBundle,
) -> FinalReport:
    """Builds the report from deterministic checks without making an LLM call."""
    score, verdict, coverage, cap_reasons = compute_deterministic_score_and_verdict(
        red_flags=red_flags,
        checks=verification.checks,
    )
    return FinalReport(
        verdict=verdict,
        legitimacy_score=score,
        evidence_coverage=coverage,
        summary=_build_summary(
            verdict=verdict,
            score=score,
            company=extraction.extracted.company,
            red_flags=red_flags,
            checks=verification.checks,
            cap_reasons=cap_reasons,
        ),
        red_flags=red_flags,
        checks=verification.checks,
        positive_signs=verification.positive_signs,
        next_steps=list(MANDATORY_NEXT_STEPS),
        verify_links=verification.verify_links,
        extracted=extraction.extracted,
    )
