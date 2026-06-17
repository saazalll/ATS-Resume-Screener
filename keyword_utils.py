import re
from typing import Tuple, Set, List
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

SHARED_NOISE_TERMS = {
    "experience", "experienced", "knowledge", "ability", "candidate", "candidates",
    "requirements", "requirement", "responsibilities", "responsibility", "preferred",
    "mandatory", "must", "good", "strong", "excellent", "team", "teams", "project",
    "projects", "work", "working", "role", "job", "profile", "plus", "need", "needs",
    "needed", "seeking", "looking", "required", "require", "requires", "applicant",
    "applicants", "skills", "skill", "tools", "year", "years", "patient", "care",
    "with", "from", "that", "this", "have", "will", "your", "their", "using",
    "for", "and", "the", "you", "are", "our", "into"
}

def is_noisy_term(term: str) -> bool:
    parts = [p for p in term.split() if p]
    if not parts:
        return True
    if all(p in SHARED_NOISE_TERMS for p in parts):
        return True
    if len(parts) == 1 and len(parts[0]) <= 2:
        return True
    if len(parts) == 1 and parts[0] in SHARED_NOISE_TERMS:
        return True
    return False

def extract_dynamic_keywords(jd_text: str, resume_text: str, max_terms: int = 35) -> Tuple[Set[str], Set[str]]:
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
            token_pattern=r"(?u)\b[a-zA-Z](?:[a-zA-Z0-9+#.-]*[a-zA-Z0-9+#])?",
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
            if not term or is_noisy_term(term):
                continue
            if len(term) < 4:
                continue
            out.append(term)
            if len(out) >= max_terms:
                break
        return set(out)

    return _top_terms(jd_scores), _top_terms(resume_scores)

def extract_top_terms_freq(text: str, limit: int = 10) -> List[str]:
    """Fallback term extraction using term frequency."""
    raw_tokens = re.findall(r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.-]*", text.lower())
    tokens = [t.strip(" .,-_") for t in raw_tokens if t.strip(" .,-_")]
    filt = [t for t in tokens if t not in SHARED_NOISE_TERMS and len(t) > 3]
    freq = Counter(filt)
    return [w for w, _ in freq.most_common(limit)]
