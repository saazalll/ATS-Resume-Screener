from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

# Initialize engines globally to avoid reloading them on every request
try:
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
    anonymizer = AnonymizerEngine()
except Exception as e:
    # If spacy en_core_web_sm is missing, this will fail. We'll handle it gracefully.
    analyzer = None
    anonymizer = None
    print(f"Presidio Initialization Error: {e}")

def scrub_pii(text: str) -> str:
    """
    Scrub PII (Personally Identifiable Information) from text using Presidio.
    Targets: PERSON, EMAIL_ADDRESS, PHONE_NUMBER, LOCATION.
    """
    if not analyzer or not anonymizer:
        return text  # Fallback to returning original text if engine failed to load

    if not text or not text.strip():
        return text

    # Entities we care about for blind screening
    entities = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION"]

    results = analyzer.analyze(
        text=text,
        entities=entities,
        language='en'
    )

    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )

    return anonymized_result.text
