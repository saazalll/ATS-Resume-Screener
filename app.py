import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import html

from read_resume import safe_extract_text
from resume_builder import (
    build_resume_markdown,
    build_resume_pdf_bytes,
    build_resume_scoring_text,
    get_resume_builder_feedback,
)
from smart_builder import generate_smart_builder_suggestions
from skill_gap import get_skill_match_details
from svm_model import ATSMatcher
from text_cleaner import clean_text
from video_screening import screen_video_resume


st.set_page_config(page_title="ATS Nexus", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

if "light_mode" not in st.session_state:
    st.session_state.light_mode = False

_top_left, _top_right = st.columns([0.82, 0.18])
with _top_right:
    st.toggle("Light Mode", key="light_mode")

if st.session_state.light_mode:
    # User-provided Light Palette
    # bg: #FFFFFF, text: #1A1A1A, accent: #3B82F6, secondary: #F3F4F6
    theme = {
        "bg": "#FFFFFF",
        "text": "#1A1A1A",
        "accent": "#3B82F6",
        "accent_2": "#2563EB",
        "secondary": "#F3F4F6",
        "muted": "#4B5563",
        "app_bg": "#FFFFFF",
        "sidebar_bg": "#F3F4F6",
        "sidebar_border": "#E5E7EB",
        "sidebar_text": "#1A1A1A",
        "brand_border": "#E5E7EB",
        "brand_bg": "#FFFFFF",
        "brand_sub": "#4B5563",
        "topbar_border": "#E5E7EB",
        "topbar_bg": "#FFFFFF",
        "card_border": "#E5E7EB",
        "card_bg": "#FFFFFF",
        "mini_card_border": "#E5E7EB",
        "mini_card_bg": "#F3F4F6",
        "mini_title": "#1A1A1A",
        "mini_sub": "#4B5563",
        "video_stat_border": "#E5E7EB",
        "video_stat_bg": "#F3F4F6",
        "video_label": "#4B5563",
        "video_value": "#1A1A1A",
        "section_head": "#1A1A1A",
        "section_sub": "#4B5563",
        "radio_bg": "#F3F4F6",
        "radio_border": "#D1D5DB",
        "radio_label_bg": "#FFFFFF",
        "radio_label_border": "#D1D5DB",
        "radio_label_text": "#1A1A1A",
        "sidebar_tab_wrap_bg": "#EEF2FF",
        "sidebar_tab_wrap_border": "#D1D5DB",
        "sidebar_tab_bg": "#FFFFFF",
        "sidebar_tab_border": "#D1D5DB",
        "sidebar_tab_text": "#1A1A1A",
        "sidebar_tab_active_border": "#3B82F6",
        "uploader_bg": "#FFFFFF",
        "uploader_border": "#1A1A1A",
        "uploader_text": "#1A1A1A",
        "dropzone_bg": "#FFFFFF",
        "dropzone_border": "#1A1A1A",
        "dropzone_text": "#1A1A1A",
        "uploader_filename_text": "#1A1A1A",
        "uploader_filesub_text": "#4B5563",
        "uploader_delete": "#1A1A1A",
        "uploader_file_bg": "#FFFFFF",
        "uploader_file_border": "#D1D5DB",
        "button_border": "#D1D5DB",
        "button_bg": "#FFFFFF",
        "button_text": "#1A1A1A",
        "input_bg": "#F9FAFB",
        "input_border": "#D1D5DB",
        "input_text": "#111827",
        "input_placeholder": "#9CA3AF",
        "metric_bg": "#F3F4F6",
        "metric_border": "#E5E7EB",
        "df_border": "#E5E7EB",
        "progress_track": "#D1D5DB",
        "alert_text": "#1A1A1A",
        "alert_bg": "#F3F4F6",
        "job_input_bg": "#F9FAFB",
        "job_input_text": "#111827",
        "job_input_border": "#D1D5DB",
        "job_input_placeholder": "#9CA3AF",
    }
else:
    # User-provided Dark Palette
    # bg: #0F172A, text: #F8FAFC, accent: #60A5FA, secondary: #1E293B
    theme = {
        "bg": "#0F172A",
        "text": "#F8FAFC",
        "accent": "#60A5FA",
        "accent_2": "#3B82F6",
        "secondary": "#1E293B",
        "muted": "#CBD5E1",
        "app_bg": "#0F172A",
        "sidebar_bg": "#1E293B",
        "sidebar_border": "#334155",
        "sidebar_text": "#F8FAFC",
        "brand_border": "#334155",
        "brand_bg": "#1E293B",
        "brand_sub": "#CBD5E1",
        "topbar_border": "#334155",
        "topbar_bg": "#1E293B",
        "card_border": "#334155",
        "card_bg": "#1E293B",
        "mini_card_border": "#334155",
        "mini_card_bg": "#0F172A",
        "mini_title": "#F8FAFC",
        "mini_sub": "#CBD5E1",
        "video_stat_border": "#334155",
        "video_stat_bg": "#0F172A",
        "video_label": "#CBD5E1",
        "video_value": "#F8FAFC",
        "section_head": "#F8FAFC",
        "section_sub": "#CBD5E1",
        "radio_bg": "#0F172A",
        "radio_border": "#334155",
        "radio_label_bg": "#1E293B",
        "radio_label_border": "#334155",
        "radio_label_text": "#F8FAFC",
        "sidebar_tab_wrap_bg": "#0F172A",
        "sidebar_tab_wrap_border": "#334155",
        "sidebar_tab_bg": "#1E293B",
        "sidebar_tab_border": "#334155",
        "sidebar_tab_text": "#F8FAFC",
        "sidebar_tab_active_border": "#60A5FA",
        "uploader_bg": "#FFFFFF",
        "uploader_border": "#1A1A1A",
        "uploader_text": "#1A1A1A",
        "dropzone_bg": "#FFFFFF",
        "dropzone_border": "#1A1A1A",
        "dropzone_text": "#1A1A1A",
        "uploader_filename_text": "#1A1A1A",
        "uploader_filesub_text": "#4B5563",
        "uploader_delete": "#1A1A1A",
        "uploader_file_bg": "#FFFFFF",
        "uploader_file_border": "#1A1A1A",
        "button_border": "#334155",
        "button_bg": "#0F172A",
        "button_text": "#F8FAFC",
        "input_bg": "#1E293B",
        "input_border": "#334155",
        "input_text": "#F8FAFC",
        "input_placeholder": "#94A3B8",
        "metric_bg": "#0F172A",
        "metric_border": "#334155",
        "df_border": "#334155",
        "progress_track": "#D1D5DB",
        "alert_text": "#F8FAFC",
        "alert_bg": "#1E293B",
        "job_input_bg": "#1E293B",
        "job_input_text": "#F8FAFC",
        "job_input_border": "#334155",
        "job_input_placeholder": "#94A3B8",
    }

css_template = """
<style>
:root {
  --bg: __BG__;
  --line: __CARD_BORDER__;
  --text: __TEXT__;
  --muted: __MUTED__;
  --accent: __ACCENT__;
  --accent-2: __ACCENT_2__;
  --secondary: __SECONDARY__;
}
.stApp {
  background: __APP_BG__;
  color: var(--text);
}
p, li {
  color: var(--text);
}
[data-testid="stSidebar"] {
  background: __SIDEBAR_BG__;
  border-right: 1px solid __SIDEBAR_BORDER__;
}
[data-testid="stSidebar"] * { color: __SIDEBAR_TEXT__; }
.main .block-container { max-width: 1250px; padding-top: 1.25rem; }
.brand {
  border: 1px solid __BRAND_BORDER__;
  border-radius: 16px;
  background: __BRAND_BG__;
  padding: 14px 14px;
  margin-bottom: 12px;
}
.brand h1 { margin: 0; font-size: 1.8rem; }
.brand p { margin: .15rem 0 0 0; color: __BRAND_SUB__; }
.topbar {
  border: 1px solid __TOPBAR_BORDER__;
  border-radius: 16px;
  background: __TOPBAR_BG__;
  padding: 14px 16px;
  margin-bottom: 16px;
}
.topbar h2 { margin: 0; }
.topbar .main-title { font-family: "Trebuchet MS", "Avenir Next", "Segoe UI", sans-serif; letter-spacing: .2px; }
.app-card {
  border: 1px solid __CARD_BORDER__;
  border-radius: 16px;
  background: __CARD_BG__;
  padding: 18px;
  margin-bottom: 14px;
}
.small-note { color: var(--muted); margin-top: 0; }
.smart-suggestion-box {
  width: 100%;
  background: #1E293B;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 1rem;
  margin-top: 0.35rem;
  margin-bottom: 0.75rem;
}
.smart-suggestion-title {
  color: #93C5FD;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 0.4rem;
}
.smart-suggestion-content {
  color: #F8FAFC;
  font-size: 0.9rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: hidden;
  overflow-y: visible;
}
.mini-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(140px, 1fr));
  gap: 10px;
  margin-top: 4px;
  margin-bottom: 10px;
}
.mini-card {
  border: 1px solid __MINI_CARD_BORDER__;
  border-radius: 10px;
  background: __MINI_CARD_BG__;
  padding: 10px 11px;
}
.mini-title {
  font-size: 0.9rem;
  color: __MINI_TITLE__;
  font-family: "Avenir Next", "Trebuchet MS", "Segoe UI", sans-serif;
  margin: 0;
  line-height: 1.2;
}
.video-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 8px;
}
.video-stat {
  border: 1px solid __VIDEO_STAT_BORDER__;
  border-radius: 10px;
  background: __VIDEO_STAT_BG__;
  padding: 9px 10px;
}
.video-stat-label {
  margin: 0;
  font-size: 0.73rem;
  color: __VIDEO_LABEL__;
  font-family: "Avenir Next", "Trebuchet MS", "Segoe UI", sans-serif;
}
.video-stat-value {
  margin: 2px 0 0 0;
  font-size: 1.02rem;
  color: __VIDEO_VALUE__;
  font-weight: 700;
  font-family: "Avenir Next", "Trebuchet MS", "Segoe UI", sans-serif;
  line-height: 1.2;
}
.mini-sub {
  margin: 3px 0 0 0;
  font-size: 0.74rem;
  color: __MINI_SUB__;
  font-family: "Avenir Next", "Trebuchet MS", "Segoe UI", sans-serif;
  line-height: 1.2;
}
.section-head {
  font-family: "Avenir Next", "Trebuchet MS", "Segoe UI", sans-serif;
  color: __SECTION_HEAD__;
  letter-spacing: .2px;
  margin-bottom: .15rem;
  font-size: 1.28rem;
}
.section-sub {
  font-family: "Avenir Next", "Trebuchet MS", "Segoe UI", sans-serif;
  color: __SECTION_SUB__;
  margin-top: 0;
  margin-bottom: .65rem;
  font-size: .87rem;
}
.stRadio > div {
  background: __RADIO_BG__;
  border: 1px solid __RADIO_BORDER__;
  border-radius: 12px;
  padding: 0.35rem;
}
.stRadio label {
  background: __RADIO_LABEL_BG__;
  border: 1px solid __RADIO_LABEL_BORDER__;
  border-radius: 10px;
  color: __RADIO_LABEL_TEXT__;
  padding: .5rem .65rem;
  margin-bottom: .3rem;
}
.stRadio label:has(input:checked) {
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  color: #fff;
  border-color: transparent;
}
[data-testid="stSidebar"] .stRadio > div {
  background: __SIDEBAR_TAB_WRAP_BG__ !important;
  border: 1px solid __SIDEBAR_TAB_WRAP_BORDER__ !important;
}
[data-testid="stSidebar"] .stRadio label {
  background: __SIDEBAR_TAB_BG__ !important;
  border: 1px solid __SIDEBAR_TAB_BORDER__ !important;
  color: __SIDEBAR_TAB_TEXT__ !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
  background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
  color: #ffffff !important;
  border-color: __SIDEBAR_TAB_ACTIVE_BORDER__ !important;
}
.stFileUploader > div > div {
  background: __UPLOADER_BG__;
  border: 1px dashed __UPLOADER_BORDER__;
  border-radius: 14px;
  padding: 1.1rem;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] {
  background: __DROPZONE_BG__ !important;
  border: 2px dashed __DROPZONE_BORDER__ !important;
  border-radius: 14px !important;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] * {
  color: __DROPZONE_TEXT__ !important;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] button {
  background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  padding: 0.35rem 0.75rem !important;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] button:hover,
.stFileUploader [data-testid="stFileUploaderDropzone"] button:active {
  filter: brightness(0.96) !important;
}
.stFileUploader [data-testid="stFileUploaderFileName"],
.stFileUploader [data-testid="stFileUploaderDropzoneInstructions"],
.stFileUploader small,
.stFileUploader span,
.stFileUploader p {
  color: __UPLOADER_TEXT__ !important;
}
.stFileUploader button {
  color: __UPLOADER_TEXT__ !important;
}
.stFileUploader [data-testid="stFileUploaderFile"] {
  background: __UPLOADER_FILE_BG__ !important;
  border: 1px solid __UPLOADER_FILE_BORDER__ !important;
  border-radius: 10px !important;
  padding: 10px 12px !important;
}
.stFileUploader [data-testid="stFileUploaderFileName"] {
  color: __UPLOADER_FILENAME_TEXT__ !important;
  font-weight: 600 !important;
}
.stFileUploader [data-testid="stFileUploaderFileSize"],
.stFileUploader [data-testid="stFileUploaderFile"] small,
.stFileUploader [data-testid="stFileUploaderFile"] span,
.stFileUploader [data-testid="stFileUploaderFile"] div {
  color: __UPLOADER_FILESUB_TEXT__ !important;
}
/* Uploaded-file remove button: plain white X on transparent background */
.stFileUploader [data-testid="stFileUploaderFile"] button,
.stFileUploader [data-testid="stFileUploaderDeleteBtn"] {
  color: __UPLOADER_DELETE__ !important;
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  width: 26px !important;
  height: 26px !important;
  min-width: 26px !important;
  min-height: 26px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-shadow: none !important;
  padding: 0 !important;
  position: relative !important;
}
.stFileUploader [data-testid="stFileUploaderFile"] button svg,
.stFileUploader [data-testid="stFileUploaderFile"] button path,
.stFileUploader [data-testid="stFileUploaderDeleteBtn"] svg,
.stFileUploader [data-testid="stFileUploaderDeleteBtn"] path {
  opacity: 0 !important;
  fill: transparent !important;
  stroke: transparent !important;
}
.stFileUploader [data-testid="stFileUploaderFile"] button::before,
.stFileUploader [data-testid="stFileUploaderDeleteBtn"]::before {
  content: "×";
  color: __UPLOADER_DELETE__ !important;
  font-size: 28px !important;
  font-weight: 500 !important;
  line-height: 1 !important;
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -56%) !important;
}
.stFileUploader [data-testid="stFileUploaderFile"] button:hover,
.stFileUploader [data-testid="stFileUploaderFile"] button:active,
.stFileUploader [data-testid="stFileUploaderDeleteBtn"]:hover,
.stFileUploader [data-testid="stFileUploaderDeleteBtn"]:active {
  background: transparent !important;
  opacity: 0.82 !important;
}
/* Progress bar styling inside uploaded row */
.stFileUploader [role="progressbar"] {
  background: __PROGRESS_TRACK__ !important;
  border-radius: 999px !important;
  height: 14px !important;
}
.stFileUploader [role="progressbar"] > div {
  background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
  border-radius: 999px !important;
}
[data-baseweb="input"] > div,
[data-baseweb="textarea"] {
  background: __INPUT_BG__ !important;
  border: 1px solid __INPUT_BORDER__ !important;
  border-radius: 10px !important;
}
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background: __INPUT_BG__ !important;
  color: __INPUT_TEXT__ !important;
  -webkit-text-fill-color: __INPUT_TEXT__ !important;
}
[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder {
  color: __INPUT_PLACEHOLDER__ !important;
  opacity: 1 !important;
}
[data-testid="stSidebar"] div[data-baseweb="textarea"] {
  border: 1px solid __JOB_INPUT_BORDER__ !important;
  border-radius: 10px !important;
  background: __JOB_INPUT_BG__ !important;
}
[data-testid="stSidebar"] div[data-baseweb="textarea"] textarea {
  background: __JOB_INPUT_BG__ !important;
  color: __JOB_INPUT_TEXT__ !important;
  -webkit-text-fill-color: __JOB_INPUT_TEXT__ !important;
}
[data-testid="stSidebar"] div[data-baseweb="textarea"] textarea::placeholder {
  color: __JOB_INPUT_PLACEHOLDER__ !important;
}
.stButton > button {
  width: 100%;
  border: 1px solid __BUTTON_BORDER__;
  border-radius: 10px;
  background: __BUTTON_BG__;
  color: __BUTTON_TEXT__;
  font-weight: 700;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  border: none;
}
.stDownloadButton > button,
[data-testid="stDownloadButton"] button {
  background: linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}
.stDownloadButton > button:hover,
.stDownloadButton > button:active,
[data-testid="stDownloadButton"] button:hover,
[data-testid="stDownloadButton"] button:active {
  filter: brightness(0.96) !important;
}
.stMetric {
  border: 1px solid __METRIC_BORDER__;
  border-radius: 12px;
  background: __METRIC_BG__;
  padding: .75rem .9rem;
}
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
}
[data-testid="stDataFrame"] {
  border: 1px solid __DF_BORDER__;
  border-radius: 12px;
}
[data-testid="stAlert"] {
  background: __ALERT_BG__;
}
[data-testid="stAlert"] * {
  color: __ALERT_TEXT__ !important;
}
</style>
"""

css = css_template
for key, value in theme.items():
    css = css.replace(f"__{key.upper()}__", value)

st.markdown(css, unsafe_allow_html=True)


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
          <h1>⚡ ATS Nexus</h1>
          <p>AI Hiring Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    nav = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Single Resume",
            "Bulk Analysis",
            "Video Resume",
            "Resume Builder",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    job_description = st.text_area(
        "Target Job Description",
        key="sidebar_job_description",
        height=210,
        placeholder="Paste job description here for ATS scoring...",
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


clean_jd, matcher = _build_matcher(job_description)


def _require_model():
    if matcher is None:
        st.warning("Add a valid Job Description in the left panel to run ATS scoring.")
        return False
    return True


def _render_smart_suggestion_box(title: str, content: str):
    safe = html.escape(content or "").replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="smart-suggestion-box">
          <div class="smart-suggestion-title">{html.escape(title)}</div>
          <div class="smart-suggestion-content">{safe}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    f"""
    <div class="topbar">
      <h2 class="main-title">AI-Based ATS Resume Screening System</h2>
    </div>
    """,
    unsafe_allow_html=True,
)


if nav == "Dashboard":
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.write(
        """
        This platform helps recruiters and students quickly evaluate resume relevance against a target job description.
        It uses NLP preprocessing, TF-IDF feature extraction, and an SVM model to produce ATS score, prediction confidence,
        and skill-gap insights.
        """
    )

    st.markdown("#### What You Can Do")
    st.markdown(
        """
        <div class="mini-grid">
          <div class="mini-card"><p class="mini-title">Single Resume</p><p class="mini-sub">PDF Screening</p></div>
          <div class="mini-card"><p class="mini-title">Bulk Analysis</p><p class="mini-sub">100+ Resumes</p></div>
          <div class="mini-card"><p class="mini-title">Video Resume</p><p class="mini-sub">Speech + ATS</p></div>
          <div class="mini-card"><p class="mini-title">Resume Builder</p><p class="mini-sub">ATS-Ready PDF</p></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How To Use This Website")
    st.markdown(
        """
        1. Paste the **Job Description** in the left sidebar (required for all ATS scoring).
        2. Go to **Single Resume** to upload one PDF and view ATS score, confidence, and matched/missing skills.
        3. Go to **Bulk Analysis** to upload multiple PDFs, rank candidates, and view score heatmaps.
        4. Go to **Video Resume** to upload a video CV and evaluate transcript-based ATS fit.
        5. Go to **Resume Builder** to create a resume from scratch and download it as **PDF/MD/TXT**.
        """
    )

    st.markdown("#### Tips For Better Results")
    st.markdown(
        """
        - Use text-based PDFs (not scanned images) for better extraction.
        - Keep the job description specific (skills, responsibilities, tools).
        - Include project impact, metrics, and role-specific keywords in resumes.
        - For video screening, use clear voice audio and minimal background noise.
        """
    )

    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Single Resume":
    if not _require_model():
        st.stop()

    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-head'>Single Resume Screening</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-sub'>Upload one PDF resume and get ATS score, confidence, and skill-gap analysis.</p>",
        unsafe_allow_html=True,
    )

    uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="single_pdf")
    if uploaded_resume:
        raw_text = safe_extract_text(uploaded_resume)
        if raw_text is None:
            st.error("Could not parse this PDF. Please try another file.")
        elif not raw_text.strip():
            st.warning("No readable text found in the uploaded PDF.")
        else:
            resume_clean = clean_text(raw_text)
            prediction = matcher.predict_match(resume_clean)
            skills = get_skill_match_details(clean_jd, resume_clean)

            c1, c2, c3 = st.columns(3)
            c1.metric("ATS Score", f"{prediction.score_percent}%")
            c2.metric("Confidence", f"{prediction.confidence_percent}%")
            c3.metric("Prediction", prediction.label)
            st.progress(min(max(prediction.score_percent / 100.0, 0.0), 1.0))

            st.write(f"Matched Skills: {', '.join(skills['matched_skills']) if skills['matched_skills'] else 'None'}")
            st.write(f"Missing Skills: {', '.join(skills['missing_skills']) if skills['missing_skills'] else 'None'}")

            with st.expander("Extracted Resume Text"):
                st.write(raw_text[:10000])

    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Bulk Analysis":
    if not _require_model():
        st.stop()

    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-head'>Bulk Resume Screening</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-sub'>Upload multiple PDF resumes and visualize ATS score + confidence insights.</p>",
        unsafe_allow_html=True,
    )

    uploaded_bulk = st.file_uploader(
        "Upload Multiple Resumes (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
        key="bulk_pdf",
    )

    if uploaded_bulk:
        results = []
        progress = st.progress(0.0)
        total = len(uploaded_bulk)

        for idx, file in enumerate(uploaded_bulk, start=1):
            raw_text = safe_extract_text(file)
            if raw_text is None or not raw_text.strip():
                results.append(
                    {
                        "Resume": file.name,
                        "ATS Score (%)": 0.0,
                        "Confidence (%)": 0.0,
                        "Prediction": "Parsing Failed",
                        "Matched Skills": "",
                        "Missing Skills": "",
                    }
                )
            else:
                resume_clean = clean_text(raw_text)
                prediction = matcher.predict_match(resume_clean)
                skills = get_skill_match_details(clean_jd, resume_clean)
                results.append(
                    {
                        "Resume": file.name,
                        "ATS Score (%)": prediction.score_percent,
                        "Confidence (%)": prediction.confidence_percent,
                        "Prediction": prediction.label,
                        "Matched Skills": ", ".join(skills["matched_skills"]),
                        "Missing Skills": ", ".join(skills["missing_skills"]),
                    }
                )
            progress.progress(idx / total)

        df = pd.DataFrame(results).sort_values(by="ATS Score (%)", ascending=False).reset_index(drop=True)
        st.session_state["bulk_results_df"] = df

        st.dataframe(df, use_container_width=True)

        graph_df = df.copy()
        graph_df["short_name"] = graph_df["Resume"].apply(lambda x: x if len(x) <= 40 else x[:37] + "...")

        st.markdown("#### ATS Score Graph")
        fig_height = max(6, min(18, 0.52 * len(graph_df)))
        chart_bg = theme["card_bg"]
        chart_text = theme["text"]
        chart_grid = theme["card_border"]
        bar_color = theme["accent"]
        bar_edge = theme["accent_2"]
        fig1, ax1 = plt.subplots(figsize=(14, fig_height))
        fig1.patch.set_facecolor(chart_bg)
        ax1.set_facecolor(chart_bg)
        bars = ax1.barh(graph_df["short_name"], graph_df["ATS Score (%)"], color=bar_color, edgecolor=bar_edge)
        ax1.set_xlim(0, 100)
        ax1.set_xlabel("ATS Score (%)", color=chart_text)
        ax1.set_ylabel("Resume", color=chart_text)
        ax1.tick_params(colors=chart_text)
        ax1.grid(axis="x", linestyle="--", alpha=0.25, color=chart_grid)
        ax1.invert_yaxis()
        for spine in ax1.spines.values():
            spine.set_color(chart_grid)
        for bar, score in zip(bars, graph_df["ATS Score (%)"]):
            ax1.text(min(score + 1.2, 98), bar.get_y() + bar.get_height() / 2, f"{score:.1f}%", va="center", color=chart_text, fontsize=9)
        plt.tight_layout()
        st.pyplot(fig1, use_container_width=True)

        st.markdown("#### Score vs Confidence Heatmap")
        heatmap_values = graph_df[["ATS Score (%)", "Confidence (%)"]].values
        fig2, ax2 = plt.subplots(figsize=(12, fig_height))
        fig2.patch.set_facecolor(chart_bg)
        ax2.set_facecolor(chart_bg)
        im = ax2.imshow(heatmap_values, cmap="Blues", aspect="auto", vmin=0, vmax=100)
        ax2.set_xticks([0, 1])
        ax2.set_xticklabels(["ATS Score (%)", "Confidence (%)"], color=chart_text)
        ax2.set_yticks(range(len(graph_df)))
        ax2.set_yticklabels(graph_df["short_name"], color=chart_text)
        ax2.tick_params(colors=chart_text)
        for i in range(heatmap_values.shape[0]):
            for j in range(heatmap_values.shape[1]):
                value = float(heatmap_values[i, j])
                color = "#1A1A1A" if value < 55 else "#F8FAFC"
                ax2.text(j, i, f"{value:.1f}", ha="center", va="center", color=color, fontsize=9, fontweight="bold")
        cbar = fig2.colorbar(im, ax=ax2, fraction=0.03, pad=0.02)
        cbar.set_label("Percentage", color=chart_text)
        cbar.ax.yaxis.set_tick_params(color=chart_text)
        plt.setp(cbar.ax.get_yticklabels(), color=chart_text)
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)

        st.download_button(
            "Download Results CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="ats_bulk_screening_results.csv",
            mime="text/csv",
        )

    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Video Resume":
    if not _require_model():
        st.stop()

    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("<h3 class='section-head'>Video Resume Screening</h3>", unsafe_allow_html=True)
        st.markdown(
            "<p class='section-sub'>Upload .mp4/.mov/.avi/.mkv, transcribe speech, and score ATS match.</p>",
            unsafe_allow_html=True,
        )
        uploaded_video = st.file_uploader("Upload Video Resume", type=["mp4", "mov", "avi", "mkv"], key="video")
        run = st.button("Analyse Video Resume", type="primary")

        if run and uploaded_video:
            with st.spinner("Processing video and transcribing audio..."):
                result = screen_video_resume(uploaded_video.read(), job_description, video_name=uploaded_video.name)

            st.markdown(
                f"""
                <div class="video-stats">
                  <div class="video-stat">
                    <p class="video-stat-label">Video ATS</p>
                    <p class="video-stat-value">{result['ats_score']}%</p>
                  </div>
                  <div class="video-stat">
                    <p class="video-stat-label">Prediction</p>
                    <p class="video-stat-value">{result['label']}</p>
                  </div>
                  <div class="video-stat">
                    <p class="video-stat-label">Transcript Length</p>
                    <p class="video-stat-value">{len(result['transcript'].split())} words</p>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(min(max(result["ats_score"] / 100.0, 0.0), 1.0))
            st.write(f"Matched Skills: {', '.join(result['matched_skills']) if result['matched_skills'] else 'None'}")
            st.write(f"Missing Skills: {', '.join(result['missing_skills']) if result['missing_skills'] else 'None'}")
            with st.expander("Transcript"):
                st.write(result["transcript"] if result["transcript"].strip() else "No speech could be transcribed.")
        elif run and not uploaded_video:
            st.warning("Upload a video resume first.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.subheader("What We Evaluate")
        st.markdown(
            """
            - Speech clarity and consistency
            - Content relevance to job description
            - ATS semantic alignment score
            - Matched vs missing skill signals
            - Overall classification confidence
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

else:
    if not _require_model():
        st.stop()

    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-head'>Resume Builder</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p class='section-sub'>Create an ATS-focused resume and download it as Markdown, Text, or polished PDF.</p>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 0.75], gap="large")
    with left:
        st.markdown("#### Contact")
        c1, c2 = st.columns(2)
        name = c1.text_input("Name", placeholder="Ananya Saini")
        email = c2.text_input("Email ID", placeholder="name@email.com")
        c3, c4, c5, c6 = st.columns(4)
        phone = c3.text_input("Phone", placeholder="+91 XXXXX XXXXX")
        location = c4.text_input("Location", placeholder="Dehradun")
        linkedin = c5.text_input("LinkedIn", placeholder="linkedin.com/in/username")
        github = c6.text_input("GitHub", placeholder="github.com/username")

        summary = st.text_area("Professional Summary", height=120, placeholder="Write a concise summary aligned to the job description...")
        skills_csv = st.text_area("Skills (comma-separated)", height=90, placeholder="Python, SQL, Machine Learning, Streamlit")
        certifications_csv = st.text_input("Certifications (comma-separated)", placeholder="Certification A, Certification B")

        st.markdown("#### Experience")
        experience_rows = st.data_editor(
            pd.DataFrame([{"Type": "Internship", "Role": "", "Company": "", "Duration": "", "Location": "", "Achievements": ""}]),
            num_rows="dynamic",
            use_container_width=True,
            key="resume_exp_editor",
        ).to_dict("records")

        st.markdown("#### Projects")
        project_rows = st.data_editor(
            pd.DataFrame([{"Project": "", "Tech": "", "Project Link": "", "Details": ""}]),
            num_rows="dynamic",
            use_container_width=True,
            key="resume_project_editor",
        ).to_dict("records")

        st.markdown("#### Education")
        education_rows = st.data_editor(
            pd.DataFrame([{"Degree": "", "Institute": "", "Year": "", "Location": "", "CGPA": ""}]),
            num_rows="dynamic",
            use_container_width=True,
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
    feedback = get_resume_builder_feedback(resume_scoring_text, matcher, clean_jd)

    with right:
        st.markdown("#### Smart Builder Suggestions")
        smart_suggestions = generate_smart_builder_suggestions(resume_data, job_description)

        st.markdown("**Keyword Analysis**")
        st.markdown(
            f"- JD Technical Skills: {', '.join(smart_suggestions['jd_technical_skills']) if smart_suggestions['jd_technical_skills'] else 'None'}"
        )
        st.markdown(
            f"- JD Soft Skills: {', '.join(smart_suggestions['jd_soft_skills']) if smart_suggestions['jd_soft_skills'] else 'None'}"
        )
        st.markdown(
            f"- Matched Skills: {', '.join(smart_suggestions['matched_skills']) if smart_suggestions['matched_skills'] else 'None'}"
        )

        st.markdown("**Key Skills to Add**")
        _render_smart_suggestion_box(
            "Key Skills to Add",
            ", ".join(smart_suggestions["recommended_skills"]) if smart_suggestions["recommended_skills"] else "No major gaps detected.",
        )

        st.markdown("**Suggested Summary**")
        _render_smart_suggestion_box("Suggested Summary", smart_suggestions["suggested_summary"])

        st.markdown("**STAR Experience Rewrite (Copy into Experience)**")
        _render_smart_suggestion_box(
            "STAR Experience Rewrite (Copy into Experience)",
            smart_suggestions["star_experience_rewrite"],
        )

        st.markdown("#### ATS Fit")
        m1, m2 = st.columns(2)
        m1.metric("Score", f"{feedback['score']}%")
        m2.metric("Prediction", feedback["label"])
        st.progress(min(max(feedback["score"] / 100.0, 0.0), 1.0))

        st.write(f"Matched Skills: {', '.join(feedback['matched_skills']) if feedback['matched_skills'] else 'None'}")
        st.write(f"Missing Skills: {', '.join(feedback['missing_skills']) if feedback['missing_skills'] else 'None'}")

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
