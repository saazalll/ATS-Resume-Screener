from dataclasses import dataclass
from typing import List
import numpy as np
import re

@dataclass
class PredictionResult:
    label: str
    overall_score: float
    semantic_score: float
    hard_skills_score: float
    soft_skills_score: float
    
    # Backwards compatibility properties for app.py before Phase 2 UI updates
    @property
    def score_percent(self) -> float:
        return self.overall_score
        
    @property
    def confidence_percent(self) -> float:
        # Confidence is not strictly applicable to cosine similarity, return semantic score
        return self.semantic_score


# Global model reference
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        # Load model once at startup
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


class ATSMatcher:
    """
    Semantic-based ATS matcher replacing the old SVM.
    Uses sentence-transformers to compute cosine similarity between JD and Resume chunks.
    """

    def __init__(self):
        self.jd_embeddings = None
        self.jd_chunks = []

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into sentences/bullets to avoid truncation by the embedding model."""
        # Split on newlines or sentence boundaries
        lines = re.split(r'\n|(?<=[.!?])\s+', text)
        chunks = [line.strip() for line in lines if len(line.strip()) > 15]
        if not chunks:
            chunks = [text.strip()]
        return chunks

    def fit(self, job_description_clean: str):
        self.jd_chunks = self._chunk_text(job_description_clean)
        model = get_embedding_model()
        self.jd_embeddings = model.encode(self.jd_chunks)

    def predict_match(self, resume_clean: str) -> PredictionResult:
        if self.jd_embeddings is None:
            raise RuntimeError("Model must be fitted before prediction.")

        resume_chunks = self._chunk_text(resume_clean)
        if not resume_chunks or not resume_chunks[0]:
            return PredictionResult("Not Matched", 0.0, 0.0, 0.0, 0.0)

        model = get_embedding_model()
        resume_embeddings = model.encode(resume_chunks)

        from sklearn.metrics.pairwise import cosine_similarity
        sim_matrix = cosine_similarity(self.jd_embeddings, resume_embeddings)

        # Take the best matching resume chunk for each JD chunk, then average
        best_matches = np.max(sim_matrix, axis=1)
        raw_semantic_score = float(np.mean(best_matches))

        # Calibration based on Phase 7 Empirical Testing
        MIN_SIM = 0.30
        MAX_SIM = 0.55
        
        calibrated = (raw_semantic_score - MIN_SIM) / (MAX_SIM - MIN_SIM) * 100.0
        semantic_score = round(max(0.0, min(100.0, calibrated)), 2)

        # Phase 1 only replaces the semantic part. We default hard/soft to 0 here.
        # Phase 2 will compute and combine them properly.
        overall_score = semantic_score
        label = "Matched" if overall_score >= 50 else "Not Matched"

        return PredictionResult(
            label=label,
            overall_score=overall_score,
            semantic_score=semantic_score,
            hard_skills_score=0.0,
            soft_skills_score=0.0
        )
