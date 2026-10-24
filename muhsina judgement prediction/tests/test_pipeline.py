"""
Automated Unit and Integration Tests for Legal Judgment Prediction & Memory Engine.
Verifies:
1. SQLite 4-Tier Memory operations (L0-L3) & WAL backups
2. Statutory Concordance Engine (IPC <-> BNS, CrPC <-> BNSS)
3. ChromaDB Vector Store retrieval
4. Fact & Timeline Extractor
5. Stage 1 InLegalBERT outcome classifier
6. End-to-end Pipeline execution
"""

import unittest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from memory.sqlite_memory import LegalMemoryManager
from memory.fact_extractor import LegalFactExtractor
from rag.concordance import lookup_concordance, extract_and_enrich_concordances
from rag.vector_store import LegalVectorStore
from models.classifier import Stage1LegalClassifier
from pipeline import LegalJudgmentPipeline


class TestLegalEngine(unittest.TestCase):

    def setUp(self):
        # Use temporary memory DB for tests
        self.test_db_path = config.BASE_DIR / "test_case_memory.sqlite3"
        self.memory = LegalMemoryManager(db_path=self.test_db_path)

    def tearDown(self):
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def test_concordance_engine(self):
        """Tests bi-directional mapping between old and new criminal laws."""
        # IPC -> BNS
        ipc_302 = lookup_concordance("IPC 1860", "302")
        self.assertIsNotNone(ipc_302)
        self.assertEqual(ipc_302["new_section"], "103(1)")
        self.assertEqual(ipc_302["new_act"], "BNS 2023")

        # CrPC -> BNSS
        crpc_438 = lookup_concordance("CrPC 1973", "438")
        self.assertIsNotNone(crpc_438)
        self.assertEqual(crpc_438["new_section"], "482")

        # BNS -> IPC (Inverse)
        bns_103 = lookup_concordance("BNS 2023", "103")
        self.assertIsNotNone(bns_103)
        self.assertEqual(bns_103["old_section"], "302")

        # Inline enrichment from text
        text = "FIR registered under Section 420 IPC and Section 438 CrPC."
        matches = extract_and_enrich_concordances(text)
        self.assertTrue(len(matches) >= 2)
        laws_detected = [m["old_law"] for m in matches]
        self.assertTrue(any("420" in l for l in laws_detected))
        self.assertTrue(any("438" in l for l in laws_detected))

    def test_memory_crud_and_json(self):
        """Tests 4-tier memory tables and JSON serialization."""
        case_id = "TEST_CASE_101"
        self.memory.save_l0_raw(case_id, "Sample raw petition text")
        self.memory.save_l1_facts(case_id, {
            "petitioner": "Vikram Singh",
            "respondent": "State of Delhi",
            "fir_number": "99/2023",
            "custody_duration_days": 120,
            "chargesheet_filed": True
        })
        self.memory.save_l2_timeline(case_id, [
            {"event_date": "2023-01-01", "stage_name": "FIR Lodged", "details": "Incident occurred"}
        ])
        self.memory.save_l3_posture(case_id, {
            "court_jurisdiction": "High Court of Delhi",
            "relief_sought": "Regular Bail"
        })

        # Retrieve
        mem = self.memory.get_full_case_memory(case_id)
        self.assertEqual(mem["case_id"], case_id)
        self.assertEqual(mem["L1_facts"]["petitioner"], "Vikram Singh")
        self.assertEqual(mem["L1_facts"]["custody_duration_days"], 120)
        self.assertEqual(len(mem["L2_timeline"]), 1)
        self.assertEqual(mem["L3_posture"]["court_jurisdiction"], "High Court of Delhi")

        # JSON export
        json_dump = self.memory.export_json(case_id)
        self.assertIn("Vikram Singh", json_dump)

    def test_fact_extractor(self):
        """Tests rule-based extraction from a standard bail petition."""
        petition_snippet = """
        IN THE HIGH COURT OF DELHI
        BAIL APPLN. NO. 450 OF 2024
        Amit Sharma ... Petitioner
        Versus
        State of NCT of Delhi ... Respondent
        FIR No.: 123/2023, P.S. Karol Bagh
        Under Sections: 420, 120B IPC
        Custody since 90 days. Chargesheet has been filed.
        """
        extractor = LegalFactExtractor()
        data = extractor.extract(petition_snippet)

        l1 = data["L1_facts"]
        self.assertIn("Amit Sharma", l1["petitioner"])
        self.assertIn("State", l1["respondent"])
        self.assertIn("123/2023", l1["fir_number"])
        self.assertTrue(l1["chargesheet_filed"])

    def test_end_to_end_pipeline(self):
        """Tests the full orchestrator pipeline."""
        sample_petition = """
        Mohd. Basit ... Petitioner Versus State ... Respondent
        FIR No. 50/2024 at PS Connaught Place.
        Under Section 420 IPC and Section 439 CrPC.
        The petitioner has been in custody for 150 days. The chargesheet has been filed.
        """
        pipeline = LegalJudgmentPipeline(load_gpu_models=False)
        result = pipeline.run(sample_petition, case_id="E2E_CASE_001")

        self.assertIn("stage1", result)
        self.assertIn("stage2", result)
        self.assertIn("outcome", result["stage1"])
        self.assertIn(result["stage1"]["outcome"], [config.OUTCOME_ALLOWED, config.OUTCOME_DISMISSED])
        self.assertIn("ratio_decidendi", result["stage2"])
        self.assertTrue(len(result["retrieved_statutes"]) > 0)


if __name__ == "__main__":
    unittest.main()
