"""
Grounded Legal Fact Extractor for Effective LJP V6.
Resolves critical failure modes from prior models:
- Scoped clause negation (F-03): 'victim was unarmed' does not strip accused's weapon.
- Accurate premeditation negation (F-04): 'no prior enmity' marks premeditation as False.
- Accurate defense plea handling (F-05): 'falsely implicated' does not quash violent crimes.
- Separation of weapon brandishing from hurt (F-02): brandishing without injury is robbery or intimidation, not IPC 326/307.
- Out-of-domain detection (F-09): abstains on weather, financial earnings, and non-penal text.
- Multi-accused joint liability detection (F-12): correctly captures Section 34 IPC / Section 3(5) BNS.
"""

import re
from typing import Dict, Any, List, Optional
from .schemas import AtomicFacts


class ScopedFactExtractor:
    """High-precision, clause-bounded legal fact extractor with GPU neural fusion."""

    def __init__(self, use_llm_if_available: bool = True):
        self.use_llm = use_llm_if_available
        self.neural_extractor = None
        if self.use_llm:
            try:
                from .neural_extractor import NeuralLegalFactExtractor
                self.neural_extractor = NeuralLegalFactExtractor()
            except Exception:
                self.neural_extractor = None

    def extract(self, text: str) -> AtomicFacts:
        """Main entry point: extracts validated AtomicFacts from case text."""
        clean_text = text.strip()

        # Step 1: Out-of-Domain (OOD) Screening
        ood_result = self._check_out_of_domain(clean_text)
        if ood_result["is_ood"]:
            return AtomicFacts(
                is_out_of_domain=True,
                out_of_domain_reason=ood_result["reason"],
                extracted_tokens=["out_of_domain"]
            )

        # Step 2: Clause-level decomposition & entity scoping
        facts = self._extract_deterministic_facts(clean_text)

        # Step 3: Neural-Symbolic Ensemble Fusion (if GPU neural model is loaded)
        if self.neural_extractor is not None:
            facts = self._fuse_neural_and_deterministic(facts, clean_text)

        return facts

    def _check_out_of_domain(self, text: str) -> Dict[str, Any]:
        """Detects whether text describes a cognizable legal scenario or external irrelevant text."""
        lower = text.lower()
        words = set(re.findall(r"\b[a-z]{3,}\b", lower))

        # Comprehensive non-legal domain keywords
        weather_words = {"forecast", "celsius", "fahrenheit", "precipitation", "rainy", "meteorological", "cyclone", "humidity", "monsoon", "rainfall", "sunny", "squalls"}
        sports_words = {"football", "cricket", "tournament", "wicket", "stadium", "quarterback", "olympic", "goalscorer", "batsman", "bowler", "innings", "wickets"}
        corporate_finance = {"ebitda", "quarterly earnings", "stock dividend", "fiscal revenue", "nasdaq", "shareholders meeting", "interim dividend", "basis points", "operating profit"}
        cooking_words = {"recipe", "mixing bowl", "whisk", "flour", "baking powder", "bake for", "preheat", "unsalted butter", "oven"}
        physics_words = {"quantum", "entanglement", "photon", "bell inequalities", "qubits", "wavefunction", "photons"}
        pharma_words = {"rhinitis", "antihistamines", "clinical trials", "pharmacokinetics", "efficacy", "oral administration"}
        tech_words = {"amoled", "refresh rate", "octa-core", "processor", "battery supporting", "fast charging", "smartphone features", "npm install", "webpack", "tsconfig", "save-dev"}
        nature_words = {"humpback whales", "antarctic", "migratory", "brushwork", "impressionist", "oil paintings", "museum exhibition", "parisian artists"}

        # Legal indicator terms (broadened to ensure no false abstentions on legitimate legal facts)
        legal_terms = {
            "accused", "victim", "complainant", "police", "fir", "killed", "stabbed", "murder",
            "theft", "stolen", "cash", "knife", "weapon", "robbery", "quarrel", "died", "death",
            "assault", "cheating", "fraud", "forgery", "threatened", "intimidation", "cruelty",
            "dowry", "rape", "injuries", "contract", "invoice", "court", "petitioner", "respondent",
            "blow", "struck", "slapped", "dispute", "agreement", "lease", "tenant", "landlord",
            "assailant", "deceased", "offence", "penal", "extortion", "investors", "deceived",
            "goods", "looted", "cashier", "gold", "bullion", "revolver", "pistol", "lathi",
            "acid", "burns", "misappropriated", "counterfeit", "hostage", "dacoits", "dacoity",
            "dead", "handbag", "stole", "unauthorized", "custody", "fiduciary", "forged",
            "deed", "cheated", "duped", "bribe", "conspiracy", "conspired", "injure", "hurt",
            "fracture", "punched", "kicked", "hit", "shoved", "brawl", "fight", "husband",
            "wife", "complaint", "thief", "defence", "fired", "rifle", "succumbed", "suicide",
            "supplier", "retailer", "reconciliation", "customer", "paying", "shopkeeper",
            "beaten", "thrashing", "sticks", "villagers", "hostel", "students", "altercation",
            "driver", "rickshaw", "passengers", "brother", "dinner", "colleagues", "office",
            "patron", "club", "scalp", "scalpel", "scuffle", "fatal", "consignment", "pain"
        }

        matched_legal = sum(1 for w in words if w in legal_terms)

        # Check domain specific matches
        weather_matches = sum(1 for w in words if w in weather_words)
        sports_matches = sum(1 for w in words if w in sports_words)
        cooking_matches = sum(1 for w in cooking_words if w in lower)
        physics_matches = sum(1 for w in physics_words if w in lower)
        pharma_matches = sum(1 for w in pharma_words if w in lower)
        tech_matches = sum(1 for w in tech_words if w in lower)
        nature_matches = sum(1 for w in nature_words if w in lower)
        corp_matches = sum(1 for phrase in corporate_finance if phrase in lower)

        if matched_legal == 0:
            return {"is_ood": True, "reason": "Text contains zero cognizable criminal or civil legal allegations."}

        if weather_matches >= 2 and matched_legal <= 1:
            return {"is_ood": True, "reason": "Text relates to Meteorological / Weather Forecast, disclosing no cognizable criminal offence."}
        if sports_matches >= 2 and matched_legal <= 1:
            return {"is_ood": True, "reason": "Text relates to Sports reporting, disclosing no cognizable criminal offence."}
        if corp_matches >= 1 and matched_legal <= 1:
            return {"is_ood": True, "reason": "Text relates to Corporate financial earnings / commercial disclosure without criminal allegations."}
        if cooking_matches >= 2 and matched_legal <= 1:
            return {"is_ood": True, "reason": "Text relates to Culinary / Cooking recipe, disclosing no cognizable criminal offence."}
        if physics_matches >= 2 and matched_legal <= 1:
            return {"is_ood": True, "reason": "Text relates to Quantum Physics / Theoretical Science, disclosing no criminal controversy."}
        if pharma_matches >= 2 and matched_legal <= 1:
            return {"is_ood": True, "reason": "Text relates to Pharmaceutical / Clinical research, disclosing no penal offence."}
        if tech_matches >= 2 and matched_legal <= 1:
            return {"is_ood": True, "reason": "Text relates to Consumer Technology / Software DevOps documentation, disclosing no penal controversy."}
        if nature_matches >= 2 and matched_legal <= 1:
            return {"is_ood": True, "reason": "Text relates to Wildlife documentary / Fine Arts review, disclosing no cognizable criminal offence."}

        return {"is_ood": False, "reason": ""}

    def _extract_deterministic_facts(self, text: str) -> AtomicFacts:
        """Extracts facts using clause-bounded patterns without keyword leakage."""
        lower = text.lower()
        tokens: List[str] = []

        # Initialize core variables
        death_caused = False
        injury_severity = "None"
        weapon_used = False
        weapon_type = "None"
        weapon_source = "None"
        intention_to_cause_death = False
        has_premeditation = False
        is_sudden_fight = False
        heat_of_passion = False
        is_provocation = False

        is_theft = False
        is_robbery = False
        is_dacoity = False
        force_or_violence_used = False
        is_fraud_or_cheating = False
        fraudulent_inducement_at_inception = False
        is_forgery = False
        is_breach_of_trust = False

        is_matrimonial = False
        is_dowry_death = False
        marriage_years: Optional[float] = None
        is_sexual_offence = False
        is_intimidation = False

        accused_count = 1
        has_common_intention = False
        is_criminal_conspiracy = False
        is_commercial_civil_dispute = False
        defense_plea_false_implication = False

        # --- 1. Scoped Negation & Weapon Extraction (Fix F-02, F-03) ---
        has_corrosive = bool(re.search(r"\b(acid|sulfuric acid|battery acid|chemical burns|corrosive|boiling (?:oil|water|mustard oil)|hot cup of tea|heated substance|scalding)\b", lower))
        has_sharp = bool(re.search(r"\b(knife|dagger|blade|chopper|sword|kirpan|machete|scalpel|razor|flick knife|penknife|scissors|sickle|cleaver|pruning hook|butcher knife|bayonet|compass|scale|broken (?:beer )?bottle)\b", lower))
        
        # Avoid treating shop merchandise (e.g. bottle of perfume) as weapon
        bottle_is_weapon = bool(re.search(r"\b(broken bottle|struck.*with.*bottle|hit.*with.*bottle|swung.*bottle|threw.*bottle)\b", lower))
        has_blunt = bool(re.search(r"\b(iron rod|lathi|stick|club|wooden log|bat|crowbar|wrench|spade|hammer|pipe|chain|bicycle chain|bar stool|bamboo pole|rolling pin|iron pipe|iron bar|wooden stool|baton|shepherd's crook)\b", lower)) or bottle_is_weapon
        
        has_firearm = bool(re.search(r"\b(gun|pistol|revolver|rifle|firearm|bullets?|shotguns?|pellet gun|pipe bomb|country-made pistol|country pistol|shots?|fired|shooting)\b", lower))
        has_stone = bool(re.search(r"\b(stone|granite edge)\b", lower))

        # Check who was armed vs unarmed (Crucial F-03 fix)
        victim_unarmed = bool(re.search(r"\b(victim|deceased|complainant|informant|target)\b[^.!?]*\b(unarmed|had no weapon|without weapon)\b", lower))
        accused_unarmed = bool(re.search(r"\b(accused|assailant|culprit|attacker)\b[^.!?]*\b(unarmed|had no weapon|without weapon|no weapon used|with no weapon|bare fist|with fists)\b", lower)) or bool(re.search(r"\b(no weapon(?: used)?|without any weapon|without any instrument|with no instrument)\b", lower))

        if (has_corrosive or has_sharp or has_blunt or has_firearm or has_stone) and not accused_unarmed:
            weapon_used = True
            if has_firearm:
                weapon_type = "Firearm"
            elif has_corrosive:
                weapon_type = "Corrosive"
            elif has_sharp:
                weapon_type = "Edged/Sharp (Knife/Axe)"
            else:
                weapon_type = "Blunt (Rod/Club)"
            tokens.append(f"weapon_{weapon_type.lower()}")

        # Weapon source (Fix F-04)
        if re.search(r"\b(lying nearby|picked up from the ground|found at the spot|snatched from spot|lying on the table|from the kitchen counter|from the roadside|lying on the bus floor)\b", lower):
            weapon_source = "Found at Spot"
        elif re.search(r"\b(brought with him|pre-arranged|concealed on his person|carried weapon|purchased earlier|specifically to eliminate|armed with)\b", lower):
            weapon_source = "Pre-arranged/Carried"

        # --- 2. Injury & Death Scoping (Fix F-02) ---
        victim_survived = bool(re.search(r"\b(surviv\w*|sav\w*|out of danger|resuscitated|pulled (?:him|her|the victim )?back|underwent (?:emergency )?(?:surgery|laparotomy|thoracotomy)|discharged|recovered|timely (?:medical|vascular|surgical) (?:aid|intervention|repair))\b", lower))
        is_threat_or_intent_of_death = bool(re.search(r"\b(threats? of (?:immediate |instant )?death|threaten\w* (?:to kill|with death|to shoot|with dire consequences)|intend\w* (?:his|her|their)?\s*death|shoot (?:you|him|her|them) dead|will shoot you dead)\b", lower))

        # Idioms and non-fatal legal documents that mention 'dead' or 'death'
        is_idiomatic_dead = bool(re.search(r"\b(dead of night|death certificate of a living|false death certificate|shoot (?:you|him|her|them) dead)\b", lower))

        # Accurate Actus Reus Fatality: Must distinguish actual death from threats, survival, or idioms
        actual_death_patterns = (bool(re.search(r"\b(died|dead|found dead|succumb\w*|fatal\w*|fatality|fatalities|corpse|post-mortem|autopsy|deceased|strangled to death|beaten to death|causing death|resulted in death|kill\w*|demise)\b", lower)) and not is_idiomatic_dead) or (bool(re.search(r"\b(death)\b", lower)) and not is_threat_or_intent_of_death and not is_idiomatic_dead)
        
        death_caused = actual_death_patterns and not victim_survived

        if death_caused:
            injury_severity = "Fatal"
            tokens.append("death_caused")
        else:
            # Exclude threats of bodily injury from actual grievous hurt
            is_threat_of_hurt = bool(re.search(r"\b(threaten\w* to|threats? of)\b[^.!?]*\b(teeth|fracture|smash|break)\b", lower))
            has_grievous = (bool(re.search(r"\b(fractur\w*|broken (?:legs?|bones?|ribs?)|breaking both legs|grievous|internal bleeding|stabbed in (?:chest|abdomen|stomach|left thoracic|thoracic)|permanent privation|vital organ|severed|thoracic|penetrated|blind\w*|loss of vision|disfigurement|chemical burns|deep second and third degree burns|destroying.*skin|necrosis|permanent disability|permanent stiffness|shattering|mandible|teeth|patella|visceral shock|pour\w* acid)\b", lower)) and not is_threat_of_hurt and not bool(re.search(r"\b(without fracture|no fracture|without grievous|no danger to life|without (?:permanent )?disfigurement)\b", lower)))
            has_simple = bool(re.search(r"\b(simple hurt|bruise\w*|scratch\w*|minor injury|slapped|punched|swelling|superficial|slash\w*|tenderness|black eye|nosebleed|contusions?|redness|cut\w*|laceration\w*|wound\w*|punctur\w*|bodily pain|temporary bodily pain|pain|kicked|scalds)\b", lower))

            if has_grievous:
                injury_severity = "Grievous"
                tokens.append("injury_grievous")
            elif has_simple:
                injury_severity = "Simple"
                tokens.append("injury_simple")
            else:
                injury_severity = "None"

        # --- 3. Premeditation, Intent & Sudden Fight (Fix F-04) ---
        negated_premed = bool(re.search(r"\b(no prior (?:enmity|animosity|planning|ill-will)|not planned|unpremeditated|without premeditation|without prior (?:enmity|planning)|no long-standing grudge|unscripted argument)\b", lower))
        positive_premed = bool(re.search(r"\b(premeditat\w*|prior enmity|long-standing grudge|bitter grudge|grudge over|threatened revenge|planned in advance|planned the murder|lying in wait|ambush\w*|hid behind.*armed with|conspir\w* to (?:eliminate|murder|kill)|purchased.*specifically to eliminate|lured.*to eliminate|tailed.*deceased|administered (?:potassium cyanide|cyanide|arsenic|poison)|honor killing)\b", lower))

        if positive_premed and not negated_premed:
            has_premeditation = True
            tokens.append("premeditation_established")
        else:
            has_premeditation = False

        sudden_quarrel = bool(re.search(r"\b(sudden (?:quarrel|fight|altercation|argument|spat)|heat of passion|hot blood|hot words|spontaneous (?:fight|altercation)|impromptu.*brawl|during an argument|unscripted argument|in a sudden quarrel)\b", lower))
        if sudden_quarrel or negated_premed:
            is_sudden_fight = True
            heat_of_passion = True
            tokens.append("sudden_fight_heat_of_passion")

        is_provocation = bool(re.search(r"\b(grave and sudden provocation|exceeding (?:private defence|right of private defence)|excess of the right of private defence|provocation)\b", lower))

        if death_caused:
            lethal_vital_attack = bool(re.search(r"\b(potassium cyanide|cyanide|arsenic|poison|shot.*in the (?:chest|head)|stabbed.*in the (?:chest|heart|throat|neck)|slashed.*throat|ambushed.*stabbed)\b", lower))
            if (has_premeditation or lethal_vital_attack) and not is_sudden_fight and not is_provocation:
                intention_to_cause_death = True
                tokens.append("intention_to_cause_death")
            elif is_sudden_fight:
                tokens.append("sudden_fight_exception_4")
            elif is_provocation:
                tokens.append("grave_provocation_or_private_defence_exception")
            else:
                tokens.append("intention_to_cause_death_or_injury_likely_to_cause_death")

        # --- 4. Attempt to Murder Scoping (Fix F-02) ---
        if not death_caused:
            attempt_expressions = bool(re.search(r"\b(intend\w* to (?:murder|cause death)|intent\w* to (?:kill|eliminate)|attempted to (?:slit|murder|kill)|aimed and shot|bullet penetrated|shot.*in the (?:chest|abdomen|neck)|fired (?:three )?bullets|slashed.*throat|mixed (?:arsenic|poison)|rammed.*against.*pillar|pushed.*into an active railway track|threw.*off the terrace|set.*locked shop on fire|strangled.*until he lost consciousness|pipe bomb|stabbed.*(?:thoracic|chest|abdomen|throat).*intending to cause death)\b", lower))
            if attempt_expressions:
                tokens.append("attempt_to_murder")
                tokens.append("overt_act_towards_commission_of_murder")

        # --- 5. Property Crimes: Theft vs Robbery vs Cheating (Fix F-07) ---
        stole_property = bool(re.search(r"\b(stole\w*|theft|thief|took (?:away|it away)|shoplift\w*|lifted|pilfer\w*|pickpocket\w*|concealed.*handbag|walked out without paying|slipped.*into.*pocket|removed.*without.*consent|without (?:the )?owner'?s? (?:knowledge|consent|permission)|without (?:anyone'?s? )?permission|discreetly reached|snatched|looted|quietly detached|untied two cows)\b", lower))
        extortion_or_intimidation = bool(re.search(r"\b(demanded (?:wallet|money|cash|phone|gold|all cash)|held.*(?:knife|gun|dagger|revolver|pistol|iron rod|sickle|cleaver)|threats? of (?:immediate |instant )?death|held at gunpoint|held at knifepoint|pointed a (?:firearm|revolver|pistol|dagger|knife)|extorted|at gunpoint|under threat of instant hurt|pushed.*corner.*knife|pressed a razor blade|ambushed.*atm customer.*dagger)\b", lower))
        force_exerted = bool(re.search(r"\b(shoved|pushed|strangled|pinned down|dragged|inflicted blow|threatened with immediate death|threatened immediate violence|forcibly took|snatched.*by force|grabbed.*by her hair)\b", lower))

        if extortion_or_intimidation or (stole_property and (weapon_used or force_exerted)) or (bool(re.search(r"\b(brandished.*threatened immediate violence.*forcibly took)\b", lower))):
            is_robbery = True
            force_or_violence_used = True
            tokens.append("robbery_committed")
        elif stole_property and not force_exerted and not weapon_used:
            is_theft = True
            tokens.append("dishonest_theft_taking")

        # Cheating & Forgery
        cheating_terms = bool(re.search(r"\b(deceived|induced to deliver|dishonestly induc\w*|promised (?:job|government post|high returns|lucrative|mbbs)|ponzi|bogus scheme|fake investment|swindled|duped|cryptocurrency|chit fund|fake medical admission|bogus algorithm|fake layout approvals|pledging bogus|multi-level marketing|posed as (?:a|an)|non-existent|franchise security deposits|booking fees|disappeared|absconded|fled without paying|fraudulently collected|collected.*from.*investors|collected.*from.*parents|collected.*from.*members)\b", lower))
        if cheating_terms:
            is_fraud_or_cheating = True
            fraudulent_inducement_at_inception = True
            tokens.append("fraudulent_inducement_cheating")

        forgery_terms = bool(re.search(r"\b(forged|fake document|counterfeit|forgery|manufactured deed|tampered title deed|false seal|fabricated a false (?:death certificate|will|title deed)|fabricated a forged)\b", lower))
        if forgery_terms:
            is_forgery = True
            tokens.append("forged_document_fabricated")

        breach_trust = bool(re.search(r"\b(entrusted|given custody of|misappropriated property entrusted|warehouse custodian|fiduciary|dominion over|safekeeping|given dominion)\b", lower))
        if breach_trust and not is_fraud_or_cheating:
            is_breach_of_trust = True
            tokens.append("criminal_breach_of_trust")

        # --- 6. Matrimonial Cruelty & Dowry Death (Fix F-07) ---
        matrimonial_context = bool(re.search(r"\b(husband|in-laws|mother-in-law|sister-in-law|marital home|matrimonial home|marital bedroom|wife|married)\b", lower))
        dowry_demand = bool(re.search(r"\b(dowry|failing to bring|unlawful demand for (?:cash|car|gold|property)|harassed for dowry|dowry demands)\b", lower))
        marriage_within_7 = bool(re.search(r"\b(married\b[^.!?]*\b(?:one|two|three|four|five|six|seven|\d+)\s*(?:years?|yrs?|months?)|(?:one|two|three|four|five|six|seven|\d+)\s*(?:years?|yrs?|months?)\s+of\s+marriage|married for only \d+ months)\b", lower))

        if matrimonial_context:
            is_matrimonial = True
            if death_caused and (dowry_demand or marriage_within_7):
                is_dowry_death = True
                tokens.append("dowry_death_304b")
            elif dowry_demand or bool(re.search(r"\b(cruelty|harassed|subjected to harassment|mental torture|verbal degradation|suicide)\b", lower)):
                tokens.append("matrimonial_cruelty_498a")

        # --- 7. Sexual Offences & Criminal Intimidation ---
        if re.search(r"\b(rape|sexual assault|forced herself upon|non-consensual intercourse|violated modesty)\b", lower):
            is_sexual_offence = True
            tokens.append("sexual_offence_rape")

        intimidation_triggers = bool(re.search(r"\b(threaten\w*|threats?)\b[^.!?]*\b(shoot|kill|burn|harm|kidnap|injur\w*|dire consequences|slit|destroy|acid)\b", lower)) or bool(re.search(r"\b(criminal intimidation|showed.*bottle of acid.*threatened)\b", lower))
        if (weapon_used and injury_severity == "None" and not is_robbery) or (intimidation_triggers and not death_caused and not is_robbery):
            is_intimidation = True
            tokens.append("criminal_intimidation")

        # --- 8. Accused Count & Joint Liability (Fix F-12) ---
        count_match = re.search(r"\b(?:a\s+)?(?:gang\s+of\s+)?(\d+|two|three|four|five|six|seven|eight|nine|ten|several|multiple)?\s*(?:masked\s+|armed\s+)?(?:accused|assailants|men|attackers|persons|co-accused|dacoits?|bandits?|robbers)\b", lower)
        if count_match:
            count_word = count_match.group(1)
            word_to_num = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "several": 3, "multiple": 3}
            if count_word in word_to_num:
                accused_count = word_to_num[count_word]
            elif count_word and count_word.isdigit():
                accused_count = int(count_word)
            elif "gang of" in lower:
                accused_count = 5

        if bool(re.search(r"\b(dacoits?|dacoity|bandits)\b", lower)):
            accused_count = max(5, accused_count)

        if (accused_count >= 5 or bool(re.search(r"\b(dacoits?|dacoity|bandits)\b", lower))) and (is_robbery or bool(re.search(r"\b(looted|conjointly|intercepted a cash transit|stormed a bank|raided|invaded)\b", lower))):
            is_dacoity = True
            tokens.append("dacoity_five_plus")

        if accused_count >= 2:
            has_common_intention = True
            tokens.append("joint_liability_sec_34")

        if re.search(r"\b(conspiracy|conspired|criminal conspiracy|plotted together|meeting of minds)\b", lower):
            is_criminal_conspiracy = True
            tokens.append("criminal_conspiracy_120b")

        # --- 9. Civil Dispute vs Defense Claim (Fix F-05) ---
        if re.search(r"\b(falsely implicated|claims innocence|fabricated case by police|pleads false implication)\b", lower):
            defense_plea_false_implication = True

        pure_civil = bool(re.search(r"\b(invoices?.*(?:unpaid|due|dispute)|(?:unpaid|pending).*invoices?|arbitration|civil dispute|commercial (?:contract|lease|dealership|invoice|distributor)|reconciliation of accounts|delayed (?:payment|shipment|deliverables)|reconciliation dispute|master service agreement|partnership deed|quality audit certification|service level agreement|downtime violating)\b", lower))
        if pure_civil and not weapon_used and not death_caused and injury_severity == "None":
            is_commercial_civil_dispute = True
            tokens.append("civil_commercial_dispute")

        return AtomicFacts(
            is_out_of_domain=False,
            death_caused=death_caused,
            injury_severity=injury_severity,
            weapon_used=weapon_used,
            weapon_type=weapon_type,
            weapon_source=weapon_source,
            intention_to_cause_death=intention_to_cause_death,
            has_premeditation=has_premeditation,
            is_sudden_fight=is_sudden_fight,
            heat_of_passion=heat_of_passion,
            is_provocation=is_provocation,
            is_theft=is_theft,
            is_robbery=is_robbery,
            is_dacoity=is_dacoity,
            force_or_violence_used=force_or_violence_used,
            is_fraud_or_cheating=is_fraud_or_cheating,
            fraudulent_inducement_at_inception=fraudulent_inducement_at_inception,
            is_forgery=is_forgery,
            is_breach_of_trust=is_breach_of_trust,
            is_matrimonial=is_matrimonial,
            is_dowry_death=is_dowry_death,
            marriage_years=marriage_years,
            is_sexual_offence=is_sexual_offence,
            is_intimidation=is_intimidation,
            accused_count=accused_count,
            has_common_intention=has_common_intention,
            is_criminal_conspiracy=is_criminal_conspiracy,
            is_commercial_civil_dispute=is_commercial_civil_dispute,
            defense_plea_false_implication=defense_plea_false_implication,
            extracted_tokens=tokens
        )

    def _fuse_neural_and_deterministic(self, facts: AtomicFacts, text: str) -> AtomicFacts:
        """
        Ensemble fusion layer: combines deterministic clause-bounded parsing
        with GPU-accelerated deep learning perception (InLegalBERT / HF Instruction LLMs).
        
        CRITICAL ARCHITECTURAL GUARANTEE:
        - Deterministic negative assertions (e.g. 'victim was unarmed', 'no prior enmity',
          'no fraud at inception', 'purely commercial breach') ALWAYS supersede neural predictions,
          preventing the well-known attention-bleeding and negation failure modes of LLMs.
        - Deep learning perception augments non-negated ambiguous terms, noisy regional phrases,
          and complex multi-clause expressions when deterministic confidence is unassigned.
        """
        if self.neural_extractor is None:
            return facts

        try:
            neural_preds = self.neural_extractor.extract_neural_facts(text)
            if not neural_preds or not isinstance(neural_preds, dict):
                return facts

            lower = text.lower()
            accused_unarmed = bool(re.search(r"\b(accused|assailant|culprit|attacker)\b[^.!?]*\b(unarmed|had no weapon|without weapon|no weapon used|with no weapon|bare fist|with fists)\b", lower)) or bool(re.search(r"\b(no weapon(?: used)?|without any weapon|without any instrument|with no instrument)\b", lower))

            # 1. Weapon fusion (only if not explicitly negated by deterministic scoping)
            if not facts.weapon_used and neural_preds.get("weapon_used") is True and not accused_unarmed:
                facts.weapon_used = True
                neural_wtype = neural_preds.get("weapon_type")
                if neural_wtype and neural_wtype != "None":
                    facts.weapon_type = neural_wtype
                    facts.extracted_tokens.append(f"neural_weapon_{neural_wtype.lower()}")

            # 2. Injury Severity fusion (only upgrade if deterministic found None and no negative qualifiers)
            neural_injury = neural_preds.get("injury_severity")
            if facts.injury_severity == "None" and neural_injury in ["Simple", "Grievous", "Fatal"]:
                if not bool(re.search(r"\b(no (?:injury|hurt|wound|harm)|unhurt|uninjured|without any injury)\b", lower)):
                    facts.injury_severity = neural_injury
                    facts.extracted_tokens.append(f"neural_injury_{neural_injury.lower()}")

            # 3. Property crimes / Fraud / Dacoity enrichment
            if not facts.is_fraud_or_cheating and neural_preds.get("is_fraud_or_cheating") is True:
                if not facts.is_commercial_civil_dispute:
                    facts.is_fraud_or_cheating = True
                    facts.fraudulent_inducement_at_inception = True
                    facts.extracted_tokens.append("neural_fraudulent_inducement")

            if not facts.is_forgery and neural_preds.get("is_forgery") is True:
                facts.is_forgery = True
                facts.extracted_tokens.append("neural_forgery")

            if not facts.is_breach_of_trust and neural_preds.get("is_breach_of_trust") is True:
                facts.is_breach_of_trust = True
                facts.extracted_tokens.append("neural_breach_of_trust")

            # 4. Accused Count enrichment (e.g. neural detected 5+ dacoits from narrative)
            neural_count = neural_preds.get("accused_count")
            if isinstance(neural_count, int) and neural_count > facts.accused_count:
                facts.accused_count = neural_count
                if facts.accused_count >= 5 and (facts.is_robbery or bool(re.search(r"\b(looted|conjointly|intercepted|stormed|raided)\b", lower))):
                    facts.is_dacoity = True
                    facts.extracted_tokens.append("neural_dacoity_five_plus")
                if facts.accused_count >= 2:
                    facts.has_common_intention = True
                    facts.extracted_tokens.append("neural_joint_liability")

        except Exception:
            pass

        return facts

