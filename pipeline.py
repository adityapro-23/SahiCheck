"""pipeline.py – Streaming generator for the SahiCheck pipeline.

`run(normalized_input, run_web_checks)` is a **synchronous** generator that
yields JSON-serialisable dicts.  FastAPI's StreamingResponse wraps this in a
threadpool so it does not block the event loop.

Event shapes (all serialised to one JSON line each):
  {"type":"stage","id":"extract","state":"running|done"}
  {"type":"check","id":N,"state":"running|done","status":"...","points":N,"max_points":N}
  {"type":"final","score":N,"cap_reason":"...|null"}
  {"type":"error","message":"..."}

Rules enforced here:
- Exactly one spinner at any moment (running -> done before the next running).
- Offline checks are revealed one-by-one with a short sleep so the UI is readable.
- Web checks (14 RDAP, 15 legal pages) emit running BEFORE the network call.
- Any failure emits {"type":"error",...} and the generator returns immediately.
- No uploaded content is ever logged.
"""

import time
from typing import Any, Dict, Generator, Iterator, List, Optional, Tuple

from agents.check import run_red_flag_checks
from agents.extract import run_extraction
from agents.verify import (
    _check_domain_age_rdap,
    _check_official_domain,
    _check_salary_plausibility,
    _check_site_legal_pages,
    _build_verify_links,
    _extract_candidate_corporate_domains,
)
from checks_registry import get_checks
from schemas import (
    CheckResult,
    ExtractionResult,
    NormalizedInput,
    RedFlag,
    VerificationBundle,
    VerifyLink,
)

import json
import os

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Minimum reveal delay (seconds) for offline checks so the spinner is visible.
_OFFLINE_MIN_DELAY = 0.40


def _load_json(name: str) -> Any:
    with open(os.path.join(_DATA_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _compute_score(
    check_results: Dict[str, CheckResult],  # keyed by check id (position string 0-15)
    checks_meta: List[Dict[str, Any]],
) -> Tuple[int, Optional[str]]:
    """
    New scoring scheme:
      raw = sum of max_points for every check whose status is 'passed'.
      Cap: checks 5/6/7 (payment, otp, id_doc) failed → cap 29.
           checks 2/4 (blocklisted, lookalike) failed → cap 35.
           Lowest cap wins.
      score = clamp(min(raw, cap), 1, 99)
    """
    # Build a name->result map for easy cap lookups
    by_registry_id: Dict[str, CheckResult] = {}
    for i, meta in enumerate(checks_meta):
        key = str(i)
        if key in check_results:
            by_registry_id[meta["id"]] = check_results[key]

    raw = 0
    for i, meta in enumerate(checks_meta):
        res = check_results.get(str(i))
        if res and res.status == "passed":
            raw += meta["max_points"]

    cap: Optional[int] = None
    cap_reason: Optional[str] = None

    # Check 5 (index 4), 6 (index 5), 7 (index 6) – payment / otp / id
    high_cap_ids = ["payment_demand", "otp_request", "id_doc_request"]
    for cid in high_cap_ids:
        res = by_registry_id.get(cid)
        if res and res.status == "failed":
            candidate = 29
            if cap is None or candidate < cap:
                cap = candidate
                label = {"payment_demand": "a payment demand", "otp_request": "an OTP/PIN request", "id_doc_request": "an ID document request"}[cid]
                cap_reason = f"Limited to 29 because {label} was found."

    # Check 2 (index 1), 4 (index 3) – blocklisted / lookalike
    domain_cap_ids = ["blocklisted_domain", "lookalike_domain"]
    for cid in domain_cap_ids:
        res = by_registry_id.get(cid)
        if res and res.status == "failed":
            candidate = 35
            if cap is None or candidate < cap:
                cap = candidate
                label = "a blocklisted domain" if cid == "blocklisted_domain" else "a lookalike domain"
                cap_reason = f"Limited to 35 because {label} was found."

    score = raw if cap is None else min(raw, cap)
    score = max(1, min(99, score))
    return score, cap_reason


def _verdict_for_score(score: int) -> str:
    thresholds = _load_json("rules.json")["scoring"]["verdict_thresholds"]
    if score >= int(thresholds["safe_min"]):
        return "SAFE"
    if score >= int(thresholds["suspicious_min"]):
        return "SUSPICIOUS"
    return "SCAM"


# ---------------------------------------------------------------------------
# Per-check runners  (checks 1-11 are red-flag based; 12-15 are verify-based)
# ---------------------------------------------------------------------------

def _red_flag_present(flags: List[RedFlag], flag_ids: List[str]) -> bool:
    """Returns True if ANY of the given flag IDs appear in the flags list."""
    flag_id_set = {f.id for f in flags}
    return bool(flag_id_set & set(flag_ids))


def _make_rf_check(meta: Dict[str, Any], flags: List[RedFlag]) -> CheckResult:
    """
    For checks 1-11 (red-flag based):
      Passed = the flag was NOT found.
      Failed = the flag WAS found.
    """
    hit = _red_flag_present(flags, meta["flag_ids"])
    if hit:
        evidence = next(
            (f.evidence for f in flags if f.id in meta["flag_ids"]), ""
        )
        detail = evidence[:120] if evidence else "Red flag triggered."
        return CheckResult(
            id=meta["id"], name=meta["name"],
            tier=meta["tier"], source=meta["source"],
            status="failed", detail=detail,
        )
    return CheckResult(
        id=meta["id"], name=meta["name"],
        tier=meta["tier"], source=meta["source"],
        status="passed", detail="Not detected.",
    )


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def run(
    norm: NormalizedInput,
    run_web_checks: bool,
) -> Generator[Dict[str, Any], None, None]:
    """
    Yields streaming event dicts.
    Catches all exceptions so the client always gets an 'error' event rather
    than a silent stream close.
    """
    checks_meta = get_checks()          # 16 entries in order
    check_results: Dict[str, CheckResult] = {}  # index string -> CheckResult

    try:
        # ---------------------------------------------------------------
        # Stage: extract (Agent 1)
        # ---------------------------------------------------------------
        yield {"type": "stage", "id": "extract", "state": "running"}
        extraction: ExtractionResult = run_extraction(norm)
        yield {"type": "stage", "id": "extract", "state": "done"}

        # ---------------------------------------------------------------
        # Agent 2 – run all red-flag checks in one shot (offline, fast)
        # ---------------------------------------------------------------
        all_flags: List[RedFlag] = run_red_flag_checks(extraction)

        # Load verify-side data (needed for checks 12-15)
        blocklist_data = _load_json("blocklist.json")
        companies_list = _load_json("real_companies.json").get("companies", [])
        salary_data = _load_json("salary_bands.json")
        free_mail_domains = {d.lower() for d in blocklist_data.get("free_email_providers", [])}

        # Check 12 (official_domain) result – needed to know lookalike override
        domain_check, matched_comp = _check_official_domain(
            extraction, companies_list, free_mail_domains
        )

        # Check 13 (salary)
        salary_check = _check_salary_plausibility(extraction, salary_data)

        # Candidate domain for web checks
        candidate_domains = _extract_candidate_corporate_domains(extraction, free_mail_domains)
        primary_domain: Optional[str] = candidate_domains[0] if candidate_domains else None

        # ---------------------------------------------------------------
        # Reveal checks 1-16 one by one
        # ---------------------------------------------------------------
        for i, meta in enumerate(checks_meta):
            yield {"type": "check", "id": i, "state": "running"}
            t0 = time.monotonic()

            result: CheckResult

            # --- Checks 1-11: red-flag based (offline) ---
            if meta["flag_ids"]:  # non-empty flag_ids means it's a red-flag check
                result = _make_rf_check(meta, all_flags)

                # Special case: check 4 (lookalike) failed → force check 12 to also fail
                if meta["id"] == "lookalike_domain" and result.status == "failed":
                    domain_check = CheckResult(
                        id=domain_check.id, name=domain_check.name,
                        tier=domain_check.tier, source=domain_check.source,
                        status="failed",
                        detail="Forced failed because a lookalike/spoof domain was detected.",
                    )

                # Throttle so spinner is visible
                elapsed = time.monotonic() - t0
                if elapsed < _OFFLINE_MIN_DELAY:
                    time.sleep(_OFFLINE_MIN_DELAY - elapsed)

            # --- Check 12: official_domain (offline) ---
            elif meta["id"] == "official_domain":
                result = domain_check
                elapsed = time.monotonic() - t0
                if elapsed < _OFFLINE_MIN_DELAY:
                    time.sleep(_OFFLINE_MIN_DELAY - elapsed)

            # --- Check 13: pay plausibility (offline) ---
            elif meta["id"] == "pay_plausibility":
                if _red_flag_present(all_flags, ["unrealistic_daily_or_part_time_pay"]):
                    evidence = next(
                        f.evidence for f in all_flags
                        if f.id == "unrealistic_daily_or_part_time_pay"
                    )
                    result = CheckResult(
                        id=meta["id"], name=meta["name"],
                        tier=meta["tier"], source=meta["source"],
                        status="failed",
                        detail=f"An unrealistic payout pattern was detected: {evidence[:120]}",
                    )
                else:
                    result = salary_check
                elapsed = time.monotonic() - t0
                if elapsed < _OFFLINE_MIN_DELAY:
                    time.sleep(_OFFLINE_MIN_DELAY - elapsed)

            # --- Check 14: RDAP domain age (web) ---
            elif meta["id"] == "domain_age":
                if not run_web_checks:
                    result = CheckResult(
                        id=meta["id"], name=meta["name"],
                        tier=meta["tier"], source=meta["source"],
                        status="skipped", detail="Web checks are turned off.",
                    )
                else:
                    # running event already emitted; do the real web call now
                    result = _check_domain_age_rdap(primary_domain, run_web_checks=True)

            # --- Check 15: site legal pages (web) ---
            elif meta["id"] == "site_legal_pages":
                if not run_web_checks:
                    result = CheckResult(
                        id=meta["id"], name=meta["name"],
                        tier=meta["tier"], source=meta["source"],
                        status="skipped", detail="Web checks are turned off.",
                    )
                else:
                    result, _socials = _check_site_legal_pages(primary_domain, run_web_checks=True)

            # --- Check 16: verify links (info, 0 points) ---
            elif meta["id"] == "verify_links":
                verify_links: List[VerifyLink] = _build_verify_links(
                    extraction.extracted.company, matched_comp
                )
                links_text = " | ".join(f"{l.label}: {l.url}" for l in verify_links[:4])
                result = CheckResult(
                    id=meta["id"], name=meta["name"],
                    tier=meta["tier"], source=meta["source"],
                    status="info",
                    detail=links_text or "No company match found for verify links.",
                )
                links_payload = [link.model_dump() for link in verify_links[:4]]
                elapsed = time.monotonic() - t0
                if elapsed < _OFFLINE_MIN_DELAY:
                    time.sleep(_OFFLINE_MIN_DELAY - elapsed)

            else:
                # Fallback – should not happen
                result = CheckResult(
                    id=meta["id"], name=meta["name"],
                    tier=meta["tier"], source=meta["source"],
                    status="unavailable", detail="Unknown check.",
                )

            check_results[str(i)] = result
            points_earned = meta["max_points"] if result.status == "passed" else 0

            event = {
                "type": "check",
                "id": i,
                "state": "done",
                "status": result.status,
                "detail": result.detail,
                "points": points_earned,
                "max_points": meta["max_points"],
            }
            if meta["id"] == "verify_links":
                event["links"] = links_payload
            yield event

        # ---------------------------------------------------------------
        # Final scoring
        # ---------------------------------------------------------------
        score, cap_reason = _compute_score(check_results, checks_meta)
        yield {
            "type": "final",
            "score": score,
            "verdict": _verdict_for_score(score),
            "cap_reason": cap_reason,
        }

    except Exception as exc:
        # Never expose internal traces; just a safe message.
        yield {"type": "error", "message": f"Pipeline error: {type(exc).__name__}. Please try again."}
