"""
Hybrid Legal Knowledge Retriever for Effective LJP V6.
Combines exact word-boundary BM25 lexical retrieval with dense semantic vector scoring.
Fixes F-18 (no substring bugs), F-19 (instant memory re-indexing), and F-15 (correct essential_ingredients).
"""

import math
import os
import json
import re
from typing import List, Dict, Any, Optional
from .schemas import CandidateKnowledge, AtomicFacts


class HybridLegalRetriever:
    """Production-grade hybrid retriever combining token-exact BM25 and dense semantic similarity."""

    def __init__(self, kb_path: Optional[str] = None):
        if kb_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_path = os.path.join(base_dir, "knowledge_base", "statutes_dual_code.json")

        self.kb_path = kb_path
        self.statutes: List[Dict[str, Any]] = []
        self._load_corpus()
        self._init_dense_embedder()

    def _load_corpus(self):
        """Loads canonical statutes and builds BM25 index."""
        if os.path.exists(self.kb_path):
            with open(self.kb_path, "r", encoding="utf-8") as f:
                self.statutes = json.load(f)
        else:
            raise FileNotFoundError(f"Statutory KB not found at {self.kb_path}")

        # Build corpus inverted index for BM25
        self.doc_count = len(self.statutes)
        self.doc_lengths = []
        self.inverted_index: Dict[str, Dict[int, int]] = {}
        self.doc_tokens: List[List[str]] = []

        total_tokens = 0
        for doc_id, statute in enumerate(self.statutes):
            combined_text = f"{statute['ipc_section']} {statute['bns_section']} {statute['statute_title']} {statute['charge_category']} {statute['legal_definition']} {' '.join(statute['essential_ingredients'])}"
            tokens = self._tokenize(combined_text)
            self.doc_tokens.append(tokens)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_tokens += doc_len

            term_freqs: Dict[str, int] = {}
            for t in tokens:
                term_freqs[t] = term_freqs.get(t, 0) + 1

            for term, freq in term_freqs.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = {}
                self.inverted_index[term][doc_id] = freq

        self.avg_doc_len = total_tokens / max(1, self.doc_count)

    def _init_dense_embedder(self):
        """Initializes dense sentence transformer and cross-encoder on GPU (Kaggle 30GB CUDA) or TF-IDF fallback."""
        self.dense_model = None
        self.cached_embeddings = None
        self.cross_encoder = None
        self.device = "cpu"

        try:
            import torch
            from sentence_transformers import SentenceTransformer, CrossEncoder
            
            if torch.cuda.is_available():
                self.device = "cuda"
            
            # High-performance legal / semantic bi-encoder
            model_candidate = os.getenv("LJP_RETRIEVER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            self.dense_model = SentenceTransformer(model_candidate, device=self.device)
            if self.device == "cuda":
                self.dense_model = self.dense_model.half()

            corpus_texts = [
                f"{s['statute_title']}. {s['legal_definition']} Applicable charges: {s['charge_category']}."
                for s in self.statutes
            ]
            self.cached_embeddings = self.dense_model.encode(
                corpus_texts,
                convert_to_tensor=True,
                normalize_embeddings=True,
                device=self.device
            )

            # Optional GPU Cross-Encoder Reranker
            try:
                self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device=self.device)
            except Exception:
                self.cross_encoder = None

        except Exception:
            self.dense_model = None
            self.cross_encoder = None

    def _tokenize(self, text: str) -> List[str]:
        """Strict word-boundary tokenization preventing substring bleed."""
        lower = text.lower()
        # Strictly tokenize words, stripping punctuation and non-alphanumeric
        tokens = re.findall(r"\b[a-z0-9_]{3,}\b", lower)
        # Filter general English stopwords but preserve legal terms
        stopwords = {
            "the", "and", "for", "with", "that", "this", "from", "any", "which", "shall",
            "been", "have", "were", "they", "their", "under", "where", "into", "more"
        }
        return [t for t in tokens if t not in stopwords]

    def _compute_bm25_score(self, query_tokens: List[str], doc_id: int) -> float:
        """Computes Okapi BM25 score with k1=1.5 and b=0.75."""
        k1 = 1.5
        b = 0.75
        doc_len = self.doc_lengths[doc_id]
        score = 0.0

        for term in query_tokens:
            if term not in self.inverted_index:
                continue
            df = len(self.inverted_index[term])
            idf = math.log(1.0 + (self.doc_count - df + 0.5) / (df + 0.5))
            tf = self.inverted_index[term].get(doc_id, 0)
            if tf > 0:
                numerator = tf * (k1 + 1.0)
                denominator = tf + k1 * (1.0 - b + b * (doc_len / self.avg_doc_len))
                score += idf * (numerator / denominator)
        return max(0.0, score)

    def _compute_dense_similarity(self, query_text: str, doc_id: int) -> float:
        """Computes dense cosine similarity between query and statute representation."""
        if self.dense_model is not None and self.cached_embeddings is not None:
            try:
                import torch
                query_emb = self.dense_model.encode(query_text, convert_to_tensor=True, normalize_embeddings=True)
                cosine = torch.dot(query_emb, self.cached_embeddings[doc_id]).item()
                return max(0.0, min(1.0, float(cosine)))
            except Exception:
                pass

        # TF-IDF Cosine Similarity Fallback
        q_tokens = self._tokenize(query_text)
        d_tokens = self.doc_tokens[doc_id]
        if not q_tokens or not d_tokens:
            return 0.0

        q_set = set(q_tokens)
        d_set = set(d_tokens)
        overlap = len(q_set.intersection(d_set))
        return overlap / math.sqrt(len(q_set) * len(d_set))

    def retrieve(self, case_text: str, facts: AtomicFacts, top_k: Optional[int] = None) -> List[CandidateKnowledge]:
        """
        Executes hybrid retrieval:
        Augments raw query with atomic legal tokens extracted from the narrative.
        """
        # Formulate enriched query
        query_components = [case_text[:600]]
        if facts.death_caused:
            query_components.append("death murder homicide post-mortem fatal")
        if facts.is_sudden_fight:
            query_components.append("sudden fight quarrel heat of passion without premeditation exception 4")
        if facts.has_premeditation:
            query_components.append("premeditated murder intention to cause death ambush")
        if "attempt_to_murder" in facts.extracted_tokens:
            query_components.append("attempt to murder 307 109 overt act towards murder life-threatening")
        if facts.injury_severity == "Grievous":
            query_components.append("voluntarily causing grievous hurt 326 118 dangerous weapons acid fractures")
        elif facts.injury_severity == "Simple":
            query_components.append("voluntarily causing simple hurt 324 323 pain assault")
        if facts.is_theft:
            query_components.append("theft dishonest taking movable property without consent 379")
        if facts.is_dacoity:
            query_components.append("dacoity 395 310 five or more persons conjointly robbing looted")
        elif facts.is_robbery:
            query_components.append("robbery force violence extorted instant death hurt 392")
        if facts.is_fraud_or_cheating:
            query_components.append("cheating fraud deception dishonestly inducing delivery of property 420")
        if facts.is_forgery:
            query_components.append("forgery false document valuable security electronic record 468 471")
        if facts.is_breach_of_trust:
            query_components.append("criminal breach of trust 406 316 entrusted dominion over property")
        if getattr(facts, "is_breach_of_trust_clerk_servant", False):
            query_components.append("criminal breach of trust clerk servant employee 408 316")
        if getattr(facts, "is_criminal_negligence", False):
            query_components.append("causing death by negligence rash negligent driving vehicle 304a 106")
        if getattr(facts, "is_sexual_harassment", False):
            query_components.append("sexual harassment unwelcome remarks demands 354a 75")
        if facts.is_matrimonial:
            query_components.append("cruelty harassment husband in-laws dowry 498a 304b")
        if facts.is_intimidation:
            query_components.append("criminal intimidation 506 351 threatening injury reputation")
        if getattr(facts, "is_criminal_trespass", False):
            query_components.append("criminal trespass entered property without permission 447 329 fenced boundary")
        if getattr(facts, "is_defamation", False):
            query_components.append("defamation harm reputation published false social media post 500 356")
        if getattr(facts, "is_housebreaking", False):
            query_components.append("house-breaking lurking house-trespass night rear window dwelling house 457 331")
        if getattr(facts, "is_theft_in_dwelling", False):
            query_components.append("theft dwelling house residential building laptop gold 380 305")
        if getattr(facts, "is_robbery_with_hurt", False):
            query_components.append("robbery causing hurt knife chain snatching 394 309")
        if getattr(facts, "is_corruption_or_bribery", False):
            query_components.append("corruption bribery public servant illegal gratification vigilance trap marked notes 7")
        if getattr(facts, "is_suicide_abetment", False):
            query_components.append("abetment of suicide suicide note mental physical torture 306 108")
        if getattr(facts, "is_ndps_narcotics", False):
            query_components.append("ndps act narcotics possession commercial quantity heroin diacetylmorphine 21")
        if getattr(facts, "is_cheque_dishonour", False):
            query_components.append("negotiable instruments act dishonour of cheque insufficient funds statutory notice 138")
        if getattr(facts, "is_pocso_child_abuse", False):
            query_components.append("pocso act child sexual abuse aggravated penetrative sexual assault student 6 376")
        if facts.is_commercial_civil_dispute:
            query_components.append("civil commercial contract invoice arbitration quash 482 528")

        query_str = " ".join(query_components)
        query_tokens = self._tokenize(query_str)

        # Calculate BM25 scores
        raw_bm25_scores = [self._compute_bm25_score(query_tokens, i) for i in range(self.doc_count)]
        max_bm25 = max(raw_bm25_scores) if raw_bm25_scores and max(raw_bm25_scores) > 0 else 1.0

        candidates: List[CandidateKnowledge] = []
        for i, statute in enumerate(self.statutes):
            norm_bm25 = raw_bm25_scores[i] / max_bm25
            dense_sim = self._compute_dense_similarity(case_text[:512], i)

            # Combined weighted score
            combined = 0.55 * norm_bm25 + 0.45 * dense_sim

            candidate = CandidateKnowledge(
                id=statute["id"],
                ipc_section=statute["ipc_section"],
                bns_section=statute["bns_section"],
                statute_title=statute["statute_title"],
                charge_category=statute["charge_category"],
                statutory_ceiling_tier=statute["statutory_ceiling_tier"],
                statutory_max_years=statute["statutory_max_years"],
                lexical_bm25_score=round(norm_bm25, 4),
                dense_cosine_score=round(dense_sim, 4),
                combined_relevance=round(combined, 4),
                matched_ingredients=[],
                missing_ingredients=[]
            )
            candidates.append(candidate)

        # Cross-Encoder GPU Reranking (when loaded in Kaggle 30GB GPU environment)
        if self.cross_encoder is not None and len(candidates) > 0:
            try:
                pairs = [[case_text[:400], f"{c.ipc_section} {c.statute_title} {c.charge_category}"] for c in candidates]
                cross_scores = self.cross_encoder.predict(pairs)
                min_s, max_s = float(min(cross_scores)), float(max(cross_scores))
                denom = (max_s - min_s) if max_s > min_s else 1.0
                for idx, c in enumerate(candidates):
                    norm_ce = float((cross_scores[idx] - min_s) / denom)
                    c.combined_relevance = round(0.40 * c.lexical_bm25_score + 0.30 * c.dense_cosine_score + 0.30 * norm_ce, 4)
            except Exception:
                pass

        # Sort descending by combined relevance
        candidates.sort(key=lambda c: c.combined_relevance, reverse=True)
        return candidates if top_k is None else candidates[:top_k]
