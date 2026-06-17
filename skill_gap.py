from typing import Dict, List, Set, Tuple

from skill_catalog import extract_tech_skills, extract_soft_skills
from keyword_utils import extract_dynamic_keywords
from ner_utils import extract_entities

def get_skill_match_details(job_description_clean: str, resume_clean: str) -> Dict[str, any]:
    jd_text = job_description_clean or ""
    resume_text = resume_clean or ""

    # Phase 4 NER Extraction
    resume_entities = extract_entities(resume_text)
    jd_entities = extract_entities(jd_text)

    # Hard Skills (Tech + Dynamic)
    jd_hard = set(extract_tech_skills(jd_text))
    res_hard = set(extract_tech_skills(resume_text))
    
    jd_dynamic, resume_dynamic = extract_dynamic_keywords(jd_text, resume_text)
    
    jd_hard = {t for t in (jd_hard | set(jd_dynamic)) if t}
    res_hard = {t for t in (res_hard | set(resume_dynamic)) if t}
    
    matched_hard = jd_hard & res_hard
    missing_hard = jd_hard - res_hard
    
    hard_score = (len(matched_hard) / len(jd_hard)) * 100 if jd_hard else 100.0

    # Soft Skills
    jd_soft = set(extract_soft_skills(jd_text))
    res_soft = set(extract_soft_skills(resume_text))
    
    jd_soft = {t for t in jd_soft if t}
    res_soft = {t for t in res_soft if t}
    
    matched_soft = jd_soft & res_soft
    missing_soft = jd_soft - res_soft
    
    soft_score = (len(matched_soft) / len(jd_soft)) * 100 if jd_soft else 100.0

    # Phase 4: Give a slight bump (up to 10%) to the soft score if candidate shows structured experience (dates/orgs)
    # This helps reward resumes that have clear timelines vs just keyword dumps
    if resume_entities["dates"] or resume_entities["organizations"]:
        soft_score = min(soft_score + 10.0, 100.0)

    # Combine for UI list display
    matched = sorted(matched_hard | matched_soft)
    missing = sorted(missing_hard | missing_soft)

    return {
        "matched_skills": matched[:35],
        "missing_skills": missing[:35],
        "hard_score": round(hard_score, 2),
        "soft_score": round(soft_score, 2),
        "dates": resume_entities["dates"],
        "organizations": resume_entities["organizations"]
    }
