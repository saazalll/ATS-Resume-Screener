from typing import Dict, List, Set, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from skill_catalog import extract_tech_skills


def _tokenize_skills(text: str) -> Set[str]:
    return set(extract_tech_skills(text))


NOISE_TERMS = {
    "experience",
    "experienced",
    "knowledge",
    "ability",
    "candidate",
    "candidates",
    "requirements",
    "requirement",
    "responsibilities",
    "responsibility",
    "preferred",
    "mandatory",
    "must",
    "good",
    "strong",
    "excellent",
    "team",
    "teams",
    "project",
    "projects",
    "work",
    "working",
    "role",
    "job",
    "profile",
    "plus",
    "need",
    "needs",
    "needed",
    "seeking",
    "looking",
    "required",
    "require",
    "requires",
    "applicant",
    "applicants",
    "skills",
    "skill",
    "tools",
    "year",
    "years",
    "patient",
    "care",
}


def _is_noisy_term(term: str) -> bool:
    parts = [p for p in term.split() if p]
    if not parts:
        return True
    if all(p in NOISE_TERMS for p in parts):
        return True
    if len(parts) == 1 and len(parts[0]) <= 2:
        return True
    if len(parts) == 1 and parts[0] in NOISE_TERMS:
        return True
    return False


def _extract_dynamic_keywords(jd_text: str, resume_text: str, max_terms: int = 35) -> Tuple[Set[str], Set[str]]:
    """
    Extract dynamic keywords from JD/resume with TF-IDF so non-catalog terms
    can still be matched (for cross-domain usage).
    """
    jd = (jd_text or "").strip().lower()
    resume = (resume_text or "").strip().lower()
    if not jd or not resume:
        return set(), set()

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 1),
            token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.-]{1,}\b",
        )
        matrix = vectorizer.fit_transform([jd, resume])
    except ValueError:
        return set(), set()

    features = vectorizer.get_feature_names_out()
    jd_scores = matrix[0].toarray().ravel()
    resume_scores = matrix[1].toarray().ravel()

    def _top_terms(scores) -> Set[str]:
        ranked = scores.argsort()[::-1]
        out: List[str] = []
        for idx in ranked:
            score = float(scores[idx])
            if score <= 0:
                break
            term = features[idx].strip(" .,-_")
            if not term or _is_noisy_term(term):
                continue
            if len(term) < 4:
                continue
            out.append(term)
            if len(out) >= max_terms:
                break
        return set(out)

    return _top_terms(jd_scores), _top_terms(resume_scores)


def get_skill_match_details(job_description_clean: str, resume_clean: str) -> Dict[str, List[str]]:
    jd_text = job_description_clean or ""
    resume_text = resume_clean or ""

    jd_catalog = _tokenize_skills(jd_text)
    resume_catalog = _tokenize_skills(resume_text)

    jd_dynamic, resume_dynamic = _extract_dynamic_keywords(jd_text, resume_text)

    jd_terms = jd_catalog | jd_dynamic
    resume_terms = resume_catalog | resume_dynamic

    # Keep dynamic terms as fallback only when not already captured in catalog.
    # This preserves literal catalog matches while still allowing non-catalog
    # keywords to match consistently.
    jd_terms = {t for t in jd_terms if t}
    resume_terms = {t for t in resume_terms if t}

    matched = sorted(jd_terms & resume_terms)
    missing = sorted(jd_terms - resume_terms)

    # Keep output readable in UI.
    matched = matched[:35]
    missing = missing[:35]

    return {
        "matched_skills": matched,
        "missing_skills": missing,
    }
