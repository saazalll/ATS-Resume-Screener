import re
from functools import lru_cache

import nltk
from nltk.corpus import stopwords

FALLBACK_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "or", "if", "but", "this",
    "these", "those", "you", "your", "we", "our", "they", "their", "i",
    "me", "my", "mine", "him", "his", "her", "hers", "them", "what",
    "which", "who", "whom", "when", "where", "why", "how", "can", "could",
    "should", "would", "do", "does", "did", "done", "not", "no", "yes",
    "than", "then", "so", "such", "too", "very", "also", "up", "down",
    "out", "over", "under", "again", "further", "about", "into", "through",
    "during", "before", "after", "above", "below", "off", "same", "other",
    "some", "any", "each", "few", "more", "most", "own", "both", "all",
}


@lru_cache(maxsize=1)
def _get_stopwords():
    """Lazy-load stopwords to avoid repeated downloads."""
    try:
        return set(stopwords.words("english"))
    except LookupError:
        try:
            nltk.download("stopwords", quiet=True)
            return set(stopwords.words("english"))
        except Exception:
            return FALLBACK_STOPWORDS


def clean_text(text: str) -> str:
    """Normalize text for ML pipeline."""
    if not text:
        return ""

    text = text.lower()
    # Preserve +, #, ., - inside tokens (e.g. c++, node.js)
    # Replaced trailing \b with a non-capturing group that allows the token to end in +, #, or a word character
    tokens = re.findall(r"(?u)\b[a-z](?:[a-z0-9+#.-]*[a-z0-9+#])?", text)

    sw = _get_stopwords()
    filtered_tokens = [tok for tok in tokens if tok not in sw and len(tok) > 1]

    return " ".join(filtered_tokens)
