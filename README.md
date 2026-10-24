# SahiCheck (Job Offer Fraud Detector)

> Transparent, multi-agent AI web application for detecting fraudulent job offers and fake recruiter communications in India (English, Hindi, and Hinglish).

Built for Hacktoberfest 2026 Hack Day (Track 1: "Best Open-Source AI Project").

## Models & Tools
- **Primary LLM/VLM**: Gemma 4 31B-it (`gemma-4-31b-it`) via Gemini API (`google-genai` SDK - Apache 2.0).
- **Offline Fallback LLM/VLM**: Gemma 4 E4B-it (`gemma4:e4b`) via local Ollama.
- **Unified Gateway**: `llm.py` (Gemini API with seamless local Ollama fallback).
- **PDF Extraction**: `pypdfium2` (rendering) and `pypdf` (text layer) (Permissive licenses).
- **Domain Verification**: `tldextract` (BSD) & `rapidfuzz` (MIT).
- **Web Verification**: `httpx` (BSD-3-Clause) with custom safe fetch gate (`safe_fetch.py`).
- **Data Validation**: `pydantic` v2 (MIT).
- **User Interface**: `gradio` (Apache 2.0).

## License
Apache-2.0
