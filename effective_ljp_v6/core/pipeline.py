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
        elif "408" in ipc:
            ratio = (
                f"The accused, being an employee, clerk or servant entrusted with collections or property, "
                f"dishonestly misappropriated the same, attracting Section 408 IPC / Section 316(4) BNS."
            )
            cited_precedents.append("State of U.P. v. Babu Ram Upadhya AIR 1961 SC 751")
        elif "304A" in ipc or "106" in top_art.bns_section:
            ratio = (
                f"Death was caused by a rash or negligent act (such as reckless driving) without homicidal intention or knowledge, "
                f"constituting causing death by negligence under Section 304A IPC / Section 106 BNS."
            )
            cited_precedents.append("State of Karnataka v. Satish (1998) 8 SCC 493")
            cited_precedents.append("Jacob Mathew v. State of Punjab (2005) 6 SCC 1")
        elif "354A" in ipc or "75" in top_art.bns_section:
            ratio = (
                f"The accused committed unwelcome sexual remarks or demands, satisfying the statutory definition of sexual harassment "
                f"under Section 354A IPC / Section 75 BNS."
            )
            cited_precedents.append("Apparel Export Promotion Council v. A.K. Chopra (1999) 1 SCC 759")
        elif "468" in ipc or "471" in ipc:
            ratio = (
                f"A forged document or valuable electronic record was intentionally fabricated and used as genuine for the purpose of cheating, "
                f"attracting Sections 468 & 471 IPC / Sections 336 & 340 BNS."
            )
            cited_precedents.append("Sheila Sebastian v. R. Jawaharaj (2018) 7 SCC 581")
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
        elif "500" in ipc or "356" in top_art.bns_section:
            ratio = (
                f"The accused published false defamatory statements harming the reputation of the complainant, "
                f"constituting criminal defamation under Section 500 IPC / Section 356 BNS."
            )
            cited_precedents.append("Subramanian Swamy v. Union of India (2016) 7 SCC 221")
        elif "457" in ipc or "331" in top_art.bns_section:
            ratio = (
                f"The accused committed house-breaking or lurking house-trespass by night to commit theft, "
                f"constituting an aggravated property offence under Section 457 IPC / Section 331(4) BNS."
            )
            cited_precedents.append("Ram Ratan v. State of U.P. AIR 1977 SC 612")
        elif "380" in ipc or "305" in top_art.bns_section:
            ratio = (
                f"The accused committed theft of movable property in a dwelling house/building without consent, "
                f"attracting Section 380 IPC / Section 305(a) BNS."
            )
            cited_precedents.append("Puran v. State of Rajasthan (1976) 1 SCC 560")
        elif "394" in ipc:
            ratio = (
                f"The accused committed robbery and in doing so voluntarily caused hurt using a deadly weapon, "
                f"attracting Section 394 IPC / Section 309(4) BNS."
            )
            cited_precedents.append("State of Maharashtra v. Joseph Mingel Koli (1997) 2 Crimes 228 (Bom)")
        elif "pc act" in ipc.lower() or "corruption" in top_art.charge_category.lower():
            ratio = (
                f"The accused, being a public servant, demanded and accepted illegal gratification for performing official duty, "
                f"attracting Section 7 of the Prevention of Corruption Act, 1988."
            )
            cited_precedents.append("P. Satyanarayana Murthy v. District Inspector of Police (2015) 10 SCC 152")
            cited_precedents.append("Neeraj Dutta v. State (Govt. of NCT of Delhi) (2023) 4 SCC 731")
        elif "447" in ipc:
            ratio = (
                f"The accused entered or remained upon property in possession of the complainant without permission "
                f"with intent to intimidate, insult or annoy, constituting criminal trespass under Section 447 IPC / Section 329(3) BNS."
            )
            if facts.is_intimidation:
                ratio += " In view of the intent to intimidate the owner, Section 506 IPC / Section 351 BNS is also attracted."
            cited_precedents.append("Mathuri & Ors. v. State of Punjab AIR 1964 SC 986")
        elif "506" in ipc:
            ratio = (
                f"The accused extended threats of injury with intent to cause alarm, constituting criminal intimidation under Section 506 IPC / Section 351 BNS."
            )
            if getattr(facts, "is_criminal_trespass", False):
                ratio += " The unauthorized entry into fenced property in furtherance of intimidation also constitutes criminal trespass under Section 447 IPC / Section 329(3) BNS."
            cited_precedents.append("Vikram Johar v. State of U.P. (2019) 14 SCC 207")
        elif "306" in ipc:
            ratio = (
                f"The deceased died by suicide following persistent mental or physical torture, "
                f"attracting Section 306 IPC / Section 108 BNS (Abetment of Suicide)."
            )
            cited_precedents.append("Sanju v. State of M.P. (2002) 5 SCC 371")
        elif "ndps" in ipc.lower() or "narcotic" in top_art.charge_category.lower():
            ratio = (
                f"The accused was found in possession of contraband/manufactured drugs (commercial quantity), "
                f"attracting Section 21 of the NDPS Act, 1985."
            )
            cited_precedents.append("Union of India v. Mohanlal (2016) 3 SCC 379")
        elif "138" in ipc or "cheque" in top_art.charge_category.lower():
            ratio = (
                f"A cheque issued towards discharge of debt was dishonoured due to insufficient funds and remained unpaid after statutory demand, "
                f"attracting Section 138 of the Negotiable Instruments Act, 1881."
            )
            cited_precedents.append("Rangappa v. Sri Mohan (2010) 11 SCC 441")
        elif "pocso" in ipc.lower() or "child" in top_art.charge_category.lower():
            ratio = (
                f"The accused committed penetrative sexual assault on a child in a position of trust, "
                f"constituting aggravated offence under Section 6 of the POCSO Act, 2012 read with Section 376 IPC / Section 64 BNS."
            )
            cited_precedents.append("Alakh Alok Srivastava v. Union of India (2018) 7 SCC 393")
        elif "384" in ipc:
            ratio = (
                f"The accused intentionally put the complainant in fear of injury and dishonestly induced delivery of property, "
                f"attracting Section 384 IPC / Section 308(2) BNS."
            )
            cited_precedents.append("Dhananjay v. State of Bihar (2007) 14 SCC 768")
        elif "326a" in ipc.lower() or "acid" in top_art.charge_category.lower():
            ratio = (
                f"The accused threw corrosive acid on the victim causing permanent disfigurement and grievous injury, "
                f"attracting Section 326A IPC / Section 124(1) BNS."
            )
            cited_precedents.append("Laxmi v. Union of India (2014) 4 SCC 427")
        elif "364a" in ipc.lower() or "ransom" in top_art.charge_category.lower():
            ratio = (
                f"The accused kidnapped or abducted the victim, kept him in detention, and demanded ransom under threat of death or hurt, "
                f"attracting Section 364A IPC / Section 140(2) BNS."
            )
            cited_precedents.append("Vikram Singh v. Union of India (2015) 9 SCC 502")
        elif "66d" in ipc.lower() or "cyber" in top_art.charge_category.lower():
            ratio = (
                f"The accused cheated by personation using a computer resource to fraudulently siphon funds, "
                f"attracting Section 66D of the IT Act, 2000 read with Section 420 IPC / Section 318(4) BNS."
            )
            cited_precedents.append("Sharat Babu Digumarti v. Govt. (NCT of Delhi) (2017) 2 SCC 18")
        elif "395" in ipc:
            ratio = (
                f"Five or more persons conjointly committed armed robbery, storming the premises and overpowering security guards, "
                f"constituting dacoity under Section 395 IPC / Section 310(2) BNS."
            )
            cited_precedents.append("Om Prakash v. State of Rajasthan (1998) 1 SCC 4")
            cited_precedents.append("Raj Kumar v. State (NCT of Delhi) (2017) 11 SCC 160")
        elif "153a" in ipc.lower() or "hate" in top_art.charge_category.lower():
            ratio = (
                f"The accused published spoken, written, or visual representations promoting feelings of enmity, hatred, or ill-will "
                f"between different religious or social groups, prejudicial to public harmony under Section 153A IPC / Section 196 BNS."
            )
            cited_precedents.append("Pravasi Bhalai Sangathan v. Union of India (2014) 11 SCC 477")
            cited_precedents.append("Bilal Ahmed Kaloo v. State of A.P. (1997) 7 SCC 431")
        elif "arms" in ipc.lower() or "arms" in top_art.charge_category.lower():
            ratio = (
                f"The accused was found in conscious and unlawful possession of a prohibited country-made firearm and live ammunition "
                f"without holding a valid licence, attracting Section 25 of the Arms Act, 1959."
            )
            cited_precedents.append("Sanjay Dutt v. State through CBI (1994) 5 SCC 410")
        elif "409" in ipc or "public servant" in top_art.charge_category.lower():
            ratio = (
                f"The accused, being entrusted with property in his capacity as a public servant, banker, or commercial agent, "
                f"committed dishonest misappropriation or conversion, attracting Section 409 IPC / Section 316(5) BNS."
            )
            cited_precedents.append("State of Gujarat v. Jaswantlal Nathalal (1968) 2 SCR 408")
        elif "436" in ipc or "arson" in top_art.charge_category.lower():
            ratio = (
                f"The accused committed mischief by fire or explosive substance with intent to destroy a building, dwelling house, "
                f"or place used for the custody of property, attracting Section 436 IPC / Section 326(f) BNS."
            )
            cited_precedents.append("Santosh v. State of M.P. (2006) 10 SCC 714")
        elif "363" in ipc or "guardianship" in top_art.charge_category.lower():
            ratio = (
                f"The accused took or enticed a minor out of the keeping of the lawful guardian without consent, "
                f"attracting Section 363 IPC / Section 137(2) BNS."
            )
            cited_precedents.append("S. Varadarajan v. State of Madras AIR 1965 SC 942")
        elif "354d" in ipc.lower() or "stalking" in top_art.charge_category.lower():
            ratio = (
                f"The accused persistently followed a woman or monitored her electronic communications despite clear indication of disinterest, "
                f"constituting stalking under Section 354D IPC / Section 78 BNS."
            )
            cited_precedents.append("State of Maharashtra v. Raju (2018) 14 SCC 566")
        elif "201" in ipc or "evidence" in top_art.charge_category.lower():
            ratio = (
                f"The accused caused evidence of an offence to disappear or gave false information with the intention of screening the offender "
                f"from legal punishment, attracting Section 201 IPC / Section 238 BNS."
            )
            cited_precedents.append("Palvinder Kaur v. State of Punjab AIR 1952 SC 354")
        elif "489a" in ipc.lower() or "counterfeit" in top_art.charge_category.lower():
            ratio = (
                f"The accused knowingly performed part of the process of counterfeiting currency notes or banknotes, "
                f"attracting Section 489A IPC / Section 178 BNS."
            )
            cited_precedents.append("Umashanker v. State of Chhattisgarh (2001) 9 SCC 642")
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
