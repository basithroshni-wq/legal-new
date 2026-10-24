"""
End-to-End Orchestrator Pipeline for Indian Legal Judgment Prediction & Memory Engine.
Chains:
L0 Raw Ingestion -> L1/L2/L3 Extraction -> Statutory RAG & Concordance ->
Stage 1 InLegalBERT Classification -> Stage 2 Nyaya-LLaMA Reasoning -> 4-Tier Memory Persistence.
"""

import uuid
from typing import Dict, Any, Optional
import config
from memory.sqlite_memory import LegalMemoryManager
from memory.fact_extractor import LegalFactExtractor
from rag.concordance import extract_and_enrich_concordances
from rag.vector_store import LegalVectorStore
from models.classifier import Stage1LegalClassifier
from models.reasoning_engine import Stage2ReasoningEngine


class LegalJudgmentPipeline:
    def __init__(self, load_gpu_models: bool = False):
        self.memory = LegalMemoryManager()
        self.vector_store = LegalVectorStore()
        self.classifier = Stage1LegalClassifier()
        self.reasoning_engine = Stage2ReasoningEngine()
        self.fact_extractor = LegalFactExtractor()

        if load_gpu_models:
            self.load_models()

    def load_models(self):
        """Loads HuggingFace transformer models if environment has GPU."""
        print("[Pipeline] Initializing models...")
        self.classifier.load_model()
        self.reasoning_engine.load_model()
        print("[Pipeline] Initialization complete.")

    def run(self, petition_text: str, case_id: Optional[str] = None, source_filename: str = "") -> Dict[str, Any]:
        """
        Executes the full legal judgment prediction workflow.
        """
        if not case_id:
            case_id = f"CASE_{uuid.uuid4().hex[:8].upper()}"

        print(f"\n[Pipeline] === Processing Case: {case_id} ===")

        # Step 1: L0 Raw Ingestion
        print("[Step 1/6] Ingesting L0 Raw Document into SQLite Memory...")
        self.memory.save_l0_raw(case_id, petition_text, source_filename)

        # Step 2: L1, L2, L3 Fact & Timeline Extraction
        print("[Step 2/6] Extracting L1 Atomic Facts, L2 Procedural Timeline, L3 Posture...")
        extracted_data = self.fact_extractor.extract(petition_text)
        l1_facts = extracted_data.get("L1_facts", {})
        l2_timeline = extracted_data.get("L2_timeline", [])
        l3_posture = extracted_data.get("L3_posture", {})

        # Persist extracted tiers to SQLite
        self.memory.save_l1_facts(case_id, l1_facts)
        self.memory.save_l2_timeline(case_id, l2_timeline)
        self.memory.save_l3_posture(case_id, l3_posture)

        # Step 3: Statutory Concordance & RAG Retrieval
        print("[Step 3/6] Retrieving Statutory Provisions & Performing Dual-Code Concordance...")
        query_terms = f"{l1_facts.get('alleged_acts_sections', '')} {l3_posture.get('relief_sought', '')} {l1_facts.get('summary_of_allegations', '')[:200]}"
        retrieved_statutes = self.vector_store.search(query_terms, top_k=3)

        # Also extract inline statutory cross-references (IPC <-> BNS, CrPC <-> BNSS)
        inline_concordances = extract_and_enrich_concordances(petition_text)

        # Step 4: Stage 1 InLegalBERT Classification
        print("[Step 4/6] Executing Stage 1 Statistical Outcome Prediction...")
        stage1_result = self.classifier.predict(petition_text, l1_facts)

        # Step 5: Stage 2 Judicial Reasoning & Ratio Decidendi
        print("[Step 5/6] Generating Stage 2 Judicial Opinion and Ratio Decidendi...")
        case_mem = self.memory.get_full_case_memory(case_id)
        stage2_result = self.reasoning_engine.generate_opinion(
            case_mem,
            retrieved_statutes,
            stage1_result
        )

        # Step 6: Memory Persistence of Predictions
        print("[Step 6/6] Caching Final Prediction & Order in Memory Layer...")
        self.memory.save_prediction(
            case_id=case_id,
            stage1_outcome=stage1_result["outcome"],
            p_allowed=stage1_result["probability_allowed"],
            p_dismissed=stage1_result["probability_dismissed"],
            stage2_ratio=stage2_result["ratio_decidendi"],
            stage2_opinion=stage2_result["opinion_text"],
            statutes_cited=stage2_result.get("statutes_cited", [])
        )

        print(f"[Pipeline] Case {case_id} successfully adjudicated: {stage1_result['outcome']}.\n")

        return {
            "case_id": case_id,
            "stage1": stage1_result,
            "stage2": stage2_result,
            "L1_facts": l1_facts,
            "L2_timeline": l2_timeline,
            "L3_posture": l3_posture,
            "retrieved_statutes": retrieved_statutes,
            "concordances": inline_concordances,
            "memory_export_json": self.memory.export_json(case_id)
        }

    def backup_session(self) -> Dict[str, Any]:
        """Flushes and backups all SQLite memory to Google Drive."""
        return self.memory.backup_to_drive()
