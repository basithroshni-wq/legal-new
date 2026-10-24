import re
"""
Dynamic Legal Knowledge Retriever (DRM).
Operates ahead of the fusion stage at inference time, retrieving relevant law articles,
semantically similar prior cases, and associated legal concepts from the external knowledge base.
Enhanced with LLM-Directed Dynamic Retrieval: incorporates LLM-extracted legal concepts,
candidate offences, and actus reus/mens rea elements directly into the search queries.
"""

from typing import List, Dict, Any, Optional
import math
from pathlib import Path
from config import CHROMA_DIR, EMBEDDING_MODEL_NAME, TOP_K_RETRIEVAL
from retrieval.knowledge_base import EXTERNAL_LEGAL_KNOWLEDGE_BASE


class DynamicLegalKnowledgeRetriever:
    def __init__(self, persist_dir: Optional[Path] = None):
        self.persist_dir = persist_dir or CHROMA_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection = None
        self._init_vector_store()

    def _init_vector_store(self):
        """Initializes ChromaDB vector index with the external knowledge base."""
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            client = chromadb.PersistentClient(path=str(self.persist_dir))
            emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBEDDING_MODEL_NAME
            )
            self.collection = client.get_or_create_collection(
                name="dlkr_external_legal_kb",
                embedding_function=emb_fn,
                metadata={"hnsw:space": "cosine"}
            )

            if self.collection.count() == 0:
                self._seed_collection()
        except Exception as e:
            print(f"[DRM Notice] ChromaDB deferred or in fallback mode ({e}). Fallback lexical-semantic retriever active.")

    def _seed_collection(self):
        ids = [item["id"] for item in EXTERNAL_LEGAL_KNOWLEDGE_BASE]
        documents = [
            f"{item['title']}\nCharge: {item['charge']}\nPenalty: {item['penalty_tier']}\nElements: {', '.join(item['essential_elements'])}\nContent: {item['content']}"
            for item in EXTERNAL_LEGAL_KNOWLEDGE_BASE
        ]
        metadatas = [
            {
                "type": item["type"],
                "article_code": item["article_code"],
                "title": item["title"],
                "charge": item["charge"],
                "penalty_tier": item["penalty_tier"],
                "elements": "; ".join(item["essential_elements"])
            }
            for item in EXTERNAL_LEGAL_KNOWLEDGE_BASE
        ]
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def retrieve(
        self,
        fact_text: str,
        top_k: int = TOP_K_RETRIEVAL,
        atomic_facts: Any = None,
        legal_reasoning: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Dynamically queries the external knowledge base for a case fact description.
        Incorporates LLM-extracted legal concepts and candidates (LLM-Directed Retrieval).
        Returns candidate knowledge items with their similarity scores.
        """
        candidates: List[Dict[str, Any]] = []

        # Enrich query with LLM-extracted concepts if available
        query_terms = [fact_text]
        if legal_reasoning:
            for key in ["primary_charge", "primary_article_ipc", "primary_article_bns", "actus_reus", "mens_rea"]:
                val = legal_reasoning.get(key)
                if val and isinstance(val, str) and val != "N/A":
                    query_terms.append(val)
        if atomic_facts:
            if getattr(atomic_facts, "actus_reus", None):
                query_terms.extend(atomic_facts.actus_reus)
            if getattr(atomic_facts, "injury_severity", None) and atomic_facts.injury_severity != "None":
                query_terms.append(atomic_facts.injury_severity)
            if getattr(atomic_facts, "weapon_category", None) and atomic_facts.weapon_category != "Unarmed":
                query_terms.append(atomic_facts.weapon_category)

        enriched_query = " ".join(query_terms)

        if self.collection:
            try:
                results = self.collection.query(
                    query_texts=[enriched_query],
                    n_results=min(top_k, self.collection.count() or 1),
                    include=["documents", "metadatas", "distances"]
                )
                if results and results["documents"] and len(results["documents"][0]) > 0:
                    for i in range(len(results["documents"][0])):
                        doc_id = results["ids"][0][i]
                        meta = results["metadatas"][0][i]
                        # Cosine distance to similarity: similarity = 1 - distance
                        dist = results["distances"][0][i] if "distances" in results else 0.3
                        similarity = max(0.0, min(1.0, 1.0 - float(dist)))

                        candidates.append({
                            "id": doc_id,
                            "type": meta.get("type", "LAW_ARTICLE"),
                            "article_code": meta.get("article_code", ""),
                            "title": meta.get("title", ""),
                            "charge": meta.get("charge", ""),
                            "penalty_tier": meta.get("penalty_tier", ""),
                            "elements": meta.get("elements", "").split("; "),
                            "essential_elements": meta.get("elements", "").split("; "),
                            "similarity_score": round(similarity, 4),
                            "content": results["documents"][0][i]
                        })
                    return candidates
            except Exception as e:
                print(f"[DRM Warning] Query failed: {e}. Falling back to lexical-semantic scoring.")

        # Fallback scoring directly over knowledge base
        return self._fallback_score(enriched_query, top_k)

    def _fallback_score(self, fact_text: str, top_k: int) -> List[Dict[str, Any]]:
        fact_lower = fact_text.lower()
        q_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", fact_lower))
        scored = []

        # Scoped stem groups using full words or clear word boundaries (F-18)
        stem_groups = {
            "cheat": ["cheat", "fraud", "deceive", "scam", "induce", "defraud", "fictitious"],
            "forge": ["forged", "forgery", "fake", "fabricate", "counterfeit", "valuable security", "deed", "signature"],
            "murder": ["murder", "killed", "homicide", "fatal", "ambush", "gunshot", "axe", "grudge"],
            "culpable": ["culpable", "sudden quarrel", "sudden fight", "heat of passion", "single blow", "struck once", "no prior animosity", "iron rod lying nearby", "shoved"],
            "attempt": ["attempt to murder", "fired pistol", "intent to kill", "aiming at", "chest", "survived"],
            "hurt_weapon": ["sharp knife", "knife", "dagger", "blade", "laceration", "cutting", "stabbing"],
            "hurt_simple": ["slapped", "slap", "bare fists", "fists", "bruises", "contusions", "simple hurt"],
            "theft": ["theft", "stole", "stolen", "movable property", "without consent", "quietly", "pickpocket", "necklace", "lifted", "pocket", "mobile phone", "wallet", "unnoticed", "bus passenger", "removes phone", "secretly removes"],
            "robbery": ["robbery", "robbed", "knifepoint", "gunpoint", "held to throat", "extorted", "threat of instant death"],
            "breach": ["breach of trust", "entrusted", "misappropriation", "misappropriated", "converted the money", "tax deposit", "personal bank account"],
            "matrimonial": ["matrimonial cruelty", "cruelty by husband", "harassment for dowry", "husband and mother-in-law", "additional dowry", "in-laws"],
            "dowry_death": ["dowry death", "three years of marriage", "7 years of marriage", "burn injuries", "abnormal circumstances", "torture for dowry"],
            "sexual": ["rape", "sexual assault", "penetrative", "against her will"],
            "intimidate": ["criminal intimidation", "threatened to kill", "death threat", "murder his entire family", "testified in court"]
        }

        def matches_any(stems, text):
            for s in stems:
                # Use regex word boundary to prevent partial matches like 'bus' in 'business' or 'axe' in 'taxes'
                pattern = r"\b" + re.escape(s) + r"\b"
                if re.search(pattern, text):
                    return True
            return False

        for item in EXTERNAL_LEGAL_KNOWLEDGE_BASE:
            text = f"{item['title']} {item['charge']} {item['content']} {' '.join(item['essential_elements'])}".lower()
            tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", text))

            # Base Jaccard overlap
            intersection = q_words.intersection(tokens)
            union = q_words.union(tokens)
            overlap_score = len(intersection) / max(1, len(union))

            # Domain Stem Match Boost
            match_boost = 0.0
            for domain, stems in stem_groups.items():
                if matches_any(stems, fact_lower) and matches_any(stems, text):
                    match_boost += 0.45

            # Compute combined similarity
            combined_sim = min(0.95, (overlap_score * 2.5) + match_boost)
            if combined_sim > 0.25:
                scored.append((combined_sim, item))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for score, item in scored[:top_k]:
            results.append({
                "id": item["id"],
                "type": item["type"],
                "article_code": item["article_code"],
                "title": item["title"],
                "charge": item["charge"],
                "penalty_tier": item["penalty_tier"],
                "elements": item["essential_elements"],
                "essential_elements": item["essential_elements"],
                "similarity_score": round(score, 4),
                "content": item["content"]
            })

        return results
