# 🚀 AI-Assisted Resume Intelligence Platform

🔗 **Live Demo:** https://ats-resume-pro.streamlit.app/

A SaaS-style Resume Intelligence Platform that evaluates resumes using NLP techniques and skill gap analysis to generate explainable ATS scores, visual insights, and candidate ranking.

---

## 🎯 Problem Statement

Recruiters receive hundreds of resumes for a single job role, making manual screening:

- Time-consuming  
- Inconsistent  
- Difficult to scale  

Most traditional ATS systems rely only on keyword matching and do not provide clear feedback to candidates.

---

## 💡 Solution

This project introduces a **Resume Intelligence Platform** that combines:

- Rule-based skill extraction  
- NLP-based semantic similarity (TF-IDF + cosine similarity)  
- Interactive visual analytics  

It helps:

- 👨‍💼 Recruiters → Quickly evaluate and rank candidates  
- 👨‍🎓 Candidates → Understand resume-job alignment  

---

## 🔥 Key Features

- 📄 Resume Parsing from PDF files  
- 🧠 Hybrid ATS Scoring (Skill Match + Semantic Similarity)  
- 📊 Interactive Dashboard (Streamlit)  
- 📈 Score Visualization (Gauge + Charts)  
- 🧩 Skill Gap Analysis (Matched vs Missing Skills)  
- 🔍 Keyword Extraction from Job Description  
- 📂 Bulk Resume Ranking System  
- 📥 CSV Export for candidate ranking  

---

## 🧠 AI Component

The system uses **Natural Language Processing (NLP)** techniques:

- **TF-IDF Vectorization** → Converts text into numerical representation  
- **Cosine Similarity** → Measures semantic similarity between resume and job description  
- **Hybrid Approach** → Combines rule-based skill matching with NLP for improved evaluation  

---

## ⚙️ How It Works

1. Upload resume (PDF)
2. Extract text from document
3. Clean and preprocess text
4. Extract relevant skills using rule-based matching
5. Compute semantic similarity using TF-IDF
6. Generate final ATS score
7. Display insights via dashboard
8. Rank candidates (bulk mode)

---

## 📊 Features Overview

| Feature | Description |
|--------|------------|
| ATS Score | Combined score based on skill + semantic match |
| Skill Gap Analysis | Identifies missing and matched skills |
| Keyword Insights | Highlights important job description keywords |
| Dashboard | Visual analytics with charts and metrics |
| Bulk Mode | Compare and rank multiple resumes |
| Export | Download candidate ranking as CSV |

---

## 🧱 Tech Stack

- **Python**
- **Streamlit** (Frontend Dashboard)
- **Scikit-learn** (TF-IDF, Cosine Similarity)
- **Plotly** (Visualization)
- **pdfplumber** (PDF Parsing)
- **Pandas** (Data Handling)

---

## 🧠 Learnings
Applied NLP techniques to real-world resume screening
Designed modular and scalable architecture
Built interactive SaaS-style dashboard using Streamlit
Implemented explainable scoring system


## 👨‍💻 Author

Sajal Singhal
B.Tech CSE | Data Science & AI Enthusiast
