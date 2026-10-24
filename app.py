# TODO: Gradio UI implementation for SahiCheck v2

"""Gradio UI for SahiCheck (app.py).
Features:
- Strictly TWO input options: Image/PDF uploader and Pasted-Text box.
- 'Run web checks' toggle (on by default) and 'Check Offer Authenticity' button.
- Color-coded Verdict Card (Green SAFE, Amber SUSPICIOUS, Red SCAM) with legitimacy score and evidence coverage.
- Structured Checks Table with status badges, tiers, sources, and score deltas.
- Clickable Verify Links section & Next Steps.
- Expandable pipeline transparency panels (Transcribed Text, Extracted Fields + Visual Cues, Red-Flag Hits, Final JSON).
"""

import html
import json
import os
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
from typing import Any, Dict, Optional, Tuple

import gradio as gr

from agents.check import run_red_flag_checks
from agents.extract import run_extraction
from agents.synthesize import run_synthesis
from agents.verify import run_verification_checks
from inputs import normalize_input
from schemas import FinalReport

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")

CUSTOM_CSS = """
:root {
    --sc-bg: #0b0f19;
    --sc-surface: #111827;
    --sc-surface-2: #1e293b;
    --sc-border: #334155;
    --sc-text: #f8fafc;
    --sc-muted: #94a3b8;
    --sc-primary: #10b981;
    --sc-safe-bg: rgba(16, 185, 129, 0.14);
    --sc-safe-border: #10b981;
    --sc-safe-text: #34d399;
    --sc-warn-bg: rgba(245, 158, 11, 0.14);
    --sc-warn-border: #f59e0b;
    --sc-warn-text: #fbbf24;
    --sc-scam-bg: rgba(239, 68, 68, 0.15);
    --sc-scam-border: #ef4444;
    --sc-scam-text: #f87171;
}

.gradio-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
    font-family: 'Inter', 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
}

.sc-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 18px;
    color: #f8fafc;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35);
}

.sc-header-badge {
    display: inline-block;
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 999px;
    margin-bottom: 10px;
}

.sc-header h1 {
    margin: 0 0 6px 0;
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
}

.sc-header p {
    margin: 0;
    color: #cbd5e1;
    font-size: 14.5px;
    line-height: 1.5;
}

.sc-verdict-card {
    border-radius: 16px;
    padding: 22px 26px;
    margin-bottom: 16px;
    border-width: 2px;
    border-style: solid;
}

.sc-verdict-SAFE {
    background: var(--sc-safe-bg);
    border-color: var(--sc-safe-border);
}

.sc-verdict-SUSPICIOUS {
    background: var(--sc-warn-bg);
    border-color: var(--sc-warn-border);
}

.sc-verdict-SCAM {
    background: var(--sc-scam-bg);
    border-color: var(--sc-scam-border);
}

.sc-verdict-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 12px;
}

.sc-verdict-pill {
    font-size: 20px;
    font-weight: 800;
    padding: 6px 16px;
    border-radius: 999px;
    letter-spacing: 0.04em;
}

.sc-pill-SAFE { background: #065f46; color: #ecfdf5; }
.sc-pill-SUSPICIOUS { background: #78350f; color: #fffbeb; }
.sc-pill-SCAM { background: #7f1d1d; color: #fef2f2; }

.sc-score-box {
    display: flex;
    gap: 18px;
    align-items: center;
    font-size: 14px;
}

.sc-score-num {
    font-size: 26px;
    font-weight: 800;
}

.sc-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    font-size: 14px;
}

.sc-table th, .sc-table td {
    border-bottom: 1px solid rgba(148, 163, 184, 0.25);
    padding: 10px 12px;
    text-align: left;
}

.sc-table th {
    font-weight: 700;
    opacity: 0.85;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 0.04em;
}

.sc-link-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 10px;
    margin-top: 10px;
}

.sc-verify-link {
    display: block;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid rgba(148, 163, 184, 0.35);
    text-decoration: none !important;
    font-weight: 600;
    font-size: 13.5px;
    transition: all 0.15s ease;
}

.sc-verify-link:hover {
    border-color: #10b981;
    transform: translateY(-1px);
}

.sc-disclaimer {
    font-size: 12.5px;
    opacity: 0.8;
    border-top: 1px solid rgba(148, 163, 184, 0.25);
    padding-top: 12px;
    margin-top: 16px;
}
"""


def _render_verdict_card(report: FinalReport) -> str:
    icon_map = {"SAFE": "🟢", "SUSPICIOUS": "🟡", "SCAM": "🔴"}
    icon = icon_map.get(report.verdict, "🟡")
    summary_esc = html.escape(report.summary)
    company_esc = html.escape(report.extracted.company or "Not explicitly stated")
    role_esc = html.escape(report.extracted.role or "Not explicitly stated")

    flags_html = ""
    if report.red_flags:
        items = []
        for f in report.red_flags:
            sev_badge = f.severity.upper()
            ev = html.escape(f.evidence)
            why = html.escape(f.why_it_matters)
            items.append(
                f"<li style='margin-bottom:8px;'><strong>[{sev_badge}] {html.escape(f.id)}:</strong> "
                f"<code>{ev}</code> — {why}</li>"
            )
        flags_html = (
            "<div style='margin-top:14px;'>"
            "<strong>🚩 Key Red Flags Triggered:</strong>"
            f"<ul style='margin:6px 0 0 18px;'>{''.join(items)}</ul></div>"
        )

    pos_html = ""
    if report.positive_signs:
        p_items = "".join(f"<li>{html.escape(p)}</li>" for p in report.positive_signs)
        pos_html = (
            "<div style='margin-top:12px;'>"
            "<strong>✅ Positive Legitimacy Signals:</strong>"
            f"<ul style='margin:6px 0 0 18px;'>{p_items}</ul></div>"
        )

    steps_items = "".join(f"<li style='margin-bottom:4px;'>{html.escape(s)}</li>" for s in report.next_steps)
    steps_html = (
        "<div style='margin-top:14px;'>"
        "<strong>🛡️ Recommended Next Steps:</strong>"
        f"<ol style='margin:6px 0 0 18px;'>{steps_items}</ol></div>"
    )

    return f"""
    <div class="sc-verdict-card sc-verdict-{report.verdict}">
        <div class="sc-verdict-top">
            <span class="sc-verdict-pill sc-pill-{report.verdict}">{icon} VERDICT: {report.verdict}</span>
            <div class="sc-score-box">
                <div>Legitimacy Score: <span class="sc-score-num">{report.legitimacy_score}/100</span></div>
                <div>Evidence Coverage: <strong>{report.evidence_coverage.upper()}</strong></div>
            </div>
        </div>
        <div style="font-size:15.5px; line-height:1.55; margin-bottom:10px;">
            <strong>Summary:</strong> {summary_esc}
        </div>
        <div style="font-size:13.5px; opacity:0.9;">
            <strong>Claimed Company:</strong> {company_esc} &nbsp;|&nbsp;
            <strong>Claimed Role:</strong> {role_esc}
        </div>
        {flags_html}
        {pos_html}
        {steps_html}
    </div>
    """


def _render_checks_table(report: FinalReport) -> str:
    status_icon = {
        "passed": "✅ passed",
        "failed": "❌ failed",
        "unavailable": "⚪ unavailable",
    }
    rows = []
    for c in report.checks:
        st = status_icon.get(c.status, c.status)
        delta_str = f"+{c.score_delta}" if c.score_delta > 0 else str(c.score_delta)
        rows.append(
            f"<tr>"
            f"<td><strong>{html.escape(c.name)}</strong></td>"
            f"<td>{st}</td>"
            f"<td><code>{html.escape(c.tier)}</code></td>"
            f"<td><code>{html.escape(c.source)}</code></td>"
            f"<td><strong>{delta_str}</strong></td>"
            f"<td>{html.escape(c.detail)}</td>"
            f"</tr>"
        )
    return f"""
    <div style="margin-top:8px;">
        <h3 style="margin-bottom:6px;">🔍 Verification Checks Breakdown (Agent 2b)</h3>
        <table class="sc-table">
            <thead>
                <tr>
                    <th>Check</th>
                    <th>Status</th>
                    <th>Tier</th>
                    <th>Source</th>
                    <th>Score Impact</th>
                    <th>Detail</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
    """


def _render_verify_links(report: FinalReport) -> str:
    cards = []
    for link in report.verify_links:
        url_esc = html.escape(link.url, quote=True)
        label_esc = html.escape(link.label)
        cards.append(
            f'<a class="sc-verify-link" href="{url_esc}" target="_blank" rel="noopener noreferrer">'
            f"🔗 {label_esc} &rarr;</a>"
        )
    return f"""
    <div style="margin-top:16px;">
        <h3 style="margin-bottom:4px;">🌐 Independent Verification Links (Confirm Yourself)</h3>
        <p style="font-size:13px; opacity:0.8; margin-top:0;">
            SahiCheck never scrapes private platforms. Open these official search & reporting links directly:
        </p>
        <div class="sc-link-grid">
            {''.join(cards)}
        </div>
    </div>
    """


def run_sahicheck_pipeline(
    uploaded_file: Optional[str],
    pasted_text: Optional[str],
    run_web_checks: bool,
) -> Tuple[str, str, str, str, Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Executes Step 0 -> Agent 1 -> Agent 2 & Agent 2b -> Agent 3 and returns UI outputs."""
    try:
        norm = normalize_input(file_path=uploaded_file, pasted_text=pasted_text)
    except ValueError as err:
        err_html = (
            f'<div class="sc-verdict-card sc-verdict-SUSPICIOUS">'
            f"<strong>⚠️ Input Error:</strong> {html.escape(str(err))}</div>"
        )
        return err_html, "", "", "", {}, {}, {}

    # Agent 1: Extraction
    extraction = run_extraction(norm)

    # Agent 2: Offline Red Flags
    red_flags = run_red_flag_checks(extraction)

    # Agent 2b: Verification Checks + Verify Links
    verification = run_verification_checks(extraction, run_web_checks=bool(run_web_checks))

    # Agent 3: Deterministic Scoring + Gemma 4 Synthesis
    final_report = run_synthesis(extraction, red_flags, verification)

    verdict_html = _render_verdict_card(final_report)
    checks_html = _render_checks_table(final_report)
    links_html = _render_verify_links(final_report)

    transcription_display = extraction.verbatim_transcription
    if norm.warnings:
        transcription_display = "WARNINGS: " + " | ".join(norm.warnings) + "\n\n" + transcription_display

    extracted_debug = {
        "model_used": extraction.model_used,
        "extracted_fields": extraction.extracted.model_dump(),
        "visual_cues": extraction.visual_cues.model_dump(),
    }
    flags_debug = {
        "flag_count": len(red_flags),
        "red_flags": [f.model_dump() for f in red_flags],
    }

    return (
        verdict_html,
        checks_html,
        links_html,
        transcription_display,
        extracted_debug,
        flags_debug,
        final_report.model_dump(),
    )


def _load_demo_sample(filename: str) -> Tuple[None, str]:
    path = os.path.join(SAMPLES_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return None, f.read()
    return None, ""


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="SahiCheck — Job Offer Fraud Detector") as demo:
        gr.HTML(
            """
            <div class="sc-header">
                <div class="sc-header-badge">Open-Source Multi-Agent Harness • Gemma 4</div>
                <h1>🛡️ SahiCheck — Job Offer & Recruiter Fraud Detector</h1>
                <p>
                    Built for students, freshers, and job seekers in India. Upload an offer letter screenshot/PDF
                    or paste a suspicious WhatsApp/Telegram/email message (English, Hindi, or Hinglish) to inspect
                    red flags, verify company domains, and get an explainable verdict.
                </p>
            </div>
            """
        )

        with gr.Row():
            with gr.Column(scale=1):
                image_input = gr.File(
                    label="1. Upload Image or PDF (Offer Letter / Chat Screenshot)",
                    file_types=[".png", ".jpg", ".jpeg", ".webp", ".pdf"],
                    type="filepath",
                )
            with gr.Column(scale=1):
                text_input = gr.Textbox(
                    label="2. Or Paste Message Text (WhatsApp / Telegram / Email / SMS)",
                    placeholder="Paste the recruiter message or offer text here (English, Hindi, or Hinglish)...",
                    lines=7,
                )

        with gr.Row():
            web_toggle = gr.Checkbox(
                label="Run web checks (RDAP domain age & company homepage legal links via safe_fetch)",
                value=True,
            )
            check_btn = gr.Button("🔍 Check Offer Authenticity", variant="primary", scale=1)

        with gr.Row():
            sample_scam_btn = gr.Button("🧪 Load Demo Scam (Fee + Spoof Domain)", size="sm")
            sample_safe_btn = gr.Button("🧪 Load Demo Safe Offer (Verified Domain)", size="sm")
            clear_btn = gr.Button("🧹 Clear Inputs", size="sm")

        # Main Output Area
        verdict_output = gr.HTML(label="Verdict Card")
        checks_output = gr.HTML(label="Verification Checks")
        links_output = gr.HTML(label="Verify Links")

        # Transparent Multi-Agent Harness Panels for Live Demo Judges
        gr.Markdown("### 🔬 Transparent Multi-Agent Pipeline Inspector (Live Demo)")
        with gr.Accordion("Agent 1 — Verbatim Transcription (Vision / PDF Text Layer)", open=False):
            transcription_out = gr.Textbox(label="Transcribed Text", lines=6, interactive=False)

        with gr.Accordion("Agent 1 — Extracted Structured Fields & Visual Cues (Unverified Fields Marked)", open=False):
            extracted_json_out = gr.JSON(label="Agent 1 Output")

        with gr.Accordion("Agent 2 — Offline Deterministic Red-Flag Hits", open=False):
            flags_json_out = gr.JSON(label="Agent 2 Red Flags")

        with gr.Accordion("Agent 3 — Final Validated Output Schema (JSON)", open=False):
            final_json_out = gr.JSON(label="Final SahiCheck Schema")

        gr.HTML(
            """
            <div class="sc-disclaimer">
                <strong>Privacy & Safety Notes:</strong>
                Uploads are processed strictly in memory and are never stored or logged.
                When "Run web checks" is enabled, the extracted company domain may be queried via public RDAP and HTTP.
                Because the primary Gemma 4 model is called via API (with local Ollama fallback), avoid uploading
                sensitive personal ID numbers. SahiCheck provides automated guidance, not legal advice.
            </div>
            """
        )

        check_btn.click(
            fn=run_sahicheck_pipeline,
            inputs=[image_input, text_input, web_toggle],
            outputs=[
                verdict_output,
                checks_output,
                links_output,
                transcription_out,
                extracted_json_out,
                flags_json_out,
                final_json_out,
            ],
        )

        sample_scam_btn.click(
            fn=lambda: _load_demo_sample("demo_scam_fee.txt"),
            inputs=[],
            outputs=[image_input, text_input],
        )
        sample_safe_btn.click(
            fn=lambda: _load_demo_sample("demo_safe_offer.txt"),
            inputs=[],
            outputs=[image_input, text_input],
        )
        clear_btn.click(
            fn=lambda: (None, "", "", "", "", "", {}, {}, {}),
            inputs=[],
            outputs=[
                image_input,
                text_input,
                verdict_output,
                checks_output,
                links_output,
                transcription_out,
                extracted_json_out,
                flags_json_out,
                final_json_out,
            ],
        )

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch(server_name="127.0.0.1", server_port=7860, css=CUSTOM_CSS)