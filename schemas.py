"""Pydantic v2 models for SahiCheck's transparent multi-agent pipeline."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class NormalizedInput(BaseModel):
    """Step 0 output from inputs.py."""
    input_type: Literal["image", "text"]
    images: List[bytes] = Field(default_factory=list, description="PNG-encoded image bytes for vision calls")
    text: Optional[str] = None
    pdf_text_layer: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class VisualCues(BaseModel):
    """Visual inspection cues extracted from an image or rendered PDF page."""
    logo_quality: str = "Not applicable (text input)"
    letterhead_and_layout: str = "Not applicable (text input)"
    formatting_errors: str = "None observed"
    tone_and_pressure: str = "Neutral"


class ExtractedFields(BaseModel):
    """Structured fields extracted by Agent 1 (extract.py)."""
    company: str = ""
    role: str = ""
    pay: str = ""
    sender_channel: str = "unknown"
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    upi_ids: List[str] = Field(default_factory=list)
    amounts: List[str] = Field(default_factory=list)
    unverified_fields: List[str] = Field(default_factory=list)
    pdf_mismatch_notes: List[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    """Full output of Agent 1."""
    verbatim_transcription: str = ""
    extracted: ExtractedFields = Field(default_factory=ExtractedFields)
    visual_cues: VisualCues = Field(default_factory=VisualCues)
    model_used: str = "unknown"


class RedFlag(BaseModel):
    """A deterministic red flag detected by Agent 2 (check.py)."""
    id: str
    severity: Literal["low", "medium", "high"]
    evidence: str
    why_it_matters: str
    category: str = "general"
    unverified_downgraded: bool = False


class CheckResult(BaseModel):
    """An independent verification check from Agent 2b (verify.py)."""
    id: str
    name: str
    tier: Literal["strong", "supporting", "weak"]
    status: Literal["passed", "failed", "unavailable"]
    detail: str
    source: Literal["offline", "web"]
    score_delta: int = 0


class VerifyLink(BaseModel):
    """A safe user-clickable verification link."""
    label: str
    url: str


class VerificationBundle(BaseModel):
    """Full output of Agent 2b."""
    checks: List[CheckResult] = Field(default_factory=list)
    verify_links: List[VerifyLink] = Field(default_factory=list)
    positive_signs: List[str] = Field(default_factory=list)


class FlagExplanationItem(BaseModel):
    """Per-flag plain-language explanation returned by Gemma in Agent 3."""
    id: str
    why_it_matters: str


class GemmaSynthesisOutput(BaseModel):
    """Schema for Gemma 4's explanation response in Agent 3."""
    summary: str
    flag_explanations: List[FlagExplanationItem] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)


class FinalReport(BaseModel):
    """Final SahiCheck output schema matching the Project Brief."""
    verdict: Literal["SAFE", "SUSPICIOUS", "SCAM"]
    legitimacy_score: int = Field(ge=3, le=97)
    evidence_coverage: Literal["low", "medium", "high"]
    summary: str
    red_flags: List[RedFlag] = Field(default_factory=list)
    checks: List[CheckResult] = Field(default_factory=list)
    positive_signs: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    verify_links: List[VerifyLink] = Field(default_factory=list)
    extracted: ExtractedFields = Field(default_factory=ExtractedFields)