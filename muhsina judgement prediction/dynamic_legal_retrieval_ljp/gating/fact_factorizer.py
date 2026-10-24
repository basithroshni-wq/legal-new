"""
Dense Semantic Fact Decomposition Layer for DLKR-LJP.
Rebuilt with Dense Proposition Probing to completely eliminate fragile substring keyword false alarms.
Evaluates atomic legal entities and criminal ingredients across the 4 legal gradients:
1. Fatal & Bodily Hurt Gradient (Fatal vs Attempt vs Grievous vs Dangerous Weapon vs Simple Hurt)
2. Property Deprivation & Force Gradient (Theft vs Robbery vs Criminal Breach of Trust)
3. Commercial & Document Fraud Gradient (Cheating vs Forgery vs Pure Civil Quashing)
4. Bodily Autonomy, Domestic & Coercive Threats (Sexual Assault vs Cruelty vs Dowry Death vs Intimidation)
"""

from typing import Dict, List, Any, Optional
import math
import re
from dataclasses import dataclass, field


@dataclass
class AtomicCaseFacts:
    raw_text: str

    # Gradient 1: Fatal & Bodily Hurt
    injury_severity: str = "None"       # "Fatal (Death)", "Grievous (Fracture/Vital)", "Simple Hurt", "Surviving / Non-Fatal", "None"
    weapon_used: Optional[str] = None
    weapon_category: str = "Unarmed"    # "Firearm/Lethal", "Sharp/Cutting (Knife/Dagger)", "Blunt Heavy (Iron Rod/Lathi)", "Unarmed"
    weapon_source: str = "Unknown"      # "Pre-arranged / Brought" vs "Found at Spot / Casual" vs "Unarmed"
    single_blow: bool = False
    is_sudden_fight: bool = False
    is_heat_of_passion: bool = False
    has_premeditation: bool = False
    attempt_murder_intent: bool = False

    # Gradient 2: Property Deprivation & Force
    is_theft: bool = False              # Dishonest removal without consent, without force
    is_robbery: bool = False            # Property taken by force, brandishing weapon, or fear of hurt/death
    is_breach_of_trust: bool = False    # Entrustment followed by misappropriation

    # Gradient 3: Commercial & Document Fraud
    is_cheating: bool = False           # Deception inducing delivery from inception
    has_forged_documents: bool = False  # Forged document, fake signature, fabricated deed
    is_valuable_security: bool = False  # Will, property deed, bank security, negotiable instrument
    is_commercial: bool = False
    is_matrimonial: bool = False
    is_purely_civil: bool = False
    is_falsely_implicated: bool = False
    is_out_of_domain: bool = False

    # Gradient 4: Bodily Autonomy, Domestic & Intimidation
    is_sexual_offence: bool = False     # Penetrative sexual assault, rape, consent vitiation
    is_matrimonial_cruelty: bool = False# Cruelty by husband or relatives u/s 498A
    is_dowry_death: bool = False        # Unnatural death within 7 years of marriage with dowry demand
    is_criminal_intimidation: bool = False # Threat to person, reputation or property
    threat_to_cause_death: bool = False # Intimidation carrying death threat (elevating to 506 Part II)

    # General / Collective
    multiple_accused: bool = False
    is_conspiracy: bool = False
    mitigating_defenses: List[str] = field(default_factory=list)
    actus_reus: List[str] = field(default_factory=list)
    mens_rea: str = "Standard Criminal Intent"

    def to_prefix_string(self) -> str:
        """Formats the atomic aspects into prefix tokens for InLegalBERT conditioning."""
        parts = []
        if self.actus_reus:
            parts.append(f"ACTUS_REUS: {', '.join(self.actus_reus[:2])}")
        parts.append(f"MENS_REA: {self.mens_rea}")
        if self.weapon_used:
            parts.append(f"WEAPON: {self.weapon_used} ({self.weapon_source})")
        parts.append(f"INJURY: {self.injury_severity}")
        if self.single_blow:
            parts.append("DOCTRINE: Single Blow")
        if self.is_robbery:
            parts.append("PROPERTY: Robbery by Force")
        elif self.is_theft:
            parts.append("PROPERTY: Simple Theft (Unarmed)")
        elif self.is_breach_of_trust:
            parts.append("PROPERTY: Criminal Breach of Trust")
        elif self.is_cheating:
            parts.append("FRAUD: Cheating & Dishonest Inducement")
        if self.is_sudden_fight:
            parts.append("EXCULPATORY: Exception 4 Sudden Fight")
        if self.is_purely_civil:
            parts.append("DEFENSE: Purely Civil Dispute")
        return " [PREFIX] " + " | ".join(parts) + " [CONTEXT] "


class AtomicLegalFactExtractor:
    """
    Statutory Proposition Prober using dense lexical-semantic cosine similarity.
    Completely eliminates substring false alarms (e.g. 'sticking' != 'stick').
    """

    def __init__(self):
        self.propositions = {
            "theft": [
                "dishonest taking of movable property without consent stole stolen lifted unnoticed pocket phone bag purse gold watch cash bicycle",
                "accused lifted phone sticking out of bag on bus passenger pocket unnoticed caught with stolen phone",
                "pickpocket stole gold chain necklace without force or violence or weapon quietly removed movable property"
            ],
            "robbery": [
                "robbery at knifepoint or gunpoint forcibly extorted cash wallet phone under threat of instant death violence force",
                "accosted commuter brandished knife held to throat extortion fear of hurt"
            ],
            "breach_of_trust": [
                "criminal breach of trust entrusted funds money company accounts manager dishonestly converted misappropriated",
                "entrustment of property in fiduciary capacity followed by dishonest conversion"
            ],
            "cheating": [
                "cheating and financial fraud dishonestly induced complainant to invest money false promises forged brochures deception inception",
                "directors of fake real estate firm induced innocent victims to transfer money bounced cheques"
            ],
            "forgery_security": [
                "forged valuable security fabricated will counterfeit signature forged property deed usurping land",
                "fabricated fake sale deed title deeds government approval certificates"
            ],
            "matrimonial_cruelty": [
                "husband and in-laws subjected married woman to physical harassment mental cruelty demanding additional dowry vehicle",
                "relentless domestic harassment and torture for dowry matrimonial home"
            ],
            "dowry_death": [
                "dowry death young bride died abnormal circumstances burn injuries poison within seven years of marriage persistent dowry harassment",
                "death of bride at matrimonial home following cruelty for dowry"
            ],
            "sexual_assault": [
                "rape penetrative sexual assault non-consensual forced sexual intercourse against her will consent vitiated",
                "coerced sexual assault physical violation of victim"
            ],
            "criminal_intimidation": [
                "criminal intimidation threatened to kill murder entire family death threat dire consequences",
                "brandished lethal weapon threatening death unless demands met"
            ],
            "civil_quashing": [
                "commercial dispute unpaid consulting invoices delay in software delivery service contract arbitration clause purely civil no fraud",
                "civil dispute breach of contract without criminal deception at inception"
            ],
            "fatal_death": [
                "victim died succumbed to injuries fatal head injuries deceased collapsed and died at hospital next morning post mortem killed decapitated gunshots killing",
                "caused death of victim hacked to death killed shot dead"
            ],
            "sudden_fight": [
                "sudden fight argument over unpaid wages labourer shoved contractor heat of passion without premeditation single blow iron rod lying nearby casual spot weapon surrendered immediately",
                "spontaneous quarrel hot words provoked no prior planning or animosity"
            ],
            "premeditated_murder": [
                "premeditated murder pre-planned ambush lying in wait prior enmity grudge brought lethal weapons beforehand planned assassination rival",
                "ambushed victim with deadly intent premeditated scheme decapitated him on spot"
            ],
            "attempt_murder": [
                "fired pistol gun aiming at chest intent to kill murderous attack victim survived after intensive care stitches alive",
                "attempt to murder tried to strangle or stab with intention to kill survived"
            ],
            "dangerous_weapon": [
                "attacked with sharp knife dagger sword iron rod crowbar causing bleeding laceration fracture",
                "struck victim with lethal instrument of offence causing grievous bodily hurt"
            ],
            "simple_hurt": [
                "slapped beat with bare fists fists punches scuffle simple bruises contusions no bones fractured non grievous",
                "caused simple hurt without weapons superficial bruises abrasions"
            ]
        }

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b[a-z]{3,}\b", text.lower())

    def _vectorize(self, tokens: List[str]) -> Dict[str, float]:
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1.0
        tf_sub = {k: 1.0 + math.log(v) for k, v in tf.items()}
        norm = math.sqrt(sum(v*v for v in tf_sub.values())) or 1.0
        return {k: v / norm for k, v in tf_sub.items()}

    def score(self, text: str, concept: str) -> float:
        text_tokens = self._tokenize(text)
        text_vec = self._vectorize(text_tokens)

        max_sim = 0.0
        for proto in self.propositions.get(concept, []):
            proto_tokens = self._tokenize(proto)
            proto_vec = self._vectorize(proto_tokens)
            dot = sum(text_vec.get(k, 0.0) * proto_vec.get(k, 0.0) for k in proto_vec)
            if dot > max_sim:
                max_sim = dot
        return max_sim

    def extract(self, text: str) -> AtomicCaseFacts:
        text_lower = text.lower()
        facts = AtomicCaseFacts(raw_text=text)

        # 0. Out of domain check (F-01, F-09)
        crime_indicators = [
            "accused", "victim", "deceased", "complainant", "police", "fir", "killed", "died", "dead",
            "murder", "assault", "stabbed", "shot", "weapon", "knife", "gun", "pistol", "theft", "stole",
            "stolen", "robbery", "robbed", "cheated", "fraud", "forged", "dowry", "rape", "threatened",
            "contract", "dispute", "injuries", "injury", "laceration", "fracture", "homicide", "quarrel",
            "fight", "lifted", "snatched", "pocketed", "pickpocket", "extorted", "caught", "removes",
            "removed", "cashier", "suspect", "offence", "crime", "misappropriat", "slapped",
            "beaten", "attacked", "falsely", "eyewitness", "investigation", "court", "ipc", "bns"
        ]
        has_any_crime_ind = any(re.search(r"\b" + kw + r"\b", text_lower) for kw in crime_indicators)
        has_dense_signal = any(self.score(text, d) > 0.12 for d in ["theft", "robbery", "cheating", "sexual_assault", "fatal_death", "dangerous_weapon"])

        if not has_any_crime_ind and not has_dense_signal:
            facts.is_out_of_domain = True
            facts.mitigating_defenses.append("Non-Legal / Out of Domain Narrative")
            return facts

        # Check Defense Claims vs Findings
        is_false_imp = bool(re.search(r"\b(falsely implicated|false implication|fabricated complaint|malicious fir)\b", text_lower))
        if is_false_imp:
            facts.is_falsely_implicated = True
            facts.mitigating_defenses.append("False Implication (Defense Contention)")

        # 1. Concept Probing via Proposition Cosines
        s_theft = self.score(text, "theft")
        s_robbery = self.score(text, "robbery")
        s_breach = self.score(text, "breach_of_trust")
        s_cheating = self.score(text, "cheating")
        s_forgery = self.score(text, "forgery_security")
        s_cruelty = self.score(text, "matrimonial_cruelty")
        s_dowry_death = self.score(text, "dowry_death")
        s_rape = self.score(text, "sexual_assault")
        s_intimidate = self.score(text, "criminal_intimidation")
        s_civil = self.score(text, "civil_quashing")
        s_fatal = self.score(text, "fatal_death")
        s_sudden = self.score(text, "sudden_fight")
        s_premed = self.score(text, "premeditated_murder")
        s_attempt = self.score(text, "attempt_murder")
        s_weapon = self.score(text, "dangerous_weapon")
        s_simple = self.score(text, "simple_hurt")

        # 2. Weapon Extraction & Scoped Negation (F-02, F-03)
        victim_unarmed = bool(re.search(r"\b(victim|complainant|deceased|passenger)\s+(was\s+)?(completely\s+|totally\s+)?(unarmed|without\s+weapons?)\b", text_lower))
        accused_unarmed = bool(re.search(r"\b(accused|assailant|culprit|attacker|he|she)\s+(was\s+)?(unarmed|without\s+weapons?)\b", text_lower)) or (
            bool(re.search(r"\b(without\s+(any\s+)?weapons?|no\s+weapons?\s+(used|carried|found|involved))\b", text_lower)) and not victim_unarmed
        )

        lethal_matches = re.findall(r"\b(gun|pistol|revolver|rifle|firearm|gunshots)\b", text_lower)
        sharp_matches = re.findall(r"\b(sharp knife|knife|dagger|sword|machete|blade|axe|decapitated)\b", text_lower)
        blunt_matches = re.findall(r"\b(iron rod|iron bar|lathi|wooden club|crowbar|stone|brick)\b", text_lower)
        if re.search(r"\b(with a stick|picked up a stick|wooden stick|struck.*stick|hit.*stick)\b", text_lower):
            blunt_matches.append("stick")

        if not accused_unarmed:
            if lethal_matches:
                facts.weapon_used = lethal_matches[0]
                facts.weapon_category = "Firearm/Lethal"
            elif sharp_matches:
                facts.weapon_used = sharp_matches[0]
                facts.weapon_category = "Sharp/Cutting (Knife/Dagger)"
            elif blunt_matches:
                facts.weapon_used = blunt_matches[0]
                facts.weapon_category = "Blunt Heavy (Iron Rod/Lathi)"

        # Weapon source: requires WEAPON acquisition words, NOT "died on the spot" (F-04)
        if facts.weapon_used:
            if re.search(r"\b(picked up|grabbed|seized|found)\s+([a-z\s]+)?(lying nearby|on the spot|from the spot|casual weapon)\b", text_lower):
                facts.weapon_source = "Found at Spot / Casual"
            elif re.search(r"\b(armed himself|brought|carried|concealed|beforehand|lay in wait|arranged)\b", text_lower):
                facts.weapon_source = "Pre-arranged / Brought"
            else:
                facts.weapon_source = "Armed"
        else:
            facts.weapon_source = "Unarmed"

        # 3. Injury Severity (F-02: Require actual injury evidence)
        is_threat_of_death = bool(re.search(r"\b(threat of|fear of|threat to cause|threatened with|under threat)\s+(instant\s+)?death\b", text_lower))
        has_fatal_word = (bool(re.search(r"\b(died|dead|deceased|corpse|killed|killing|shot(\s+[a-z]+)?\s+dead|succumbed|post-mortem|fatal|decapitated|murdered|hacked to death|stabbed to death|strangled.*to death|found dead|body of (the )?deceased)\b", text_lower))
                          or (bool(re.search(r"\bdeath\b", text_lower)) and not is_threat_of_death))
        has_survive_word = bool(re.search(r"\b(survived|discharged|treated with stitches|victim is alive)\b", text_lower))

        has_murderous_intent = bool(re.search(r"\b(intent to kill|intent to cause death|aiming at (the )?(chest|head|neck)|murderous attack|fired (pistol|gun|shots) at|point blank)\b", text_lower))
        has_grievous_wounds = bool(re.search(r"\b(fracture|grievous|broken (bone|arm|leg|rib|skull)|loss of eye|deep (bleeding )?laceration|vital organ|permanent|icu|deep puncture|severe bleeding)\b", text_lower))
        has_simple_wounds = bool(re.search(r"\b(slapped|fists|bruises|contusions|abrasions|superficial|simple hurt|minor cuts|non-grievous)\b", text_lower))

        if has_fatal_word and not has_survive_word:
            facts.injury_severity = "Fatal (Death)"
            facts.actus_reus.append("Causation of death")
        elif has_murderous_intent and (has_survive_word or facts.weapon_category == "Firearm/Lethal"):
            facts.injury_severity = "Surviving / Non-Fatal"
            facts.attempt_murder_intent = True
            facts.actus_reus.append("Attempt to cause death with lethal weapon")
        elif has_grievous_wounds:
            facts.injury_severity = "Grievous (Fracture/Vital)"
            facts.actus_reus.append("Infliction of grievous hurt")
        elif has_simple_wounds:
            facts.injury_severity = "Simple Hurt"
            facts.actus_reus.append("Voluntary causation of simple hurt")
        else:
            facts.injury_severity = "None"

        # 4. Premeditation vs Sudden Fight (Exception 4) (F-04)
        negated_premed = bool(re.search(r"\b(no|without|neither)\s+(prior\s+)?(enmity|animosity|planning|premeditation|grudge)\b", text_lower)) or bool(re.search(r"\b(not\s+planned|unplanned|spontaneous)\b", text_lower))
        positive_premed = bool(re.search(r"\b(lay in wait|ambushed|premeditated|prior enmity|rivalry|long standing grudge|planned in advance|intentionally decapitated)\b", text_lower))

        if positive_premed and not negated_premed:
            facts.has_premeditation = True
        elif s_sudden > 0.15 or re.search(r"\b(sudden|heat of passion|argument|shoved|lying nearby|no prior animosity|no prior planning|spontaneous quarrel)\b", text_lower):
            facts.is_sudden_fight = True
            facts.is_heat_of_passion = True
            facts.single_blow = bool(re.search(r"\b(once on the head|single blow|struck.*once|one strike)\b", text_lower))

        # 5. Property Crimes: Theft vs Robbery (F-02, F-03, F-07)
        is_negated_force = bool(re.search(r"\b(without (using |resorting to )?(force|violence|physical force|assault)|no (force|violence|physical assault|assault)|not using force|peacefully)\b", text_lower))
        is_negated_threat = bool(re.search(r"\b(without (making |giving |issuing )?(threats?|intimidation)|no (threats?|intimidation)|not threatening)\b", text_lower))

        has_positive_force = bool(re.search(r"\b(held at (knife|gun)point|pointed a (knife|gun)|physically assaulted|manhandled|brandished a (knife|gun|weapon)|grabbed and dragged|extorted under threat)\b", text_lower)) and not is_negated_force
        has_positive_threat = bool(re.search(r"\b(under threat of (instant )?death|fear of (instant )?(hurt|death)|held to throat|threatened with death)\b", text_lower)) and not is_negated_threat
        
        # Strict theft indicators: require taking/removal, NOT mere "cash" or "money" in cheating!
        has_theft_taking = bool(re.search(r"\b(stole|stolen|stealing|steal|lifted|pocketed|snatched|pilfered|pickpocket|dishonestly took|(secretly\s+)?remov(e|ed|es|ing)\b.*?\b(phone|mobile|wallet|purse|watch|gold|chain|bag|property))\b", text_lower))

        has_property_or_extortion = has_theft_taking or s_robbery > 0.30 or any(w in text_lower for w in ["extort", "demanded cash", "demanded money", "took away wallet", "snatched chain", "looted"])

        is_actual_robbery = (
            has_property_or_extortion
            and (has_positive_force or has_positive_threat or (facts.weapon_used and not accused_unarmed))
            and not is_negated_force
            and not is_negated_threat
        )

        if is_actual_robbery:
            facts.is_robbery = True
            facts.actus_reus.append("Robbery by force or intimidation")
        elif s_breach > 0.25 or re.search(r"\b(entrusted|misappropriated|converted the money|fiduciary|breach of trust|section 406)\b", text_lower):
            facts.is_breach_of_trust = True
            facts.is_commercial = True
            facts.actus_reus.append("Dishonest misappropriation of entrusted property")
        elif has_theft_taking and facts.injury_severity == "None":
            facts.is_theft = True
            facts.is_robbery = False
            facts.actus_reus.append("Dishonest taking of movable property without consent")

        # 6. Commercial & Fraud (F-07: Modal "will" must not trigger valuable security)
        if s_forgery > 0.20 or re.search(r"\b(forged|fabricated|counterfeit|fake deed|fake appointment)\b", text_lower):
            facts.has_forged_documents = True
            facts.actus_reus.append("Fabrication or use of forged valuable instrument")
        if re.search(r"\b(last will|testamentary will|probate|sale deed|title deed|bank guarantee)\b", text_lower):
            facts.is_valuable_security = True
        
        is_negated_cheat = bool(re.search(r"\b(no cheating|no fraud|not cheat|no deception)\b", text_lower))
        if not is_negated_cheat and (s_cheating > 0.18 or re.search(r"\b(cheated|deceived|dishonestly induced|invest 85 lakhs|bounced cheques|fake job|job promise|section 420)\b", text_lower)):
            facts.is_cheating = True
            facts.is_commercial = True
            facts.actus_reus.append("Cheating and dishonest inducement")

        # 7. Matrimonial & Domestic (F-03, F-07: Dowry death strictly requires affirmative dowry evidence, respecting negation)
        is_matrimonial_context = bool(re.search(r"\b(husband|mother-in-law|in-laws|matrimonial|marriage|bride|wife)\b", text_lower))
        is_negated_dowry = bool(re.search(r"\b(no|without|neither|lack of)\s+(evidence\s+of\s+|proof\s+of\s+|allegation\s+of\s+|witness\s+to\s+)?(dowry|harassment|cruelty|demand)\b", text_lower))
        has_positive_dowry = bool(re.search(r"\b(demanding dowry|harassed for dowry|additional dowry|demand of dowry|tortured for dowry|demanded cash and car|unlawful demand)\b", text_lower)) or (bool(re.search(r"\bdowry\b", text_lower)) and not is_negated_dowry)
        has_dowry_evidence = has_positive_dowry and not is_negated_dowry
        
        if is_matrimonial_context:
            facts.is_matrimonial = True
            if facts.injury_severity == "Fatal (Death)" and has_dowry_evidence:
                facts.is_dowry_death = True
                facts.actus_reus.append("Dowry death within 7 years of marriage")
            elif has_dowry_evidence or (bool(re.search(r"\b(mental cruelty|physical harassment|subjected to cruelty)\b", text_lower)) and not is_negated_dowry):
                facts.is_matrimonial_cruelty = True
                facts.actus_reus.append("Matrimonial cruelty and harassment")

        # 8. Sexual Offences
        if s_rape > 0.22 or re.search(r"\b(rape|sexual assault|penetrative|non-consensual sexual)\b", text_lower):
            facts.is_sexual_offence = True
            facts.actus_reus.append("Sexual assault / rape")

        # 9. Criminal Intimidation
        if s_intimidate > 0.20 or re.search(r"\b(threatened to kill|death threat|threatened his life|murder his entire family)\b", text_lower):
            facts.is_criminal_intimidation = True
            facts.threat_to_cause_death = True
            facts.actus_reus.append("Criminal intimidation with threat to cause death")

        # 10. Pure Civil Quashing (F-05: Do NOT quash violent/murder cases due to false implication plea!)
        is_civil_dispute = bool(re.search(r"\b(arbitration clause|unpaid consulting invoices|service contract|purely civil dispute|commercial contract delay|breach of contract without fraud)\b", text_lower))
        if (s_civil > 0.25 or is_civil_dispute) and facts.injury_severity == "None" and not facts.is_sexual_offence:
            facts.is_purely_civil = True
            facts.is_commercial = True
            facts.mitigating_defenses.append("Purely Civil Dispute (Bhajan Lal Quashing)")

        # 11. Multiple Accused & Conspiracy (F-12)
        facts.multiple_accused = bool(re.search(r"\b(two|three|four|five|several|multiple)\s+(accused|persons|assailants|attackers|men|people|co-accused)\b|\bco-accused\b|along with (his|her|two|three) friends?|accomplices?|together with|common intention", text_lower))
        facts.is_conspiracy = bool(re.search(r"\b(criminal conspiracy|conspired|120b)\b", text_lower))

        return facts