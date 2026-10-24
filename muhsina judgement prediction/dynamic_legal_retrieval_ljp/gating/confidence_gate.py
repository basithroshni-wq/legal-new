import re
"""
Relevance and Confidence Gating Layer (RCG) - Dual-Check Matrix with Atomic Fact Factorization.
Evaluates dynamically retrieved candidate statutes against:
1. Semantic Cosine Similarity Score (S_cosine)
2. Statutory Ingredient Alignment Score (S_ingredient: 0.0 to 1.0 across all 20 IPC/BNS articles)
Enforces strict domain isolation, statutory exception conversion, and exculpatory quashing.
"""

from typing import List, Dict, Any, Tuple, Optional
import config
from gating.fact_factorizer import AtomicLegalFactExtractor, AtomicCaseFacts


class RelevanceAndConfidenceGate:
    def __init__(
        self,
        threshold_tau: float = getattr(config, 'SIMILARITY_THRESHOLD_TAU', 0.40),
        max_items: int = getattr(config, 'MAX_GATED_KNOWLEDGE_ITEMS', 3),
        min_floor: float = getattr(config, 'MIN_CONFIDENCE_FLOOR', 0.35),
        adaptive: bool = getattr(config, 'ENABLE_ADAPTIVE_GATING', True)
    ):
        self.threshold_tau = threshold_tau
        self.max_items = max_items
        self.min_floor = min_floor
        self.adaptive = adaptive
        self.extractor = AtomicLegalFactExtractor()

    def filter_knowledge(self, fact_text: str, candidates: List[Dict[str, Any]], atomic_facts: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes Dual-Check Matrix Gating:
        1. Decomposes fact narrative into AtomicCaseFacts across 4 legal gradients (or uses LLM-extracted facts).
        2. Computes S_cosine and S_ingredient for each candidate.
        3. Filters into Gated Knowledge vs Filtered Noise.
        """
        if atomic_facts is None:
            atomic_facts = self.extractor.extract(fact_text)

        passed_items: List[Dict[str, Any]] = []
        discarded_items: List[Dict[str, Any]] = []

        if not candidates:
            return {
                "gated_knowledge": [],
                "filtered_noise": [],
                "passed_count": 0,
                "noise_count": 0,
                "atomic_facts": atomic_facts
            }

        # Global Exculpatory Filter (Civil Quashing u/s 482) - F-05
        is_violent = (atomic_facts.injury_severity in ["Fatal (Death)", "Grievous (Fracture/Vital)"]
                      or atomic_facts.weapon_used is not None
                      or atomic_facts.is_sexual_offence)
        if atomic_facts.is_purely_civil and not is_violent:
            exculp_reason = "Commercial / Civil Contract Dispute (Quashing Standard u/s 482 CrPC)"
            for candidate in candidates:
                discarded_items.append({
                    "id": candidate["id"],
                    "title": candidate["title"],
                    "similarity": candidate.get("similarity_score", 0.0),
                    "ingredient_score": 0.0,
                    "reason": f"Element Consistency Gate / Exculpatory Defense Gate: {exculp_reason}"
                })
            return {
                "gated_knowledge": [],
                "filtered_noise": discarded_items,
                "passed_count": 0,
                "noise_count": len(discarded_items),
                "atomic_facts": atomic_facts,
                "is_exculpatory": True
            }

        # Determine effective adaptive threshold
        top_sim = max((c.get("similarity_score", 0.0) for c in candidates), default=0.0)
        if self.adaptive and top_sim >= self.min_floor:
            effective_tau = max(self.min_floor, min(self.threshold_tau, round(top_sim - 0.12, 3)))
        else:
            effective_tau = self.threshold_tau

        for candidate in candidates:
            sim = float(candidate.get("similarity_score", 0.0))
            title = candidate.get("title", "")
            art_code = candidate.get("article_code", "")
            charge = candidate.get("charge", "")
            elements = candidate.get("essential_elements") or candidate.get("elements") or []

            # Compute Dual-Check Ingredient Alignment Score (0.0 to 1.0)
            alignment_score, alignment_reason = self._compute_ingredient_alignment(atomic_facts, candidate)

            # Strict Domain Isolation Checks
            is_fatal_or_violent = atomic_facts.injury_severity in ["Fatal (Death)", "Grievous (Fracture/Vital)"] or atomic_facts.weapon_used is not None
            is_economic_cand = any(ec in charge.lower() for ec in ["cheating", "financial fraud", "breach of trust", "forgery"])
            
            # Violent narrative without property/commercial elements rejects financial fraud
            if is_fatal_or_violent and not atomic_facts.is_theft and not atomic_facts.is_robbery and not atomic_facts.is_cheating and is_economic_cand:
                discarded_items.append({
                    "id": candidate["id"],
                    "title": title,
                    "similarity": sim,
                    "ingredient_score": 0.0,
                    "reason": "Strict Domain Isolation: Financial cheating/forgery excluded from non-commercial violent narrative."
                })
                continue

            # Property/commercial narrative without bodily harm rejects violent homicide
            if (atomic_facts.is_theft or atomic_facts.is_cheating or atomic_facts.has_forged_documents) and not is_fatal_or_violent and not atomic_facts.is_robbery:
                if any(vc in charge.lower() for vc in ["murder", "culpable homicide", "grievous hurt", "sexual offences"]):
                    discarded_items.append({
                        "id": candidate["id"],
                        "title": title,
                        "similarity": sim,
                        "ingredient_score": 0.0,
                        "reason": "Strict Domain Isolation: Violent/homicide offenses excluded from non-violent property/commercial dispute."
                    })
                    continue

            # Check 1: Similarity Cutoff
            if sim < effective_tau:
                discarded_items.append({
                    "id": candidate["id"],
                    "title": title,
                    "similarity": sim,
                    "ingredient_score": alignment_score,
                    "reason": f"Low Confidence Gate: Similarity {sim:.3f} is below effective threshold ({effective_tau:.2f})"
                })
                continue

            # Check 2: Ingredient Alignment Threshold (Must be >= 0.40)
            if alignment_score < 0.40:
                discarded_items.append({
                    "id": candidate["id"],
                    "title": title,
                    "similarity": sim,
                    "ingredient_score": alignment_score,
                    "reason": f"Element Consistency Gate / Dual-Check Alignment Gate: {alignment_reason}"
                })
                continue

            # Passed Both Checks
            passed_items.append({
                "id": candidate["id"],
                "type": candidate["type"],
                "article_code": art_code,
                "title": title,
                "charge": charge,
                "penalty_tier": candidate.get("penalty_tier", ""),
                "similarity": sim,
                "ingredient_score": alignment_score,
                "content": candidate["content"],
                "matched_elements": self._get_matched_elements(elements, atomic_facts)
            })

        # Sort by combination of ingredient alignment (60%) & semantic similarity (40%)
        passed_items.sort(key=lambda x: (x["ingredient_score"] * 0.6) + (x["similarity"] * 0.4), reverse=True)
        gated_knowledge = passed_items[:self.max_items]

        if len(passed_items) > self.max_items:
            for surplus in passed_items[self.max_items:]:
                discarded_items.append({
                    "id": surplus["id"],
                    "title": surplus["title"],
                    "similarity": surplus["similarity"],
                    "ingredient_score": surplus["ingredient_score"],
                    "reason": "Capacity Gate: Exceeded prefix budget slot limit"
                })

        return {
            "gated_knowledge": gated_knowledge,
            "filtered_noise": discarded_items,
            "passed_count": len(gated_knowledge),
            "noise_count": len(discarded_items),
            "effective_tau": effective_tau,
            "atomic_facts": atomic_facts
        }

    def _get_matched_elements(self, elements: List[str], atomic_facts: Any) -> List[str]:
        matched = []
        raw_lower = atomic_facts.raw_text.lower()
        stopwords = {"with", "that", "this", "from", "have", "been", "under", "which", "into", "their", "there", "other", "when", "such"}
        for elem in elements:
            elem_lower = elem.lower()
            sub_words = [w for w in re.findall(r"\b[a-zA-Z]{4,}\b", elem_lower) if w not in stopwords]
            if any(re.search(r"\b" + re.escape(w) + r"\b", raw_lower) for w in sub_words):
                matched.append(elem)
            elif any(k in elem_lower for k in ["theft", "movable property", "taking"]) and getattr(atomic_facts, "is_theft", False):
                matched.append(elem)
            elif any(k in elem_lower for k in ["death", "bodily injury", "homicide"]) and getattr(atomic_facts, "injury_severity", "") == "Fatal (Death)":
                matched.append(elem)
            elif any(k in elem_lower for k in ["weapon", "dangerous", "instrument"]) and getattr(atomic_facts, "weapon_used", None) is not None:
                matched.append(elem)
            elif any(k in elem_lower for k in ["quarrel", "sudden", "heat of passion"]) and getattr(atomic_facts, "is_sudden_fight", False):
                matched.append(elem)
            elif any(k in elem_lower for k in ["deception", "inducement", "fraud", "dishonest"]) and getattr(atomic_facts, "is_cheating", False):
                matched.append(elem)
            elif any(k in elem_lower for k in ["sexual", "penetrative", "consent"]) and getattr(atomic_facts, "is_sexual_offence", False):
                matched.append(elem)
            elif any(k in elem_lower for k in ["dowry", "marriage", "harassment"]) and getattr(atomic_facts, "is_dowry_death", False):
                matched.append(elem)
        return matched

    def _compute_ingredient_alignment(self, facts: AtomicCaseFacts, candidate: Dict[str, Any]) -> Tuple[float, str]:
        """
        Computes statutory ingredient fulfillment score (0.0 to 1.0)
        across all 20 IPC/BNS criminal articles and extracted AtomicCaseFacts.
        """
        code = candidate.get("article_code", "").upper()
        cand_id = candidate.get("id", "").upper()
        charge = candidate.get("charge", "").lower()

        # =========================================================================
        # GRADIENT 1: FATAL & BODILY HURT
        # =========================================================================
        # 1. Section 304 Part II (Culpable Homicide Not Amounting to Murder)
        if "304_PART2" in code or "PULICHERLA" in cand_id or "GHAPOO" in cand_id:
            if facts.injury_severity == "Fatal (Death)":
                if facts.is_heat_of_passion or (facts.is_sudden_fight and (facts.single_blow or facts.weapon_source == "Found at Spot / Casual")):
                    return 0.96, "Fulfills Exception 4 essentials: sudden fight, single blow with casual weapon, no premeditation."
                elif facts.is_sudden_fight:
                    return 0.88, "Mutual altercation in heat of passion satisfies Section 304 Part II ingredients."
                else:
                    return 0.35, "Lacks sudden fight or heat of passion."
            else:
                return 0.10, "Victim did not succumb to fatal injuries; homicide elements not satisfied."

        # 2. Section 304 Part I (Culpable Homicide - Intention to cause bodily injury likely to cause death)
        if "304_PART1" in code or "KALU_RAM" in cand_id:
            if facts.injury_severity == "Fatal (Death)":
                if not facts.has_premeditation and (facts.is_sudden_fight or facts.injury_severity == "Fatal (Death)"):
                    return 0.85, "Fatal injury likely to cause death without premeditated murder plan satisfies Section 304 Part I."
                return 0.60, "Fatal injury present without premeditation."
            return 0.10, "Requires causation of death."

        # 3. Section 302 (Murder)
        if "302" in code or "VIRSA_SINGH" in cand_id or "BACHAN_SINGH" in cand_id:
            if facts.injury_severity != "Fatal (Death)":
                return 0.05, "Victim survived; substantive murder requires death."
            # Exception 4 conversion: if sudden fight + heat of passion / single blow, suppress 302
            if facts.is_heat_of_passion or (facts.is_sudden_fight and (facts.single_blow or facts.weapon_source == "Found at Spot / Casual")):
                return 0.10, "Statutory Exception 4 to Sec 300 applies: absence of premeditation converts charge to 304 Part II."
            if facts.has_premeditation:
                return 0.96, "Premeditated malice aforethought and lethal outcome satisfy Section 302."
            return 0.65, "Fatal injury present without verified Exception 4 or premeditation."

        # 4. Section 307 (Attempt to Murder)
        if "307" in code or "BALRAM_PATIL" in cand_id:
            if facts.injury_severity != "Fatal (Death)" and (facts.attempt_murder_intent or (facts.weapon_used and facts.weapon_category in ["Firearm/Lethal", "Sharp/Cutting (Knife/Dagger)"])):
                return 0.95, "Lethal weapon attack with survival of victim satisfies Section 307 Attempt to Murder."
            if facts.injury_severity == "Fatal (Death)":
                return 0.15, "Death ensued; substantive offence (302/304) applies rather than inchoate attempt."
            if facts.weapon_used:
                return 0.70, "Weapon attack satisfies attempt elements."
            return 0.25, "Lacks lethal weapon or murderous intent."

        # 5. Section 326 (Grievous Hurt by Dangerous Weapon)
        if "326" in code or "MATHURADAS" in cand_id:
            if facts.weapon_used and (facts.injury_severity in ["Grievous (Fracture/Vital)", "Fatal (Death)"]):
                return 0.90, "Dangerous weapon causing fracture or vital bodily injury satisfies Section 326."
            if facts.weapon_used:
                return 0.70, "Dangerous weapon used in assault."
            return 0.20, "Lacks dangerous weapon or grievous injury."

        # 6. Section 324 (Causing Hurt by Dangerous Weapons)
        if "324" in code or "ANWARUL_HAQ" in cand_id:
            if facts.weapon_used and facts.injury_severity in ["Simple Hurt", "Surviving / Non-Fatal"] and not facts.attempt_murder_intent:
                return 0.92, "Use of cutting, stabbing or dangerous weapon causing non-grievous hurt satisfies Section 324."
            if facts.weapon_used and facts.injury_severity != "Fatal (Death)":
                return 0.75, "Dangerous weapon utilized without fatal outcome."
            return 0.20, "Lacks dangerous weapon."

        # 7. Section 323 (Simple Hurt)
        if "323" in code or "BISHEN_SINGH" in cand_id:
            if facts.injury_severity in ["Simple Hurt", "Surviving / Non-Fatal"] and not facts.weapon_used:
                return 0.90, "Unarmed assault causing simple hurt satisfies Section 323."
            if facts.injury_severity in ["Simple Hurt", "Surviving / Non-Fatal"]:
                return 0.65, "Bodily hurt present."
            return 0.25, "Minor or unverified physical injury."

        # =========================================================================
        # GRADIENT 2: PROPERTY & THEFT / ROBBERY
        # =========================================================================
        # 8. Section 392 (Robbery)
        if "392" in code or "JOSEPH_KOLI" in cand_id:
            if facts.is_robbery:
                return 0.96, "Movable property taken by force, violence, or brandishing weapon satisfies Section 392 Robbery."
            if facts.is_theft and facts.weapon_used:
                return 0.88, "Theft accompanied by weapon brandishing elevates to Robbery."
            return 0.15, "Lacks force, violence, or weapon brandishing in taking property."

        # 9. Section 379 (Theft)
        if "379" in code or "KN_MEHRA" in cand_id:
            if facts.is_theft and not facts.is_robbery:
                return 0.95, "Dishonest taking of movable property without consent satisfies Section 379 Theft."
            if facts.is_robbery:
                return 0.60, "Theft is constituent base of robbery."
            return 0.15, "Lacks dishonest taking of movable property."

        # 10. Section 406 (Criminal Breach of Trust)
        if "406" in code or "VIJAYASARATHY" in cand_id:
            if facts.is_breach_of_trust:
                return 0.95, "Lawful entrustment followed by dishonest conversion satisfies Section 406."
            if facts.is_cheating:
                return 0.50, "Financial misappropriation overlap."
            return 0.20, "Lacks entrustment of property."

        # =========================================================================
        # GRADIENT 3: COMMERCIAL & DOCUMENT FRAUD
        # =========================================================================
        # 11. Section 420 (Cheating & Dishonest Inducement)
        if "420" in code or "HRIDAYA_RANJAN" in cand_id or "BHAJAN_LAL" in cand_id or "SATENDER_ANTIL" in cand_id:
            if facts.is_cheating:
                return 0.95, "Fraudulent deception inducing delivery of property satisfies Section 420 Cheating."
            if facts.has_forged_documents:
                return 0.70, "Forgery used in aid of cheating."
            return 0.20, "Lacks deceptive inducement from inception."

        # 12. Section 467 (Forgery of Valuable Security or Will)
        if "467" in code or "SHEILA_SEBASTIAN" in cand_id:
            if facts.has_forged_documents and facts.is_valuable_security:
                return 0.96, "Forged will, valuable security, or property title satisfies Section 467."
            if facts.has_forged_documents:
                return 0.70, "Forged document present."
            return 0.10, "Lacks forged valuable security."

        # 13. Section 468 (Forgery for Purpose of Cheating)
        if "468" in code:
            if facts.has_forged_documents and facts.is_cheating:
                return 0.95, "Fabrication of false document specifically to cheat satisfies Section 468."
            if facts.has_forged_documents:
                return 0.80, "Document forgery present."
            return 0.10, "Lacks forged document."

        # 14. Section 471 (Using Forged Document as Genuine)
        if "471" in code or "AS_KRISHNAN" in cand_id:
            if facts.has_forged_documents:
                return 0.92, "Use or presentation of forged record as genuine satisfies Section 471."
            return 0.10, "Lacks forged record."

        # =========================================================================
        # GRADIENT 4: SEXUAL, DOMESTIC & INTIMIDATION
        # =========================================================================
        # 15. Section 376 (Rape & Sexual Assault)
        if "376" in code or "PRAMOD_PAWAR" in cand_id:
            if facts.is_sexual_offence:
                return 0.96, "Non-consensual penetrative sexual assault satisfies Section 376."
            return 0.05, "Lacks sexual offence elements."

        # 16. Section 304B (Dowry Death)
        if "304B" in code or "SATBIR_SINGH" in cand_id:
            if facts.is_dowry_death:
                return 0.96, "Unnatural death of woman within statutory period linked to dowry satisfies Section 304B."
            if facts.is_matrimonial_cruelty and facts.injury_severity == "Fatal (Death)":
                return 0.88, "Fatal outcome linked to matrimonial cruelty."
            return 0.10, "Lacks dowry death ingredients."

        # 17. Section 498A (Matrimonial Cruelty)
        if "498A" in code or "ARNESH_KUMAR" in cand_id or "KAHKASHAN" in cand_id:
            if facts.is_matrimonial_cruelty and facts.injury_severity != "Fatal (Death)":
                return 0.95, "Harassment and cruelty by husband/relatives satisfies Section 498A."
            if facts.is_matrimonial_cruelty:
                return 0.70, "Matrimonial cruelty present."
            return 0.10, "Lacks matrimonial relationship context."

        # 18. Section 506 (Criminal Intimidation)
        if "506" in code or "VIKRAM_JOHAR" in cand_id:
            if facts.is_criminal_intimidation:
                if facts.threat_to_cause_death:
                    return 0.96, "Death threat satisfies Section 506 Part II (elevated penalty up to 7 years)."
                return 0.90, "Threat of injury to person/property satisfies Section 506 Part I."
            return 0.20, "Lacks intimidation elements."

        # =========================================================================
        # INCHOATE / ADJECTIVE: CONSPIRACY & COMMON INTENTION
        # =========================================================================
        # 19. Section 120B (Criminal Conspiracy)
        if "120B" in code or "NAVJOT_SANDHU" in cand_id:
            if facts.is_conspiracy and facts.multiple_accused:
                return 0.95, "Prior criminal agreement between multiple accused satisfies Section 120B."
            if facts.multiple_accused:
                return 0.70, "Multiple accused participating in crime."
            return 0.10, "Single accused; conspiracy requires agreement of two or more persons."

        # 20. Section 34 (Common Intention)
        if "34" in code or "PANDURANG" in cand_id:
            if facts.multiple_accused:
                return 0.85, "Multiple accused acting in concert satisfies Section 34 common intention."
            return 0.05, "Single accused; Section 34 requires multiple persons."

        return 0.50, "General criminal element compatibility."
