# AI-Based ATS Resume Screening System (SVM)

A Streamlit web app that screens resumes against a job description using NLP + TF-IDF + SVM.

## Features
- Single PDF resume ATS scoring
- Bulk PDF screening (100+ supported)
- Skill gap analysis (matched vs missing skills)
- Video resume screening (speech-to-text + ATS score)
- Resume Builder with ATS-fit preview and downloadable resume output

## Project Structure
- `app.py` - Streamlit UI
- `read_resume.py` - PDF text extraction
- `text_cleaner.py` - NLP preprocessing
- `svm_model.py` - SVM ATS model
- `skill_gap.py` - skill matching logic
- `video_screening.py` - video transcription + scoring
- `resume_builder.py` - resume generation + ATS feedback

