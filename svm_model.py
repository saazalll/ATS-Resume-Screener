from dataclasses import dataclass
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC


@dataclass
class PredictionResult:
    label: str
    score_percent: float
    confidence_percent: float


class ATSMatcher:
    """
    SVM-based ATS matcher.

    We create a lightweight training set from the JD itself and a synthetic
    negative sample so the model can estimate match probability robustly.
    """

    def __init__(self):
        self.pipeline = Pipeline(
            steps=[
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=7000)),
                ("svm", SVC(kernel="linear", probability=True, random_state=42)),
            ]
        )
        self._is_fitted = False

    @staticmethod
    def _build_training_data(job_text: str) -> Tuple[List[str], List[int]]:
        positive = [
            job_text,
            f"required skills experience {job_text}",
            f"candidate profile {job_text}",
        ]

        negative = [
            "kitchen recipes cooking food ingredients baking",
            "sports football basketball baseball tournament league",
            "music dance singing guitar piano drums performance",
        ]

        X_train = positive + negative
        y_train = [1] * len(positive) + [0] * len(negative)
        return X_train, y_train

    def fit(self, job_description_clean: str):
        X_train, y_train = self._build_training_data(job_description_clean)
        self.pipeline.fit(X_train, y_train)
        self._is_fitted = True

    def predict_match(self, resume_clean: str) -> PredictionResult:
        if not self._is_fitted:
            raise RuntimeError("Model must be fitted before prediction.")

        probs = self.pipeline.predict_proba([resume_clean])[0]
        pos_prob = float(probs[1])
        neg_prob = float(probs[0])
        score = round(pos_prob * 100, 2)
        confidence = round(max(pos_prob, neg_prob) * 100, 2)
        label = "Matched" if score >= 50 else "Not Matched"

        return PredictionResult(label=label, score_percent=score, confidence_percent=confidence)
