import io
import textwrap
from typing import Dict, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from skill_gap import get_skill_match_details
from text_cleaner import clean_text


def _split_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _non_empty_lines(value: str) -> List[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _format_experience(rows: List[Dict[str, str]]) -> str:
    internships = []
    simulations = []
    others = []

    for row in rows:
        exp_type = str(row.get("Type", "")).strip().lower()
        role = str(row.get("Role", "")).strip()
        company = str(row.get("Company", "")).strip()
        duration = str(row.get("Duration", "")).strip()
        location = str(row.get("Location", "")).strip()
        achievements = str(row.get("Achievements", "")).strip()

        if not any([exp_type, role, company, duration, location, achievements]):
            continue

        headline = " - ".join([x for x in [role, company] if x]) or "Experience"
        meta = " | ".join([x for x in [duration, location] if x])
        block = [f"### {headline}"]
        if meta:
            block.append(meta)
        block.extend([f"- {a}" for a in _non_empty_lines(achievements)])
        block.append("")

        if "simulation" in exp_type:
            simulations.extend(block)
        elif "intern" in exp_type:
            internships.extend(block)
        else:
            others.extend(block)

    out = []
    if internships:
        out.extend(["#### Internships", *internships])
    if simulations:
        out.extend(["#### Job Simulations", *simulations])
    if others:
        out.extend(["#### Other Experience", *others])

    return "\n".join(out).strip()


def _format_education(rows: List[Dict[str, str]]) -> str:
    out = []
    for row in rows:
        degree = str(row.get("Degree", "")).strip()
        institute = str(row.get("Institute", "")).strip()
        year = str(row.get("Year", "")).strip()
        location = str(row.get("Location", "")).strip()
        cgpa = str(row.get("CGPA", "")).strip()

        if not any([degree, institute, year, location, cgpa]):
            continue

        header = " - ".join([item for item in [degree, institute] if item])
        meta = " | ".join([item for item in [year, location] if item])
        out.append(f"- {header}" if header else "- Education")
        if meta:
            out.append(f"  {meta}")
        if cgpa:
            out.append(f"  CGPA: {cgpa}")
        out.append("")

    return "\n".join(out).strip()


def _format_projects(rows: List[Dict[str, str]]) -> str:
    out = []
    for row in rows:
        name = str(row.get("Project", "")).strip()
        tech = str(row.get("Tech", "")).strip()
        link = str(row.get("Project Link", "")).strip() or str(row.get("Link", "")).strip()
        details = str(row.get("Details", "")).strip()

        if not any([name, tech, link, details]):
            continue

        title = name if name else "Project"
        out.append(f"### {title}")

        if tech:
            skill_line = " ".join([t.strip() for t in tech.split(",") if t.strip()]) or tech
            out.append(f"Key Skills: {skill_line}")
        if link:
            out.append(f"Project Link: {link}")

        details_lines = _non_empty_lines(details)
        if details_lines:
            out.append(" ".join(details_lines))
        out.append("")

    return "\n".join(out).strip()


def build_resume_markdown(data: Dict) -> str:
    name = data.get("name", "").strip() or "Your Name"
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    location = data.get("location", "").strip()
    linkedin = data.get("linkedin", "").strip()
    portfolio = data.get("portfolio", "").strip()

    contact_line = " | ".join([x for x in [email, phone, location] if x])
    links_line = " | ".join([x for x in [linkedin, portfolio] if x])

    skills = _split_csv(data.get("skills_csv", ""))
    certifications = _split_csv(data.get("certifications_csv", ""))

    summary = data.get("summary", "").strip()
    experience_block = _format_experience(data.get("experience_rows", []))
    education_block = _format_education(data.get("education_rows", []))
    project_block = _format_projects(data.get("project_rows", []))

    lines = [f"# {name}"]
    if contact_line:
        lines.append(contact_line)
    if links_line:
        lines.append(links_line)

    if summary:
        lines.extend(["", "## Professional Summary", summary])

    if skills:
        lines.extend(["", "## Skills", ", ".join(skills)])

    if experience_block:
        lines.extend(["", "## Experience", experience_block])

    if project_block:
        lines.extend(["", "## Projects", project_block])

    if education_block:
        lines.extend(["", "## Education", education_block])

    if certifications:
        lines.extend(["", "## Certifications", "\n".join(f"- {c}" for c in certifications)])

    return "\n".join(lines).strip()


def build_resume_scoring_text(data: Dict) -> str:
    """
    Build plain semantic content for ATS scoring (exclude markdown headings/formatting).
    """
    parts: List[str] = []

    summary = str(data.get("summary", "")).strip()
    if summary:
        parts.append(summary)

    skills_csv = str(data.get("skills_csv", "")).strip()
    if skills_csv:
        parts.append(skills_csv)

    certifications_csv = str(data.get("certifications_csv", "")).strip()
    if certifications_csv:
        parts.append(certifications_csv)

    for row in data.get("experience_rows", []):
        exp_type = str(row.get("Type", "")).strip()
        role = str(row.get("Role", "")).strip()
        company = str(row.get("Company", "")).strip()
        duration = str(row.get("Duration", "")).strip()
        location = str(row.get("Location", "")).strip()
        achievements = str(row.get("Achievements", "")).strip()
        parts.extend([exp_type, role, company, duration, location, achievements])

    for row in data.get("project_rows", []):
        name = str(row.get("Project", "")).strip()
        tech = str(row.get("Tech", "")).strip()
        link = str(row.get("Project Link", "")).strip() or str(row.get("Link", "")).strip()
        details = str(row.get("Details", "")).strip()
        parts.extend([name, tech, link, details])

    for row in data.get("education_rows", []):
        degree = str(row.get("Degree", "")).strip()
        institute = str(row.get("Institute", "")).strip()
        year = str(row.get("Year", "")).strip()
        location = str(row.get("Location", "")).strip()
        cgpa = str(row.get("CGPA", "")).strip()
        parts.extend([degree, institute, year, location, cgpa])

    return "\n".join([p for p in parts if p]).strip()


def get_resume_builder_feedback(resume_text: str, matcher, job_description_text: str) -> Dict:
    resume_clean = clean_text(resume_text)
    prediction = matcher.predict_match(resume_clean)
    skill_feedback = get_skill_match_details(job_description_text, resume_text)

    hard = skill_feedback.get("hard_score", 0.0)
    soft = skill_feedback.get("soft_score", 0.0)
    semantic = prediction.semantic_score
    overall_score = round((0.50 * semantic) + (0.35 * hard) + (0.15 * soft), 2)
    label = "Matched" if overall_score >= 50 else "Not Matched"

    return {
        "score": overall_score,
        "semantic_score": semantic,
        "hard_skills_score": hard,
        "soft_skills_score": soft,
        "label": label,
        "matched_skills": skill_feedback["matched_skills"],
        "missing_skills": skill_feedback["missing_skills"],
        "organizations": skill_feedback.get("organizations", []),
        "dates": skill_feedback.get("dates", [])
    }


def build_resume_pdf_bytes(data: Dict) -> bytes:
    """
    Generate a professional high-contrast resume PDF with timeline structure.
    Using ReportLab for proper pagination.
    """
    name = str(data.get("name", "")).strip() or "Your Name"
    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()
    location = str(data.get("location", "")).strip()
    linkedin = str(data.get("linkedin", "")).strip()
    portfolio = str(data.get("portfolio", "")).strip()

    summary = str(data.get("summary", "")).strip()
    skills = _split_csv(str(data.get("skills_csv", "")))
    certifications = _split_csv(str(data.get("certifications_csv", "")))

    out = io.BytesIO()
    
    doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=22, spaceAfter=6, textColor="#000000")
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, spaceAfter=2, textColor="#000000")
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=11, spaceAfter=6, textColor="#000000", borderPadding=(0,0,2,0), borderWidth=1, borderColor="#CBD5E1")
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9, spaceAfter=4, textColor="#000000")
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontSize=9, spaceAfter=2, textColor="#000000", fontName='Helvetica-Bold')
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=9, spaceAfter=2, leftIndent=15, textColor="#000000", bulletIndent=5)
    subhead_style = ParagraphStyle('Subhead', parent=styles['Normal'], fontSize=9.5, spaceAfter=4, textColor="#000000", fontName='Helvetica-Bold')
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=9, spaceAfter=4, textColor="#64748B", alignment=TA_RIGHT)

    story.append(Paragraph(name, title_style))
    
    contact_line = " | ".join([x for x in [email, phone, location] if x])
    links_line = " | ".join([x for x in [linkedin, portfolio] if x])
    if contact_line:
        story.append(Paragraph(contact_line, contact_style))
    if links_line:
        story.append(Paragraph(links_line, contact_style))
        
    story.append(Spacer(1, 10))

    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(summary, normal_style))
        story.append(Spacer(1, 5))

    if skills:
        story.append(Paragraph("SKILLS", heading_style))
        dense_skills = " | ".join([s.strip() for s in skills if s.strip()])
        story.append(Paragraph(dense_skills, normal_style))
        story.append(Spacer(1, 5))

    # Helper function to create timeline header with Table
    def _timeline_header(left_text, right_text):
        if not right_text:
            story.append(Paragraph(left_text, bold_style))
            return
            
        left_p = Paragraph(left_text, bold_style)
        right_p = Paragraph(right_text, meta_style)
        
        # We use a Table to align the text. We have roughly 535 points of width (A4 width - 60 points margin).
        # We can give 70% to left and 30% to right
        t = Table([[left_p, right_p]], colWidths=['70%', '30%'])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(t)
        story.append(Spacer(1, 2))

    education_rows = data.get("education_rows", [])
    if education_rows:
        story.append(Paragraph("EDUCATION", heading_style))
        for row in education_rows:
            degree = str(row.get("Degree", "")).strip()
            institute = str(row.get("Institute", "")).strip()
            year = str(row.get("Year", "")).strip()
            edu_loc = str(row.get("Location", "")).strip()
            cgpa = str(row.get("CGPA", "")).strip()
            if not any([degree, institute, year, edu_loc, cgpa]):
                continue
            
            right_meta = " | ".join([x for x in [year, edu_loc] if x])
            _timeline_header(f"<b>{degree}</b>", right_meta)
            if institute:
                story.append(Paragraph(institute, normal_style))
            if cgpa:
                story.append(Paragraph(f"<b>CGPA:</b> {cgpa}", normal_style))
            story.append(Spacer(1, 5))

    experience_rows = data.get("experience_rows", [])
    if experience_rows:
        internships = []
        simulations = []
        others = []
        for row in experience_rows:
            exp_type = str(row.get("Type", "")).strip().lower()
            role = str(row.get("Role", "")).strip()
            company = str(row.get("Company", "")).strip()
            duration = str(row.get("Duration", "")).strip()
            exp_loc = str(row.get("Location", "")).strip()
            bullets = _non_empty_lines(str(row.get("Achievements", "")).strip())
            
            if not any([exp_type, role, company, duration, exp_loc, bullets]):
                continue
                
            entry = {"role": role, "company": company, "duration": duration, "exp_loc": exp_loc, "bullets": bullets}
            if "simulation" in exp_type:
                simulations.append(entry)
            elif "intern" in exp_type:
                internships.append(entry)
            else:
                others.append(entry)

        if internships or simulations or others:
            story.append(Paragraph("EXPERIENCE", heading_style))
            
            def _add_entries(entries_list, subtitle):
                if not entries_list:
                    return
                story.append(Paragraph(subtitle, subhead_style))
                for e in entries_list:
                    meta = " | ".join([x for x in [e['duration'], e['exp_loc']] if x])
                    _timeline_header(f"<b>{e['role']}</b> - {e['company']}", meta)
                    for bullet in e['bullets']:
                        story.append(Paragraph(f"• {bullet}", bullet_style))
                    story.append(Spacer(1, 5))

            _add_entries(internships, "INTERNSHIPS")
            _add_entries(simulations, "JOB SIMULATIONS")
            _add_entries(others, "OTHER EXPERIENCE")

    project_rows = data.get("project_rows", [])
    if project_rows:
        story.append(Paragraph("PROJECTS", heading_style))
        for row in project_rows:
            proj = str(row.get("Project", "")).strip()
            tech = str(row.get("Tech", "")).strip()
            link = str(row.get("Project Link", "")).strip() or str(row.get("Link", "")).strip()
            details_lines = _non_empty_lines(str(row.get("Details", "")).strip())
            
            if not any([proj, tech, link, details_lines]):
                continue
                
            if proj:
                story.append(Paragraph(f"<b>{proj}</b>", bold_style))
            if tech:
                skill_line = " | ".join([t.strip() for t in tech.split(",") if t.strip()]) or tech
                story.append(Paragraph(f"<b>Key Skills:</b> {skill_line}", normal_style))
            if link:
                story.append(Paragraph(f"<b>Project Link:</b> {link}", normal_style))
            for line in details_lines:
                story.append(Paragraph(f"• {line}", bullet_style))
            story.append(Spacer(1, 5))

    if certifications:
        story.append(Paragraph("CERTIFICATES", heading_style))
        for cert in certifications:
            story.append(Paragraph(f"• {cert}", bullet_style))

    doc.build(story)
    out.seek(0)
    return out.getvalue()
