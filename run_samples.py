# TODO: Test script to run SahiCheck against sample offers

"""CLI test runner (run_samples.py) to evaluate SahiCheck across sample texts and images."""

import os
from agents.check import run_red_flag_checks
from agents.extract import run_extraction
from agents.synthesize import run_synthesis
from agents.verify import run_verification_checks
from inputs import normalize_input

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")


def evaluate_sample(label: str, file_path: str = None, text: str = None, web: bool = False) -> None:
    norm = normalize_input(file_path=file_path, pasted_text=text)
    ext = run_extraction(norm)
    flags = run_red_flag_checks(ext)
    ver = run_verification_checks(ext, run_web_checks=web)
    rep = run_synthesis(ext, flags, ver)

    print("=" * 72)
    print(f"SAMPLE:   {label}")
    print(f"MODEL:    {ext.model_used}")
    print(f"VERDICT:  {rep.verdict} (Score: {rep.legitimacy_score}/100 | Coverage: {rep.evidence_coverage})")
    print(f"COMPANY:  {rep.extracted.company} | ROLE: {rep.extracted.role}")
    print(f"EMAILS:   {rep.extracted.emails} | UPI: {rep.extracted.upi_ids}")
    print(f"FLAGS ({len(rep.red_flags)}): {[f.id for f in rep.red_flags]}")
    print(f"SUMMARY:  {rep.summary}")


if __name__ == "__main__":
    demo_files = ["demo_scam_fee.txt", "demo_safe_offer.txt"]
    for fname in demo_files:
        fpath = os.path.join(SAMPLES_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                evaluate_sample(fname, text=f.read(), web=False)