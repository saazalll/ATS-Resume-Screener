import html

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from read_resume import safe_extract_text
from resume_builder import (
    build_resume_markdown,
    build_resume_pdf_bytes,
    build_resume_scoring_text,
    get_resume_builder_feedback,
)
from skill_gap import get_skill_match_details
from smart_builder import generate_smart_builder_suggestions
from svm_model import ATSMatcher
from text_cleaner import clean_text
from video_screening import screen_video_resume
from presidio_utils import scrub_pii
from github_utils import extract_github_username, fetch_github_languages
from experience_utils import estimate_years_of_experience


st.set_page_config(page_title="ATS Nexus", page_icon="📄", layout="wide", initial_sidebar_state="collapsed")

def _theme() -> dict:
    return {
        "bg": "#0A0F1E",
        "surface": "rgba(255, 255, 255, 0.05)",
        "surface_soft": "rgba(255, 255, 255, 0.02)",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "border": "rgba(255, 255, 255, 0.1)",
        "accent": "#6366F1",
        "accent2": "#22D3EE",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "hero": "linear-gradient(128deg, #1E1B4B 0%, #312E81 42%, #0891B2 100%)",
        "input_bg": "rgba(15, 23, 42, 0.6)",
        "input_text": "#F8FAFC",
        "input_border": "rgba(255, 255, 255, 0.15)",
        "file_bg": "rgba(15, 23, 42, 0.6)",
        "file_text": "#F8FAFC",
    }


def _inject_css(theme: dict) -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {{
          --bg: {theme['bg']};
          --surface: {theme['surface']};
          --surface-soft: {theme['surface_soft']};
          --text: {theme['text']};
          --muted: {theme['muted']};
          --border: {theme['border']};
          --accent: {theme['accent']};
          --accent2: {theme['accent2']};
          --success: {theme['success']};
          --warning: {theme['warning']};
          --danger: {theme['danger']};
          --input-bg: {theme['input_bg']};
          --input-text: {theme['input_text']};
          --input-border: {theme['input_border']};
          --file-bg: {theme['file_bg']};
          --file-text: {theme['file_text']};
        }}

        @keyframes meshMove {{
          0% {{ background-position: 0% 50%; }}
          50% {{ background-position: 100% 50%; }}
          100% {{ background-position: 0% 50%; }}
        }}

        html, body, [class*="css"] {{
          font-family: "Inter", "Segoe UI", sans-serif;
        }}

        .stApp {{
          background: radial-gradient(circle at top left, rgba(99, 102, 241, 0.15), transparent 40%),
                      radial-gradient(circle at bottom right, rgba(34, 211, 238, 0.15), transparent 40%),
                      var(--bg);
          background-size: 200% 200%;
          animation: meshMove 15s ease infinite;
          color: var(--text);
        }}

        [data-testid="stSidebar"] {{ display: none; }}

        .main .block-container {{
          max-width: 1220px;
          padding-top: 2rem;
          padding-bottom: 3rem;
        }}

        .mast {{
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
          padding: 1.2rem 1.5rem;
          border: 1px solid var(--border);
          border-radius: 16px;
          background: var(--surface);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          margin-bottom: 1rem;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }}

        .mast-title {{
          margin: 0;
          font-size: 1.4rem;
          font-weight: 800;
          color: var(--text);
          letter-spacing: -0.5px;
          background: linear-gradient(90deg, #F8FAFC, #94A3B8);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }}

        .mast-sub {{
          margin: 0.3rem 0 0 0;
          font-size: 0.9rem;
          color: var(--muted);
        }}

        .hero {{
          background: {theme['hero']};
          color: #FFFFFF;
          border-radius: 24px;
          border: 1px solid rgba(255,255,255,0.1);
          padding: 2.5rem 2rem;
          margin-bottom: 1.5rem;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
          position: relative;
          overflow: hidden;
        }}
        
        .hero::before {{
            content: '';
            position: absolute;
            top: 0; right: 0; bottom: 0; left: 0;
            background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
            pointer-events: none;
        }}

        .hero, .hero * {{
          color: #F8FAFC !important;
        }}

        .brand-title {{
          margin: 0;
          font-size: 2.5rem;
          font-weight: 800;
          letter-spacing: -1px;
          line-height: 1.2;
        }}

        .brand-sub {{
          margin: 0.8rem 0 1.5rem 0;
          font-size: 1.1rem;
          color: #CBD5E1 !important;
          max-width: 600px;
        }}

        .hero-pills {{
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex-wrap: wrap;
          margin-bottom: 2rem;
        }}

        .hero-pill {{
          border: 1px solid rgba(255,255,255,0.2);
          background: rgba(255,255,255,0.05);
          backdrop-filter: blur(8px);
          border-radius: 999px;
          padding: 0.4rem 1rem;
          font-size: 0.8rem;
          color: #E2E8F0;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 0.4rem;
        }}

        .hero-grid {{
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 1rem;
          border-top: 1px solid rgba(255,255,255,0.1);
          padding-top: 1.5rem;
        }}

        .stat-val {{
            font-size: 1.5rem;
            font-weight: 800;
            margin: 0;
        }}
        .stat-label {{
            font-size: 0.8rem;
            color: #94A3B8 !important;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .section-card {{
          background: var(--surface);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
          border: 1px solid var(--border);
          border-radius: 16px;
          padding: 1.5rem;
          margin-bottom: 1rem;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        }}

        .section-head {{
          margin: 0;
          color: var(--text);
          font-size: 1.3rem;
          font-weight: 800;
          letter-spacing: -0.2px;
        }}

        .section-sub {{
          margin: 0.4rem 0 1rem 0;
          color: var(--muted);
          font-size: 0.95rem;
        }}

        .stRadio > div {{
          border: none;
          background: transparent;
          border-radius: 0;
          padding: 0;
          margin: 0;
        }}

        .stRadio div[role="radiogroup"] {{
          display: flex;
          gap: 0.4rem;
          flex-wrap: wrap;
        }}

        .stRadio div[role="radiogroup"] > label {{
          border-radius: 10px !important;
          border: 1px solid var(--border) !important;
          padding: 0.45rem 0.82rem !important;
          font-weight: 700 !important;
          background: var(--surface-soft) !important;
          min-height: 2.15rem !important;
          display: inline-flex !important;
          align-items: center !important;
          justify-content: center !important;
          transition: all .16s ease;
        }}

        .stRadio div[role="radiogroup"] > label > div:first-child {{
          display: none !important;
        }}

        .stRadio div[role="radiogroup"] > label p,
        .stRadio div[role="radiogroup"] > label span {{
          color: var(--text) !important;
          opacity: 1 !important;
          margin: 0 !important;
        }}

        .stRadio div[role="radiogroup"] > label:has(input:checked) {{
          background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
          border-color: transparent !important;
          box-shadow: 0 8px 20px rgba(79, 70, 229, 0.32);
        }}

        .stRadio div[role="radiogroup"] > label:has(input:checked) p,
        .stRadio div[role="radiogroup"] > label:has(input:checked) span {{
          color: #FFFFFF !important;
        }}

        [data-testid="stWidgetLabel"] p,
        label[data-baseweb="checkbox"] > span {{
          color: var(--text) !important;
          font-weight: 700 !important;
        }}

        label[data-baseweb="checkbox"] > div:first-of-type {{
          background: #CBD5E1 !important;
          border: 1px solid var(--border) !important;
        }}

        label[data-baseweb="checkbox"] input:checked + div {{
          background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
          border-color: transparent !important;
        }}

        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] {{
          background: var(--input-bg) !important;
          border: 1px solid var(--input-border) !important;
          border-radius: 10px !important;
        }}

        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea {{
          background: var(--input-bg) !important;
          color: var(--input-text) !important;
          -webkit-text-fill-color: var(--input-text) !important;
        }}

        [data-baseweb="input"] input::placeholder,
        [data-baseweb="textarea"] textarea::placeholder {{
          color: #94A3B8 !important;
          opacity: 1 !important;
        }}

        [data-baseweb="input"] > div:focus-within,
        [data-baseweb="textarea"]:focus-within {{
          border-color: var(--accent) !important;
          box-shadow: 0 0 0 0.14rem rgba(59, 130, 246, 0.16);
        }}

        .stFileUploader > div > div {{
          background: var(--file-bg);
          border: 1px dashed var(--border);
          border-radius: 14px;
          padding: 0.9rem;
        }}

        .stFileUploader [data-testid="stFileUploaderDropzone"] {{
          background: var(--file-bg) !important;
          border: 2px dashed #64748B !important;
          border-radius: 14px !important;
          min-height: 158px;
        }}

        .stFileUploader [data-testid="stFileUploaderDropzone"] * {{
          color: var(--file-text) !important;
        }}

        .stFileUploader [data-testid="stFileUploaderDropzone"] button {{
          border-radius: 9px !important;
          border: none !important;
          color: #FFFFFF !important;
          background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
          font-weight: 700 !important;
        }}

        .stFileUploader [data-testid="stFileUploaderFile"] {{
          background: var(--file-bg) !important;
          border: 1px solid var(--border) !important;
          border-radius: 12px !important;
        }}

        .stFileUploader [data-testid="stFileUploaderFileName"] {{
          color: var(--file-text) !important;
          font-weight: 700 !important;
        }}

        .stFileUploader [data-testid="stFileUploaderFileSize"] {{
          color: #475569 !important;
        }}

        .stFileUploader [data-testid="stFileUploaderFile"] *,
        .stFileUploader [data-testid="stFileUploaderFile"] small,
        .stFileUploader [data-testid="stFileUploaderFile"] span,
        .stFileUploader [data-testid="stFileUploaderFile"] p {{
          color: var(--file-text) !important;
          opacity: 1 !important;
        }}

        .stFileUploader [data-testid="stFileUploaderFileSize"] {{
          color: var(--muted) !important;
          font-weight: 600 !important;
        }}

        .stButton > button {{
          width: 100%;
          min-height: 2.65rem;
          border-radius: 11px;
          border: 1px solid var(--border);
          background: var(--surface-soft);
          color: var(--text);
          font-weight: 700;
        }}

        .stButton > button[kind="primary"] {{
          border: none;
          background: linear-gradient(90deg, var(--accent), var(--accent2));
          color: #FFFFFF;
        }}

        .stDownloadButton > button,
        [data-testid="stDownloadButton"] button {{
          border: none !important;
          border-radius: 11px !important;
          background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
          color: #FFFFFF !important;
          font-weight: 800 !important;
        }}

        .stMetric {{
          border: 1px solid var(--border);
          border-radius: 12px;
          background: var(--surface-soft);
          padding: 0.75rem 0.8rem;
        }}

        .stMetric * {{
          opacity: 1 !important;
        }}

        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] *,
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] *,
        [data-testid="stMetricDelta"],
        [data-testid="stMetricDelta"] * {{
          color: var(--text) !important;
          -webkit-text-fill-color: var(--text) !important;
        }}

        [data-testid="stMetricLabel"] {{
          color: var(--muted) !important;
          font-weight: 700 !important;
        }}

        [data-testid="stMetricValue"] {{
          font-weight: 800 !important;
        }}

        .stProgress > div > div > div > div {{
          background: linear-gradient(90deg, var(--accent), var(--accent2));
        }}

        [data-testid="stDataFrame"] {{
          border: 1px solid var(--border);
          border-radius: 12px;
          overflow: hidden;
        }}

        .mini-grid {{
          display: grid;
          grid-template-columns: repeat(4, minmax(130px, 1fr));
          gap: 0.62rem;
          margin-top: 0.2rem;
        }}

        .mini-box {{
          background: var(--surface-soft);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 0.72rem;
        }}

        .mini-k {{
          margin: 0;
          font-size: 0.75rem;
          color: var(--muted);
          font-weight: 700;
        }}

        .mini-v {{
          margin: 0.14rem 0 0 0;
          font-size: 0.96rem;
          color: var(--text);
          font-weight: 800;
        }}

        .smart-box {{
          width: 100%;
          background: var(--surface-soft);
          border: 1px solid var(--border);
          border-radius: 12px;
          padding: 0.85rem;
          margin-top: 0.3rem;
          margin-bottom: 0.7rem;
        }}

        .smart-title {{
          margin: 0 0 0.42rem 0;
          color: var(--accent);
          font-size: 0.88rem;
          font-weight: 800;
        }}

        .smart-content {{
          color: var(--text);
          font-size: 0.9rem;
          line-height: 1.55;
          white-space: pre-wrap;
          word-break: break-word;
          overflow-x: hidden;
        }}

        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary *,
        [data-testid="stExpanderDetails"] *,
        [data-testid="stAlert"] * {{
          color: var(--text) !important;
        }}

        @media (max-width: 980px) {{
          .mast {{
            flex-direction: column;
            align-items: flex-start;
          }}
          .hero-top {{
            flex-direction: column;
            align-items: flex-start;
          }}
          .hero-grid {{
            grid-template-columns: 1fr;
          }}
          .feature-card {{
            min-height: 88px;
          }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _build_matcher(jd_text: str):
    if not jd_text.strip():
        return "", None
    clean_jd_local = clean_text(jd_text)
    if not clean_jd_local:
        return "", None
    model = ATSMatcher()
    model.fit(clean_jd_local)
    return clean_jd_local, model


def _require_model(matcher_obj) -> bool:
    if matcher_obj is None:
        st.warning("Please paste a valid Job Description first to run ATS scoring.")
        return False
    return True


def _render_smart_box(title: str, content: str):
    safe = html.escape(content or "").replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="smart-box">
          <p class="smart-title">{html.escape(title)}</p>
          <div class="smart-content">{safe}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_hero():
    st.markdown(
        """
        <div class="hero">
          <div class="hero-top">
            <div>
              <h1 class="brand-title">Screen Smarter. Hire Better.</h1>
              <p class="brand-sub">Powered by all-MiniLM-L6-v2 · Presidio PII Shield · spaCy NER</p>
            </div>
          </div>
          <div class="hero-pills">
            <span class="hero-pill">🤖 Semantic AI</span>
            <span class="hero-pill">🛡️ Privacy-First</span>
            <span class="hero-pill">✅ GitHub Verified</span>
            <span class="hero-pill">⚡ 100% Offline</span>
          </div>
          <div class="hero-grid">
            <div class="feature-card">
              <p class="stat-val">35</p>
              <p class="stat-label">Resumes Tested</p>
            </div>
            <div class="feature-card">
              <p class="stat-val">68.3s</p>
              <p class="stat-label">Bulk Scan Time</p>
            </div>
            <div class="feature-card">
              <p class="stat-val">7</p>
              <p class="stat-label">AI Processing Phases</p>
            </div>
            <div class="feature-card">
              <p class="stat-val">0</p>
              <p class="stat-label">Cloud API Calls</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


theme = _theme()
_inject_css(theme)

st.markdown(
    """
    <div class="mast">
      <div>
        <p class="mast-title">ATS Nexus</p>
        <p class="mast-sub">High-performance AI applicant tracking dashboard.</p>
      </div>
      <div class="mast-badges">
        <span class="mast-badge" style="border-color:var(--accent); color:var(--accent);">🟢 System Online</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_col, toggle_col = st.columns([0.9, 0.1], gap="small")
with nav_col:
    nav = st.radio(
        "Navigation",
        ["🏠 Dashboard", "🔍 Single Resume", "📊 Bulk Analysis", "🎥 Video Resume", "✏️ Resume Builder"],
        horizontal=True,
        label_visibility="collapsed",
    )
with toggle_col:
    st.empty()

if nav == "🏠 Dashboard":
    _render_hero()

job_description = ""
clean_jd, matcher = "", None
if nav != "🏠 Dashboard":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("<p class='section-head'>🎯 Target Job Description</p>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-sub'>Paste a detailed JD here. The more context you provide, the more accurate the ATS semantic embeddings will be.</p>",
        unsafe_allow_html=True,
    )
    job_description = st.text_area(
        "Job Description",
        label_visibility="collapsed",
        key="jd_main",
        placeholder="Paste job description (required for scoring)...",
        height=180,
    )
    if job_description.strip():
        st.markdown("<div style='margin-top:0.5rem; color:var(--success); font-size:0.85rem; font-weight:700;'>✅ Job Description Loaded & Vectorized</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    clean_jd, matcher = _build_matcher(job_description)


if nav == "🏠 Dashboard":
    pass

elif nav == "🔍 Single Resume":
    if not _require_model(matcher):
        st.stop()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("<p class='section-head'>Single Resume Screening</p>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-sub'>Upload one PDF resume and review ATS score, confidence, and matched/missing skills.</p>",
        unsafe_allow_html=True,
    )

    c_up1, c_up2 = st.columns([3, 1])
    with c_up1:
        uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="single_pdf")
    with c_up2:
        st.markdown("<br>", unsafe_allow_html=True)
        blind_mode = st.toggle("Enable Blind Screening Mode", key="single_blind")
        if blind_mode:
            st.warning("Blind Mode removes names and contact info, but cannot guarantee 100% removal of identifying context.")

    if uploaded_resume:
        raw_text = safe_extract_text(uploaded_resume)
        if blind_mode and raw_text:
            raw_text = scrub_pii(raw_text)
        if raw_text is None:
            st.error("Could not parse this PDF. Please try another file.")
        elif not raw_text.strip():
            st.warning("No readable text found in the uploaded PDF.")
        else:
            resume_clean = clean_text(raw_text)
            with st.spinner("⚙️ ATS Nexus is computing semantic, hard, and soft skill vectors..."):
                prediction = matcher.predict_match(resume_clean)
                skills = get_skill_match_details(job_description, raw_text)
                
                # Phase 2: Compute overall score
                prediction.hard_skills_score = skills.get("hard_score", 0.0)
                prediction.soft_skills_score = skills.get("soft_score", 0.0)
                prediction.overall_score = round((0.50 * prediction.semantic_score) + (0.35 * prediction.hard_skills_score) + (0.15 * prediction.soft_skills_score), 2)
                prediction.label = "Matched" if prediction.overall_score >= 50 else "Not Matched"

            st.markdown("#### ATS Verdict")
            banner_color = "var(--success)" if prediction.overall_score >= 50 else "var(--danger)"
            banner_bg = "rgba(16, 185, 129, 0.1)" if prediction.overall_score >= 50 else "rgba(239, 68, 68, 0.1)"
            
            st.markdown(
                f"""
                <div style="border: 1px solid {banner_color}; background: {banner_bg}; border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1.5rem;">
                    <p style="margin:0; color:{banner_color}; font-size:1.1rem; font-weight:800; text-transform:uppercase; letter-spacing:1px;">{prediction.label}</p>
                    <p style="margin:0; font-size:4.5rem; font-weight:800; color:var(--text); line-height:1.2;">{prediction.overall_score}%</p>
                    <p style="margin:0; color:var(--muted); font-size:0.95rem; font-weight:600;">Overall Tripartite Match Score</p>
                </div>
                """, unsafe_allow_html=True
            )

            st.markdown("#### Score Breakdown")
            st.markdown(
                f"""
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem;">
                    <div style="background:var(--surface-soft); border:1px solid var(--border); border-radius:12px; padding:1.2rem; text-align:center;">
                        <p style="margin:0; color:var(--accent); font-size:2.2rem; font-weight:800;">{prediction.semantic_score}%</p>
                        <p style="margin:0.2rem 0 0 0; color:var(--muted); font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Semantic Fit (50%)</p>
                    </div>
                    <div style="background:var(--surface-soft); border:1px solid var(--border); border-radius:12px; padding:1.2rem; text-align:center;">
                        <p style="margin:0; color:var(--accent2); font-size:2.2rem; font-weight:800;">{prediction.hard_skills_score}%</p>
                        <p style="margin:0.2rem 0 0 0; color:var(--muted); font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Hard Skills (35%)</p>
                    </div>
                    <div style="background:var(--surface-soft); border:1px solid var(--border); border-radius:12px; padding:1.2rem; text-align:center;">
                        <p style="margin:0; color:var(--success); font-size:2.2rem; font-weight:800;">{prediction.soft_skills_score}%</p>
                        <p style="margin:0.2rem 0 0 0; color:var(--muted); font-size:0.85rem; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Soft Skills (15%)</p>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

            def _render_chips(items, color_var):
                if not items: return "<span style='color:var(--muted);font-size:0.85rem;'>None</span>"
                return "".join([f'<span style="display:inline-block; border:1px solid {color_var}; color:{color_var}; background:rgba(255,255,255,0.05); border-radius:999px; padding:0.25rem 0.75rem; font-size:0.75rem; font-weight:600; margin:0.2rem;">{html.escape(str(x))}</span>' for x in items])

            st.markdown("#### Skills Analysis")
            st.markdown(f"<div style='margin-bottom:0.5rem;'><strong>✅ Matched Skills:</strong><br>{_render_chips(skills['matched_skills'], 'var(--success)')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='margin-bottom:1.5rem;'><strong>❌ Missing Skills:</strong><br>{_render_chips(skills['missing_skills'], 'var(--danger)')}</div>", unsafe_allow_html=True)
            
            # Phase 5: GitHub Verification
            gh_username = extract_github_username(raw_text)
            if gh_username:
                gh_langs = fetch_github_languages(gh_username)
                if gh_langs:
                    st.success(f"✅ **GitHub Verified ({gh_username}):** Found active repositories using **{', '.join(gh_langs).title()}**")
                    
                    # If github languages match any missing skills, we can conceptually rescue them!
                    rescued = [lang for lang in gh_langs if lang in skills['missing_skills']]
                    if rescued:
                        st.info(f"💡 GitHub rescued missing skills: {', '.join(rescued).title()}! (Score bumped slightly)")
                        prediction.overall_score = min(prediction.overall_score + 5.0, 100.0)
                else:
                    st.warning(f"⚠️ **GitHub Link Found ({gh_username})**, but no public repositories or languages were detected.")
            
            if skills.get('organizations'):
                st.write(f"**Recognized Orgs:** {', '.join(skills['organizations'][:8])}")
            if skills.get('dates'):
                st.write(f"**Recognized Timelines:** {', '.join(skills['dates'][:8])}")
                
                # Phase 4: Experience Match heuristic
                est_years = estimate_years_of_experience(skills['dates'])
                if est_years > 0:
                    st.write(f"**Experience Match:** ~{est_years} years (Estimate from recognized dates)")

            with st.expander("Extracted Resume Text"):
                st.write(raw_text[:10000])

    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "📊 Bulk Analysis":
    if not _require_model(matcher):
        st.stop()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("<p class='section-head'>Bulk Resume Screening</p>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-sub'>Upload multiple resumes, then review ranking, score graph, and score-confidence heatmap.</p>",
        unsafe_allow_html=True,
    )

    c_bulk1, c_bulk2 = st.columns([3, 1])
    with c_bulk1:
        uploaded_bulk = st.file_uploader(
            "Upload Multiple Resumes (PDF)",
            type=["pdf"],
            accept_multiple_files=True,
            key="bulk_pdf",
        )
    with c_bulk2:
        st.markdown("<br>", unsafe_allow_html=True)
        blind_mode_bulk = st.toggle("Enable Blind Screening Mode", key="bulk_blind")
        if blind_mode_bulk:
            st.warning("Blind Mode removes names and contact info, but cannot guarantee 100% removal of identifying context.")

    if uploaded_bulk:
        results = []
        progress = st.progress(0.0)
        total = len(uploaded_bulk)

        for idx, file in enumerate(uploaded_bulk, start=1):
            raw_text = safe_extract_text(file)
            if blind_mode_bulk and raw_text:
                raw_text = scrub_pii(raw_text)
                
            if raw_text is None or not raw_text.strip():
                results.append(
                    {
                        "Resume": file.name,
                        "ATS Score (%)": 0.0,
                        "Semantic (%)": 0.0,
                        "Hard Skills (%)": 0.0,
                        "Soft Skills (%)": 0.0,
                        "Prediction": "Parsing Failed",
                        "Matched Skills": "",
                        "Missing Skills": "",
                    }
                )
            else:
                resume_clean = clean_text(raw_text)
                prediction = matcher.predict_match(resume_clean)
                skills = get_skill_match_details(job_description, raw_text)
                
                # Phase 2 Scoring
                prediction.hard_skills_score = skills.get("hard_score", 0.0)
                prediction.soft_skills_score = skills.get("soft_score", 0.0)
                prediction.overall_score = round((0.50 * prediction.semantic_score) + (0.35 * prediction.hard_skills_score) + (0.15 * prediction.soft_skills_score), 2)
                prediction.label = "Matched" if prediction.overall_score >= 50 else "Not Matched"

                results.append(
                    {
                        "Resume": file.name,
                        "ATS Score (%)": prediction.overall_score,
                        "Semantic (%)": prediction.semantic_score,
                        "Hard Skills (%)": prediction.hard_skills_score,
                        "Soft Skills (%)": prediction.soft_skills_score,
                        "Prediction": prediction.label,
                        "Matched Skills": ", ".join(skills["matched_skills"]),
                        "Missing Skills": ", ".join(skills["missing_skills"]),
                    }
                )
            progress.progress(idx / total)

        df = pd.DataFrame(results).sort_values(by="ATS Score (%)", ascending=False).reset_index(drop=True)
        st.session_state["bulk_results_df"] = df

        st.markdown("#### 🏆 Top Candidates Podium")
        if len(df) >= 1:
            p1 = f"<div style='background:linear-gradient(145deg, rgba(245, 158, 11, 0.1) 0%, transparent 100%); border:1px solid rgba(245, 158, 11, 0.3); border-radius:12px; padding:1.2rem; text-align:center;'><p style='margin:0; font-size:2.5rem;'>🥇</p><p style='margin:0.5rem 0 0 0; color:var(--text); font-size:1.1rem; font-weight:800;'>{df.iloc[0]['Resume']}</p><p style='margin:0.2rem 0 0 0; color:var(--accent); font-size:1.5rem; font-weight:800;'>{df.iloc[0]['ATS Score (%)']}%</p></div>"
            p2 = f"<div style='background:linear-gradient(145deg, rgba(226, 232, 240, 0.1) 0%, transparent 100%); border:1px solid rgba(226, 232, 240, 0.3); border-radius:12px; padding:1.2rem; text-align:center;'><p style='margin:0; font-size:2.5rem;'>🥈</p><p style='margin:0.5rem 0 0 0; color:var(--text); font-size:1.1rem; font-weight:800;'>{df.iloc[1]['Resume']}</p><p style='margin:0.2rem 0 0 0; color:var(--accent); font-size:1.5rem; font-weight:800;'>{df.iloc[1]['ATS Score (%)']}%</p></div>" if len(df) >= 2 else "<div></div>"
            p3 = f"<div style='background:linear-gradient(145deg, rgba(180, 83, 9, 0.1) 0%, transparent 100%); border:1px solid rgba(180, 83, 9, 0.3); border-radius:12px; padding:1.2rem; text-align:center;'><p style='margin:0; font-size:2.5rem;'>🥉</p><p style='margin:0.5rem 0 0 0; color:var(--text); font-size:1.1rem; font-weight:800;'>{df.iloc[2]['Resume']}</p><p style='margin:0.2rem 0 0 0; color:var(--accent); font-size:1.5rem; font-weight:800;'>{df.iloc[2]['ATS Score (%)']}%</p></div>" if len(df) >= 3 else "<div></div>"
            
            st.markdown(f'<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 2rem;">{p1}{p2}{p3}</div>', unsafe_allow_html=True)

        st.markdown("#### Full Rankings")
        st.dataframe(df, width="stretch")

        graph_df = df.copy()
        graph_df["short_name"] = graph_df["Resume"].apply(lambda x: x if len(x) <= 45 else x[:42] + "...")

        st.markdown("#### ATS Score Graph")
        fig_height = max(6, min(18, 0.5 * len(graph_df)))
        fig1, ax1 = plt.subplots(figsize=(15, fig_height))
        fig1.patch.set_facecolor(theme["surface"])
        ax1.set_facecolor(theme["surface"])
        bars = ax1.barh(graph_df["short_name"], graph_df["ATS Score (%)"], color=theme["accent"], edgecolor=theme["accent2"])
        ax1.set_xlim(0, 100)
        ax1.set_xlabel("ATS Score (%)", color=theme["text"])
        ax1.set_ylabel("Resume", color=theme["text"])
        ax1.tick_params(colors=theme["text"])
        ax1.grid(axis="x", linestyle="--", alpha=0.25, color=theme["border"])
        ax1.invert_yaxis()
        for spine in ax1.spines.values():
            spine.set_color(theme["border"])
        for bar, score in zip(bars, graph_df["ATS Score (%)"]):
            ax1.text(min(score + 1.2, 98), bar.get_y() + bar.get_height() / 2, f"{score:.1f}%", va="center", color=theme["text"], fontsize=9)
        plt.tight_layout()
        st.pyplot(fig1, width="stretch")

        st.markdown("#### ATS Score vs Semantic Fit Heatmap")
        heatmap_values = graph_df[["ATS Score (%)", "Semantic (%)"]].values
        fig2, ax2 = plt.subplots(figsize=(13, fig_height))
        fig2.patch.set_facecolor(theme["surface"])
        ax2.set_facecolor(theme["surface"])
        im = ax2.imshow(heatmap_values, cmap="magma", aspect="auto", vmin=0, vmax=100)
        ax2.set_xticks([0, 1])
        ax2.set_xticklabels(["ATS Score (%)", "Semantic (%)"], color=theme["text"])
        ax2.set_yticks(range(len(graph_df)))
        ax2.set_yticklabels(graph_df["short_name"], color=theme["text"])
        ax2.tick_params(colors=theme["text"])
        for i in range(heatmap_values.shape[0]):
            for j in range(heatmap_values.shape[1]):
                value = float(heatmap_values[i, j])
                color = "#111827" if value < 58 else "#F8FAFC"
                ax2.text(j, i, f"{value:.1f}", ha="center", va="center", color=color, fontsize=9, fontweight="bold")
        cbar = fig2.colorbar(im, ax=ax2, fraction=0.03, pad=0.02)
        cbar.set_label("Percentage", color=theme["text"])
        cbar.ax.yaxis.set_tick_params(color=theme["text"])
        plt.setp(cbar.ax.get_yticklabels(), color=theme["text"])
        plt.tight_layout()
        st.pyplot(fig2, width="stretch")

        st.download_button(
            "Download Results CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="ats_bulk_screening_results.csv",
            mime="text/csv",
        )

    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "🎥 Video Resume":
    if not _require_model(matcher):
        st.stop()

    left, right = st.columns([1.25, 0.75], gap="large")

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("<p class='section-head'>Video Resume Screening</p>", unsafe_allow_html=True)
        st.markdown(
            "<p class='section-sub'>Upload MP4/MOV/AVI/MKV, extract transcript, and compute ATS fit.</p>",
            unsafe_allow_html=True,
        )

        uploaded_video = st.file_uploader("Upload Video Resume", type=["mp4", "mov", "avi", "mkv"], key="video")
        run = st.button("Analyse Video Resume", type="primary")

        if run and uploaded_video:
            with st.spinner("Processing video and transcribing audio..."):
                result = screen_video_resume(uploaded_video.read(), job_description, video_name=uploaded_video.name)

            m1, m2, m3 = st.columns(3)
            m1.metric("Video ATS", f"{result['ats_score']}%")
            m2.metric("Prediction", result["label"])
            m3.metric("Transcript Length", f"{len(result['transcript'].split())} words")
            st.progress(min(max(result["ats_score"] / 100.0, 0.0), 1.0))

            st.write(f"Matched Skills: {', '.join(result['matched_skills']) if result['matched_skills'] else 'None'}")
            st.write(f"Missing Skills: {', '.join(result['missing_skills']) if result['missing_skills'] else 'None'}")
            with st.expander("Transcript"):
                st.write(result["transcript"] if result["transcript"].strip() else "No speech could be transcribed.")

        elif run and not uploaded_video:
            st.warning("Upload a video resume first.")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("<p class='section-head'>What This Analysis Includes</p>", unsafe_allow_html=True)
        st.markdown(
            """
            - Speaking rate metric (Words / clip duration)
            - Transcript relevance to target role
            - Tripartite Semantic Alignment Score (Semantic + Hard + Soft Skills)
            - Matched and missing skill indicators
            - Fully offline privacy-preserving transcription
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

else:
    if not _require_model(matcher):
        st.stop()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("<p class='section-head'>Resume Builder</p>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-sub'>Build your resume, get smart suggestions, and download as PDF/MD/TXT.</p>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 0.75], gap="large")

    with left:
        c1, c2 = st.columns(2)
        name = c1.text_input("Name", placeholder="Ananya Saini")
        email = c2.text_input("Email ID", placeholder="name@email.com")

        c3, c4, c5, c6 = st.columns(4)
        phone = c3.text_input("Phone", placeholder="+91 XXXXX XXXXX")
        location = c4.text_input("Location", placeholder="Dehradun")
        linkedin = c5.text_input("LinkedIn", placeholder="linkedin.com/in/username")
        github = c6.text_input("GitHub", placeholder="github.com/username")

        summary = st.text_area(
            "Professional Summary",
            height=120,
            placeholder="Write a 3-4 line summary aligned to your target role...",
        )
        skills_csv = st.text_area("Skills (comma-separated)", height=90, placeholder="Python, SQL, Machine Learning, Streamlit")
        certifications_csv = st.text_input("Certifications (comma-separated)", placeholder="Certification A, Certification B")

        st.markdown("#### Experience")
        experience_rows = st.data_editor(
            pd.DataFrame([{"Type": "Internship", "Role": "", "Company": "", "Duration": "", "Location": "", "Achievements": ""}]),
            num_rows="dynamic",
            width="stretch",
            key="resume_exp_editor",
        ).to_dict("records")

        st.markdown("#### Projects")
        project_rows = st.data_editor(
            pd.DataFrame([{"Project": "", "Tech": "", "Project Link": "", "Details": ""}]),
            num_rows="dynamic",
            width="stretch",
            key="resume_project_editor",
        ).to_dict("records")

        st.markdown("#### Education")
        education_rows = st.data_editor(
            pd.DataFrame([{"Degree": "", "Institute": "", "Year": "", "Location": "", "CGPA": ""}]),
            num_rows="dynamic",
            width="stretch",
            key="resume_edu_editor",
        ).to_dict("records")

    resume_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "portfolio": github,
        "summary": summary,
        "skills_csv": skills_csv,
        "certifications_csv": certifications_csv,
        "experience_rows": experience_rows,
        "project_rows": project_rows,
        "education_rows": education_rows,
    }

    resume_markdown = build_resume_markdown(resume_data)
    resume_scoring_text = build_resume_scoring_text(resume_data)
    resume_pdf = build_resume_pdf_bytes(resume_data)
    feedback = get_resume_builder_feedback(resume_scoring_text, matcher, job_description)

    with right:
        st.markdown("#### Smart Builder Suggestions")
        smart = generate_smart_builder_suggestions(resume_data, job_description)

        st.markdown("**Keyword Analysis**")
        st.markdown(f"- JD Technical Skills: {', '.join(smart['jd_technical_skills']) if smart['jd_technical_skills'] else 'None'}")
        st.markdown(f"- JD Soft Skills: {', '.join(smart['jd_soft_skills']) if smart['jd_soft_skills'] else 'None'}")
        st.markdown(f"- Matched Skills: {', '.join(smart['matched_skills']) if smart['matched_skills'] else 'None'}")

        st.markdown("**Key Skills to Add**")
        _render_smart_box(
            "Key Skills to Add",
            ", ".join(smart["recommended_skills"]) if smart["recommended_skills"] else "No major gaps detected.",
        )

        st.markdown("**Suggested Summary**")
        _render_smart_box("Suggested Summary", smart["suggested_summary"])

        st.markdown("**STAR Experience Rewrite (Copy into Experience)**")
        _render_smart_box("STAR Rewrite", smart["star_experience_rewrite"])

        st.markdown("#### ATS Fit")
        st.markdown("#### ATS Fit")
        c_fit1, c_fit2 = st.columns([1, 2])
        c_fit1.metric("Score", f"{feedback['score']}%")
        c_fit1.metric("Prediction", feedback["label"])
        
        with c_fit2:
            import plotly.express as px
            df_polar = pd.DataFrame(dict(
                r=[feedback["semantic_score"], feedback["hard_skills_score"], feedback["soft_skills_score"]],
                theta=['Semantic Fit', 'Hard Skills', 'Soft Skills']
            ))
            fig = px.line_polar(df_polar, r='r', theta='theta', line_close=True, range_r=[0,100], color_discrete_sequence=['#06B6D4'])
            fig.update_traces(fill='toself')
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=250)
            st.plotly_chart(fig, width="stretch")

        st.write(f"**Matched Skills:** {', '.join(feedback['matched_skills']) if feedback['matched_skills'] else 'None'}")
        st.write(f"**Missing Skills:** {', '.join(feedback['missing_skills']) if feedback['missing_skills'] else 'None'}")
        if feedback.get('organizations'):
            st.write(f"**Recognized Orgs:** {', '.join(feedback['organizations'][:8])}")
        if feedback.get('dates'):
            st.write(f"**Recognized Timelines:** {', '.join(feedback['dates'][:8])}")

        st.markdown("#### Resume Preview")
        st.markdown(resume_markdown)

        st.download_button(
            "Download Resume (.pdf)",
            data=resume_pdf,
            file_name="ats_resume.pdf",
            mime="application/pdf",
            type="primary",
        )
        st.download_button(
            "Download Resume (.md)",
            data=resume_markdown.encode("utf-8"),
            file_name="ats_resume.md",
            mime="text/markdown",
        )
        st.download_button(
            "Download Resume (.txt)",
            data=resume_markdown.encode("utf-8"),
            file_name="ats_resume.txt",
            mime="text/plain",
        )

    st.markdown("</div>", unsafe_allow_html=True)
