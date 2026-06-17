# ATS Nexus — Final Implementation Plan for Coding Agent

This is the corrected, final version of the plan. It keeps the phase numbering and substance from the original spec and the file-tagging/verification format from the agent's draft, with three gaps fixed: a missing system dependency, a calibration step that was about to use synthetic test data instead of real judged examples, and several UI-honesty requirements that had been dropped.

## Hard Constraints — Read Before Starting

- **No paid APIs anywhere.** Every library must be open-source and run locally (CPU only, no GPU assumed). Do not substitute a hosted embeddings API, hosted NER API, or hosted speech-to-text API. The only network call permitted anywhere in this plan is the GitHub REST API in Phase 5, using a free Personal Access Token.
- Target deployment is Streamlit Community Cloud (free tier): limited RAM, no GPU, app sleeps when idle and reloads models on wake. Prefer small/distilled models throughout.
- Development is happening locally on Windows before deployment. `packages.txt` only affects the Streamlit Cloud (Debian) environment — it installs nothing on the local Windows machine. Any system binary needed for local testing (Tesseract, Poppler, ffmpeg) must be installed manually on Windows (via direct installer or a tool like Chocolatey) before that phase can be tested locally.
- Do not calibrate or validate any scoring logic against synthetic/dummy test data. Use the real, human-judged test set from Phase 7 for every calibration and validation step — this whole plan exists partly to get away from the original synthetic-data SVM problem, and recreating it at the calibration step would defeat the purpose.
- Every phase must be runnable and smoke-tested before the next phase begins. Do not skip ahead.

## User Review Required

> [!IMPORTANT]
> **Local resources:** New ML models (`all-MiniLM-L6-v2`, `en_core_web_sm`, the chosen `faster-whisper` size) download on first run. CPU-friendly but they take disk space and add load time, especially on a free-tier app waking from sleep.
>
> **Tesseract OCR:** Needs the Tesseract binary on the host. On Streamlit Cloud this comes from `packages.txt`; locally on Windows it needs the official Windows installer.
>
> **Poppler (for `pdf2image`):** Needs Poppler binaries on the host. On Streamlit Cloud this comes from `packages.txt` (`poppler-utils`) — this was missing from the previous draft and must be included. Locally on Windows, Poppler has no simple installer; binaries must be downloaded and added to PATH manually before OCR can be tested on your machine.
>
> **GitHub Verification:** Needs a free GitHub Personal Access Token added to `.streamlit/secrets.toml` to raise the rate limit from 60/hr to 5,000/hr.

## Open Questions

- Do you already have 10–20 real resume/JD pairs with a rough "strong fit / weak fit / no fit" judgment for calibration (Phase 7), or should we draft a starter set together before Phase 1's calibration step?
- For `faster-whisper` in Phase 6: `base` model balances speed/accuracy reasonably on CPU — confirm or prefer `small`/`tiny`?
- For the final score weighting in Phase 2 (hard skill / semantic / soft skill), is an initial 50/35/15 split acceptable as a starting point to tune later against Phase 7's test set, or do you want different starting weights?

---

## Phase 0 — Stabilize Existing Code (prerequisite for everything else)

#### [MODIFY] `text_cleaner.py`
Update `clean_text`'s regex to `r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.-]{1,}\b"` so it preserves `+`, `#`, `.`, `-` inside tokens. Currently "C++" becomes "c" and "Node.js" becomes "node js" before scoring ever sees them — this silently destroys signal for every phase built afterward.

#### [MODIFY] `resume_builder.py`
Replace the matplotlib-based renderer in `build_resume_pdf_bytes()` with `reportlab.platypus` (`SimpleDocTemplate`, `Paragraph`, `Table`, `Spacer`). The current renderer draws on one fixed-size axes with no page-break logic, so long resumes silently run off the bottom of the page. Preserve existing sections (header, summary, skills, education, experience grouped by internship/simulation/other, projects, certifications).

#### [NEW] `packages.txt`
Add `ffmpeg`, `tesseract-ocr`, and `poppler-utils`. All three are required: `ffmpeg` for moviepy/faster-whisper, `tesseract-ocr` for `pytesseract`, `poppler-utils` for `pdf2image` (this last one was missing from the previous draft and is required for the OCR fallback below to function at all).

#### [MODIFY] `read_resume.py`
In `extract_text_from_pdf`, if `pdfplumber` returns empty/near-empty text, fall back to converting pages to images with `pdf2image` and running `pytesseract` on them.

#### [MODIFY] `skill_gap.py` & `smart_builder.py`
Extract the duplicated TF-IDF dynamic-keyword extraction logic (currently implemented twice with slightly different noise-word lists) into a single shared helper in a new `keyword_utils.py`. Both files import from it so Single Resume, Bulk, and Resume Builder never disagree on the same input.

**Acceptance criteria:** "C++" and "Node.js" score as distinct tokens from "C". A long resume (3+ experience entries, 3+ projects) paginates fully across multiple PDF pages with no cut-off content. A scanned/image-only PDF returns extracted text via OCR. Skill match results are identical across all three modes for the same input.

---

## Phase 1 — Replace Synthetic SVM with Real Semantic Matching

#### [MODIFY] `requirements.txt`
Add `sentence-transformers`.

#### [MODIFY] `svm_model.py`
Remove `SVC`, `TfidfVectorizer`, and the `Pipeline` entirely — there's no classifier needed once you have a direct similarity number. Load `SentenceTransformer('all-MiniLM-L6-v2')` once at startup, not per-request. Split the resume into chunks (each experience bullet, each project description, the summary) before embedding — `all-MiniLM-L6-v2` truncates around 256 tokens, so embedding the full resume as one string silently drops everything past that point. Embed the JD (as a whole, or split into requirement-like lines if long) and each resume chunk, compute pairwise cosine similarity, and aggregate by taking the best-matching resume chunk per JD line, then averaging.

Apply min-max or sigmoid rescaling to the raw cosine similarity (which typically falls in a narrow 0.3–0.7 band for real resume/JD pairs) so the displayed score spreads meaningfully across 0–100. **Pick the scaling parameters using the Phase 7 real test set only — not synthetic examples.**

Keep the existing rule-based skill catalog matching running in parallel as a separate signal; do not remove it. Update `PredictionResult` (or replace it) to carry `semantic_score`, `hard_skills_score`, and `soft_skills_score` separately, in addition to whatever `overall_score` Phase 2 produces.

**Acceptance criteria:** Scoring is a direct embed-and-compare with no per-request training. A resume describing equivalent experience in different wording than the JD scores meaningfully higher than an unrelated resume. Scores across 10+ varied resumes against the same JD show real spread, not clustering in one narrow band.

---

## Phase 2 — Explainable Score Breakdown

#### [MODIFY] `requirements.txt`
Add `plotly`.

#### [MODIFY] `svm_model.py` (or wherever final scoring logic lives)
Combine `hard_skills_score`, `semantic_score`, and `soft_skills_score` into `overall_score` using clearly commented, named weights (starting point: 50% hard skill, 35% semantic, 15% soft skill — confirm with the Open Questions answer above). Document the weighting choice in a code comment so it can be retuned later against Phase 7's test set without reverse-engineering the logic.

#### [MODIFY] `app.py`
Add `st.metric` columns or a plotly radar chart in Single Resume, Bulk, and Resume Builder views showing all sub-scores, not just the final number. In Bulk Analysis, add the sub-scores as extra CSV export columns.

**Acceptance criteria:** Every view that currently shows one ATS score now shows the breakdown, and the combination logic is documented in code, not implicit.

---

## Phase 3 — Blind Screening Mode

#### [MODIFY] `requirements.txt`
Add `presidio-analyzer`, `presidio-anonymizer`.

#### [NEW] `anonymizer.py`
Build a redaction module: run Presidio's analyzer for `PERSON`, `EMAIL_ADDRESS`, `PHONE_NUMBER`, `GPE`, and optionally `ORG`, then anonymize matches into placeholders (`[CANDIDATE_NAME]`, `[EMAIL_REDACTED]`, etc.).

**Test against a deliberately diverse sample before trusting this** — include Indian names, Indian phone formats (`+91`), and non-US university names. Presidio's default recognizers are tuned for US/UK formats; add a custom recognizer pattern for Indian phone numbers if default accuracy is poor.

#### [MODIFY] `app.py`
Add a "Blind Mode" toggle in Single Resume and Bulk views. When enabled, the extracted-text expander and any name references show the redacted version only.

**UI copy requirement:** Do not present this as full anonymization. The interface must state plainly that it redacts direct identifiers (name, contact info, location) but cannot guarantee indirect signals (writing style, specific employer, distinctive project names) are removed — claims should match what's actually tested, not be aspirational.

**Acceptance criteria:** Name, email, and phone number are reliably redacted across at least 10 varied test resumes, with false positives/negatives manually reviewed and documented. UI copy includes the limitation disclaimer.

---

## Phase 4 — Lightweight NER for Experience Extraction (best-effort)

#### [MODIFY] `requirements.txt`
Add `spacy` (and download `en_core_web_sm`).

#### [NEW or MODIFY] `experience_extraction.py` / `skill_gap.py`
Run resume text through spaCy to extract `ORG` and `DATE` entities. Build a simple heuristic for total estimated years of experience from extracted date ranges. **Do not attempt to link individual skills to specific date ranges in this phase** — that requires substantially more custom logic than a small general-purpose NER model supports reliably, and should only be scoped as separate future work if this simpler version proves useful.

#### [MODIFY] `app.py` (Phase 2 breakdown)
Feed the estimated years into the score breakdown as an "Experience Match" sub-score (JD years requested vs. resume years extracted), visibly labeled as an estimate in the UI.

**Acceptance criteria:** Total years-of-experience estimate is in a reasonable ballpark on at least 7 of 10 test resumes with manually known experience lengths. Per-skill year attribution is explicitly out of scope.

---

## Phase 5 — GitHub Verification (optional, lowest priority)

#### [MODIFY] `read_resume.py`
Extract `github.com/<username>` links via regex. Call the GitHub REST API (`/users/{username}/repos`) using a free Personal Access Token from `st.secrets` (never hardcoded) — unauthenticated calls cap at 60/hour, which bulk mode would exhaust almost immediately. Cache results per username for the session so bulk mode doesn't repeat calls for the same candidate.

Aggregate the `language` field across public, **non-fork** repositories only — forked repos and coursework skew the signal and should be excluded. If a skill claimed on the resume appears among the candidate's top GitHub languages, show a "✅ Activity found on GitHub" badge next to it.

**UI copy requirement:** Include an honest fallback message when no public activity is found ("No verifiable public activity found") rather than treating absence as a negative signal, and do not claim this proves skill proficiency — frame it as a supporting signal only.

**Acceptance criteria:** Badge appears correctly for a test profile with known public activity, handles profiles with no/private repos gracefully, stays within the authenticated rate limit during a 50-resume bulk test, and excludes forked repos from language aggregation.

---

## Phase 6 — Local, Private Video Transcription

#### [MODIFY] `requirements.txt`
Add `faster-whisper`; remove `SpeechRecognition` if no longer used elsewhere.

#### [MODIFY] `video_screening.py`
Replace the `recognize_google` call with `faster-whisper`, using the model size confirmed in the Open Questions above. This depends on `ffmpeg` from Phase 0 — confirm it's installed locally (manually on Windows) before testing.

**UI copy requirement:** Update the Video Resume section so it no longer implies analysis of "communication and delivery signal" or "confidence behavior" unless those are actually computed — current code only transcribes and scores the transcript text. A real, optional additive feature here is a literal speaking-rate metric (words per minute from transcript length and clip duration), clearly labeled as such if built.

**Acceptance criteria:** Video transcription works fully offline with no external API call, and UI claims match what's actually computed.

---

## Phase 7 — Build a Ground-Truth Test Set (run in parallel with Phases 1–4, not after)

Assemble 10–20 resume/JD pairs with a rough human judgment of fit ("strong fit," "weak fit," "no fit") — real examples, not synthetic/dummy data. Use this set to calibrate Phase 1's scaling and Phase 2's weighting, and re-run it any time scoring logic changes later, so regressions are caught immediately.

**Acceptance criteria:** Score ordering on the test set roughly matches human judgment ordering. Document any clear mismatches and use them to adjust calibration/weights before considering Phases 1–2 complete.

---

## Verification Plan

**Automated/local tests:** Run the updated `svm_model.py` against the Phase 7 real test set (not dummy data) to confirm cosine similarity scaling distributes scores meaningfully across 0–100 and roughly tracks human judgment. Test `anonymizer.py` against varied PII (US/UK/Indian names and phone formats) to confirm redaction without over-redacting skill terms.

**Manual verification:** Upload a multi-page resume to Resume Builder and confirm the PDF paginates correctly. Upload an image-only PDF to confirm the `pytesseract`/`poppler` fallback triggers and extracts text. Upload a sample video to confirm `faster-whisper` transcribes entirely offline with no connection errors. Confirm Blind Mode and GitHub badge UI copy includes the required disclaimers, not just the functional toggle/badge.

---

## Summary of New Dependencies

`sentence-transformers`, `reportlab`, `pdf2image`, `pytesseract`, `presidio-analyzer`, `presidio-anonymizer`, `spacy` (+ `en_core_web_sm`), `faster-whisper`, `plotly`. System packages for `packages.txt`: `ffmpeg`, `tesseract-ocr`, `poppler-utils`. All free and open-source — no paid API required anywhere in this plan except an optional free GitHub PAT for higher rate limits.
