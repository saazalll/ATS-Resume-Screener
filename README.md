# 🚀 ATS Nexus: AI-Assisted Resume Intelligence Platform

A cutting-edge, fully localized SaaS-style Resume Intelligence Platform that evaluates candidate fit using advanced Machine Learning, semantic embeddings, and verifiable heuristic signals. 

This platform transforms the traditional "black-box" keyword-scanner into a highly explainable, privacy-first AI screening engine.

---

## 🔥 Key Upgrades (ATS Nexus Architecture)

The system has been completely rebuilt from the ground up to feature:

- **True Semantic Understanding**: Removed legacy TF-IDF in favor of the `all-MiniLM-L6-v2` transformer model to score resumes based on true semantic intent, not just keyword matching.
- **Tripartite Scoring Engine**: Replaced single-score systems with a 50/35/15 weighted breakdown of Semantic Fit, Hard Skills, and Soft Skills.
- **Privacy-First Blind Screening**: Integrated Microsoft `presidio` to automatically redact PII (Names, Emails, Phone Numbers) from resumes *before* evaluation to guarantee unbiased screening.
- **Contextual Verification**: 
  - Integrated `spaCy` NER to extract organizational timelines and penalize "keyword stuffing" without backing experience.
  - Connected the **GitHub API** to cross-reference and verify developer activity, allowing candidates to "rescue" missing skills if they are actively using them in open-source projects.
- **Fully Offline Video Screening**: Replaced cloud APIs with `faster-whisper` to transcribe and analyze video resumes entirely locally on the CPU.
- **Dynamic Visual Analytics**: Implemented interactive Plotly radar charts and bulk-analysis heatmaps in the Streamlit UI.

---

## ⚙️ How It Works (The 7-Phase Pipeline)

1. **Extraction**: `pdfplumber` parses the PDF into raw text (with Tesseract OCR fallback).
2. **Blind Screening**: `presidio-analyzer` and `presidio-anonymizer` scan the text and redact sensitive entities (e.g., `<PERSON>`, `<PHONE_NUMBER>`).
3. **Semantic Matching**: The `all-MiniLM-L6-v2` Sentence-Transformer chunks the text and computes dense cosine similarities against the Job Description.
4. **NER Contextualization**: `spaCy` extracts Dates, Times, and Organizations to ensure the candidate actually has real-world experience, not just a list of words.
5. **Heuristic Verification**: The system attempts to scrape the candidate's GitHub handle (if provided) to cross-verify missing technical skills.
6. **Tripartite Calculation**: The system merges Semantic (50%), Hard Skills (35%), and Soft Skills (15%) into a final, explainable score.
7. **Visualization**: Streamlit plots the results dynamically using Plotly Radar Charts and Confidence Heatmaps.

---

## 📊 Features Overview

| Feature | Description |
|--------|------------|
| **Single Resume Analysis** | Upload a PDF and get a deep, explainable breakdown of the candidate's fit. |
| **Bulk Analysis Heatmaps** | Upload 50+ resumes to instantly generate a candidate ranking table and visual heatmap. |
| **Resume Builder** | Generate an ATS-optimized, machine-readable PDF resume directly from the dashboard. |
| **Video Resume Screening** | Upload an MP4 video to transcribe and score the candidate's speech locally using `faster-whisper`. |

---

## 🧱 Tech Stack

- **Python 3.11**
- **Frontend**: Streamlit
- **Visualization**: Plotly, Matplotlib
- **Machine Learning / NLP**: 
  - `sentence-transformers` (`all-MiniLM-L6-v2`)
  - `spacy` (`en_core_web_sm`)
  - `presidio-analyzer` / `presidio-anonymizer`
  - `faster-whisper` (Local Audio Transcription)
- **Data Processing**: Pandas, NumPy, pdfplumber

---

## 🛠️ Installation & Setup

Ensure you are using Python 3.11 for optimal compatibility.

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
pip install plotly presidio-analyzer presidio-anonymizer
```

2. **Download spaCy Core**:
```bash
python -m spacy download en_core_web_sm
```

3. **(Optional) Add GitHub Token**:
For higher rate limits on the Github Verification API, add a classic token to your environment variables:
```bash
export GITHUB_TOKEN="your_classic_token_here"
```

4. **Run the Dashboard**:
```bash
streamlit run app.py
```

---

## 👨‍💻 Author

**Sajal Singhal**
B.Tech CSE | Data Science & AI Enthusiast
