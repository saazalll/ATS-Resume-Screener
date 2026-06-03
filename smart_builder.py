import re
from collections import Counter
from typing import Dict, List, Tuple

from skill_catalog import SOFT_SKILLS, TECH_SKILLS, extract_soft_skills, extract_tech_skills

TECH_PHRASES = TECH_SKILLS
SOFT_PHRASES = SOFT_SKILLS


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _extract_top_terms(text: str, limit: int = 10) -> List[str]:
    raw_tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", text.lower())
    tokens = [t.strip(" .,-_") for t in raw_tokens if t.strip(" .,-_")]
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
        "must",
        "preferred",
        "candidate",
        "requirements",
        "requirement",
        "responsibilities",
        "experience",
        "skills",
        "strong",
        "need",
        "needed",
        "seeking",
        "looking",
        "required",
        "require",
        "candidate",
    }
    filt = [t for t in tokens if t not in stop and len(t) > 3]
    freq = Counter(filt)
    return [w for w, _ in freq.most_common(limit)]


def _remove_phrase_parts(terms: List[str]) -> List[str]:
    phrase_parts = {part for term in terms if " " in term for part in term.split()}
    out = []
    for term in terms:
        if " " not in term and term in phrase_parts:
            continue
        out.append(term)
    return out


def _collect_user_skills(data: Dict) -> List[str]:
    chunks: List[str] = []
    chunks.append(str(data.get("skills_csv", "")))
    chunks.append(str(data.get("summary", "")))
    chunks.append(str(data.get("certifications_csv", "")))

    for row in data.get("project_rows", []):
        chunks.append(str(row.get("Project", "")))
        chunks.append(str(row.get("Tech", "")))
        chunks.append(str(row.get("Details", "")))

    for row in data.get("experience_rows", []):
        chunks.append(str(row.get("Role", "")))
        chunks.append(str(row.get("Company", "")))
        chunks.append(str(row.get("Achievements", "")))

    all_text = " ".join(chunks)
    catalog_terms = extract_tech_skills(all_text)
    fallback_terms = _extract_top_terms(all_text, limit=60)
    combined = []
    seen = set()
    for term in catalog_terms + fallback_terms:
        if term not in seen:
            combined.append(term)
            seen.add(term)
    return _remove_phrase_parts(combined)


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
    jd_tech = extract_tech_skills(jd)
    jd_soft = extract_soft_skills(jd)
    if len(jd_tech) < 8:
        fallback_terms = _extract_top_terms(jd, limit=20)
        combined = []
        seen = set()
        for term in jd_tech + fallback_terms:
            if term not in seen:
                combined.append(term)
                seen.add(term)
        jd_tech = _remove_phrase_parts(combined)[:12]

    user_skills = set(_collect_user_skills(user_data))
    matched = [s for s in jd_tech if s in user_skills]
    recommended = [s for s in jd_tech if s not in user_skills][:12]

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
