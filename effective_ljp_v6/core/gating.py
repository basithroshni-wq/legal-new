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
            # or if overt act towards causing death is completely absent
            elif candidate.id == "STAT_307_IPC" and (facts.death_caused or ("attempt_to_murder" not in facts.extracted_tokens and not (facts.injury_severity == "Grievous" and facts.weapon_used))):
                is_disqualified = True
                rejection_reason = "Disqualified: Essential ingredients of attempt to murder (overt act towards causing death with murderous intent) are absent."

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

            # Criminal intimidation disqualified if physical violence, death, robbery, or sexual offences
            elif candidate.id == "STAT_506_IPC" and (facts.death_caused or facts.injury_severity in ("Simple", "Grievous") or facts.is_robbery or facts.is_sexual_offence or "attempt_to_murder" in facts.extracted_tokens):
                is_disqualified = True
                rejection_reason = "Disqualified: Overt physical violence, robbery, sexual offence, or homicide elevates crime beyond mere criminal intimidation."

            # Criminal trespass disqualified if fatality or robbery occurred
            elif candidate.id == "STAT_447_IPC" and (facts.death_caused or facts.is_robbery):
                is_disqualified = True
                rejection_reason = "Disqualified: Fatality or robbery eclipses simple criminal trespass."

            # Criminal negligence: If death was caused by negligence / rash driving without homicidal intent
            elif getattr(facts, "is_criminal_negligence", False) and candidate.id in ("STAT_302_IPC", "STAT_304_P1_IPC", "STAT_304_P2_IPC", "STAT_304B_IPC", "STAT_307_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Death was caused by criminal negligence / rash act without homicidal mens rea (governed by Section 304A)."

            elif candidate.id == "STAT_304A_IPC" and (not getattr(facts, "is_criminal_negligence", False) or facts.has_premeditation or facts.weapon_used or not facts.death_caused):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 304A strictly applies to rash/negligent death without intentional violence."

            # If robbery occurred, simple hurt under 323 or 324 is absorbed into robbery with hurt (394 / 309(4))
            elif candidate.id in ("STAT_323_IPC", "STAT_324_IPC") and facts.is_robbery:
                is_disqualified = True
                rejection_reason = "Disqualified: Hurt caused during robbery is subsumed under Section 394 / Section 392."

            # Defamation: Non-violent, reputational offence
            elif getattr(facts, "is_defamation", False) and candidate.id in ("STAT_471_IPC", "STAT_468_IPC", "STAT_420_IPC", "STAT_506_IPC", "STAT_379_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Publication damaging reputation is governed by Section 500 Defamation, not document forgery or cheating."

            elif candidate.id == "STAT_500_IPC" and not getattr(facts, "is_defamation", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 500 requires defamatory imputation harming reputation."

            # Bribery & Corruption (PC Act):
            elif getattr(facts, "is_corruption_or_bribery", False) and candidate.id in ("STAT_420_IPC", "STAT_406_IPC", "STAT_CIVIL_482", "STAT_379_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Public servant taking illegal gratification / trap is governed by Section 7 PC Act."

            elif candidate.id == "STAT_PC_ACT_7" and not getattr(facts, "is_corruption_or_bribery", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 7 PC Act requires public servant demand/acceptance of illegal gratification."

            # House-breaking / Lurking house-trespass by night:
            elif candidate.id == "STAT_457_IPC" and not getattr(facts, "is_housebreaking", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 457 requires house-breaking or lurking house-trespass."

            # Theft in dwelling:
            elif candidate.id == "STAT_380_IPC" and (not getattr(facts, "is_theft_in_dwelling", False) or not facts.is_theft):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 380 requires theft in human dwelling."

            # Robbery with hurt:
            elif candidate.id == "STAT_394_IPC" and (not facts.is_robbery or not getattr(facts, "is_robbery_with_hurt", False)):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 394 requires robbery coupled with causing hurt."

            # Section 408 requires clerk, servant or employee capacity
            elif candidate.id == "STAT_408_IPC" and not getattr(facts, "is_breach_of_trust_clerk_servant", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 408 requires clerk, servant or employee capacity."

            # Rape / Sexual offences strictly require sexual offence facts
            elif candidate.id == "STAT_376_IPC" and not facts.is_sexual_offence:
                is_disqualified = True
                rejection_reason = "Disqualified: Section 376 strictly requires sexual assault / rape allegations."

            elif candidate.id == "STAT_POCSO_6" and (not facts.is_sexual_offence or not getattr(facts, "is_pocso_child_abuse", False)):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 6 POCSO Act requires aggravated sexual assault on child."

            elif candidate.id == "STAT_447_IPC" and not getattr(facts, "is_criminal_trespass", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 447 requires criminal trespass into property."

            elif candidate.id == "STAT_498A_IPC" and (not facts.is_matrimonial or not any(k in facts.extracted_tokens for k in ("matrimonial_cruelty_498a", "dowry_death_304b", "suicide_abetment_306"))):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 498A strictly requires harassment or cruelty towards a woman in matrimonial context."

            # Abetment of suicide
            elif getattr(facts, "is_suicide_abetment", False) and candidate.id in ("STAT_302_IPC", "STAT_304_P1_IPC", "STAT_304_P2_IPC", "STAT_307_IPC", "STAT_379_IPC", "STAT_392_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Victim died by suicide; direct homicide/theft inapplicable."

            elif candidate.id == "STAT_306_IPC" and not getattr(facts, "is_suicide_abetment", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 306 requires suicide committed by victim."

            # NDPS Act
            elif getattr(facts, "is_ndps_narcotics", False) and candidate.id in ("STAT_379_IPC", "STAT_392_IPC", "STAT_420_IPC", "STAT_406_IPC", "STAT_506_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Possession of commercial narcotics governed by NDPS Act."

            elif candidate.id == "STAT_NDPS_21" and not getattr(facts, "is_ndps_narcotics", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 21 NDPS Act requires narcotic drugs or psychotropic substances."

            # Cheque Dishonour
            elif getattr(facts, "is_cheque_dishonour", False) and candidate.id in ("STAT_379_IPC", "STAT_392_IPC", "STAT_302_IPC", "STAT_506_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Governed by Section 138 NI Act."

            elif candidate.id == "STAT_NI_138" and not getattr(facts, "is_cheque_dishonour", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 138 NI Act requires cheque dishonour."

            # Extortion
            elif getattr(facts, "is_extortion", False) and candidate.id in ("STAT_379_IPC", "STAT_392_IPC", "STAT_420_IPC", "STAT_406_IPC", "STAT_419_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Putting in fear to extort property is governed by Section 384 Extortion."

            elif candidate.id == "STAT_384_IPC" and not getattr(facts, "is_extortion", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 384 requires putting in fear to extort property."

            # Acid Attack
            elif getattr(facts, "is_acid_attack", False) and candidate.id in ("STAT_323_IPC", "STAT_324_IPC", "STAT_326_IPC", "STAT_307_IPC") and candidate.id != "STAT_326A_IPC":
                is_disqualified = True
                rejection_reason = "Disqualified: Grievous hurt by acid is specifically governed by Section 326A IPC."

            elif candidate.id == "STAT_326A_IPC" and not getattr(facts, "is_acid_attack", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 326A requires use of acid or corrosive substance."

            # Kidnapping for Ransom
            elif getattr(facts, "is_kidnapping_ransom", False) and candidate.id in ("STAT_506_IPC", "STAT_384_IPC", "STAT_420_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Kidnapping/abduction with ransom demand is governed by Section 364A."

            elif candidate.id == "STAT_364A_IPC" and not getattr(facts, "is_kidnapping_ransom", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 364A requires kidnapping or abduction for ransom."

            # Cyber Phishing / Personation
            elif getattr(facts, "is_cyber_phishing", False) and candidate.id in ("STAT_379_IPC", "STAT_392_IPC", "STAT_406_IPC", "STAT_419_IPC", "STAT_420_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Cheating by personation using computer resource is governed by Section 66D IT Act."

            elif candidate.id == "STAT_IT_66D" and not getattr(facts, "is_cyber_phishing", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 66D IT Act requires cheating by personation using computer device."

            # Hate Speech (Section 153A IPC / Section 196 BNS)
            elif getattr(facts, "is_hate_speech_153a", False) and candidate.id in ("STAT_506_IPC", "STAT_500_IPC", "STAT_420_IPC", "STAT_379_IPC", "STAT_307_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Promoting enmity between different religious/social groups is governed by Section 153A."

            elif candidate.id == "STAT_153A_IPC" and not getattr(facts, "is_hate_speech_153a", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 153A requires promoting enmity between different groups or hate speech."

            # Arms Act (Section 25 Arms Act, 1959)
            elif getattr(facts, "is_arms_act", False) and candidate.id in ("STAT_506_IPC", "STAT_379_IPC", "STAT_392_IPC", "STAT_307_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Unlawful possession of prohibited firearm without licence is governed by Section 25 Arms Act."

            elif candidate.id == "STAT_ARMS_25" and not getattr(facts, "is_arms_act", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 25 Arms Act requires unlicensed possession of arms or ammunition."

            # Sexual harassment: Non-penetrative unwelcome remarks/advances (Section 354A)
            elif getattr(facts, "is_sexual_harassment", False) and candidate.id in ("STAT_376_IPC", "STAT_498A_IPC", "STAT_506_IPC") and not facts.is_matrimonial and not facts.is_sexual_offence:
                is_disqualified = True
                rejection_reason = "Disqualified: Non-penetrative workplace sexual harassment governed by Section 354A."

            elif candidate.id == "STAT_354A_IPC" and facts.is_sexual_offence:
                is_disqualified = True
                rejection_reason = "Disqualified: Penetrative assault elevates offence to Section 376."

            # CBT by Public Servant/Banker (Section 409)
            elif getattr(facts, "is_cbt_public_servant_banker", False) and candidate.id in ("STAT_379_IPC", "STAT_392_IPC", "STAT_420_IPC", "STAT_406_IPC", "STAT_408_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Criminal breach of trust by public servant/banker is specifically governed by Section 409."

            elif candidate.id == "STAT_409_IPC" and not getattr(facts, "is_cbt_public_servant_banker", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 409 requires entrustment in capacity of public servant, banker, or agent."

            # Arson / Mischief by Fire (Section 436)
            elif getattr(facts, "is_arson_fire", False) and candidate.id in ("STAT_379_IPC", "STAT_447_IPC", "STAT_457_IPC", "STAT_506_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Arson / mischief by fire to building is governed by Section 436."

            elif candidate.id == "STAT_436_IPC" and not getattr(facts, "is_arson_fire", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 436 requires mischief by fire to house or building."

            # Kidnapping from Lawful Guardianship (Section 363)
            elif getattr(facts, "is_kidnapping_lawful_guardian", False) and candidate.id in ("STAT_364A_IPC", "STAT_379_IPC", "STAT_506_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Kidnapping from lawful guardianship without ransom is governed by Section 363."

            elif candidate.id == "STAT_363_IPC" and not getattr(facts, "is_kidnapping_lawful_guardian", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 363 requires taking or enticing minor out of keeping of lawful guardian."

            # Stalking (Section 354D)
            elif getattr(facts, "is_stalking", False) and candidate.id in ("STAT_354A_IPC", "STAT_376_IPC", "STAT_506_IPC", "STAT_447_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Persistent following or monitoring of woman is governed by Section 354D Stalking."

            elif candidate.id == "STAT_354D_IPC" and not getattr(facts, "is_stalking", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 354D requires persistent following or electronic monitoring."

            # Causing Disappearance of Evidence (Section 201)
            elif getattr(facts, "is_destruction_of_evidence", False) and candidate.id in ("STAT_302_IPC", "STAT_304_P1_IPC", "STAT_379_IPC", "STAT_506_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Screening offender or causing disappearance of evidence is governed by Section 201."

            elif candidate.id == "STAT_201_IPC" and not getattr(facts, "is_destruction_of_evidence", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 201 requires causing disappearance of evidence to screen offender."

            # Counterfeiting Currency Notes FICN (Section 489A)
            elif getattr(facts, "is_counterfeit_currency", False) and candidate.id in ("STAT_420_IPC", "STAT_468_IPC", "STAT_471_IPC", "STAT_379_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Counterfeiting currency notes or banknotes is specifically governed by Section 489A."

            elif candidate.id == "STAT_489A_IPC" and not getattr(facts, "is_counterfeit_currency", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 489A requires counterfeiting currency notes or banknotes."

            # Rioting (Section 147)
            elif getattr(facts, "is_rioting", False) and candidate.id in ("STAT_379_IPC", "STAT_420_IPC", "STAT_CIVIL_482"):
                is_disqualified = True
                rejection_reason = "Disqualified: Rioting and public violence is governed by Section 147 IPC / Section 191(2) BNS."

            elif candidate.id == "STAT_147_IPC" and not getattr(facts, "is_rioting", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 147 requires force or violence used by unlawful assembly."

            # Unlawful Assembly (Section 149)
            elif getattr(facts, "is_unlawful_assembly", False) and candidate.id in ("STAT_379_IPC", "STAT_420_IPC", "STAT_CIVIL_482"):
                is_disqualified = True
                rejection_reason = "Disqualified: Constructive liability of unlawful assembly is governed by Section 149 IPC / Section 190 BNS."

            elif candidate.id == "STAT_149_IPC" and not getattr(facts, "is_unlawful_assembly", False) and not getattr(facts, "is_rioting", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 149 requires offence committed in prosecution of common object by unlawful assembly."

            # Wrongful Confinement (Section 343)
            elif getattr(facts, "is_wrongful_confinement", False) and candidate.id in ("STAT_379_IPC", "STAT_420_IPC", "STAT_CIVIL_482", "STAT_506_IPC"):
                is_disqualified = True
                rejection_reason = "Disqualified: Wrongful confinement is specifically governed by Section 343 IPC / Section 127(3) BNS."

            elif candidate.id == "STAT_343_IPC" and not getattr(facts, "is_wrongful_confinement", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 343 requires wrongful confinement for three or more days."

            # Dishonestly Receiving Stolen Property (Section 411)
            elif getattr(facts, "is_stolen_property_possession", False) and candidate.id in ("STAT_420_IPC", "STAT_406_IPC", "STAT_CIVIL_482"):
                is_disqualified = True
                rejection_reason = "Disqualified: Possession of stolen property is specifically governed by Section 411 IPC / Section 317(2) BNS."

            elif candidate.id == "STAT_411_IPC" and not getattr(facts, "is_stolen_property_possession", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 411 requires dishonestly receiving or retaining stolen property."

            # Cheating by Personation (Section 419)
            elif getattr(facts, "is_cheating_personation", False) and candidate.id in ("STAT_379_IPC", "STAT_406_IPC", "STAT_CIVIL_482"):
                is_disqualified = True
                rejection_reason = "Disqualified: Cheating by personation is specifically governed by Section 419 IPC / Section 319 BNS."

            elif candidate.id == "STAT_419_IPC" and not getattr(facts, "is_cheating_personation", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 419 requires cheating by personation."

            # Cruelty to Animals (Section 11 PCA Act)
            elif getattr(facts, "is_cruelty_to_animals", False) and candidate.id in ("STAT_302_IPC", "STAT_304_P1_IPC", "STAT_304_P2_IPC", "STAT_304A_IPC", "STAT_379_IPC", "STAT_CIVIL_482"):
                is_disqualified = True
                rejection_reason = "Disqualified: Cruelty to animals is governed by Section 11 PCA Act, not human homicide or civil dispute."

            elif candidate.id == "STAT_PCA_11" and not getattr(facts, "is_cruelty_to_animals", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 11 PCA Act requires cruelty to animals."

            # UAPA (Section 10 UAPA)
            elif getattr(facts, "is_uapa_offence", False) and candidate.id in ("STAT_379_IPC", "STAT_420_IPC", "STAT_CIVIL_482"):
                is_disqualified = True
                rejection_reason = "Disqualified: Unlawful association membership is governed by Section 10 UAPA."

            elif candidate.id == "STAT_UAPA_10" and not getattr(facts, "is_uapa_offence", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 10 UAPA requires membership of banned or unlawful association."

            # Wildlife Protection Act (Section 51 Wildlife Protection Act)
            elif getattr(facts, "is_wildlife_poaching", False) and candidate.id in ("STAT_302_IPC", "STAT_304_P1_IPC", "STAT_304_P2_IPC", "STAT_379_IPC", "STAT_CIVIL_482"):
                is_disqualified = True
                rejection_reason = "Disqualified: Hunting/poaching of wild animals is governed by Section 51 Wildlife Protection Act."

            elif candidate.id == "STAT_WPA_51" and not getattr(facts, "is_wildlife_poaching", False):
                is_disqualified = True
                rejection_reason = "Disqualified: Section 51 Wildlife Protection Act requires poaching or trophy possession."

            # Domain-targeted protection: Do NOT noise filter candidates directly matched by extracted facts
            domain_protected = False
            if getattr(facts, "is_defamation", False) and candidate.id == "STAT_500_IPC":
                domain_protected = True
            elif getattr(facts, "is_corruption_or_bribery", False) and candidate.id == "STAT_PC_ACT_7":
                domain_protected = True
            elif getattr(facts, "is_housebreaking", False) and candidate.id == "STAT_457_IPC":
                domain_protected = True
            elif getattr(facts, "is_theft_in_dwelling", False) and candidate.id == "STAT_380_IPC":
                domain_protected = True
            elif getattr(facts, "is_robbery_with_hurt", False) and candidate.id in ("STAT_394_IPC", "STAT_392_IPC"):
                domain_protected = True
            elif getattr(facts, "is_extortion", False) and candidate.id == "STAT_384_IPC":
                domain_protected = True
            elif getattr(facts, "is_acid_attack", False) and candidate.id == "STAT_326A_IPC":
                domain_protected = True
            elif getattr(facts, "is_kidnapping_ransom", False) and candidate.id == "STAT_364A_IPC":
                domain_protected = True
            elif getattr(facts, "is_cyber_phishing", False) and candidate.id == "STAT_IT_66D":
                domain_protected = True
            elif facts.is_intimidation and candidate.id == "STAT_506_IPC":
                domain_protected = True
            elif getattr(facts, "is_criminal_trespass", False) and candidate.id == "STAT_447_IPC":
                domain_protected = True
            elif getattr(facts, "is_breach_of_trust_clerk_servant", False) and candidate.id == "STAT_408_IPC":
                domain_protected = True
            elif getattr(facts, "is_criminal_negligence", False) and candidate.id == "STAT_304A_IPC":
                domain_protected = True
            elif getattr(facts, "is_sexual_harassment", False) and candidate.id == "STAT_354A_IPC":
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
            elif facts.death_caused and not getattr(facts, "is_criminal_negligence", False) and facts.is_sudden_fight and candidate.id == "STAT_304_P2_IPC":
                domain_protected = True
            elif facts.death_caused and not getattr(facts, "is_criminal_negligence", False) and facts.has_premeditation and candidate.id == "STAT_302_IPC":
                domain_protected = True
            elif facts.death_caused and not getattr(facts, "is_criminal_negligence", False) and not facts.is_sudden_fight and candidate.id == "STAT_304_P1_IPC":
                domain_protected = True
            elif facts.death_caused and facts.is_dowry_death and candidate.id == "STAT_304B_IPC":
                domain_protected = True
            elif "attempt_to_murder" in facts.extracted_tokens and candidate.id == "STAT_307_IPC":
                domain_protected = True
            elif facts.is_sexual_offence and candidate.id == "STAT_376_IPC":
                domain_protected = True
            elif facts.is_matrimonial and not facts.death_caused and candidate.id == "STAT_498A_IPC":
                domain_protected = True
            elif getattr(facts, "is_suicide_abetment", False) and candidate.id == "STAT_306_IPC":
                domain_protected = True
            elif getattr(facts, "is_ndps_narcotics", False) and candidate.id == "STAT_NDPS_21":
                domain_protected = True
            elif getattr(facts, "is_cheque_dishonour", False) and candidate.id == "STAT_NI_138":
                domain_protected = True
            elif getattr(facts, "is_pocso_child_abuse", False) and candidate.id in ("STAT_POCSO_6", "STAT_376_IPC"):
                domain_protected = True
            elif getattr(facts, "is_hate_speech_153a", False) and candidate.id == "STAT_153A_IPC":
                domain_protected = True
            elif getattr(facts, "is_arms_act", False) and candidate.id == "STAT_ARMS_25":
                domain_protected = True
            elif getattr(facts, "is_cbt_public_servant_banker", False) and candidate.id == "STAT_409_IPC":
                domain_protected = True
            elif getattr(facts, "is_arson_fire", False) and candidate.id == "STAT_436_IPC":
                domain_protected = True
            elif getattr(facts, "is_kidnapping_lawful_guardian", False) and candidate.id == "STAT_363_IPC":
                domain_protected = True
            elif getattr(facts, "is_stalking", False) and candidate.id == "STAT_354D_IPC":
                domain_protected = True
            elif getattr(facts, "is_destruction_of_evidence", False) and candidate.id == "STAT_201_IPC":
                domain_protected = True
            elif getattr(facts, "is_counterfeit_currency", False) and candidate.id == "STAT_489A_IPC":
                domain_protected = True
            elif getattr(facts, "is_rioting", False) and candidate.id == "STAT_147_IPC":
                domain_protected = True
            elif getattr(facts, "is_unlawful_assembly", False) and candidate.id == "STAT_149_IPC":
                domain_protected = True
            elif getattr(facts, "is_wrongful_confinement", False) and candidate.id == "STAT_343_IPC":
                domain_protected = True
            elif getattr(facts, "is_stolen_property_possession", False) and candidate.id == "STAT_411_IPC":
                domain_protected = True
            elif getattr(facts, "is_cheating_personation", False) and candidate.id in ("STAT_419_IPC", "STAT_468_IPC"):
                domain_protected = True
            elif getattr(facts, "is_cruelty_to_animals", False) and candidate.id == "STAT_PCA_11":
                domain_protected = True
            elif getattr(facts, "is_uapa_offence", False) and candidate.id == "STAT_UAPA_10":
                domain_protected = True
            elif getattr(facts, "is_wildlife_poaching", False) and candidate.id == "STAT_WPA_51":
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

        if "enmity" in ing or "disharmony" in ing or "public_tranquillity" in ing or "spoken_or_written" in ing:
            return getattr(facts, "is_hate_speech_153a", False)
        if "firearm" in ing or "ammunition" in ing or "licence" in ing or "arms" in ing:
            return getattr(facts, "is_arms_act", False)
        if "public_servant" in ing or "banker" in ing or "capacity_of_public_servant" in ing or "merchant_banker" in ing:
            return getattr(facts, "is_cbt_public_servant_banker", False)
        if "fire" in ing or "combustible" in ing or "destruction_of_house" in ing:
            return getattr(facts, "is_arson_fire", False)
        if "taking_or_enticing" in ing or "lawful_guardian" in ing or "out_of_keeping" in ing:
            return getattr(facts, "is_kidnapping_lawful_guardian", False)
        if "stalking" in ing or "follows_a_woman" in ing or "monitors_the_use" in ing:
            return getattr(facts, "is_stalking", False)
        if "disappearance_of_evidence" in ing or "screening_offender" in ing or "concealing_evidence" in ing:
            return getattr(facts, "is_destruction_of_evidence", False)
        if "counterfeit" in ing or "currency_note" in ing or "banknote" in ing:
            return getattr(facts, "is_counterfeit_currency", False)
        if "rioting" in ing or "force_or_violence_used_by_assembly" in ing:
            return getattr(facts, "is_rioting", False)
        if "unlawful_assembly" in ing or "member_of_assembly" in ing or "prosecution_of_common_object" in ing:
            return getattr(facts, "is_unlawful_assembly", False) or getattr(facts, "is_rioting", False)
        if "wrongful_restraint_or_confinement" in ing or "confinement_preventing" in ing or "confinement_for_three_or_more_days" in ing:
            return getattr(facts, "is_wrongful_confinement", False)
        if "possession_of_stolen_property" in ing or "reason_to_believe_to_be_stolen" in ing or "dishonest_retention" in ing:
            return getattr(facts, "is_stolen_property_possession", False)
        if "cheating_by_personation" in ing or "pretending_to_be_another" in ing or "personation" in ing:
            return getattr(facts, "is_cheating_personation", False)
        if "cruelty_to_animals" in ing or "unnecessary_pain_or_suffering" in ing or "inadequate_space" in ing:
            return getattr(facts, "is_cruelty_to_animals", False)
        if "membership_of_banned" in ing or "unlawful_association" in ing or "propaganda" in ing:
            return getattr(facts, "is_uapa_offence", False)
        if "poaching" in ing or "animal_skins_claws" in ing or "tiger_reserve" in ing or "wildlife" in ing:
            return getattr(facts, "is_wildlife_poaching", False)

        if "suicide" in ing or "abetment" in ing or "instigation" in ing:
            return getattr(facts, "is_suicide_abetment", False)
        if "narcotics" in ing or "contraband" in ing or "heroin" in ing or "diacetylmorphine" in ing:
            return getattr(facts, "is_ndps_narcotics", False)
        if "cheque" in ing or "insufficient_funds" in ing or "notice" in ing or "failure_to_pay" in ing:
            return getattr(facts, "is_cheque_dishonour", False)
        if "child" in ing or "trust" in ing or "teacher" in ing:
            return getattr(facts, "is_pocso_child_abuse", False)

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
        if "clerk" in ing or "servant" in ing or "employee" in ing:
            return getattr(facts, "is_breach_of_trust_clerk_servant", False)
        if "rash" in ing or "negligent" in ing or "absence_of_intention" in ing:
            return getattr(facts, "is_criminal_negligence", False)
        if "unwelcome_sexual" in ing or "sexual_harassment" in ing:
            return getattr(facts, "is_sexual_harassment", False)
        if "cruelty" in ing or "husband" in ing:
            return facts.is_matrimonial
        if "dowry" in ing:
            return facts.is_dowry_death
        if "intimidation" in ing or "threat" in ing or "alarm" in ing or "compel" in ing:
            return facts.is_intimidation
        if "trespass" in ing or "unlawful_entry" in ing:
            return getattr(facts, "is_criminal_trespass", False)
        if "civil" in ing or "commercial" in ing:
            return facts.is_commercial_civil_dispute
        if "several_persons" in ing or "common_intention" in ing:
            return facts.has_common_intention or facts.accused_count >= 2
        if "conspiracy" in ing:
            return facts.is_criminal_conspiracy
        if "sexual" in ing or "rape" in ing or "against_will" in ing or "consent" in ing:
            return facts.is_sexual_offence

        return False
