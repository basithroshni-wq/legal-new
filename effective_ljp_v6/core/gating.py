"""
Relevance & Confidence Gating Layer (RCG) for Effective LJP V6.
Performs dual-check matrix evaluation between extracted atomic facts and candidate statutory ingredients.
Fixes F-15 (correct essential_ingredients matching) and F-16 (monotonic, mathematically sound gating thresholds).
"""

from typing import List, Dict, Any, Tuple
from .schemas import CandidateKnowledge, AtomicFacts


class RelevanceAndConfidenceGate:
    """Evaluates candidate knowledge items for statutory ingredient fulfillment and noise suppression."""

    def __init__(self, tau_relevance: float = 0.10, theta_ingredient: float = 0.15):
        self.tau = tau_relevance
        self.theta = theta_ingredient

    def audit_and_gate(
        self,
        candidates: List[CandidateKnowledge],
        facts: AtomicFacts,
        raw_kb_dict: Dict[str, Dict[str, Any]]
    ) -> Tuple[List[CandidateKnowledge], List[CandidateKnowledge]]:
        """
        Audits candidates against atomic legal facts.
        Returns:
            (gated_in_candidates, filtered_noise_candidates)
        """
        gated_in: List[CandidateKnowledge] = []
        filtered_out: List[CandidateKnowledge] = []

        for candidate in candidates:
            statute_data = raw_kb_dict.get(candidate.id, {})
            essential_ingredients = statute_data.get("essential_ingredients", [])
            negative_exceptions = statute_data.get("negative_exceptions", [])

            # Step 1: Match essential ingredients
            matched: List[str] = []
            missing: List[str] = []

            for ing in essential_ingredients:
                if self._ingredient_satisfied(ing, facts):
                    matched.append(ing)
                else:
                    missing.append(ing)

            total_req = max(1, len(essential_ingredients))
            fulfillment_ratio = len(matched) / total_req
            candidate.ingredient_fulfillment = round(fulfillment_ratio, 4)
            candidate.matched_ingredients = matched
            candidate.missing_ingredients = missing

            # Step 2: Check disqualifying negative exceptions
            is_disqualified = False
            rejection_reason = None

            # Murder cannot stand if no death occurred
            if candidate.id in ("STAT_302_IPC", "STAT_304_P1_IPC", "STAT_304_P2_IPC", "STAT_304B_IPC") and not facts.death_caused:
                is_disqualified = True
                rejection_reason = "Disqualified: Statutory premise requires death of victim, but no fatality occurred."

            # Attempt to murder cannot stand if victim died (elevates to substantive homicide)
            elif candidate.id == "STAT_307_IPC" and facts.death_caused:
                is_disqualified = True
                rejection_reason = "Disqualified: Victim succumbed to injuries; charge subsumed under substantive homicide (Sec 302/304)."

            # Simple theft cannot stand if physical force or weapons were used (elevates to robbery Sec 392)
            elif candidate.id == "STAT_379_IPC" and (facts.force_or_violence_used or facts.weapon_used or facts.is_robbery or facts.is_dacoity):
                is_disqualified = True
                rejection_reason = "Disqualified: Force or deadly weapon used to dispossess property; elevated to Robbery (Sec 392)."

            # Civil quash cannot stand if violence, weapons, or physical injuries occurred
            elif candidate.id == "STAT_CIVIL_482" and (facts.weapon_used or facts.death_caused or facts.injury_severity in ("Simple", "Grievous")):
                is_disqualified = True
                rejection_reason = "Disqualified: Allegations disclose overt physical violence/weapons, barring inherent civil quashing."

            # Grievous hurt Section 326 cannot stand if injury was merely simple hurt
            elif candidate.id == "STAT_326_IPC" and facts.injury_severity == "Simple":
                is_disqualified = True
                rejection_reason = "Disqualified: Injury is certified simple hurt; Section 326 strictly requires grievous hurt (punishable u/s 324)."

            # Section 324 requires dangerous weapons or means; unarmed hurt strictly falls under Section 323
            elif candidate.id == "STAT_324_IPC" and (not facts.weapon_used or facts.injury_severity != "Simple"):
                if not facts.weapon_used:
                    is_disqualified = True
                    rejection_reason = "Disqualified: Unarmed assault without weapons falls under Section 323."

            # Voluntarily causing hurt Section 323 cannot stand if dangerous weapons or grievous hurt are involved
            elif candidate.id == "STAT_323_IPC" and (facts.weapon_used or facts.injury_severity in ("Grievous", "Fatal")):
                is_disqualified = True
                rejection_reason = "Disqualified: Dangerous weapon or grievous hurt involved; Section 323 is restricted to simple unarmed assault."

            # Criminal intimidation disqualified if physical violence, death, or robbery
            elif candidate.id == "STAT_506_IPC" and (facts.death_caused or facts.injury_severity in ("Simple", "Grievous") or facts.is_robbery or "attempt_to_murder" in facts.extracted_tokens):
                is_disqualified = True
                rejection_reason = "Disqualified: Overt physical violence, robbery, or homicide elevates crime beyond mere criminal intimidation."

            # Domain-targeted protection: Do NOT noise filter candidates directly matched by extracted facts
            domain_protected = False
            if facts.is_intimidation and candidate.id == "STAT_506_IPC":
                domain_protected = True
            elif facts.is_fraud_or_cheating and candidate.id == "STAT_420_IPC":
                domain_protected = True
            elif facts.is_forgery and candidate.id in ("STAT_468_IPC", "STAT_471_IPC"):
                domain_protected = True
            elif facts.is_breach_of_trust and candidate.id == "STAT_406_IPC":
                domain_protected = True
            elif facts.is_dacoity and candidate.id == "STAT_395_IPC":
                domain_protected = True
            elif facts.is_robbery and candidate.id == "STAT_392_IPC":
                domain_protected = True
            elif facts.is_theft and candidate.id == "STAT_379_IPC":
                domain_protected = True
            elif facts.is_commercial_civil_dispute and candidate.id == "STAT_CIVIL_482":
                domain_protected = True
            elif facts.injury_severity == "Grievous" and candidate.id == "STAT_326_IPC":
                domain_protected = True
            elif facts.injury_severity == "Simple" and not facts.weapon_used and candidate.id == "STAT_323_IPC":
                domain_protected = True
            elif facts.injury_severity == "Simple" and facts.weapon_used and candidate.id == "STAT_324_IPC":
                domain_protected = True
            elif facts.death_caused and facts.is_sudden_fight and candidate.id == "STAT_304_P2_IPC":
                domain_protected = True
            elif facts.death_caused and facts.has_premeditation and candidate.id == "STAT_302_IPC":
                domain_protected = True
            elif facts.death_caused and not facts.is_sudden_fight and candidate.id == "STAT_304_P1_IPC":
                domain_protected = True
            elif facts.death_caused and facts.is_dowry_death and candidate.id == "STAT_304B_IPC":
                domain_protected = True
            elif "attempt_to_murder" in facts.extracted_tokens and candidate.id == "STAT_307_IPC":
                domain_protected = True

            # Low relevance or insufficient ingredient fulfillment check
            if not is_disqualified and not domain_protected:
                if candidate.combined_relevance < self.tau and fulfillment_ratio < self.theta:
                    is_disqualified = True
                    rejection_reason = f"Noise Filtered: Low combined relevance ({candidate.combined_relevance:.2f} < {self.tau}) and insufficient ingredient fulfillment ({fulfillment_ratio:.2f} < {self.theta})."

            if is_disqualified:
                candidate.is_gated_in = False
                candidate.rejection_reason = rejection_reason
                filtered_out.append(candidate)
            else:
                candidate.is_gated_in = True
                gated_in.append(candidate)

        return gated_in, filtered_out

    def _ingredient_satisfied(self, ingredient: str, facts: AtomicFacts) -> bool:
        """Determines if a specific statutory ingredient is satisfied by extracted atomic facts."""
        ing = ingredient.lower()

        # Check attempt and overt acts towards murder before general death check
        if "attempt" in ing or "overt_act" in ing or "causing_death_if_not_prevented" in ing:
            return "attempt_to_murder" in facts.extracted_tokens or (facts.weapon_used and facts.injury_severity == "Grievous")

        if "death" in ing:
            return facts.death_caused
        if "intention_to_cause_death" in ing:
            return facts.intention_to_cause_death
        if "premeditation" in ing:
            return facts.has_premeditation
        if "sudden_fight" in ing:
            return facts.is_sudden_fight or facts.heat_of_passion
        if "grievous_hurt" in ing:
            return facts.injury_severity == "Grievous"
        if "simple_hurt" in ing:
            return facts.injury_severity in ("Simple", "Grievous")
        if "dangerous_weapon" in ing or "weapon" in ing or "corrosive" in ing:
            return facts.weapon_used
        if "theft" in ing:
            return facts.is_theft or facts.is_robbery
        if "dacoity" in ing or "five_or_more" in ing or "conjointly" in ing:
            return facts.is_dacoity
        if "robbery" in ing or "force_or_intimidation" in ing:
            return facts.is_robbery or facts.force_or_violence_used
        if "cheating" in ing or "deception" in ing or "inducement" in ing:
            return facts.is_fraud_or_cheating
        if "forgery" in ing or "false_document" in ing:
            return facts.is_forgery
        if "breach_of_trust" in ing or "entrustment" in ing or "custody" in ing or "dominion" in ing:
            return facts.is_breach_of_trust
        if "cruelty" in ing or "husband" in ing:
            return facts.is_matrimonial
        if "dowry" in ing:
            return facts.is_dowry_death
        if "intimidation" in ing or "threat" in ing or "alarm" in ing or "compel" in ing:
            return facts.is_intimidation
        if "civil" in ing or "commercial" in ing:
            return facts.is_commercial_civil_dispute
        if "several_persons" in ing or "common_intention" in ing:
            return facts.has_common_intention or facts.accused_count >= 2
        if "conspiracy" in ing:
            return facts.is_criminal_conspiracy

        return False
