# TODO: Agent 2 - Offline Red Flag Checker (tldextract, rapidfuzz, regex heuristics)

"""Agent 2: Deterministic Offline Red-Flag Checker (agents/check.py).
- Parses domains with tldextract (offline mode, no network fetch).
- Flags free-mail HR addresses, blocklisted domains, suspicious TLDs, and lookalike domains
  using rapidfuzz against data/real_companies.json.
- Runs regex & keyword rules from data/rules.json (English, Hindi, Hinglish).
- Confidence guard: lowers severity by one tier if a flag relies on an unverified field.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from rapidfuzz import fuzz
import tldextract

from schemas import ExtractionResult, RedFlag

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_TLD_EXTRACTOR = tldextract.TLDExtract(suffix_list_urls=())


def _load_json(filename: str) -> Dict[str, Any]:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_registered_domain(raw_value: str) -> Tuple[str, str, str]:
    """Returns (registered_domain, domain_name_stem, suffix) in lowercase."""
    cleaned = raw_value.strip().lower()
    if "@" in cleaned and "://" not in cleaned:
        cleaned = cleaned.split("@", 1)[1]
    ext = _TLD_EXTRACTOR(cleaned)
    reg_domain = f"{ext.domain}.{ext.suffix}" if ext.domain and ext.suffix else ""
    return reg_domain, ext.domain or "", ext.suffix or ""


def _downgrade_severity(severity: str) -> str:
    if severity == "high":
        return "medium"
    if severity == "medium":
        return "low"
    return "low"


def _match_claimed_company(
    claimed_company: str, companies_list: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Finds if the claimed company matches a known company in real_companies.json."""
    if not claimed_company or not claimed_company.strip():
        return None
    norm = re.sub(r"[^a-z0-9\s]", "", claimed_company.lower()).strip()
    if not norm:
        return None

    for comp in companies_list:
        names = [comp["name"].lower()] + [a.lower() for a in comp.get("aliases", [])]
        for alias in names:
            if norm == alias or alias in norm.split() or (len(alias) >= 4 and alias in norm):
                return comp
    return None


def run_red_flag_checks(extraction: ExtractionResult) -> List[RedFlag]:
    """Runs all offline deterministic checks and returns a list of RedFlag objects."""
    blocklist_data = _load_json("blocklist.json")
    companies_data = _load_json("real_companies.json").get("companies", [])
    rules_data = _load_json("rules.json").get("rules", [])

    blocklisted_domains = {d.lower() for d in blocklist_data.get("domains", [])}
    suspicious_tlds = {t.lower() for t in blocklist_data.get("suspicious_tlds", [])}
    free_mail_domains = {d.lower() for d in blocklist_data.get("free_email_providers", [])}

    fields = extraction.extracted
    unverified_set = set(fields.unverified_fields)
    flags: List[RedFlag] = []
    seen_flag_ids = set()

    def add_flag(
        flag_id: str,
        severity: str,
        evidence: str,
        why: str,
        category: str,
        depends_on_field: Optional[str] = None,
    ) -> None:
        key = f"{flag_id}:{evidence.lower()}"
        if key in seen_flag_ids:
            return
        seen_flag_ids.add(key)

        downgraded = False
        final_sev = severity
        if depends_on_field and depends_on_field in unverified_set:
            final_sev = _downgrade_severity(severity)
            downgraded = True
            why = f"{why} (Severity lowered because extracted {depends_on_field} was marked unverified from image)."

        flags.append(
            RedFlag(
                id=flag_id,
                severity=final_sev,  # type: ignore[arg-type]
                evidence=evidence[:220],
                why_it_matters=why,
                category=category,
                unverified_downgraded=downgraded,
            )
        )

    matched_company = _match_claimed_company(fields.company, companies_data)
    all_official_domains = {
        d.lower(): comp["name"]
        for comp in companies_data
        for d in comp.get("official_domains", [])
    }

    # 1. Check Email Domains
    for email in fields.emails:
        reg_domain, stem, suffix = extract_registered_domain(email)
        if not reg_domain:
            continue

        if reg_domain in free_mail_domains:
            sev = "high" if matched_company else "medium"
            company_label = matched_company["name"] if matched_company else (fields.company or "Recruiter")
            add_flag(
                flag_id="free_email_for_hr",
                severity=sev,
                evidence=email,
                why=(
                    f"{company_label} is using a free personal email address ({reg_domain}) instead of an "
                    "official corporate domain. Legitimate HR teams do not send offer letters from personal Gmail/Yahoo/Outlook accounts."
                ),
                category="domain",
                depends_on_field="emails",
            )

        if reg_domain in blocklisted_domains:
            add_flag(
                flag_id="blocklisted_domain",
                severity="high",
                evidence=email,
                why=f"The sender domain '{reg_domain}' is on SahiCheck's known scam domain blocklist.",
                category="hard_cap_domain",
                depends_on_field="emails",
            )

    # 2. Check URLs and Sender Domains for Lookalikes & Suspicious TLDs
    domain_sources: List[Tuple[str, str]] = [(e, "emails") for e in fields.emails] + [
        (u, "urls") for u in fields.urls
    ]

    for raw_item, field_name in domain_sources:
        reg_domain, stem, suffix = extract_registered_domain(raw_item)
        if not reg_domain or reg_domain in free_mail_domains:
            continue

        if reg_domain in blocklisted_domains:
            add_flag(
                flag_id="blocklisted_domain",
                severity="high",
                evidence=raw_item,
                why=f"The domain '{reg_domain}' is in SahiCheck's known fraudulent domain blocklist.",
                category="hard_cap_domain",
                depends_on_field=field_name,
            )

        if suffix in suspicious_tlds:
            add_flag(
                flag_id="suspicious_tld",
                severity="medium",
                evidence=raw_item,
                why=f"The domain '{reg_domain}' uses a cheap top-level domain (.{suffix}) frequently abused in recruitment phishing.",
                category="domain",
                depends_on_field=field_name,
            )

        # Lookalike check against real_companies.json
        if reg_domain not in all_official_domains:
            for comp in companies_data:
                official_list = [d.lower() for d in comp.get("official_domains", [])]
                for off_dom in official_list:
                    off_stem = _TLD_EXTRACTOR(off_dom).domain
                    # Check if stem contains official brand name with extra hyphens/words (e.g., tcs-careers.com)
                    brand_in_stem = len(off_stem) >= 3 and (
                        stem.startswith(f"{off_stem}-")
                        or stem.endswith(f"-{off_stem}")
                        or (off_stem in stem and stem != off_stem)
                    )
                    sim_ratio = fuzz.ratio(stem, off_stem)
                    if brand_in_stem or (sim_ratio >= 80 and reg_domain != off_dom):
                        add_flag(
                            flag_id="lookalike_spoof_domain",
                            severity="high",
                            evidence=raw_item,
                            why=(
                                f"'{reg_domain}' looks deceptively similar to {comp['name']}'s official domain "
                                f"({off_dom}), a common spoofing tactic used by fake recruiters."
                            ),
                            category="hard_cap_domain",
                            depends_on_field=field_name,
                        )
                        break

    # 3. Check explicit UPI IDs extracted by Agent 1
    for upi in fields.upi_ids:
        add_flag(
            flag_id="upi_payment_handle_present",
            severity="high",
            evidence=upi,
            why="A UPI payment handle is included in the job offer/message. Real employers pay you; they never ask candidates to send money via UPI.",
            category="hard_cap_fee",
            depends_on_field="upi_ids",
        )

    # 4. Run Regex / Keyword Rules across Combined Text
    combined_text = "\n".join(
        filter(
            None,
            [
                extraction.verbatim_transcription,
                f"Company: {fields.company} | Role: {fields.role} | Pay: {fields.pay}",
            ],
        )
    )

    for rule in rules_data:
        rule_id = rule["id"]
        severity = rule["severity"]
        category = rule.get("category", "general")
        description = rule["description"]

        for pattern in rule.get("patterns", []):
            match = re.search(pattern, combined_text)
            if match:
                snippet = match.group(0).strip()
                add_flag(
                    flag_id=rule_id,
                    severity=severity,
                    evidence=snippet,
                    why=description,
                    category=category,
                )
                break

    return flags
