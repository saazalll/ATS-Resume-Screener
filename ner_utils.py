import spacy
from typing import Dict, List

# Load the spaCy model globally
try:
    # Try loading the large model if presidio downloaded it, otherwise fallback to sm
    try:
        nlp = spacy.load("en_core_web_lg")
    except OSError:
        nlp = spacy.load("en_core_web_sm")
except Exception as e:
    nlp = None
    print(f"Warning: Failed to load spaCy model. NER will be disabled. Error: {e}")

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extracts organizations (ORG) and dates/durations (DATE) from text using spaCy NER.
    """
    if not nlp or not text or not text.strip():
        return {"dates": [], "organizations": []}
        
    doc = nlp(text)
    
    dates = []
    orgs = []
    
    for ent in doc.ents:
        if ent.label_ == "DATE":
            # Filter out very short meaningless dates or raw numbers if spacy misclassified
            clean_date = ent.text.strip().lower()
            if len(clean_date) > 3 and clean_date not in dates:
                dates.append(clean_date.title())
        elif ent.label_ == "ORG":
            clean_org = ent.text.strip()
            # Filter out generic or overly long misclassifications
            if len(clean_org) > 2 and len(clean_org) < 40 and clean_org not in orgs:
                orgs.append(clean_org)
                
    return {
        "dates": list(set(dates)),
        "organizations": list(set(orgs))
    }
