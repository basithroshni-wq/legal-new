"""
Curated External Legal Knowledge Base for Indian Criminal Jurisprudence (IPC 1860 & BNS 2023).
Provides comprehensive statutory provisions and authoritative Supreme Court precedent ratios
across all 20 configured criminal articles and 13 major offence categories.
"""

from typing import List, Dict, Any

EXTERNAL_LEGAL_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. HOMICIDE & ATTEMPT (IPC 302, 304 PART I, 304 PART II, 307)
    # =========================================================================
    {
        "id": "ART_IPC_302_BNS_103",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_302_BNS_103",
        "title": "Murder (IPC Section 302 / BNS Section 103)",
        "charge": "Murder & Culpable Homicide",
        "penalty_tier": "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)",
        "content": "Section 302 IPC / Section 103 BNS: Punishment for murder. Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine. Attracted when the act causing death is done with the premeditated intention of causing death, or with the intention of causing bodily injury sufficient in the ordinary course of nature to cause death, without any general exceptions.",
        "essential_elements": [
            "Actus reus causing death of human being",
            "Premeditated mens rea or deliberate intention to cause death",
            "Bodily injury intended and sufficient in the ordinary course of nature to cause death",
            "Absence of sudden quarrel, heat of passion, or grave provocation"
        ]
    },
    {
        "id": "PREC_BACHAN_SINGH_DEATH",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_302_BNS_103",
        "title": "Bachan Singh v. State of Punjab (1980) 2 SCC 684",
        "charge": "Murder & Culpable Homicide",
        "penalty_tier": "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)",
        "content": "Constitution Bench ratio: Capital punishment should be awarded only in the 'rarest of rare cases' where the alternative option of life imprisonment is unquestionably foreclosed. Emphasizes balancing aggravating circumstances against mitigating circumstances, premeditation, brutality, and lack of sudden impulse.",
        "essential_elements": [
            "Extreme brutality and pre-planned execution",
            "Absence of mitigating circumstances",
            "Life sentence as primary statutory baseline"
        ]
    },
    {
        "id": "PREC_VIRSA_SINGH_INTENT",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_302_BNS_103",
        "title": "Virsa Singh v. State of Punjab (1958) SCR 1495",
        "charge": "Murder & Culpable Homicide",
        "penalty_tier": "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)",
        "content": "Four-step test for Section 300 clause 3rdly: Prosecution must prove: (1) bodily injury present, (2) nature of injury proved objectively, (3) intention to inflict that particular bodily injury, (4) injury sufficient in ordinary course of nature to cause death. Premeditation or targeted lethal attack with deadly weapon.",
        "essential_elements": [
            "Targeted lethal bodily injury",
            "Intentional infliction of vital organ strike",
            "Objective sufficiency to cause death"
        ]
    },
    {
        "id": "ART_IPC_304_PART1_BNS_105",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_304_PART1_BNS_105",
        "title": "Culpable Homicide Not Amounting to Murder - Part I (IPC Section 304 Part I / BNS Section 105)",
        "charge": "Murder & Culpable Homicide",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Section 304 Part I IPC / Section 105 BNS: If the act by which death is caused is done with the intention of causing death, or of causing such bodily injury as is likely to cause death, but falls under one of the Exceptions to Section 300 IPC (e.g., grave and sudden provocation Exception 1, excess of private defence Exception 2). Punishable with imprisonment for life, or imprisonment of either description for a term which may extend to 10 years, and fine.",
        "essential_elements": [
            "Intention to cause bodily injury likely to cause death",
            "Mitigated by statutory Exception to Section 300 (Provocation or Private Defence)",
            "Absence of premeditated cold-blooded plan"
        ]
    },
    {
        "id": "PREC_KALU_RAM_INTENTION",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_304_PART1_BNS_105",
        "title": "Kalu Ram v. State of Rajasthan (2000) 1 SCC 71",
        "charge": "Murder & Culpable Homicide",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Where death occurs due to rash act or assault without premeditation in a domestic or sudden flare-up, but bodily injury was likely to cause death, Section 304 Part I is attracted rather than Section 302, capping severity to substantial imprisonment.",
        "essential_elements": [
            "Injury inflicted likely to cause death",
            "Spontaneous eruption without prior malice",
            "Mitigated culpability below capital murder"
        ]
    },
    {
        "id": "ART_IPC_304_PART2_BNS_105",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_304_PART2_BNS_105",
        "title": "Culpable Homicide Not Amounting to Murder - Part II (IPC Section 304 Part II / BNS Section 105)",
        "charge": "Culpable Homicide (Sudden Fight / Heat of Passion)",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Section 304 Part II IPC / Section 105 BNS: If the act is done with knowledge that it is likely to cause death, but without any intention to cause death or to cause such bodily injury as is likely to cause death. Punished with imprisonment for a term which may extend to 10 years, or with fine, or both. Governs Exception 4 to Section 300 IPC (sudden fight, heat of passion, sudden quarrel, weapon found at spot, single blow).",
        "essential_elements": [
            "Act done with knowledge that it is likely to cause death",
            "Absence of premeditation or prior planning",
            "Sudden fight in heat of passion upon a sudden quarrel (Exception 4)",
            "Single blow without undue cruelty or taking undue advantage"
        ]
    },
    {
        "id": "PREC_PULICHERLA_SINGLE_BLOW",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_304_PART2_BNS_105",
        "title": "Pulicherla Nagaraju v. State of A.P. (2006) 11 SCC 444",
        "charge": "Culpable Homicide (Sudden Fight / Heat of Passion)",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Landmark Supreme Court ratio on Single Blow and Exception 4 to Section 300 IPC. Where a single blow is inflicted during a sudden quarrel without premeditation using a weapon picked up from the spot, and there is no prior animosity or intention to kill, the offense is culpable homicide not amounting to murder under Section 304 Part II IPC (up to 10 years imprisonment), not murder under Section 302 IPC.",
        "essential_elements": [
            "Sudden fight and absence of premeditation",
            "Single strike / non-cruel act",
            "Weapon picked from spot rather than pre-arranged",
            "Altercation over immediate dispute"
        ]
    },
    {
        "id": "PREC_GHAPOO_YADAV_EXCEPTION4",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_304_PART2_BNS_105",
        "title": "Ghapoo Yadav v. State of M.P. (2003) 3 SCC 528",
        "charge": "Culpable Homicide (Sudden Fight / Heat of Passion)",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Four requisites of Exception 4 to Section 300 IPC: (1) Sudden fight, (2) No premeditation, (3) Heat of passion upon a sudden quarrel, (4) No undue advantage or unusual cruelty. Offence converted from Section 302 to Section 304 Part II.",
        "essential_elements": [
            "Sudden quarrel in heat of passion",
            "No premeditation",
            "Lack of undue cruelty",
            "Mutual altercation"
        ]
    },
    {
        "id": "ART_IPC_307_BNS_109",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_307_BNS_109",
        "title": "Attempt to Murder (IPC Section 307 / BNS Section 109)",
        "charge": "Attempt to Murder",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Section 307 IPC / Section 109 BNS: Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder. Punishable with imprisonment of either description for a term which may extend to 10 years, and fine; and if hurt is caused to any person, offender shall be liable either to imprisonment for life, or to such punishment as aforesaid.",
        "essential_elements": [
            "Intention or knowledge to commit act causing death",
            "Execution of overt act towards completion",
            "Victim survived the murderous attack",
            "Weapon capable of inflicting lethal injury"
        ]
    },
    {
        "id": "PREC_BALRAM_PATIL_ATTEMPT",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_307_BNS_109",
        "title": "State of Maharashtra v. Balram Bama Patil (1983) 2 SCC 28",
        "charge": "Attempt to Murder",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Supreme Court held that to justify conviction under Section 307, it is not essential that bodily injury capable of causing death should actually have been inflicted. What matters is the intention or knowledge and the overt act executed towards murder.",
        "essential_elements": [
            "Overt assault with intention or knowledge",
            "Lethal intent irrespective of whether wound proved fatal",
            "Survival of victim"
        ]
    },

    # =========================================================================
    # 2. BODILY HURT & ASSAULT (IPC 323, 324, 326)
    # =========================================================================
    {
        "id": "ART_IPC_323_BNS_115",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_323_BNS_115",
        "title": "Voluntarily Causing Hurt (IPC Section 323 / BNS Section 115(2))",
        "charge": "Assault & Grievous Hurt",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Section 323 IPC / Section 115(2) BNS: Whoever voluntarily causes hurt shall be punished with imprisonment of either description for a term which may extend to one year, or with fine which may extend to one thousand rupees, or with both. Involves bodily pain, disease, or infirmity caused without dangerous weapons or permanent injury.",
        "essential_elements": [
            "Bodily pain, disease or infirmity caused to victim",
            "Voluntary intention or knowledge",
            "Absence of deadly or dangerous weapons",
            "Minor injury / simple bruises or contusions"
        ]
    },
    {
        "id": "PREC_BISHEN_SINGH_HURT",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_323_BNS_115",
        "title": "Bishen Singh v. State of Punjab (1973) 3 SCC 323",
        "charge": "Assault & Grievous Hurt",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Where assault is confined to fists or slaps causing simple bruises without fractures, dangerous weapons, or endangerment of life, conviction lies strictly under Section 323 IPC with penalty capped under 1 year.",
        "essential_elements": [
            "Simple hurt without weapon",
            "Superficial bruises or contusions",
            "Maximum 1 year penalty limit"
        ]
    },
    {
        "id": "ART_IPC_324_BNS_117",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_324_BNS_117",
        "title": "Voluntarily Causing Hurt by Dangerous Weapons or Means (IPC Section 324 / BNS Section 118(1))",
        "charge": "Assault & Grievous Hurt",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Section 324 IPC / Section 118(1) BNS: Whoever voluntarily causes hurt by means of any instrument for shooting, stabbing or cutting, or any instrument which used as a weapon of offence is likely to cause death, or by fire, corrosive substance, or poison. Punished with imprisonment for a term which may extend to three years, or with fine, or both.",
        "essential_elements": [
            "Causing simple hurt or injury to victim",
            "Use of weapon of offence: blade, knife, dagger, fire, corrosive substance",
            "Absence of fracture or permanent privation (which would elevate to Sec 326)",
            "Punishment ceiling of 3 years"
        ]
    },
    {
        "id": "PREC_ANWARUL_HAQ_WEAPON_HURT",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_324_BNS_117",
        "title": "Anwarul Haq v. State of U.P. (2005) 10 SCC 581",
        "charge": "Assault & Grievous Hurt",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Section 324 applies when an instrument for cutting or stabbing is used to inflict bodily hurt, but the injury does not fall under any of the eight clauses of Section 320 (grievous hurt) and lacks intention to kill under Section 307. Penalty is capped at 3 years (Tier 1).",
        "essential_elements": [
            "Sharp or dangerous weapon utilized",
            "Non-grievous bodily injury",
            "Statutory 3-year imprisonment ceiling"
        ]
    },
    {
        "id": "ART_IPC_326_BNS_118",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_326_BNS_118",
        "title": "Voluntarily Causing Grievous Hurt by Dangerous Weapons (IPC 326 / BNS 118)",
        "charge": "Assault & Grievous Hurt",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Section 326 IPC / Section 118(2) BNS: Whoever voluntarily causes grievous hurt by means of any instrument for shooting, stabbing or cutting, or deadly weapon, shall be punished with imprisonment for life, or with imprisonment for a term which may extend to ten years, and fine. Grievous hurt encompasses fracture, dislocation of bone, permanent privation of sight or hearing, or danger to life for 20 days.",
        "essential_elements": [
            "Grievous hurt (fracture, bone dislocation, permanent disability u/s 320)",
            "Dangerous weapon or instrument of shooting, stabbing, iron rod, or cutting",
            "Voluntary causation without lethal intent to commit murder u/s 307",
            "Penalty extending up to 10 years"
        ]
    },
    {
        "id": "PREC_MATHURADAS_GRIEVOUS_HURT",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_326_BNS_118",
        "title": "Mathuradas v. State of Maharashtra (1970) 1 SCC 512",
        "charge": "Assault & Grievous Hurt",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Supreme Court held that to sustain conviction under Section 326, there must be clear medical evidence of fracture or grievous bodily hurt under Section 320 caused by a dangerous weapon. Distinguishes from Section 307 where intention to kill is the paramount ingredient.",
        "essential_elements": [
            "Medical corroboration of fracture or grievous injury",
            "Dangerous weapon utilized",
            "Penalty scaled to substantial term under 10 years"
        ]
    },

    # =========================================================================
    # 3. PROPERTY OFFENCES & THEFT / ROBBERY (IPC 379, 392, 406)
    # =========================================================================
    {
        "id": "ART_IPC_379_BNS_303",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_379_BNS_303",
        "title": "Theft (IPC Section 379 / BNS Section 303(2))",
        "charge": "Theft & Dacoity",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Section 379 IPC / Section 303(2) BNS: Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both. Theft defined u/s 378: Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking.",
        "essential_elements": [
            "Dishonest intention to take movable property",
            "Property taken out of possession of another person",
            "Absence of person's consent",
            "Moving of property in order to such taking",
            "Absence of force, threat or violence (which would elevate to Robbery)"
        ]
    },
    {
        "id": "PREC_KN_MEHRA_THEFT",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_379_BNS_303",
        "title": "K.N. Mehra v. State of Rajasthan (1957) SCR 623",
        "charge": "Theft & Dacoity",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Supreme Court landmark judgment on ingredients of Theft: Dishonest taking means causing wrongful gain or wrongful loss. Even temporary taking of aircraft or movable property without consent satisfies Section 378/379. Penalty is capped at 3 years (Tier 1).",
        "essential_elements": [
            "Movable property taken dishonestly",
            "Lack of consent from possessor",
            "Moving the property constitutes complete offence",
            "Sentence capped at 3 years"
        ]
    },
    {
        "id": "ART_IPC_392_BNS_309",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_392_BNS_309",
        "title": "Robbery (IPC Section 392 / BNS Section 309(4))",
        "charge": "Theft & Dacoity",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Section 392 IPC / Section 309(4) BNS: Whoever commits robbery shall be punished with rigorous imprisonment for a term which may extend to ten years, and fine; and if the robbery be committed on the highway between sunset and sunrise, imprisonment may extend to fourteen years. Robbery defined u/s 390: Theft is robbery if the offender causes or attempts to cause death, hurt, or wrongful restraint, or fear of instant death/hurt.",
        "essential_elements": [
            "Theft or extortion of property",
            "Voluntary causation of hurt, death, or wrongful restraint, or threat thereof",
            "Force or deadly weapon used during or to effectuate the taking",
            "Punishment extending up to 10 years (Tier 3)"
        ]
    },
    {
        "id": "PREC_JOSEPH_KOLI_ROBBERY",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_392_BNS_309",
        "title": "State of Maharashtra v. Joseph Mingel Koli (1997) Cri LJ 3968",
        "charge": "Theft & Dacoity",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Supreme Court ratio on transition from Theft to Robbery: When the taking of movable property is accompanied by putting the victim in fear of instant hurt or weapon brandishing (knife/firearm), Section 379 is aggravated into Section 392 Robbery, attracting rigorous imprisonment up to 10 years.",
        "essential_elements": [
            "Aggravated theft accompanied by force or deadly threat",
            "Brandishing weapon to extort property",
            "Tier 3 sentencing severity up to 10 years"
        ]
    },
    {
        "id": "ART_IPC_406_BNS_316",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_406_BNS_316",
        "title": "Criminal Breach of Trust (IPC Section 406 / BNS Section 316)",
        "charge": "Criminal Breach of Trust",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Section 406 IPC / Section 316 BNS: Punishment for criminal breach of trust. Imprisonment of either description for a term which may extend to three years, or with fine, or with both. Requires entrustment of property and subsequent dishonest misappropriation or conversion to own use.",
        "essential_elements": [
            "Entrustment of property or dominion over property",
            "Dishonest misappropriation or conversion to accused's own use",
            "Violation of direction of law or contract",
            "Distinction from cheating (no deception at inception)"
        ]
    },
    {
        "id": "PREC_VIJAYASARATHY_BREACH_TRUST",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_406_BNS_316",
        "title": "Prof. R.K. Vijayasarathy v. Sudha Seetharam (2019) 16 SCC 739",
        "charge": "Criminal Breach of Trust",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Supreme Court held that to make out Section 406, entrustment must be proven with dishonest conversion. A mere failure to return money arising out of an ordinary civil or commercial contract does not attract criminal breach of trust without criminal mens rea.",
        "essential_elements": [
            "Lawful initial entrustment followed by dishonest conversion",
            "Distinction from ordinary commercial breach",
            "3-year statutory ceiling"
        ]
    },

    # =========================================================================
    # 4. CHEATING, FRAUD & FORGERY (IPC 420, 467, 468, 471)
    # =========================================================================
    {
        "id": "ART_IPC_420_BNS_318",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_420_BNS_318",
        "title": "Cheating and Dishonestly Inducing Delivery (IPC Section 420 / BNS Section 318(4))",
        "charge": "Cheating & Financial Fraud",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Section 420 IPC / Section 318(4) BNS: Cheating and dishonestly inducing delivery of property. Imprisonment for a term which may extend to seven years, and liable to fine. Crucial ingredient: fraudulent or dishonest intention must exist at the very inception of the transaction.",
        "essential_elements": [
            "Deception of any person",
            "Fraudulently or dishonestly inducing delivery of property or valuable security",
            "Dishonest intention at the very inception of transaction",
            "Capped at 7 years imprisonment (Tier 2)"
        ]
    },
    {
        "id": "PREC_BHAJAN_LAL_QUASHING",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_420_BNS_318",
        "title": "State of Haryana v. Bhajan Lal (1992) Supp (1) SCC 335",
        "charge": "Cheating & Financial Fraud",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Supreme Court landmark ratio on quashing criminal proceedings under Section 482 CrPC. Where civil dispute is given a criminal cloak, or uncontroverted allegations do not disclose the commission of any offence, the FIR is liable to be quashed.",
        "essential_elements": [
            "Commercial dispute given criminal cloak is liable to quashing",
            "Allegations must disclose criminal offence on face value",
            "Protection against malicious prosecution"
        ]
    },
    {
        "id": "PREC_HRIDAYA_RANJAN_CHEATING",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_420_BNS_318",
        "title": "Hridaya Ranjan Prasad Verma v. State of Bihar (2000) 4 SCC 168",
        "charge": "Cheating & Financial Fraud",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Supreme Court established the definitive distinction between mere breach of contract and cheating u/s 420. Fraudulent intention must be proven to exist at the very inception; subsequent inability to perform is purely civil.",
        "essential_elements": [
            "Deceptive intention existing at inception",
            "Subsequent breach does not constitute Section 420",
            "Tier 2 threshold"
        ]
    },
    {
        "id": "PREC_SATENDER_ANTIL_BAIL",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_420_BNS_318",
        "title": "Satender Kumar Antil v. CBI (2022) 10 SCC 51",
        "charge": "Cheating & Financial Fraud",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Guidelines on arrest and bail for offences punishable with up to 7 years imprisonment (Category A offenses under Section 420 IPC, 468 IPC). Compliance with Section 41A CrPC notice is mandatory before arrest.",
        "essential_elements": [
            "Category A offenses punishable with imprisonment up to 7 years",
            "Mandatory compliance with Sec 41A notice",
            "Bail standard for non-heinous socio-economic offences"
        ]
    },
    {
        "id": "ART_IPC_467_BNS_338",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_467_BNS_338",
        "title": "Forgery of Valuable Security or Will (IPC Section 467 / BNS Section 338)",
        "charge": "Forgery & Counterfeiting",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Section 467 IPC / Section 338 BNS: Forgery of valuable security, will, or authority to receive valuable property. Punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and fine.",
        "essential_elements": [
            "Making of a false document (Section 464)",
            "Document purports to be a valuable security, will, or authority to transfer funds",
            "Intent to cause damage, fraud, or wrongful gain",
            "Heinous document forgery carrying up to 10 years / life"
        ]
    },
    {
        "id": "PREC_SHEILA_SEBASTIAN_FORGERY",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_467_BNS_338",
        "title": "Sheila Sebastian v. R. Jawaharaj (2018) 7 SCC 581",
        "charge": "Forgery & Counterfeiting",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Supreme Court held that to attract Section 467, the accused must himself have made or forged the false document. In the absence of evidence that the accused himself made or signed the document, Section 467 cannot be sustained.",
        "essential_elements": [
            "Accused must be author/maker of forged valuable security",
            "Strict requirement of Section 464 false document",
            "Tier 3 sentencing severity up to 10 years"
        ]
    },
    {
        "id": "ART_IPC_468_BNS_336",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_468_BNS_336",
        "title": "Forgery for Purpose of Cheating (IPC Section 468 / BNS Section 336(3))",
        "charge": "Forgery & Counterfeiting",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Section 468 IPC / Section 336(3) BNS: Whoever commits forgery, intending that the document or electronic record forged shall be used for the purpose of cheating. Punished with imprisonment of either description for a term which may extend to seven years, and fine.",
        "essential_elements": [
            "Commission of forgery (making false document)",
            "Specific intent that forged document be used for cheating",
            "Punishment capped at seven years (Tier 2)"
        ]
    },
    {
        "id": "ART_IPC_471_BNS_340",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_471_BNS_340",
        "title": "Using as Genuine a Forged Document (IPC Section 471 / BNS Section 340(2))",
        "charge": "Forgery & Counterfeiting",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Section 471 IPC / Section 340(2) BNS: Whoever fraudulently or dishonestly uses as genuine any document or electronic record which he knows or has reason to believe to be a forged document, shall be punished in the same manner as if he had forged such document.",
        "essential_elements": [
            "Fraudulent or dishonest use as genuine",
            "Knowledge or reason to believe document is forged",
            "Use in legal or financial transactions",
            "Punishment equivalent to ordinary forgery"
        ]
    },
    {
        "id": "PREC_AS_KRISHNAN_FORGED_DOC",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_471_BNS_340",
        "title": "A.S. Krishnan v. State of Kerala (2004) 11 SCC 576",
        "charge": "Forgery & Counterfeiting",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Supreme Court held that knowledge or reasonable belief that the document is forged, coupled with fraudulent presentation, constitutes the complete offence under Section 471, irrespective of who fabricated the document.",
        "essential_elements": [
            "Dishonest use with knowledge of forgery",
            "Presentation as genuine to induce reliance"
        ]
    },

    # =========================================================================
    # 5. MATRIMONIAL CRUELTY, DOWRY & SEXUAL OFFENCES (IPC 498A, 304B, 376)
    # =========================================================================
    {
        "id": "ART_IPC_498A_BNS_85",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_498A_BNS_85",
        "title": "Cruelty by Husband or Relatives (IPC Section 498A / BNS Section 85/86)",
        "charge": "Matrimonial Cruelty & Harassment",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Section 498A IPC / Section 85/86 BNS: Husband or relative of husband subjecting woman to cruelty. Imprisonment for a term which may extend to three years and fine. Cruelty means wilful conduct likely to drive woman to suicide or harass her to meet unlawful demands for dowry.",
        "essential_elements": [
            "Woman subjected to cruelty by husband or in-laws",
            "Wilful conduct causing grave injury or driving to suicide",
            "Harassment with view to coercing unlawful property/dowry demands",
            "Capped at three years imprisonment (Tier 1)"
        ]
    },
    {
        "id": "PREC_ARNESH_KUMAR_NOTICE",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_498A_BNS_85",
        "title": "Arnesh Kumar v. State of Bihar (2014) 8 SCC 273",
        "charge": "Matrimonial Cruelty & Harassment",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Supreme Court landmark directions curbing automatic arrest in 498A cases and offenses punishable with imprisonment up to 7 years. Police officers must serve Notice of Appearance under Section 41A CrPC before arrest.",
        "essential_elements": [
            "Protection against mechanical arrest in matrimonial disputes",
            "Mandatory compliance with Section 41A CrPC",
            "Tier 1 sentencing ceiling (3 years)"
        ]
    },
    {
        "id": "PREC_KAHKASHAN_KAUSAR_CRUELTY",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_498A_BNS_85",
        "title": "Kahkashan Kausar @ Sonam v. State of Bihar (2022) 6 SCC 599",
        "charge": "Matrimonial Cruelty & Harassment",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Supreme Court held that general and omnibus allegations against husband's relatives without specific attributed overt acts or physical cruelty are liable to be quashed to prevent abuse of process of law.",
        "essential_elements": [
            "Specific overt acts required for 498A against relatives",
            "Omnibus allegations without dowry demand quashed",
            "Sentencing capped at Tier 1"
        ]
    },
    {
        "id": "ART_IPC_304B_BNS_80",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_304B_BNS_80",
        "title": "Dowry Death (IPC Section 304B / BNS Section 80)",
        "charge": "Dowry Death",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Section 304B IPC / Section 80 BNS: Where death of a woman is caused by burns, bodily injury, or occurs otherwise than under normal circumstances within seven years of marriage, and it is shown that soon before death she was subjected to cruelty or harassment by husband or relatives for dowry. Imprisonment for a term which shall not be less than seven years but which may extend to imprisonment for life.",
        "essential_elements": [
            "Death within 7 years of marriage",
            "Death occurring under abnormal circumstances or burns",
            "Cruelty or harassment in connection with dowry demands soon before death",
            "Mandatory minimum sentence of 7 years extending to life (Tier 3/4)"
        ]
    },
    {
        "id": "PREC_SATBIR_SINGH_DOWRY",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_304B_BNS_80",
        "title": "Satbir Singh v. State of Haryana (2021) 6 SCC 1",
        "charge": "Dowry Death",
        "penalty_tier": "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
        "content": "Supreme Court guidelines on Section 304B: 'Soon before death' requires a proximate and live nexus between cruelty for dowry and the unnatural death. Statutory presumption under Section 113B Evidence Act shifts burden to the accused once proximate cruelty is shown.",
        "essential_elements": [
            "Proximate live nexus between dowry harassment and unnatural death",
            "Statutory presumption of dowry death",
            "Minimum 7 years imprisonment (Tier 3)"
        ]
    },
    {
        "id": "ART_IPC_376_BNS_64",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_376_BNS_64",
        "title": "Rape & Sexual Assault (IPC Section 376 / BNS Section 64)",
        "charge": "Sexual Offences & Assault",
        "penalty_tier": "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)",
        "content": "Section 376 IPC / Section 64 BNS: Punishment for rape. Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than ten years, but which may extend to imprisonment for life, and shall also be liable to fine.",
        "essential_elements": [
            "Sexual penetration without consent or against will",
            "Consent obtained under fear of death, hurt, or misconception of fact",
            "Medical and prosecutrix testimony",
            "Mandatory minimum 10 years extending to life (Tier 4)"
        ]
    },
    {
        "id": "PREC_PRAMOD_PAWAR_CONSENT",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_376_BNS_64",
        "title": "Pramod Suryabhan Pawar v. State of Maharashtra (2019) 9 SCC 608",
        "charge": "Sexual Offences & Assault",
        "penalty_tier": "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)",
        "content": "Supreme Court distinction between false promise of marriage and breach of promise: Consensual physical relationship entered into freely does not amount to rape under Section 376 unless the promise of marriage was demonstrably false and made with fraudulent intent at the inception.",
        "essential_elements": [
            "Distinction between consensual relationship and rape",
            "Misconception of fact u/s 90 requires bad faith at inception",
            "Absence of consent elevates to Tier 4 severity"
        ]
    },

    # =========================================================================
    # 6. INTIMIDATION, CONSPIRACY & COMMON INTENTION (IPC 506, 120B, 34)
    # =========================================================================
    {
        "id": "ART_IPC_506_BNS_351",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_506_BNS_351",
        "title": "Criminal Intimidation (IPC Section 506 / BNS Section 351)",
        "charge": "Criminal Intimidation",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Section 506 IPC / Section 351 BNS: Punishment for criminal intimidation. Whoever commits criminal intimidation shall be punished with imprisonment for a term which may extend to two years, or with fine, or both (Part I). If threat be to cause death or grievous hurt, or destruction of property, imprisonment may extend to seven years (Part II, Tier 2).",
        "essential_elements": [
            "Threat of injury to person, reputation, or property",
            "Intent to cause alarm or compel victim to do an act against will",
            "Part I general threat capped at 2 years (Tier 1)",
            "Part II threat to kill capped at 7 years (Tier 2)"
        ]
    },
    {
        "id": "PREC_VIKRAM_JOHAR_INTIMIDATION",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_506_BNS_351",
        "title": "Vikram Johar v. State of U.P. (2019) 14 SCC 207",
        "charge": "Criminal Intimidation",
        "penalty_tier": "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
        "content": "Supreme Court held that mere casual abuses or verbal altercations without real threat or intent to cause alarm do not constitute Section 506 Criminal Intimidation.",
        "essential_elements": [
            "Mere abusive language is not criminal intimidation",
            "Actual intention to cause alarm is mandatory",
            "Sentence capped at Tier 1 / Tier 2"
        ]
    },
    {
        "id": "ART_IPC_120B_BNS_61",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_120B_BNS_61",
        "title": "Criminal Conspiracy (IPC Section 120B / BNS Section 61(2))",
        "charge": "Criminal Conspiracy",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Section 120B IPC / Section 61(2) BNS: Punishment of criminal conspiracy. Where two or more persons agree to commit an offence punishable with death, imprisonment for life or rigorous imprisonment for a term of two years or upwards, punished in same manner as if abetted such offence.",
        "essential_elements": [
            "Agreement between two or more persons",
            "Agreement to do an illegal act or act by illegal means",
            "Meeting of minds (mens rea)",
            "Sentence tracks the principal offense agreed upon"
        ]
    },
    {
        "id": "PREC_NAVJOT_SANDHU_CONSPIRACY",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_120B_BNS_61",
        "title": "State (NCT of Delhi) v. Navjot Sandhu (2005) 11 SCC 600",
        "charge": "Criminal Conspiracy",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Supreme Court held that meeting of minds is the essential nucleus of conspiracy. Can be inferred from surrounding circumstances and coordinated conduct, but mere association without criminal agreement is insufficient.",
        "essential_elements": [
            "Meeting of minds between conspirators",
            "Circumstantial inference of criminal agreement",
            "Distinct from mere casual acquaintance"
        ]
    },
    {
        "id": "ART_IPC_34_BNS_3",
        "type": "LAW_ARTICLE",
        "article_code": "IPC_34_BNS_3",
        "title": "Acts Done by Several Persons in Common Intention (IPC 34 / BNS 3(5))",
        "charge": "Criminal Conspiracy",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Section 34 IPC / Section 3(5) BNS: When a criminal act is done by several persons in furtherance of the common intention of all, each of such persons is liable for that act in the same manner as if it were done by him alone. Rule of joint vicarious liability.",
        "essential_elements": [
            "Criminal act done by multiple accused",
            "Pre-arranged plan or common intention prior to act",
            "Active physical or overt participation in furtherance of common intention",
            "Distinguished from similar intention"
        ]
    },
    {
        "id": "PREC_PANDURANG_COMMON_INTENT",
        "type": "PRIOR_CASE_PRECEDENT",
        "article_code": "IPC_34_BNS_3",
        "title": "Pandurang v. State of Hyderabad (1955) 1 SCR 1083",
        "charge": "Criminal Conspiracy",
        "penalty_tier": "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
        "content": "Constitution Bench ratio: Section 34 requires pre-arranged plan and meeting of minds in action. Common intention must be distinguished from similar or independent intention formed on the spot by co-accused.",
        "essential_elements": [
            "Prior concert and pre-arranged plan",
            "Participation in execution of plan",
            "Distinction between common vs similar intention"
        ]
    }
]
