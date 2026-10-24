"""
End-to-End Neuro-Symbolic Pipeline for Effective LJP V6.
Orchestrates:
1. Scoped Fact Extraction & Out-of-Domain Screening
2. Hybrid BM25 + Dense Semantic Retrieval
3. Dual-Check Relevance & Confidence Gating (RCG)
4. Calibrated Multi-Task Prediction (Articles, Charges, Tiers)
5. Judicial Consistency Verification & Symbolic Ceiling Enforcement (JCV)
6. Grounded Ratio Decidendi & Supreme Court Citation Synthesis
"""

import os
import json
from typing import Dict, Any, Optional
from .schemas import LjpPredictionResult, AtomicFacts, CandidateKnowledge
from .fact_extractor import ScopedFactExtractor
from .retriever import HybridLegalRetriever
from .gating import RelevanceAndConfidenceGate
from .predictor import CalibratedLegalPredictor
from .consistency_verifier import JudicialConsistencyVerifier


class EffectiveLjpPipeline:
    """Production-grade Neuro-Symbolic Legal Judgment Prediction Pipeline."""

    def __init__(self, kb_dir: Optional[str] = None):
        if kb_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            kb_dir = os.path.join(base_dir, "knowledge_base")

        statutes_path = os.path.join(kb_dir, "statutes_dual_code.json")
        precedents_path = os.path.join(kb_dir, "precedents.json")

        # Load raw KB dictionaries for gating lookups
        self.raw_kb_dict: Dict[str, Dict[str, Any]] = {}
        if os.path.exists(statutes_path):
            with open(statutes_path, "r", encoding="utf-8") as f:
                statutes_list = json.load(f)
                for item in statutes_list:
                    self.raw_kb_dict[item["id"]] = item

        self.precedents_list: list = []
        if os.path.exists(precedents_path):
            with open(precedents_path, "r", encoding="utf-8") as f:
                self.precedents_list = json.load(f)

        # Initialize pipeline stages
        self.extractor = ScopedFactExtractor()
        self.retriever = HybridLegalRetriever(kb_path=statutes_path)
        self.gate = RelevanceAndConfidenceGate(tau_relevance=0.10, theta_ingredient=0.15)
        self.predictor = CalibratedLegalPredictor(temperature=0.65)
        self.verifier = JudicialConsistencyVerifier()

    def run(self, case_narrative: str) -> LjpPredictionResult:
        """Executes full end-to-end legal judgment prediction workflow."""
        text = case_narrative.strip()

        # Step 1: Scoped Fact Extraction & Out-of-Domain Screening
        facts: AtomicFacts = self.extractor.extract(text)

        # Handle Out-of-Domain Abstention immediately (Fix F-09)
        if facts.is_out_of_domain:
            empty_penalty = self.predictor.predict([], facts)[2]
            _, _, _, audit_rep = self.verifier.verify_and_reconcile([], [], empty_penalty, facts)
            return LjpPredictionResult(
                case_summary=text[:200] + ("..." if len(text) > 200 else ""),
                is_abstained=True,
                abstain_message=f"ABSTAINED: {facts.out_of_domain_reason}",
                atomic_facts=facts,
                retrieved_statutes=[],
                filtered_out_candidates=[],
                top_articles=[],
                top_charges=[],
                penalty_prediction=empty_penalty,
                judicial_audit=audit_rep,
                ratio_decidendi="No legal ratio formulated: Narrative does not disclose ingredients of any cognizable criminal offence under IPC 1860 or BNS 2023.",
                landmark_precedents_cited=[]
            )

        # Step 2: Hybrid BM25 + Dense Semantic Retrieval
        retrieved_raw = self.retriever.retrieve(text, facts, top_k=None)

        # Step 3: Dual-Check Gating (RCG)
        gated_in, filtered_out = self.gate.audit_and_gate(retrieved_raw, facts, self.raw_kb_dict)

        # Step 4: Calibrated Multi-Task Prediction (Articles, Charges, Tiers)
        pred_articles, pred_charges, pred_penalty = self.predictor.predict(gated_in, facts)

        # Step 5: Judicial Consistency Verification (JCV) & Symbolic Ceiling Audit
        rec_articles, rec_charges, rec_penalty, audit_report = self.verifier.verify_and_reconcile(
            pred_articles, pred_charges, pred_penalty, facts
        )

        # Step 6: Derive Ratio Decidendi directly from Top Predicted Article (Fix F-01)
        ratio_decidendi, precedents_cited = self._synthesize_ratio_and_precedents(
            rec_articles, facts, audit_report
        )

        return LjpPredictionResult(
            case_summary=text[:250] + ("..." if len(text) > 250 else ""),
            is_abstained=False,
            abstain_message="",
            atomic_facts=facts,
            retrieved_statutes=gated_in,
            filtered_out_candidates=filtered_out,
            top_articles=rec_articles[:5],
            top_charges=rec_charges[:5],
            penalty_prediction=rec_penalty,
            judicial_audit=audit_report,
            ratio_decidendi=ratio_decidendi,
            landmark_precedents_cited=precedents_cited
        )

    def _synthesize_ratio_and_precedents(
        self,
        articles: list,
        facts: AtomicFacts,
        audit: Any
    ) -> tuple:
        """Synthesizes grounded judicial ratio decidendi citing matching Supreme Court precedents."""
        if not articles:
            return "No penal provision attracted on the presented factual record.", []

        top_art = articles[0]
        ipc = top_art.ipc_section
        cited_precedents = []

        # Grounded reasoning based on actual predicted section (F-01 fix: NEVER default to Theft!)
        if "302" in ipc:
            ratio = (
                f"The evidence establishes an overt, pre-planned assault resulting in fatal injuries. "
                f"The bodily injury inflicted was sufficient in the ordinary course of nature to cause death. "
                f"The act constitutes murder punishable under Section 302 IPC / Section 103(1) BNS."
            )
            cited_precedents.append("State of A.P. v. Rayavarapu Punnayya (1976) 4 SCC 382")
        elif "304 Part II" in ipc:
            ratio = (
                f"The fatal injury was inflicted in the course of a sudden quarrel in heat of passion, "
                f"without premeditation and without taking undue advantage. Under Exception 4 to Section 300 IPC, "
                f"the offence stands mitigated to culpable homicide not amounting to murder punishable under Section 304 Part II IPC / Section 105 BNS."
            )
            cited_precedents.append("Pulicherla Nagaraju v. State of A.P. (2006) 11 SCC 444")
            cited_precedents.append("Ghapoo Yadav v. State of M.P. (2003) 3 SCC 528")
        elif "304 Part I" in ipc:
            ratio = (
                f"The act causing death was done with the intention of causing such bodily injury as was likely to cause death, "
                f"attracting Section 304 Part I IPC / Section 105 BNS."
            )
            cited_precedents.append("State of A.P. v. Rayavarapu Punnayya (1976) 4 SCC 382")
        elif "307" in ipc:
            ratio = (
                f"The accused executed an overt act capable of causing death with requisite criminal intention. "
                f"Though the victim survived, the intent and capability attract Section 307 IPC / Section 109 BNS."
            )
        elif "326" in ipc:
            ratio = (
                f"Grievous hurt was voluntarily inflicted using a deadly weapon (sharp/edged instrument or firearm), "
                f"causing vital organ injury or fracture, attracting Section 326 IPC / Section 118(2) BNS."
            )
        elif "324" in ipc:
            ratio = (
                f"Hurt was voluntarily inflicted by means of an instrument for cutting or stabbing, attracting Section 324 IPC / Section 118(1) BNS."
            )
        elif "392" in ipc:
            ratio = (
                f"In committing theft, the offender voluntarily caused or threatened instant hurt and wrongful restraint, "
                f"elevating the offence to robbery under Section 392 IPC / Section 309(4) BNS."
            )
        elif "379" in ipc:
            ratio = (
                f"The accused dishonestly took movable property out of the possession of the complainant without consent, "
                f"without using violence or deadly weapons, constituting simple theft under Section 379 IPC / Section 303(2) BNS."
            )
        elif "420" in ipc:
            ratio = (
                f"The complainant was dishonestly induced to part with valuable property based on fraudulent misrepresentations "
                f"present at inception, attracting Section 420 IPC / Section 318(4) BNS."
            )
            cited_precedents.append("Satender Kumar Antil v. CBI (2022) 10 SCC 51")
        elif "468" in ipc or "471" in ipc:
            ratio = (
                f"A forged document or valuable electronic record was intentionally fabricated and used as genuine for the purpose of cheating, "
                f"attracting Sections 468 & 471 IPC / Sections 336 & 340 BNS."
            )
        elif "498A" in ipc:
            ratio = (
                f"The victim was subjected to willful cruelty and unlawful demands for dowry by the husband or his relatives, "
                f"attracting Section 498A IPC / Section 85 BNS."
            )
            cited_precedents.append("Arnesh Kumar v. State of Bihar (2014) 8 SCC 273")
        elif "304B" in ipc:
            ratio = (
                f"Death of the woman occurred under unnatural circumstances within seven years of marriage with evidence of dowry harassment, "
                f"raising statutory presumption under Section 304B IPC / Section 80 BNS and Section 113B Evidence Act."
            )
        elif "506" in ipc:
            ratio = (
                f"The accused extended threats of injury with intent to cause alarm, constituting criminal intimidation under Section 506 IPC / Section 351 BNS."
            )
        elif "482" in ipc or "Civil" in top_art.charge_category:
            ratio = (
                f"The dispute arises out of a commercial contract or reconciliation of accounts without criminal intent at inception. "
                f"The dispute is predominantly civil, warranting quashing under Section 482 CrPC / Section 528 BNSS."
            )
            cited_precedents.append("State of Haryana v. Bhajan Lal (1992) Supp (1) SCC 335")
        else:
            ratio = f"Conduct alleged discloses penal ingredients governed by {top_art.display_name}."

        if facts.has_common_intention and facts.accused_count >= 2:
            ratio += " In view of multiple assailants acting in furtherance of a shared objective, joint liability under Section 34 IPC / Section 3(5) BNS is sustained."
            cited_precedents.append("Mehboob Shah v. King-Emperor (1945)")

        return ratio, cited_precedents
