import io
import textwrap
from typing import Dict, List

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

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

    return {
        "score": prediction.score_percent,
        "label": prediction.label,
        "matched_skills": skill_feedback["matched_skills"],
        "missing_skills": skill_feedback["missing_skills"],
    }


def _wrap(text: str, width: int) -> List[str]:
    if not text.strip():
        return []
    return textwrap.wrap(text.strip(), width=width)


PRIMARY_TEXT = "#000000"
MUTED_TEXT = "#64748B"
RULE_COLOR = "#CBD5E1"


def _section_header(ax, y: float, title: str) -> float:
    ax.text(0.06, y, title.upper(), fontsize=10.8, fontweight="bold", color=PRIMARY_TEXT, va="top", family="DejaVu Sans")
    y -= 0.012
    ax.plot([0.06, 0.94], [y, y], color=RULE_COLOR, linewidth=0.85)
    return y - 0.012


def _draw_wrapped(ax, x: float, y: float, text: str, width: int, size: float, color: str, weight: str = "normal") -> float:
    for line in _wrap(text, width):
        ax.text(x, y, line, fontsize=size, color=color, va="top", family="DejaVu Sans", fontweight=weight)
        y -= 0.013
    return y


def _draw_timeline_entry(
    ax,
    y: float,
    left_title: str,
    left_subtitle: str,
    right_meta: str,
    bullets: List[str],
    cgpa: str = "",
) -> float:
    if left_title:
        ax.text(0.06, y, left_title, fontsize=10.2, color=PRIMARY_TEXT, va="top", family="DejaVu Sans", fontweight="bold")
    if right_meta:
        ax.text(0.94, y, right_meta, fontsize=9, color=MUTED_TEXT, va="top", ha="right", family="DejaVu Sans")
    y -= 0.014

    if left_subtitle:
        y = _draw_wrapped(ax, 0.06, y, left_subtitle, width=80, size=9.3, color=PRIMARY_TEXT, weight="bold")

    if cgpa:
        ax.text(0.06, y, f"CGPA: {cgpa}", fontsize=9.3, color=PRIMARY_TEXT, va="top", family="DejaVu Sans", fontweight="bold")
        y -= 0.0135

    for bullet in bullets:
        bullet_lines = _wrap(bullet, 106)
        if not bullet_lines:
            continue
        ax.text(0.065, y, f"• {bullet_lines[0]}", fontsize=8.8, color=PRIMARY_TEXT, va="top", family="DejaVu Sans")
        y -= 0.0126
        for more in bullet_lines[1:]:
            ax.text(0.083, y, more, fontsize=8.8, color=PRIMARY_TEXT, va="top", family="DejaVu Sans")
            y -= 0.0126

    return y - 0.007


def build_resume_pdf_bytes(data: Dict) -> bytes:
    """
    Generate a professional high-contrast resume PDF with timeline structure.
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
    with PdfPages(out) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        ax.text(0.5, 0.967, name, fontsize=22, fontweight="bold", color=PRIMARY_TEXT, ha="center", family="DejaVu Sans")
        contact_line = " | ".join([x for x in [email, phone, location] if x])
        links_line = " | ".join([x for x in [linkedin, portfolio] if x])
        if contact_line:
            ax.text(0.5, 0.943, contact_line, fontsize=9.1, color=PRIMARY_TEXT, ha="center", family="DejaVu Sans")
        if links_line:
            ax.text(0.5, 0.927, links_line, fontsize=8.9, color=PRIMARY_TEXT, ha="center", family="DejaVu Sans")

        ax.plot([0.06, 0.94], [0.912, 0.912], color=RULE_COLOR, linewidth=1.0)
        y = 0.895

        if summary:
            y = _section_header(ax, y, "Professional Summary")
            y = _draw_wrapped(ax, 0.06, y, summary, width=118, size=9.1, color=PRIMARY_TEXT)
            y -= 0.004

        if skills:
            y = _section_header(ax, y, "Skills")
            dense_skills = " | ".join([s.strip() for s in skills if s.strip()])
            y = _draw_wrapped(ax, 0.06, y, dense_skills, width=122, size=9.0, color=PRIMARY_TEXT)
            y -= 0.004

        # Education timeline
        education_rows = data.get("education_rows", [])
        if education_rows:
            y = _section_header(ax, y, "Education")
            for row in education_rows:
                degree = str(row.get("Degree", "")).strip()
                institute = str(row.get("Institute", "")).strip()
                year = str(row.get("Year", "")).strip()
                edu_loc = str(row.get("Location", "")).strip()
                cgpa = str(row.get("CGPA", "")).strip()
                if not any([degree, institute, year, edu_loc, cgpa]):
                    continue
                right_meta = " | ".join([x for x in [year, edu_loc] if x])
                y = _draw_timeline_entry(
                    ax,
                    y=y,
                    left_title=degree,
                    left_subtitle=institute,
                    right_meta=right_meta,
                    bullets=[],
                    cgpa=cgpa,
                )

        # Experience timeline (distinct groups)
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
                entry = {
                    "role": role,
                    "company": company,
                    "meta": " | ".join([x for x in [duration, exp_loc] if x]),
                    "bullets": bullets,
                }
                if "simulation" in exp_type:
                    simulations.append(entry)
                elif "intern" in exp_type:
                    internships.append(entry)
                else:
                    others.append(entry)

            if internships or simulations or others:
                y = _section_header(ax, y, "Experience")

            if internships:
                ax.text(0.06, y, "INTERNSHIPS", fontsize=9.6, fontweight="bold", color=PRIMARY_TEXT, va="top", family="DejaVu Sans")
                y -= 0.0125
                for e in internships:
                    y = _draw_timeline_entry(
                        ax,
                        y=y,
                        left_title=e["role"],
                        left_subtitle=e["company"],
                        right_meta=e["meta"],
                        bullets=e["bullets"],
                    )

            if simulations:
                ax.text(0.06, y, "JOB SIMULATIONS", fontsize=9.6, fontweight="bold", color=PRIMARY_TEXT, va="top", family="DejaVu Sans")
                y -= 0.0125
                for e in simulations:
                    y = _draw_timeline_entry(
                        ax,
                        y=y,
                        left_title=e["role"],
                        left_subtitle=e["company"],
                        right_meta=e["meta"],
                        bullets=e["bullets"],
                    )

            if others:
                ax.text(0.06, y, "OTHER EXPERIENCE", fontsize=9.6, fontweight="bold", color=PRIMARY_TEXT, va="top", family="DejaVu Sans")
                y -= 0.0125
                for e in others:
                    y = _draw_timeline_entry(
                        ax,
                        y=y,
                        left_title=e["role"],
                        left_subtitle=e["company"],
                        right_meta=e["meta"],
                        bullets=e["bullets"],
                    )

        # Projects with strong separation
        project_rows = data.get("project_rows", [])
        if project_rows:
            y = _section_header(ax, y, "Projects")
            for row in project_rows:
                proj = str(row.get("Project", "")).strip()
                tech = str(row.get("Tech", "")).strip()
                link = str(row.get("Project Link", "")).strip() or str(row.get("Link", "")).strip()
                details = " ".join(_non_empty_lines(str(row.get("Details", "")).strip()))
                if not any([proj, tech, link, details]):
                    continue

                if proj:
                    ax.text(0.06, y, proj, fontsize=10.2, color=PRIMARY_TEXT, va="top", family="DejaVu Sans", fontweight="bold")
                    y -= 0.0138
                if tech:
                    skill_line = " | ".join([t.strip() for t in tech.split(",") if t.strip()]) or tech
                    y = _draw_wrapped(ax, 0.06, y, f"Key Skills: {skill_line}", width=118, size=8.9, color=PRIMARY_TEXT)
                if link:
                    y = _draw_wrapped(ax, 0.06, y, f"Project Link: {link}", width=118, size=8.8, color=PRIMARY_TEXT)
                if details:
                    wrapped = _wrap(details, 118)[:3]  # keep concise 2-3 lines
                    for line in wrapped:
                        ax.text(0.06, y, line, fontsize=8.8, color=PRIMARY_TEXT, va="top", family="DejaVu Sans")
                        y -= 0.0128
                y -= 0.006

        if certifications:
            y = _section_header(ax, y, "Certificates")
            for cert in certifications:
                y = _draw_wrapped(ax, 0.06, y, f"• {cert}", width=118, size=8.9, color=PRIMARY_TEXT)

        pdf.savefig(fig)
        plt.close(fig)

    out.seek(0)
    return out.getvalue()
