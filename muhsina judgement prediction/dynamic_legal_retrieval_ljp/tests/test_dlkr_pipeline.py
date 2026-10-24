"""
Unit and Integration Tests for DLKR-LJP.
Verifies:
1. Dynamic Knowledge Retrieval from External KB
2. Relevance & Confidence Gate (Threshold cutoff & Element Consistency)
3. Prefix Knowledge Fusion formatting
4. 3-Head Multi-Task Prediction (Articles, Charges, Penalty)
5. Negation Handling & Element Consistency
6. End-to-End Pipeline Execution
"""

import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retrieval.dynamic_retriever import DynamicLegalKnowledgeRetriever
from gating.confidence_gate import RelevanceAndConfidenceGate
from models.prefix_fusion import PrefixKnowledgeFusion
from models.multi_task_heads import MultiTaskLegalPredictor
from pipeline import DynamicLjpPipeline


class TestDlkrPipeline(unittest.TestCase):

    def setUp(self):
        self.retriever = DynamicLegalKnowledgeRetriever()
        self.gate = RelevanceAndConfidenceGate()
        self.fusion = PrefixKnowledgeFusion()
        self.predictor = MultiTaskLegalPredictor()
        self.pipeline = DynamicLjpPipeline(load_transformer=False)

    def test_dynamic_retriever(self):
        """Tests that retriever fetches relevant candidates from external KB."""
        query = "The accused induced complainant to invest money and forged title deeds."
        candidates = self.retriever.retrieve(query, top_k=4)
        self.assertTrue(len(candidates) > 0)
        charges = [c["charge"].lower() for c in candidates]
        self.assertTrue(any("cheating" in c or "forgery" in c for c in charges))

    def test_relevance_and_confidence_gate(self):
        """Tests that the gate accepts relevant items and discards noise/element mismatches."""
        financial_facts = "The director of the bank cheated customers by transferring funds into fraudulent accounts."
        raw_candidates = self.retriever.retrieve(financial_facts, top_k=6)

        gate_res = self.gate.filter_knowledge(financial_facts, raw_candidates)
        gated = gate_res["gated_knowledge"]
        noise = gate_res["filtered_noise"]

        self.assertTrue(len(gated) > 0)
        gated_charges = [item["charge"].lower() for item in gated]
        self.assertTrue(any("cheating" in c or "breach" in c for c in gated_charges))

        for n in noise:
            self.assertIn("reason", n)

    def test_element_gate_rejection(self):
        """Tests that violent crimes are rejected when facts describe pure civil/commercial disputes."""
        pure_civil_facts = "Dispute over unpaid consulting invoices and delay in delivery of software source code."
        synthetic_murder_candidate = [{
            "id": "ART_IPC_302_BNS_103",
            "type": "LAW_ARTICLE",
            "article_code": "IPC_302_BNS_103",
            "title": "Murder (IPC Section 302 / BNS Section 103)",
            "charge": "Murder & Culpable Homicide",
            "penalty_tier": "Tier 4",
            "similarity_score": 0.80,
            "elements": ["Intention to cause death", "Bodily injury known to be likely to cause death"],
            "content": "Punishment for murder."
        }]

        gate_res = self.gate.filter_knowledge(pure_civil_facts, synthetic_murder_candidate)
        self.assertEqual(len(gate_res["gated_knowledge"]), 0)
        self.assertEqual(len(gate_res["filtered_noise"]), 1)
        self.assertIn("Element Consistency Gate", gate_res["filtered_noise"][0]["reason"])

    def test_prefix_fusion(self):
        """Tests prefix construction from gated items."""
        sample_gated = [{
            "title": "Cheating IPC 420",
            "charge": "Cheating & Financial Fraud",
            "penalty_tier": "Tier 2: 3 to 7 Years",
            "matched_elements": ["Deception", "Dishonest inducement"]
        }]
        fused_text, prefix_str = self.fusion.construct_fused_prompt("Case fact text here", sample_gated)
        self.assertIn("[LEGAL_KNOWLEDGE_PREFIX:", fused_text)
        self.assertIn("Cheating IPC 420", prefix_str)
        self.assertIn("Case fact text here", fused_text)

    def test_multi_head_prediction(self):
        """Tests the 3 prediction heads (Articles, Charges, Penalty)."""
        sample_gated = [{
            "article_code": "IPC_420_BNS_318",
            "title": "Cheating IPC 420",
            "charge": "Cheating & Financial Fraud",
            "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)"
        }]
        fused_text = "[PREFIX] Case facts about cheating and 420"
        fact_text = "Accused cheated victim under section 420 IPC of 50 lakhs."

        preds = self.predictor.predict(fused_text, fact_text, sample_gated)
        self.assertIn("head1_articles", preds)
        self.assertIn("head2_charges", preds)
        self.assertIn("head3_penalty_tiers", preds)
        self.assertIn("primary_penalty", preds)

        top_art = preds["head1_articles"][0]
        self.assertIn("420", top_art["article_id"])

        top_charge = preds["head2_charges"][0]
        self.assertIn("Cheating", top_charge["charge_name"])

    def test_negation_handling(self):
        """Tests that negation suppresses false positive charges."""
        fact_negated = "The accused was falsely implicated. No cheating occurred and no money was transferred."
        preds = self.predictor.predict("", fact_negated, [])
        top_charge = preds["head2_charges"][0]["charge_name"] if preds["head2_charges"] else ""
        cheat_score = next((c["probability"] for c in preds["head2_charges"] if "cheating" in c["charge_name"].lower()), 0.0)
        self.assertLess(cheat_score, 0.50)

    def test_survival_vs_murder(self):
        """Tests that victim survival suppresses Section 302 Murder in favor of Attempt (307) / Assault."""
        fact_survival = "The accused fired a pistol injuring the victim in the shoulder. The victim survived and was discharged from hospital."
        preds = self.predictor.predict("", fact_survival, [])
        top_art = preds["head1_articles"][0]["display_name"]
        self.assertNotIn("302", top_art)
        self.assertTrue("307" in top_art or "326" in top_art)

    def test_end_to_end_pipeline(self):
        """Tests complete pipeline run."""
        facts = "The accused fired gunshots killing the victim on spot due to long standing rivalry."
        res = self.pipeline.run(facts)

        self.assertIn("raw_candidates", res)
        self.assertIn("gated_knowledge", res)
        self.assertIn("filtered_noise", res)
        self.assertIn("predictions", res)
        self.assertIn("traceable_evidence", res)

        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        self.assertIn("Murder", top_chg)


    def test_exception_4_sudden_quarrel_single_blow(self):
        """Tests that sudden quarrel + single blow converts Murder (302) to Culpable Homicide (304 Part II)."""
        kakkanad_facts = "A contractor argued with a labourer over unpaid wages. The labourer shoved him, and the contractor picked up an iron rod lying nearby and struck once on the head. Labourer died next morning. No prior animosity or planning."
        res = self.pipeline.run(kakkanad_facts)
        top_art = res['predictions']['head1_articles'][0]['display_name']
        self.assertIn('304', top_art)
        self.assertNotIn('302', top_art)
        top_charge = res['predictions']['head2_charges'][0]['charge_name']
        self.assertIn('Culpable Homicide', top_charge)
        self.assertIn('Tier 3', res['predictions']['primary_penalty']['tier'])


    def test_judicial_consistency_verifier_reconciliation(self):
        """Tests that JCV catches statutory ceiling violations and reconciles penalty tier."""
        from models.judicial_verifier import JudicialConsistencyVerifier
        verifier = JudicialConsistencyVerifier()

        # Synthetic illegal combination: IPC 420 Cheating with Tier 4 Life Imprisonment
        synthetic_preds = {
            "head1_articles": [{"article_id": "IPC_420_BNS_318", "display_name": "IPC 420 | BNS 318", "probability": 0.90}],
            "head2_charges": [{"charge_name": "Cheating & Financial Fraud", "probability": 0.90}],
            "head3_penalty_tiers": [{"tier": "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)", "probability": 0.90}],
            "primary_penalty": {"tier": "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)", "probability": 0.90}
        }

        reconciled = verifier.verify_and_reconcile(synthetic_preds)
        audit = reconciled["judicial_consistency_audit"]
        self.assertEqual(audit["audit_status"], "RECONCILED BY JCV")
        self.assertTrue(len(audit["conflicts_detected"]) > 0)
        # Verify penalty was overridden to Tier 2 (max 7 years for Sec 420)
        self.assertIn("Tier 2", reconciled["primary_penalty"]["tier"])


if __name__ == "__main__":
    unittest.main()
