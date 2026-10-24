# TODO: Agent 1 - Extraction (Vision/Text via Gemma 4 + regex verification)

"""Agent 1: Extraction (agents/extract.py).
- Calls Gemma 4 (vision mode for images/PDFs, text mode for pasted text).
- Validates exact fields (emails, URLs, phones, UPI IDs) with Python regex.
- If a field from an image looks malformed, asks the model ONCE to re-read it.
- Prefers pdf_text_layer over vision transcription for exact fields when present,
  and records any mismatch in pdf_mismatch_notes.
"""

import re
from typing import Any, Dict, List, Set

from llm import call_gemma
from schemas import ExtractedFields, ExtractionResult, NormalizedInput, VisualCues

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,24}\b")
URL_REGEX = re.compile(
    r"\b(?:https?://|www\.|[a-zA-Z0-9\-]+\.(?:com|in|org|net|co\.in|io|xyz|top|site|online|icu|work|click|buzz|me))[^\s<>\"'\)\]]*",
    re.IGNORECASE,
)
PHONE_REGEX = re.compile(r"(?:\+?91[\-\s]?)?[6-9]\d{9}\b")
UPI_Handles = (
    "okaxis|okhdfcbank|okicici|oksbi|ybl|ibl|axl|paytm|apl|upi|freecharge|kotak|sbi|hdfcbank|icici|axisbank|barodampay"
)
UPI_REGEX = re.compile(rf"\b[a-zA-Z0-9.\-_]{{2,40}}@(?:{UPI_Handles})\b", re.IGNORECASE)
AMOUNT_REGEX = re.compile(
    r"(?:₹|Rs\.?|INR)\s*[0-9,]{2,10}(?:\s*(?:/\-|per\s*month|per\s*annum|lpa|ctc|daily|per\s*day))?|[0-9]+(?:\.[0-9]+)?\s*(?:LPA|lakh|lakhs)",
    re.IGNORECASE,
)

EXTRACTION_PROMPT_TEMPLATE = """You are Agent 1 (Extractor) in SahiCheck, a job offer fraud detector for India.
Analyze the provided job offer / recruiter message carefully.
Inputs may be in English, Hindi, or Hinglish.

Return ONLY a valid JSON object matching this exact structure (no markdown fences, no commentary):
{{
  "verbatim_transcription": "Exact character-by-character transcription of all visible text. Do not fix spelling or guess unclear characters.",
  "extracted": {{
    "company": "Claimed company or organization name, or empty string",
    "role": "Job title or internship role offered, or empty string",
    "pay": "Salary, stipend, or daily payout mentioned (with currency/period), or empty string",
    "sender_channel": "whatsapp | telegram | email | sms | letter | unknown",
    "emails": ["exact email addresses found"],
    "phones": ["exact phone numbers found"],
    "urls": ["exact website URLs or links found"],
    "upi_ids": ["exact UPI IDs found, e.g. name@ybl"],
    "amounts": ["any fee, deposit, or salary amounts mentioned, e.g. Rs. 2500"]
  }},
  "visual_cues": {{
    "logo_quality": "Describe logo clarity/authenticity or 'No logo'",
    "letterhead_and_layout": "Describe letterhead, alignment, stamp/signature quality",
    "formatting_errors": "Note typos, mismatched fonts, grammar errors, or 'None'",
    "tone_and_pressure": "Note urgency, threats, guaranteed selection claims, or 'Professional'"
  }}
}}

{extra_context}
"""

REREAD_PROMPT_TEMPLATE = """Re-examine the image carefully. Some extracted contact/payment fields looked malformed:
{malformed_summary}

Copy the exact characters visible in the image without guessing. Return ONLY a JSON object:
{{
  "emails": ["exact emails"],
  "phones": ["exact phone numbers"],
  "urls": ["exact URLs"],
  "upi_ids": ["exact UPI IDs"]
}}
"""


def _deterministic_regex_scan(source_text: str) -> Dict[str, List[str]]:
    """Extracts exact emails, UPI IDs, URLs, phones, and amounts directly from text via regex."""
    if not source_text:
        return {"emails": [], "upi_ids": [], "urls": [], "phones": [], "amounts": []}

    raw_emails = EMAIL_REGEX.findall(source_text)
    upi_ids = list(dict.fromkeys(m.group(0).lower() for m in UPI_REGEX.finditer(source_text)))
    upi_set = set(upi_ids)
    emails = list(dict.fromkeys(e.lower() for e in raw_emails if e.lower() not in upi_set))

    urls = []
    for m in URL_REGEX.finditer(source_text):
        candidate = m.group(0).rstrip(".,;:!)")
        if "@" not in candidate and candidate.lower() not in urls:
            urls.append(candidate)

    phones = list(dict.fromkeys(re.sub(r"[\s\-]", "", m.group(0)) for m in PHONE_REGEX.finditer(source_text)))
    amounts = list(dict.fromkeys(m.group(0).strip() for m in AMOUNT_REGEX.finditer(source_text)))

    return {
        "emails": emails,
        "upi_ids": upi_ids,
        "urls": urls,
        "phones": phones,
        "amounts": amounts,
    }


def _validate_exact_fields(fields: ExtractedFields) -> Dict[str, List[str]]:
    """Checks whether model-extracted emails, phones, URLs, and UPI IDs pass strict regex validation."""
    malformed: Dict[str, List[str]] = {}

    bad_emails = [e for e in fields.emails if not EMAIL_REGEX.fullmatch(e.strip())]
    if bad_emails:
        malformed["emails"] = bad_emails

    bad_upis = [u for u in fields.upi_ids if not UPI_REGEX.fullmatch(u.strip())]
    if bad_upis:
        malformed["upi_ids"] = bad_upis

    bad_phones = [
        p for p in fields.phones if not PHONE_REGEX.search(re.sub(r"[\s\-()]", "", p))
    ]
    if bad_phones:
        malformed["phones"] = bad_phones

    bad_urls = [u for u in fields.urls if not URL_REGEX.search(u.strip()) or " " in u.strip()]
    if bad_urls:
        malformed["urls"] = bad_urls

    return malformed


def _heuristic_fallback_extraction(text: str) -> ExtractionResult:
    """Offline fallback extraction if both Gemini API and Ollama are unreachable."""
    scanned = _deterministic_regex_scan(text)
    company = ""
    role = ""

    comp_match = re.search(
        r"(?i)(?:welcome\s+to|offer\s+from|behalf\s+of|company\s*[:\-]|at)\s+([A-Z][A-Za-z0-9&\s\.]{2,40})",
        text,
    )
    if comp_match:
        company = comp_match.group(1).strip().rstrip(".,")

    role_match = re.search(
        r"(?i)(?:role|position|designation|selected\s+as)\s*[:\-]?\s*([A-Za-z0-9\s\-/]{3,40})",
        text,
    )
    if role_match:
        role = role_match.group(1).strip().rstrip(".,")

    channel = "unknown"
    low = text.lower()
    if "whatsapp" in low or "wa.me" in low:
        channel = "whatsapp"
    elif "telegram" in low or "t.me/" in low:
        channel = "telegram"
    elif "dear candidate" in low or "offer letter" in low:
        channel = "letter"

    return ExtractionResult(
        verbatim_transcription=text,
        extracted=ExtractedFields(
            company=company,
            role=role,
            pay=scanned["amounts"][0] if scanned["amounts"] else "",
            sender_channel=channel,
            emails=scanned["emails"],
            phones=scanned["phones"],
            urls=scanned["urls"],
            upi_ids=scanned["upi_ids"],
            amounts=scanned["amounts"],
            unverified_fields=[],
        ),
        visual_cues=VisualCues(),
        model_used="deterministic-regex-fallback",
    )


def run_extraction(norm_input: NormalizedInput) -> ExtractionResult:
    """Runs Agent 1 extraction on NormalizedInput."""
    is_image_mode = norm_input.input_type == "image" and len(norm_input.images) > 0

    extra_context = ""
    if norm_input.text:
        extra_context += f"\nUSER PASTED TEXT:\n\"\"\"\n{norm_input.text}\n\"\"\"\n"
    if norm_input.pdf_text_layer:
        extra_context += f"\nPDF TEXT LAYER:\n\"\"\"\n{norm_input.pdf_text_layer}\n\"\"\"\n"

    prompt = EXTRACTION_PROMPT_TEMPLATE.format(extra_context=extra_context)

    try:
        raw_dict, model_used = call_gemma(
            prompt=prompt,
            images=norm_input.images if is_image_mode else None,
            expect_json=True,
        )
    except Exception:
        fallback_source = norm_input.pdf_text_layer or norm_input.text or ""
        return _heuristic_fallback_extraction(fallback_source)

    ext_data: Dict[str, Any] = raw_dict.get("extracted", {}) if isinstance(raw_dict, dict) else {}
    vis_data: Dict[str, Any] = raw_dict.get("visual_cues", {}) if isinstance(raw_dict, dict) else {}
    transcription = str(raw_dict.get("verbatim_transcription", "") or "").strip()

    if not is_image_mode and norm_input.text:
        transcription = norm_input.text

    fields = ExtractedFields(
        company=str(ext_data.get("company", "") or "").strip(),
        role=str(ext_data.get("role", "") or "").strip(),
        pay=str(ext_data.get("pay", "") or "").strip(),
        sender_channel=str(ext_data.get("sender_channel", "unknown") or "unknown").lower().strip(),
        emails=[str(x).strip().lower() for x in (ext_data.get("emails") or []) if str(x).strip()],
        phones=[str(x).strip() for x in (ext_data.get("phones") or []) if str(x).strip()],
        urls=[str(x).strip() for x in (ext_data.get("urls") or []) if str(x).strip()],
        upi_ids=[str(x).strip().lower() for x in (ext_data.get("upi_ids") or []) if str(x).strip()],
        amounts=[str(x).strip() for x in (ext_data.get("amounts") or []) if str(x).strip()],
    )

    # Separate any UPI IDs accidentally placed in emails
    clean_emails: List[str] = []
    for em in fields.emails:
        if UPI_REGEX.fullmatch(em):
            if em not in fields.upi_ids:
                fields.upi_ids.append(em)
        else:
            clean_emails.append(em)
    fields.emails = clean_emails

    # If image mode (and no exact PDF text layer), validate with regex and re-read ONCE if malformed
    unverified: Set[str] = set()
    if is_image_mode and not norm_input.pdf_text_layer:
        malformed = _validate_exact_fields(fields)
        if malformed:
            try:
                reread_prompt = REREAD_PROMPT_TEMPLATE.format(malformed_summary=str(malformed))
                reread_dict, _ = call_gemma(
                    prompt=reread_prompt,
                    images=norm_input.images,
                    expect_json=True,
                )
                if isinstance(reread_dict, dict):
                    for key in ("emails", "phones", "urls", "upi_ids"):
                        if key in malformed and isinstance(reread_dict.get(key), list):
                            setattr(
                                fields,
                                key,
                                [str(v).strip() for v in reread_dict[key] if str(v).strip()],
                            )
            except Exception:
                pass

            still_malformed = _validate_exact_fields(fields)
            for key in still_malformed:
                unverified.add(key)

    # Prefer exact text from pasted text or PDF text layer when available
    exact_text_source = norm_input.pdf_text_layer or norm_input.text
    if exact_text_source:
        exact_scan = _deterministic_regex_scan(exact_text_source)
        if norm_input.pdf_text_layer:
            # Record mismatches between vision transcription and exact PDF text layer
            for key in ("emails", "urls", "upi_ids", "phones"):
                vision_set = {v.lower() for v in getattr(fields, key)}
                pdf_set = {v.lower() for v in exact_scan[key]}
                if vision_set and pdf_set and vision_set != pdf_set:
                    fields.pdf_mismatch_notes.append(
                        f"Vision read {key}={sorted(vision_set)}, replaced with exact PDF text layer {sorted(pdf_set)}."
                    )
        # Merge / prefer exact regex scan from exact text source
        for key in ("emails", "urls", "upi_ids", "phones", "amounts"):
            if exact_scan[key]:
                existing = getattr(fields, key)
                merged = list(dict.fromkeys(exact_scan[key] + existing))
                setattr(fields, key, merged)
    else:
        # Also supplement image mode with regex scan over verbatim transcription
        trans_scan = _deterministic_regex_scan(transcription)
        for key in ("emails", "urls", "upi_ids", "phones", "amounts"):
            existing = getattr(fields, key)
            for item in trans_scan[key]:
                if item not in existing:
                    existing.append(item)

    fields.unverified_fields = sorted(unverified)

    visual_cues = VisualCues(
        logo_quality=str(vis_data.get("logo_quality", "Not applicable" if not is_image_mode else "Inspected")),
        letterhead_and_layout=str(
            vis_data.get("letterhead_and_layout", "Not applicable" if not is_image_mode else "Inspected")
        ),
        formatting_errors=str(vis_data.get("formatting_errors", "None observed")),
        tone_and_pressure=str(vis_data.get("tone_and_pressure", "Neutral")),
    )

    return ExtractionResult(
        verbatim_transcription=transcription or (exact_text_source or ""),
        extracted=fields,
        visual_cues=visual_cues,
        model_used=model_used,
    )