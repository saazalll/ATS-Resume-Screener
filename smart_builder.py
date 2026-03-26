import re
from collections import Counter
from typing import Dict, List, Tuple


TECH_PHRASES = [
    "machine learning",
    "data science",
    "artificial intelligence",
    "natural language processing",
    "deep learning",
    "computer vision",
    "data analysis",
    "data engineering",
    "power bi",
    "scikit-learn",
    "streamlit",
    "tableau",
    "postgresql",
    "mysql",
    "mongodb",
    "pytorch",
    "tensorflow",
    "python",
    "java",
    "sql",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "rag",
    "faiss",
    "transformers",
]

SOFT_PHRASES = [
    "communication",
    "leadership",
    "problem solving",
    "critical thinking",
    "collaboration",
    "teamwork",
    "stakeholder management",
    "adaptability",
    "time management",
    "attention to detail",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _extract_matches(text: str, phrases: List[str]) -> List[str]:
    text_l = _normalize(text)
    matches = []
    for phrase in phrases:
        if re.search(rf"\b{re.escape(phrase)}\b", text_l):
            matches.append(phrase)
    return sorted(set(matches))


def _extract_top_terms(text: str, limit: int = 10) -> List[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]+", text.lower())
    stop = {
        "with",
        "from",
        "that",
        "this",
        "have",
        "will",
        "your",
        "their",
        "using",
        "ability",
        "strong",
        "experience",
        "knowledge",
        "skills",
        "skill",
        "years",
        "year",
        "for",
        "and",
        "the",
        "you",
        "are",
        "our",
        "into",
        "role",
        "job",
    }
    filt = [t for t in tokens if t not in stop and len(t) > 2]
    freq = Counter(filt)
    return [w for w, _ in freq.most_common(limit)]


def _collect_user_skills(data: Dict) -> List[str]:
    values = []
    values.extend([s.strip().lower() for s in str(data.get("skills_csv", "")).split(",") if s.strip()])

    for row in data.get("project_rows", []):
        values.extend([s.strip().lower() for s in str(row.get("Tech", "")).split(",") if s.strip()])

    for row in data.get("experience_rows", []):
        values.extend(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]+", str(row.get("Achievements", "")).lower()))

    return sorted(set(values))


def _pick_project_for_summary(project_rows: List[Dict], jd_tech: List[str]) -> Tuple[str, str]:
    best_name = ""
    best_tech = ""
    best_score = -1

    for row in project_rows:
        name = str(row.get("Project", "")).strip()
        tech = str(row.get("Tech", "")).strip()
        if not name and not tech:
            continue
        tech_l = _normalize(tech)
        score = sum(1 for t in jd_tech if t in tech_l)
        if score > best_score:
            best_score = score
            best_name = name
            best_tech = tech

    return best_name, best_tech


def _build_summary(data: Dict, jd_tech: List[str]) -> str:
    edu = data.get("education_rows", [])
    if edu:
        first = edu[0]
        degree = str(first.get("Degree", "")).strip() or "Computer Science student"
        period = str(first.get("Year", "")).strip()
        status = f"{degree}" + (f" ({period})" if period else "")
    else:
        status = "Final-year Computer Science student"

    proj_name, proj_tech = _pick_project_for_summary(data.get("project_rows", []), jd_tech)
    if not proj_name:
        proj_name = "an end-to-end ML project"
    if not proj_tech:
        proj_tech = ", ".join(jd_tech[:3]) if jd_tech else "Python, SQL, and data analysis tools"

    jd_focus = ", ".join(jd_tech[:3]) if jd_tech else "data-driven problem solving"

    s1 = f"{status} with hands-on experience in building practical software and analytics solutions."
    s2 = (
        f"Applied {proj_name} to solve real-world problems using {proj_tech}, directly aligned with requirements in {jd_focus}."
    )
    s3 = (
        "Focused on delivering measurable business value through reliable implementation, faster insights, and clear stakeholder communication."
    )
    return f"{s1} {s2} {s3}"


def _rewrite_star_experience(data: Dict, jd_tech: List[str], jd_soft: List[str]) -> str:
    experiences = data.get("experience_rows", [])
    if not experiences:
        return "Add at least one experience entry to generate STAR bullet points."

    target = None
    for row in experiences:
        company = str(row.get("Company", "")).lower()
        if "celebal" in company:
            target = row
            break
    if target is None:
        target = experiences[0]

    role = str(target.get("Role", "")).strip() or "Data Science Intern"
    company = str(target.get("Company", "")).strip() or "the organization"
    duration = str(target.get("Duration", "")).strip()
    base_tech = ", ".join(jd_tech[:3]) if jd_tech else "Python, SQL, and ML workflows"
    base_soft = ", ".join(jd_soft[:2]) if jd_soft else "collaboration and communication"

    line1 = (
        f"At {company}{(' (' + duration + ')') if duration else ''}, supported analytics and ML initiatives where faster, reliable model delivery was required."
    )
    line2 = (
        f"As {role}, implemented data preprocessing, feature engineering, and model experimentation using {base_tech}, while collaborating with cross-functional teams."
    )
    line3 = (
        f"Improved decision readiness by producing cleaner insights and more consistent outputs, strengthening {base_soft} in business-facing workflows."
    )
    return "\n".join([f"- {line1}", f"- {line2}", f"- {line3}"])


def generate_smart_builder_suggestions(user_data: Dict, job_description: str) -> Dict:
    jd = job_description or ""
    jd_tech = _extract_matches(jd, TECH_PHRASES)
    jd_soft = _extract_matches(jd, SOFT_PHRASES)
    if not jd_tech:
        jd_tech = _extract_top_terms(jd, limit=8)

    user_skills = _collect_user_skills(user_data)
    user_skill_text = " ".join(user_skills)

    matched = [s for s in jd_tech if s in user_skill_text]
    recommended = [s for s in jd_tech if s not in user_skill_text][:12]

    summary = _build_summary(user_data, jd_tech)
    star_block = _rewrite_star_experience(user_data, jd_tech, jd_soft)

    return {
        "jd_technical_skills": jd_tech[:12],
        "jd_soft_skills": jd_soft[:8],
        "matched_skills": matched[:12],
        "recommended_skills": recommended,
        "suggested_summary": summary,
        "star_experience_rewrite": star_block,
    }
