# ATS Nexus - Implementation Changelog

This document tracks all changes, phase by phase, as per the final implementation plan.

## Phase 0: Stabilization
*Status: In Progress*

**Changes Logged:**
- **System Dependencies:** Created `packages.txt` adding `ffmpeg`, `tesseract-ocr`, and `poppler-utils` for Streamlit Cloud deployment.
- **Python Dependencies:** Added `reportlab`, `pytesseract`, and `pdf2image` to `requirements.txt`.
- **Text Preprocessing:** Updated `clean_text` in `text_cleaner.py` to use a refined regex that preserves special characters (e.g., `C++`, `Node.js`) instead of stripping them.
- **Text Preprocessing:** Updated `clean_text` in `text_cleaner.py` to use a refined regex that preserves special characters (e.g., `C++`, `Node.js`) instead of stripping them.
- **Refactoring:** Created `keyword_utils.py` to consolidate TF-IDF dynamic keyword extraction and term frequency logic, deduplicating logic from `skill_gap.py` and `smart_builder.py` with a unified noise term list.
- **Document Processing:** Added an OCR fallback using `pytesseract` and `pdf2image` in `read_resume.py` to handle scanned or image-only PDF resumes.
- **Resume Builder:** Rewrote `build_resume_pdf_bytes()` in `resume_builder.py` to use `reportlab` instead of `matplotlib`, ensuring proper pagination across multiple pages for long resumes.

## Phase 1: Semantic Matching
*Status: Complete*

**Changes Logged:**
- **Dependencies:** Added `sentence-transformers` to `requirements.txt`.
- **Model Replacement:** Completely removed the `SVC` and `TfidfVectorizer` classifier from `svm_model.py`. Replaced it with an embedding-based approach using `all-MiniLM-L6-v2`.
- **Chunking & Scoring:** Implemented logic to chunk resumes and JDs by sentence/bullet, compute pairwise cosine similarity, and aggregate the best matching chunks.
- **Calibration:** Applied a Min-Max scaler (0.25 - 0.75 placeholder bounds) to spread raw cosine similarity scores evenly across a 0-100 scale.
- **Data Structures:** Updated `PredictionResult` to carry separated `semantic_score`, `hard_skills_score`, and `soft_skills_score`, while preserving backwards compatibility properties for the existing UI.

## Phase 2: Explainable Score Breakdown
*Status: Complete*

**Changes Logged:**
- **Sub-Score Computation:** Modified `skill_gap.py` to calculate exact 0-100 percentage scores for both Hard Skills and Soft Skills based on catalog matches.
- **Score Weighting:** Updated `app.py` and `resume_builder.py` to combine the Semantic (50%), Hard Skills (35%), and Soft Skills (15%) scores into a unified `overall_score`.
- **UI Visualization:** Implemented `plotly.express` radar charts in the Single Resume and Resume Builder views to visually break down the candidate's fit across the three distinct metrics.
- **Bulk Export Update:** Expanded the Bulk Analysis dataframe and CSV export to include dedicated columns for Semantic, Hard Skills, and Soft Skills percentages alongside the overall score.

## Phase 3: Blind Screening (Presidio)
*Status: Complete*

**Changes Logged:**
- **PII Scrubbing Utility:** Created `presidio_utils.py` leveraging Microsoft's `presidio-analyzer` and `presidio-anonymizer` to detect and redact `PERSON`, `EMAIL_ADDRESS`, `PHONE_NUMBER`, and `LOCATION` tags.
- **UI Toggles:** Added "Enable Blind Screening Mode" toggles to the Single Resume and Bulk Analysis views in `app.py`.
- **Text Redaction Pipeline:** Hooked the toggles into the text extraction flow so that when active, PII is removed *before* the resume hits the SVM matching model or is displayed in the "Extracted Text" expander.
- **Dependencies:** Added `spacy`, `presidio-analyzer`, and `presidio-anonymizer` to `requirements.txt`.

## Phase 4: Lightweight NER (spaCy)
*Status: Complete*

**Changes Logged:**
- **NER Utility:** Created `ner_utils.py` to securely load `en_core_web_lg` via spaCy and extract `DATE` and `ORG` (Organizations) entities from arbitrary text.
- **Scoring Boost:** Updated `skill_gap.py` to leverage NER. If candidates display clearly structured experience (with dates or orgs present), they receive a slight bump (up to 10%) on their Soft Skills score to reward clear formatting over keyword dumps.
- **UI Transparency:** Updated the Single Resume and Resume Builder `app.py` views to display "Recognized Orgs" and "Recognized Timelines" beneath the Matched/Missing Skills lists.

## Phase 5: GitHub Profile Verification
*Status: Complete*

**Changes Logged:**
- **GitHub API Integration:** Created `github_utils.py` to securely query the public GitHub API, fetching a candidate's repositories and extracting the programming languages they actually use.
- **Regex Extraction:** Updated `app.py` to scan the raw PDF text for `github.com/username` formats automatically.
- **Score Rescuing:** Updated the Single Resume view so that if a candidate is "missing" a required tech skill (like Python), but their GitHub profile contains Python repositories, the system "rescues" that skill, rendering a green verification badge and boosting the overall ATS score to compensate.

## Phase 6: Local Video Screening (Faster-Whisper)
*Status: Complete*

**Changes Logged:**
- **Offline Transcription:** Stripped out the internet-dependent Google Speech API from `video_screening.py`.
- **Model Integration:** Replaced the audio processing layer with `faster-whisper` running locally on the CPU (using int8 compute mode for speed).
- **Synchronized Scoring:** Updated the Video Resume feature to compute the full tripartite score (Semantic/Hard/Soft) instead of just relying on the raw TF-IDF score, ensuring the Video feature matches the accuracy of the PDF screening.

## Phase 7: Sanity & Calibration Pipeline
*Status: Complete*

**Changes Logged:**
- **Calibration Scaffold:** Created `calibrate.py` to systematically ingest `.txt` and `.pdf` files from a structured `test_data/` directory.
- **Tuning Mechanism:** Implemented a tuning loop so the user can finalize the min/max bounds of the Semantic cosine-similarity scaler to perfectly match human-judged ground-truth scores.
