"""
Statutory & Case Law Vector Store using ChromaDB.
Indexes core Indian criminal statutes (IPC, CrPC, BNS, BNSS) and landmark Supreme Court ratios.
Enriches retrieved provisions with bidirectional concordance cross-references.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import config
from rag.concordance import lookup_concordance, extract_and_enrich_concordances

# Default seed knowledge corpus of landmark Indian statutory provisions & SC rulings
SEED_LEGAL_CORPUS: List[Dict[str, Any]] = [
    # Statutory Provisions (IPC)
    {
        "id": "IPC_302",
        "act": "IPC 1860",
        "section": "302",
        "title": "Murder - IPC Section 302",
        "text": "Section 302 IPC provides punishment for murder. Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine. Cognizable and non-bailable.",
        "category": "Substantive Law"
    },
    {
        "id": "IPC_420",
        "act": "IPC 1860",
        "section": "420",
        "title": "Cheating and dishonestly inducing delivery of property - IPC Section 420",
        "text": "Section 420 IPC deals with cheating and dishonestly inducing delivery of property. Essential ingredients: fraudulent or dishonest inducement causing the victim to deliver property or alter valuable security. Maximum term 7 years and fine.",
        "category": "Substantive Law"
    },
    {
        "id": "IPC_467",
        "act": "IPC 1860",
        "section": "467",
        "title": "Forgery of valuable security, will - IPC Section 467",
        "text": "Section 467 IPC penalizes whoever forges a document which purports to be a valuable security or a will. Punishable with imprisonment for life, or imprisonment extending to 10 years and fine.",
        "category": "Substantive Law"
    },
    {
        "id": "IPC_120B",
        "act": "IPC 1860",
        "section": "120B",
        "title": "Criminal Conspiracy - IPC Section 120B",
        "text": "Section 120B IPC defines punishment for criminal conspiracy. Agreement between two or more persons to do an illegal act. Conspirators are held equally liable for overt acts done in pursuance of conspiracy.",
        "category": "Substantive Law"
    },

    # Statutory Provisions (BNS 2023)
    {
        "id": "BNS_103",
        "act": "BNS 2023",
        "section": "103(1)",
        "title": "Murder - BNS Section 103",
        "text": "Section 103(1) of Bharatiya Nyaya Sanhita (BNS) 2023 replaces Section 302 IPC. Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.",
        "category": "Substantive Law"
    },
    {
        "id": "BNS_318",
        "act": "BNS 2023",
        "section": "318(4)",
        "title": "Cheating - BNS Section 318(4)",
        "text": "Section 318(4) of Bharatiya Nyaya Sanhita (BNS) 2023 replaces Section 420 IPC. Cheating and dishonestly inducing delivery of property or valuable security. Punishable with up to 7 years imprisonment.",
        "category": "Substantive Law"
    },

    # Procedural Law (CrPC & BNSS)
    {
        "id": "CRPC_438",
        "act": "CrPC 1973",
        "section": "438",
        "title": "Anticipatory Bail - CrPC Section 438",
        "text": "Section 438 CrPC empowers the High Court or Sessions Court to grant anticipatory bail to any person apprehending arrest in connection with a non-bailable offence. Principles: nature and gravity of accusation, role of accused, antecedent history, possibility of fleeing.",
        "category": "Procedural Law"
    },
    {
        "id": "CRPC_439",
        "act": "CrPC 1973",
        "section": "439",
        "title": "Regular Bail - CrPC Section 439",
        "text": "Section 439 CrPC governs special powers of High Court or Sessions Court regarding bail. A person accused of an offence and in custody may be released on bail subject to conditions. Fundamental consideration: bail is the rule and jail is the exception.",
        "category": "Procedural Law"
    },
    {
        "id": "BNSS_482",
        "act": "BNSS 2023",
        "section": "482",
        "title": "Direction for Grant of Bail (Anticipatory Bail) - BNSS Section 482",
        "text": "Section 482 of Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 replaces Section 438 CrPC for Anticipatory Bail. Directs that in the event of arrest, such person shall be released on bail on specified terms.",
        "category": "Procedural Law"
    },
    {
        "id": "BNSS_483",
        "act": "BNSS 2023",
        "section": "483",
        "title": "Special powers of High Court or Sessions regarding bail (Regular Bail) - BNSS Section 483",
        "text": "Section 483 of Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 replaces Section 439 CrPC. Re-enacts the power of Sessions Court and High Court to grant regular bail to an undertrial prisoner in custody.",
        "category": "Procedural Law"
    },
    {
        "id": "CRPC_482",
        "act": "CrPC 1973",
        "section": "482",
        "title": "Inherent Powers of High Court / Quashing - CrPC Section 482",
        "text": "Section 482 CrPC saves the inherent powers of the High Court to make such orders as necessary to give effect to any order under CrPC or prevent abuse of the process of any court or secure the ends of justice. Used to quash baseless FIRs.",
        "category": "Procedural Law"
    },
    {
        "id": "BNSS_528",
        "act": "BNSS 2023",
        "section": "528",
        "title": "Saving of Inherent Powers of High Court - BNSS Section 528",
        "text": "Section 528 of BNSS 2023 replaces Section 482 CrPC. High Court retains unhampered inherent jurisdiction to prevent abuse of judicial process and quash criminal proceedings where allegations disclose purely civil dispute or no prima facie offence.",
        "category": "Procedural Law"
    },

    # Landmark Supreme Court Precedents
    {
        "id": "SC_SATENDER_ANTIL",
        "act": "Supreme Court Precedent",
        "section": "Guidelines",
        "title": "Satender Kumar Antil v. CBI (2022) 10 SCC 51",
        "text": "Supreme Court held that bail is the rule and jail is the exception. Categorized offences into Category A (<= 7 years imprisonment, no routine arrest without compliance with 41/41A CrPC), Category B (offences punishable with death or life imprisonment), Category C (special acts like NDPS, PMLA), and Category D (economic offences).",
        "category": "Precedent"
    },
    {
        "id": "SC_CHIDAMBARAM",
        "act": "Supreme Court Precedent",
        "section": "Triple Test",
        "title": "P. Chidambaram v. Directorate of Enforcement (2019) 9 SCC 24",
        "text": "Supreme Court established the Triple Test for bail in economic offences: (1) Flight risk / abscondence danger, (2) Tampering with documentary or digital evidence, (3) Influencing or threatening prosecution witnesses. Incarceration cannot be punitive before guilt is proved.",
        "category": "Precedent"
    },
    {
        "id": "SC_BHAJAN_LAL",
        "act": "Supreme Court Precedent",
        "section": "Quashing Principles",
        "title": "State of Haryana v. Bhajan Lal (1992) Supp (1) SCC 335",
        "text": "Laid down the 7 cardinal categories where High Court should exercise inherent jurisdiction to quash an FIR: (1) Where allegations in FIR do not prima facie constitute any offence, (2) Where allegations are absurd or inherently improbable, (3) Where criminal proceeding is manifestly attended with mala fide or personal grudge.",
        "category": "Precedent"
    },
    {
        "id": "SC_SANJAY_CHANDRA",
        "act": "Supreme Court Precedent",
        "section": "Pre-trial Detention",
        "title": "Sanjay Chandra v. CBI (2012) 1 SCC 40",
        "text": "Supreme Court ruled that the object of bail is neither punitive nor preventive. Deprivation of liberty must be considered a punishment. If trial is prolonged and evidence is largely documentary already seized by police, detention in judicial custody is unjustified.",
        "category": "Precedent"
    }
]


class LegalVectorStore:
    def __init__(self, persist_directory: Optional[Path] = None):
        self.persist_dir = persist_directory or config.CHROMA_PERSIST_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection = None
        self._init_store()

    def _init_store(self):
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            client = chromadb.PersistentClient(path=str(self.persist_dir))
            emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=config.EMBEDDING_MODEL_NAME
            )
            self.collection = client.get_or_create_collection(
                name="indian_legal_statutes_precedents",
                embedding_function=emb_fn
            )

            # Seed default corpus if collection is empty
            if self.collection.count() == 0:
                self._seed_corpus()
        except Exception as e:
            print(f"[Warning] ChromaDB initialization skipped/deferred: {e}. Fallback keyword search will be active.")

    def _seed_corpus(self):
        ids = [doc["id"] for doc in SEED_LEGAL_CORPUS]
        documents = [f"{doc['title']}\n{doc['text']}" for doc in SEED_LEGAL_CORPUS]
        metadatas = [
            {
                "act": doc["act"],
                "section": doc["section"],
                "title": doc["title"],
                "category": doc["category"]
            }
            for doc in SEED_LEGAL_CORPUS
        ]
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves relevant statutes/precedents for a given legal query,
        and enriches each result with bi-directional concordance cross-references.
        """
        results: List[Dict[str, Any]] = []

        if self.collection:
            try:
                res = self.collection.query(
                    query_texts=[query],
                    n_results=min(top_k, self.collection.count() or 1)
                )
                if res and res["documents"] and len(res["documents"][0]) > 0:
                    for i in range(len(res["documents"][0])):
                        doc_text = res["documents"][0][i]
                        meta = res["metadatas"][0][i] if res["metadatas"] else {}
                        doc_id = res["ids"][0][i]

                        # Check concordance
                        concordance = lookup_concordance(meta.get("act", ""), meta.get("section", ""))

                        results.append({
                            "id": doc_id,
                            "title": meta.get("title", doc_id),
                            "act": meta.get("act", ""),
                            "section": meta.get("section", ""),
                            "category": meta.get("category", ""),
                            "snippet": doc_text,
                            "concordance": concordance
                        })
                    return results
            except Exception as e:
                print(f"[Warning] ChromaDB search error: {e}. Using fallback corpus search.")

        # Fallback keyword match from SEED_LEGAL_CORPUS
        q_lower = query.lower()
        scored = []
        for doc in SEED_LEGAL_CORPUS:
            score = 0
            if doc["act"].lower() in q_lower:
                score += 3
            if doc["section"].lower() in q_lower:
                score += 5
            for word in doc["title"].lower().split():
                if word in q_lower:
                    score += 2
            for word in ["bail", "quashing", "murder", "cheating", "custody", "chargesheet"]:
                if word in q_lower and word in doc["text"].lower():
                    score += 2
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        for _, doc in scored[:top_k]:
            concordance = lookup_concordance(doc["act"], doc["section"])
            results.append({
                "id": doc["id"],
                "title": doc["title"],
                "act": doc["act"],
                "section": doc["section"],
                "category": doc["category"],
                "snippet": f"{doc['title']}\n{doc['text']}",
                "concordance": concordance
            })

        return results
