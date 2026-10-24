# TODO: Agent 2b - Legitimacy Verifier (domain match, RDAP age, legal pages, salary bands)

"""Agent 2b: Verifier (agents/verify.py).
Runs independent positive-evidence checks (offline and optional web checks via safe_fetch.py):
1. official_domain (strong, offline)
2. salary_plausibility (supporting, offline)
3. domain_age (supporting, web via RDAP)
4. site_legal_pages (weak, web via homepage HTML footer inspection)
5. Builds non-scraping verify_links for the user to confirm company presence.
"""

from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote_plus, urljoin

from agents.check import _match_claimed_company, extract_registered_domain
from safe_fetch import SafeFetchError, safe_get_json, safe_get_text
from schemas import CheckResult, ExtractionResult, VerificationBundle, VerifyLink

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _load_json(filename: str) -> Dict[str, Any]:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class _HomepageLinkParser(HTMLParser):
    """Lightweight stdlib HTML parser to inspect anchor tags on a company homepage."""

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.links: List[Tuple[str, str]] = []
        self._current_href: Optional[str] = None
        self._current_text: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self._current_href = urljoin(self.base_url, href.strip())
                self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._current_text.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._current_href is not None:
            label = " ".join(t for t in self._current_text if t).strip()
            self.links.append((self._current_href, label))
            self._current_href = None
            self._current_text = []


def _extract_candidate_corporate_domains(
    extraction: ExtractionResult, free_mail_domains: Set[str]
) -> List[str]:
    """Collects non-freemail registered domains from extracted emails and URLs."""
    domains: List[str] = []
    for raw in extraction.extracted.emails + extraction.extracted.urls:
        reg_dom, _stem, _suf = extract_registered_domain(raw)
        if not reg_dom or reg_dom in free_mail_domains:
            continue
        if reg_dom in ("wa.me", "t.me", "bit.ly", "tinyurl.com", "forms.gle", "docs.google.com"):
            continue
        if reg_dom not in domains:
            domains.append(reg_dom)
    return domains


def _check_official_domain(
    extraction: ExtractionResult,
    companies_list: List[Dict[str, Any]],
    free_mail_domains: Set[str],
) -> Tuple[CheckResult, Optional[Dict[str, Any]]]:
    """Check 1 (strong, offline): Compares extracted domain against real_companies.json."""
    matched_comp = _match_claimed_company(extraction.extracted.company, companies_list)
    all_Extracted_domains = [
        extract_registered_domain(x)[0]
        for x in (extraction.extracted.emails + extraction.extracted.urls)
        if extract_registered_domain(x)[0]
    ]

    if not matched_comp:
        # See if any extracted domain matches a known company even if company name wasn't clear
        for comp in companies_list:
            off_doms = {d.lower() for d in comp.get("official_domains", [])}
            hit = [d for d in all_Extracted_domains if d in off_doms]
            if hit:
                return (
                    CheckResult(
                        id="official_domain",
                        name="Official Company Domain",
                        tier="strong",
                        status="passed",
                        detail=f"Domain '{hit[0]}' matches {comp['name']}'s official domain list.",
                        source="offline",
                    ),
                    comp,
                )
        return (
            CheckResult(
                id="official_domain",
                name="Official Company Domain",
                tier="strong",
                status="unavailable",
                detail="Claimed company is not in the offline directory of known major recruiters.",
                source="offline",
            ),
            None,
        )

    official_set = {d.lower() for d in matched_comp.get("official_domains", [])}
    if not all_Extracted_domains:
        return (
            CheckResult(
                id="official_domain",
                name="Official Company Domain",
                tier="strong",
                status="unavailable",
                detail=f"Claimed company is {matched_comp['name']}, but no email or website domain was present in the message.",
                source="offline",
            ),
            matched_comp,
        )

    matching = [d for d in all_Extracted_domains if d in official_set]
    non_matching = [d for d in all_Extracted_domains if d not in official_set]

    if matching and not non_matching:
        return (
            CheckResult(
                id="official_domain",
                name="Official Company Domain",
                tier="strong",
                status="passed",
                detail=f"Verified '{matching[0]}' matches {matched_comp['name']}'s official domain.",
                source="offline",
            ),
            matched_comp,
        )

    return (
        CheckResult(
            id="official_domain",
            name="Official Company Domain",
            tier="strong",
            status="failed",
            detail=(
                f"Message claims to be from {matched_comp['name']} (official: {', '.join(sorted(official_set))}), "
                f"but uses '{non_matching[0]}'."
            ),
            source="offline",
        ),
        matched_comp,
    )


def _parse_monthly_inr(pay_text: str) -> Optional[int]:
    """Converts common Indian salary/stipend strings into an approximate monthly INR figure."""
    if not pay_text:
        return None
    low = pay_text.lower()

    # Check LPA / Lakhs per annum first (e.g., "6 LPA", "4.5 Lakhs per annum")
    lpa_match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:lpa|lakh|lakhs)", low)
    if lpa_match:
        lpa_val = float(lpa_match.group(1))
        return int((lpa_val * 100000) / 12.0)

    # Extract raw numbers
    num_matches = re.findall(r"[0-9][0-9,]{2,8}", low)
    if not num_matches:
        return None
    val = int(num_matches[0].replace(",", ""))

    if any(k in low for k in ("per day", "/day", "daily", "roz")):
        return val * 26
    if any(k in low for k in ("per annum", "p.a", "/year", "yearly", "annual", "ctc")) and val >= 120000:
        return int(val / 12)
    return val


def _check_salary_plausibility(
    extraction: ExtractionResult, salary_data: Dict[str, Any]
) -> CheckResult:
    """Check 2 (supporting, offline): Compares offered pay against data/salary_bands.json."""
    role_str = (extraction.extracted.role or "").lower().strip()
    pay_str = (extraction.extracted.pay or "").strip()
    if not pay_str and extraction.extracted.amounts:
        # Only use amounts if pay wasn't populated and it doesn't look like a small fee
        for amt in extraction.extracted.amounts:
            parsed_amt = _parse_monthly_inr(amt)
            if parsed_amt and parsed_amt >= 5000:
                pay_str = amt
                break

    monthly_inr = _parse_monthly_inr(pay_str)
    if monthly_inr is None:
        return CheckResult(
            id="salary_plausibility",
            name="Salary Plausibility (India Bands)",
            tier="supporting",
            status="unavailable",
            detail="No parseable monthly salary or annual CTC figure was found to compare.",
            source="offline",
        )

    # Match band by role keywords
    matched_band = None
    for band in salary_data.get("bands", []):
        if any(kw in role_str for kw in band.get("role_keywords", [])):
            matched_band = band
            break

    if not matched_band:
        # Check combined text for role clues (e.g., intern, data entry, fresher)
        combined = f"{role_str} {extraction.verbatim_transcription.lower()}"
        for band in salary_data.get("bands", []):
            if any(kw in combined for kw in band.get("role_keywords", [])):
                matched_band = band
                break

    if not matched_band:
        return CheckResult(
            id="salary_plausibility",
            name="Salary Plausibility (India Bands)",
            tier="supporting",
            status="unavailable",
            detail=f"Extracted pay (~₹{monthly_inr:,}/month), but role '{extraction.extracted.role or 'unspecified'}' is not in offline bands.",
            source="offline",
        )

    max_monthly = int(matched_band["max_monthly_inr"])
    min_monthly = int(matched_band["min_monthly_inr"])
    note = matched_band["typical_note"]

    if monthly_inr > max_monthly * 1.35:
        return CheckResult(
            id="salary_plausibility",
            name="Salary Plausibility (India Bands)",
            tier="supporting",
            status="failed",
            detail=f"Offered pay (~₹{monthly_inr:,}/month) is far above realistic India market bands. {note}",
            source="offline",
        )

    if monthly_inr < min_monthly * 0.4:
        return CheckResult(
            id="salary_plausibility",
            name="Salary Plausibility (India Bands)",
            tier="supporting",
            status="unavailable",
            detail=f"Extracted amount (~₹{monthly_inr:,}) appears closer to a fee or partial stipend than a full salary.",
            source="offline",
        )

    return CheckResult(
        id="salary_plausibility",
        name="Salary Plausibility (India Bands)",
        tier="supporting",
        status="passed",
        detail=f"Offered pay (~₹{monthly_inr:,}/month) falls within plausible India bands. {note}",
        source="offline",
    )


def _check_domain_age_rdap(domain: Optional[str], run_web_checks: bool) -> CheckResult:
    """Check 3 (supporting, web): Public RDAP lookup for domain registration age."""
    if not run_web_checks:
        return CheckResult(
            id="domain_age",
            name="Domain Registration Age (RDAP)",
            tier="supporting",
            status="unavailable",
            detail="Web checks are turned off.",
            source="web",
        )
    if not domain:
        return CheckResult(
            id="domain_age",
            name="Domain Registration Age (RDAP)",
            tier="supporting",
            status="unavailable",
            detail="No non-freemail corporate domain found in the message to look up.",
            source="web",
        )

    rdap_url = f"https://rdap.org/domain/{domain}"
    try:
        data = safe_get_json(rdap_url, check_robots=False, timeout=4.0)
        events = data.get("events", [])
        reg_date_str = None
        for ev in events:
            if isinstance(ev, dict) and ev.get("eventAction") in ("registration", "registered"):
                reg_date_str = ev.get("eventDate")
                break

        if not reg_date_str:
            return CheckResult(
                id="domain_age",
                name="Domain Registration Age (RDAP)",
                tier="supporting",
                status="unavailable",
                detail=f"RDAP registry for '{domain}' did not expose a registration date.",
                source="web",
            )

        iso_clean = reg_date_str.replace("Z", "+00:00")
        reg_dt = datetime.fromisoformat(iso_clean)
        if reg_dt.tzinfo is None:
            reg_dt = reg_dt.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - reg_dt).days

        if age_days < 180:
            return CheckResult(
                id="domain_age",
                name="Domain Registration Age (RDAP)",
                tier="supporting",
                status="failed",
                detail=f"Domain '{domain}' was registered only {age_days} days ago ({reg_dt.date().isoformat()}) — < 6 months old.",
                source="web",
            )

        years = round(age_days / 365.25, 1)
        return CheckResult(
            id="domain_age",
            name="Domain Registration Age (RDAP)",
            tier="supporting",
            status="passed",
            detail=f"Domain '{domain}' was registered on {reg_dt.date().isoformat()} (~{years} years old).",
            source="web",
        )
    except (SafeFetchError, Exception) as exc:
        return CheckResult(
            id="domain_age",
            name="Domain Registration Age (RDAP)",
            tier="supporting",
            status="unavailable",
            detail=f"RDAP lookup for '{domain}' could not complete ({exc}).",
            source="web",
        )


def _check_site_legal_pages(
    domain: Optional[str], run_web_checks: bool
) -> Tuple[CheckResult, List[str]]:
    """Check 4 (weak, web): Fetches homepage via safe_fetch.py and checks for Privacy/Terms/About/Contact links."""
    discovered_socials: List[str] = []
    if not run_web_checks:
        return (
            CheckResult(
                id="site_legal_pages",
                name="Company Website Legal & Contact Pages",
                tier="weak",
                status="unavailable",
                detail="Web checks are turned off.",
                source="web",
            ),
            discovered_socials,
        )
    if not domain:
        return (
            CheckResult(
                id="site_legal_pages",
                name="Company Website Legal & Contact Pages",
                tier="weak",
                status="unavailable",
                detail="No corporate domain available to inspect.",
                source="web",
            ),
            discovered_socials,
        )

    homepage_url = f"https://{domain}"
    try:
        status, html_text, final_url = safe_get_text(homepage_url, check_robots=True, timeout=4.0)
        if status >= 400:
            return (
                CheckResult(
                    id="site_legal_pages",
                    name="Company Website Legal & Contact Pages",
                    tier="weak",
                    status="failed",
                    detail=f"Homepage https://{domain} returned HTTP {status}.",
                    source="web",
                ),
                discovered_socials,
            )

        parser = _HomepageLinkParser(final_url)
        parser.feed(html_text)

        found_categories: Set[str] = set()
        for href, label in parser.links:
            combined = f"{href.lower()} {label.lower()}"
            if "privacy" in combined:
                found_categories.add("Privacy")
            if "terms" in combined or "disclaimer" in combined or "legal" in combined:
                found_categories.add("Terms")
            if "about" in combined or "who-we-are" in combined or "company" in combined:
                found_categories.add("About")
            if "contact" in combined or "support" in combined or "careers" in combined:
                found_categories.add("Contact/Careers")

            for social_host in ("linkedin.com/company", "twitter.com/", "x.com/", "youtube.com/"):
                if social_host in href.lower() and href not in discovered_socials:
                    discovered_socials.append(href)

        if len(found_categories) >= 2:
            return (
                CheckResult(
                    id="site_legal_pages",
                    name="Company Website Legal & Contact Pages",
                    tier="weak",
                    status="passed",
                    detail=f"Homepage links to standard corporate pages ({', '.join(sorted(found_categories))}).",
                    source="web",
                ),
                discovered_socials,
            )
        return (
            CheckResult(
                id="site_legal_pages",
                name="Company Website Legal & Contact Pages",
                tier="weak",
                status="failed",
                detail=f"Homepage at {domain} is missing standard Privacy, Terms, About, or Contact links.",
                source="web",
            ),
            discovered_socials,
        )
    except (SafeFetchError, Exception) as exc:
        return (
            CheckResult(
                id="site_legal_pages",
                name="Company Website Legal & Contact Pages",
                tier="weak",
                status="unavailable",
                detail=f"Could not safely fetch https://{domain} ({exc}).",
                source="web",
            ),
            discovered_socials,
        )


def _build_verify_links(
    company_name: str, matched_comp: Optional[Dict[str, Any]]
) -> List[VerifyLink]:
    """Builds safe clickable verification URLs (zero scraping)."""
    clean_name = (
        matched_comp["name"]
        if matched_comp
        else (company_name.strip() or "Company")
    )
    q_comp = quote_plus(clean_name)
    q_scam = quote_plus(f"{clean_name} job offer scam fake recruitment India")

    links: List[VerifyLink] = []
    if matched_comp and matched_comp.get("careers_url"):
        links.append(
            VerifyLink(
                label=f"Official {clean_name} Careers Page",
                url=matched_comp["careers_url"],
            )
        )

    links.extend(
        [
            VerifyLink(
                label=f"LinkedIn: Search '{clean_name}' Official Page",
                url=f"https://www.linkedin.com/search/results/companies/?keywords={q_comp}",
            ),
            VerifyLink(
                label=f"AmbitionBox: '{clean_name}' Reviews & Salaries",
                url=f"https://www.ambitionbox.com/search?q={q_comp}",
            ),
            VerifyLink(
                label=f"Glassdoor: '{clean_name}' Employee Reviews",
                url=f"https://www.glassdoor.co.in/Search/results.htm?keyword={q_comp}",
            ),
            VerifyLink(
                label=f"Google Search: '{clean_name} job scam reports'",
                url=f"https://www.google.com/search?q={q_scam}",
            ),
            VerifyLink(
                label="MCA India: Verify Company Registration (CIN)",
                url="https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html",
            ),
            VerifyLink(
                label="Report Cyber Fraud (cybercrime.gov.in / 1930)",
                url="https://cybercrime.gov.in/",
            ),
        ]
    )
    return links


def run_verification_checks(
    extraction: ExtractionResult,
    run_web_checks: bool = True,
) -> VerificationBundle:
    """Runs all Agent 2b checks and returns a VerificationBundle."""
    blocklist_data = _load_json("blocklist.json")
    companies_list = _load_json("real_companies.json").get("companies", [])
    salary_data = _load_json("salary_bands.json")
    free_mail_domains = {d.lower() for d in blocklist_data.get("free_email_providers", [])}

    checks: List[CheckResult] = []
    positive_signs: List[str] = []

    # 1. Official Domain Check (strong, offline)
    domain_check, matched_comp = _check_official_domain(extraction, companies_list, free_mail_domains)
    checks.append(domain_check)
    if domain_check.status == "passed":
        positive_signs.append(domain_check.detail)

    # 2. Salary Plausibility Check (supporting, offline)
    salary_check = _check_salary_plausibility(extraction, salary_data)
    checks.append(salary_check)
    if salary_check.status == "passed":
        positive_signs.append(salary_check.detail)

    # Candidate corporate domain for web checks
    candidate_domains = _extract_candidate_corporate_domains(extraction, free_mail_domains)
    primary_domain = candidate_domains[0] if candidate_domains else None

    # 3. Domain Age via RDAP (supporting, web)
    age_check = _check_domain_age_rdap(primary_domain, run_web_checks=run_web_checks)
    checks.append(age_check)
    if age_check.status == "passed":
        positive_signs.append(age_check.detail)

    # 4. Site Legal Pages (weak, web)
    legal_check, socials = _check_site_legal_pages(primary_domain, run_web_checks=run_web_checks)
    checks.append(legal_check)
    if legal_check.status == "passed":
        positive_signs.append(legal_check.detail)
    if socials:
        positive_signs.append(f"Company website links to official social profiles ({', '.join(socials[:2])}).")

    verify_links = _build_verify_links(extraction.extracted.company, matched_comp)

    return VerificationBundle(
        checks=checks,
        verify_links=verify_links,
        positive_signs=positive_signs,
    )
