# SahiCheck v2

Open-source AI job-offer and recruiter-fraud detector for India.
**Gradio has been fully removed.** The UI is now a React + Vite + Tailwind SPA backed by a FastAPI streaming API.

---

## Dependencies and licenses

### Python (backend)
| Package | License |
|---|---|
| `fastapi` | MIT |
| `uvicorn` | BSD-3-Clause |
| `python-multipart` | Apache-2.0 |
| `pydantic` | MIT |
| `httpx` | BSD |
| `tldextract` | MIT |
| `rapidfuzz` | MIT |
| `pypdfium2` | Apache-2.0 |
| `pypdf` | MIT |
| `Pillow` | HPND (PIL License) |
| `python-dotenv` | MIT |
| `google-genai` | Apache-2.0 |

### Frontend (JavaScript)
| Package | License |
|---|---|
| `react`, `react-dom` | MIT |
| `vite`, `@vitejs/plugin-react` | MIT |
| `tailwindcss` | MIT |
| `lucide-react` | ISC |
| `@fontsource/plus-jakarta-sans` | SIL OFL 1.1 |

> The Plus Jakarta Sans font is self-hosted via `@fontsource/plus-jakarta-sans`. **No Google Fonts CDN is used.**

---

## Run instructions

### Development (two terminals)

**Terminal 1 – Backend:**
```bash
# activate venv, then:
uvicorn app:app --port 8000
```

**Terminal 2 – Frontend dev server:**
```bash
cd frontend
npm run dev          # http://localhost:5173
```
Vite proxies `/api/*` to `http://localhost:8000`.
If your proxy buffers the NDJSON stream, call the backend directly at `http://localhost:8000` from the browser (CORS is already restricted to `http://localhost:5173`; set `CORS_ORIGIN` env var to override).

### Production (single command)

```bash
cd frontend && npm run build    # builds to frontend/dist/
cd ..
uvicorn app:app --port 8000    # also serves frontend/dist as static files
```
Visit `http://localhost:8000`.

---

## Architecture

```
POST /api/check (multipart)
        │
        ▼
  pipeline.py – sync generator, runs in FastAPI threadpool
        │
        ├─ Step 0: normalize_input (inputs.py) – in-memory, no disk writes
        ├─ Stage extract: run_extraction (agents/extract.py) – Gemma 4
        ├─ Checks 1-11: run_red_flag_checks (agents/check.py) – offline regex/fuzzy
        ├─ Check 12: _check_official_domain (agents/verify.py) – offline
        ├─ Check 13: _check_salary_plausibility (agents/verify.py) – offline
        ├─ Check 14: _check_domain_age_rdap (agents/verify.py) – web (RDAP)
        ├─ Check 15: _check_site_legal_pages (agents/verify.py) – web
        └─ Check 16: _build_verify_links (agents/verify.py) – info only
```

Each step emits NDJSON events (`application/x-ndjson`) so the frontend spinner moves in real time — **no client-side timers**.

---

## Scoring (deterministic, no model involved)

| Check # | Check | Max points |
|---|---|---|
| 1 | Free-mail HR address | 5 |
| 2 | Blocklisted domain | 7 |
| 3 | Suspicious TLD | 3 |
| 4 | Lookalike domain | 8 |
| 5 | Payment demand (fee, deposit, UPI, QR) | 12 |
| 6 | OTP / PIN / password request | 8 |
| 7 | Sensitive ID document request | 7 |
| 8 | No interview / guaranteed job | 4 |
| 9 | Extreme urgency pressure | 4 |
| 10 | Chat-only recruitment | 4 |
| 11 | LinkedIn mass-hiring drive | 2 |
| 12 | Official company domain | 15 |
| 13 | Pay plausibility | 8 |
| 14 | Domain age (RDAP) | 7 |
| 15 | Company website legal pages | 5 |
| 16 | Verify links | 0 (info) |
| **Total** | | **99** |

**Formula:** `raw = sum of max_points for passed checks`.
**Caps:** checks 5/6/7 failed → cap 29; checks 2/4 failed → cap 35 (lowest cap wins).
`score = clamp(min(raw, cap), 1, 99)`. Never 0 or 100.

For checks 1–11, **Passed = flag not detected, Failed = flag detected**.
