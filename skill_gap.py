import re
from typing import Dict, List, Set


COMMON_SKILL_SET = {
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "machine",
    "learning",
    "artificial",
    "intelligence",
    "software",
    "development",
    "data",
    "analysis",
    "nlp",
    "streamlit",
    "flask",
    "django",
    "react",
    "node",
    "javascript",
    "html",
    "css",
    "excel",
    "tableau",
    "powerbi",
    "communication",
    "leadership",
    "problem",
    "solving",
    "statistics",
}

COMMON_SKILL_PHRASES = {
    "machine learning",
    "artificial intelligence",
    "software development",
    "data analysis",
    "problem solving",
}

SKILL_ALIASES = {
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "machinelearning": "machine learning",
    "artificialintelligence": "artificial intelligence",
    "softwaredevelopment": "software development",
}


def _tokenize_skills(text: str) -> Set[str]:
    text_l = text.lower()
    matched: Set[str] = set()
    tokens = re.findall(r"[a-zA-Z0-9+#.-]+", text_l)
    token_set = set(tokens)
    joined = "".join(tokens)

    # Match multi-word skills first so they appear as meaningful phrases.
    for phrase in COMMON_SKILL_PHRASES:
        words = phrase.split()
        exact_phrase = bool(re.search(rf"\b{re.escape(phrase)}\b", text_l))
        all_words_present = all(w in token_set for w in words)
        merged_present = "".join(words) in joined
        if exact_phrase or all_words_present or merged_present:
            matched.add(phrase)

    token_matches = {t for t in tokens if t in COMMON_SKILL_SET}

    # Map shorthand/merged variants to canonical phrase skills.
    for token in token_set:
        if token in SKILL_ALIASES:
            matched.add(SKILL_ALIASES[token])

    # If a phrase is present, suppress its component single-word tokens.
    phrase_parts = set()
    for phrase in matched:
        phrase_parts.update(phrase.split())
    token_matches -= phrase_parts

    return matched | token_matches


def get_skill_match_details(job_description_clean: str, resume_clean: str) -> Dict[str, List[str]]:
    jd_skills = _tokenize_skills(job_description_clean)
    resume_skills = _tokenize_skills(resume_clean)

    matched = sorted(jd_skills & resume_skills)
    missing = sorted(jd_skills - resume_skills)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
    }
