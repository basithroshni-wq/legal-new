"""
22-Case Comprehensive Held-Out Benchmark & Adversarial Stress Suite for Effective LJP V6.
Includes:
- 16 diverse criminal fact scenarios spanning the full Indian penal taxonomy.
- 4 critical adversarial negation & edge cases (Fixing F-02, F-03, F-04, F-05, F-07).
- 2 out-of-domain rejection cases requiring explicit model abstention (Fixing F-09).
"""

from typing import List, Dict, Any


BENCHMARK_CASES: List[Dict[str, Any]] = [
    # --- 16 Core Canonical Criminal Scenarios ---
    {
        "id": "CASE_01",
        "name": "Thrissur Sneak Bus Theft",
        "category": "Core Theft",
        "narrative": "At a crowded bus terminal in Thrissur, the accused discreetly reached into a commuter's leather bag and took an iPhone worth Rs. 75,000 without the owner's knowledge or consent. No weapon or physical force was used during the taking. The accused was apprehended by commuters as he attempted to alight.",
        "expected_ipc": "Section 379",
        "expected_bns": "Section 303(2)",
        "expected_charge": "Theft & Property Offences",
        "expected_tier": "Tier 1 (Up to 3 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_02",
        "name": "Kakkanad Sudden Quarrel Homicide",
        "category": "Exception 4 Homicide",
        "narrative": "A sudden argument erupted between two laborers at a construction site in Kakkanad over pending daily wage distribution. In the heat of passion upon a sudden quarrel, the accused grabbed a wooden log lying nearby at the spot and struck a single blow on the victim's head. The victim suffered a skull fracture and succumbed to injuries the following day. There was no prior planning or enmity between the parties.",
        "expected_ipc": "Section 304 Part II",
        "expected_bns": "Section 105",
        "expected_charge": "Culpable Homicide (Sudden Fight)",
        "expected_tier": "Tier 3 (7 to 10 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_03",
        "name": "Real Estate Title Deed Forgery",
        "category": "Forgery & Cheating",
        "narrative": "The accused manufactured a fabricated power of attorney and forged title deed bearing forged signatures and seals of a deceased property owner. Using this counterfeit document as genuine, he dishonestly induced a buyer into depositing Rs. 45 lakhs into a dummy bank account as an advance for the sale of land.",
        "expected_ipc": "Section 468",
        "expected_bns": "Section 336(3)",
        "expected_charge": "Forgery & Counterfeiting",
        "expected_tier": "Tier 2 (3 to 7 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_04",
        "name": "Knifepoint Highway Extortion",
        "category": "Robbery",
        "narrative": "While a commuter was walking along an isolated stretch near the bypass road after sunset, the accused intercepted him, brandished a six-inch curved dagger at his chest, and demanded his wallet and gold chain under threat of immediate death. Out of fear of instant injury, the commuter surrendered his belongings.",
        "expected_ipc": "Section 392",
        "expected_bns": "Section 309(4)",
        "expected_charge": "Theft & Property Offences (Robbery)",
        "expected_tier": "Tier 3 (7 to 10 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_05",
        "name": "Matrimonial Dowry Harassment",
        "category": "Matrimonial Cruelty",
        "narrative": "The complainant was married to the accused for four years. Throughout the cohabitation, the husband and his parents continuously subjected her to mental torture and physical abuse, demanding an additional Rs. 10 lakhs in cash and an SUV as dowry, threatening to throw her out of the matrimonial home if demands were not met.",
        "expected_ipc": "Section 498A",
        "expected_bns": "Section 85",
        "expected_charge": "Matrimonial Cruelty & Harassment",
        "expected_tier": "Tier 1 (Up to 3 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_06",
        "name": "Commercial Invoice & Reconciliation Dispute",
        "category": "Civil Dispute (Quashable)",
        "narrative": "A software consulting vendor filed an FIR against a client alleging fraud because three monthly consulting invoices totaling Rs. 18 lakhs remained unpaid following a disagreement over milestone deliveries. The parties have an existing written master service agreement containing a binding arbitration clause, with ongoing reconciliation meetings.",
        "expected_ipc": "Quashed u/s 482 CrPC",
        "expected_bns": "Section 528 BNSS",
        "expected_charge": "No Criminal Offence (Civil Dispute)",
        "expected_tier": "Quashed (No Penal Term)",
        "should_abstain": False
    },
    {
        "id": "CASE_07",
        "name": "Premeditated Ambush Axe Murder",
        "category": "Murder",
        "narrative": "Nursing a long-standing grudge over a disputed boundary wall, the accused purchased an iron axe two days prior and lay in wait behind a clump of trees along the victim's daily morning route. When the victim walked past, the accused ambushed him and delivered four deep, brutal axe blows to the victim's neck and head, killing him instantly on the spot.",
        "expected_ipc": "Section 302",
        "expected_bns": "Section 103(1)",
        "expected_charge": "Murder & Culpable Homicide",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)",
        "should_abstain": False
    },
    {
        "id": "CASE_08",
        "name": "Deep Abdominal Knife Stabbing",
        "category": "Grievous Hurt Dangerous Weapon",
        "narrative": "Following a dispute over parking space, the accused pulled a hunting knife from his pocket and stabbed the victim deeply in the abdomen, puncturing the spleen and causing severe internal bleeding requiring emergency life-saving surgery and 30 days of hospitalization. The victim survived after medical treatment.",
        "expected_ipc": "Section 326",
        "expected_bns": "Section 118(2)",
        "expected_charge": "Assault & Grievous Hurt",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)",
        "should_abstain": False
    },
    {
        "id": "CASE_09",
        "name": "Government Job Cash Scam",
        "category": "Cheating",
        "narrative": "The accused ran an unauthorized employment consultancy and dishonestly duped eight job seekers by issuing fake appointment letters for clerk posts in the state electricity board. The accused collected Rs. 35 lakhs in cash advances from the victims based on these fraudulent representations and subsequently absconded.",
        "expected_ipc": "Section 420",
        "expected_bns": "Section 318(4)",
        "expected_charge": "Cheating & Financial Fraud",
        "expected_tier": "Tier 2 (3 to 7 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_10",
        "name": "Fatal Group Assault (Joint Liability)",
        "category": "Homicide Joint Liability",
        "narrative": "Three accused persons armed with heavy wooden clubs surrounded the victim outside a tea stall. In furtherance of their shared intention to punish him for a past altercation, all three assailants struck repeated blows to his limbs and ribs, inflicting multiple fractures that resulted in shock and death. They fled together in an auto-rickshaw.",
        "expected_ipc": "Section 304 Part I",
        "expected_bns": "Section 105",
        "expected_charge": "Murder & Culpable Homicide",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)",
        "should_abstain": False
    },
    {
        "id": "CASE_11",
        "name": "Brandishing Firearm (No Hurt)",
        "category": "Criminal Intimidation",
        "narrative": "During a heated neighborhood argument over loud music, the accused produced a country-made pistol, pointed it at the complainant's face, and threatened: 'If you ever complain to the society again, I will shoot you dead.' The accused did not fire any shots and no physical injuries were caused to anyone.",
        "expected_ipc": "Section 506",
        "expected_bns": "Section 351",
        "expected_charge": "Criminal Intimidation",
        "expected_tier": "Tier 1 (Up to 3 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_12",
        "name": "Dowry Death within 3 Years of Marriage",
        "category": "Dowry Death",
        "narrative": "A 23-year-old woman was married to the accused two years prior. Soon before her death, she was repeatedly beaten and harassed by her husband for failing to bring a car from her parents. She was found dead in the matrimonial home with 80% burn injuries under unnatural circumstances.",
        "expected_ipc": "Section 304B",
        "expected_bns": "Section 80",
        "expected_charge": "Dowry Death & Heinous Matrimonial",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)",
        "should_abstain": False
    },
    {
        "id": "CASE_13",
        "name": "Superficial Forearm Slash with Blade",
        "category": "Simple Hurt Dangerous Weapon",
        "narrative": "During a minor quarrel at a marketplace, the accused took out a razor blade and inflicted a superficial horizontal cut on the complainant's forearm. The injury was examined by a medical officer who certified it as simple hurt without fracture or danger to life.",
        "expected_ipc": "Section 324",
        "expected_bns": "Section 118(1)",
        "expected_charge": "Assault & Grievous Hurt",
        "expected_tier": "Tier 1 (Up to 3 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_14",
        "name": "Warehouse Embezzlement",
        "category": "Breach of Trust",
        "narrative": "The accused was employed as the chief inventory custodian of an electronic goods warehouse and was entrusted with dominion over stock worth Rs. 50 lakhs. Without permission of the employer, the accused dishonestly misappropriated 40 high-end laptops and converted them to his personal use by selling them on grey markets.",
        "expected_ipc": "Section 406",
        "expected_bns": "Section 316(2)",
        "expected_charge": "Criminal Breach of Trust",
        "expected_tier": "Tier 1 (Up to 3 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_15",
        "name": "Shooting at Vital Organ (Victim Survived)",
        "category": "Attempt to Murder",
        "narrative": "With the intention of killing his business rival, the accused pulled out a revolver and fired two rounds point-blank at the victim's chest. One bullet penetrated the left thoracic cavity. The victim was rushed to intensive care and survived after emergency surgery.",
        "expected_ipc": "Section 307",
        "expected_bns": "Section 109",
        "expected_charge": "Attempt to Murder",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)",
        "should_abstain": False
    },
    {
        "id": "CASE_16",
        "name": "Armed Highway Dacoity",
        "category": "Dacoity",
        "narrative": "A gang of seven armed men intercepted a cash transit van on the state highway. Threatening the guards with shotguns and iron rods, the seven assailants conjointly looted Rs. 60 lakhs and escaped in two getaway vehicles.",
        "expected_ipc": "Section 395",
        "expected_bns": "Section 310(2)",
        "expected_charge": "Theft & Property Offences (Robbery)",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)",
        "should_abstain": False
    },

    # --- 4 Critical Adversarial Stress Cases (Prior Model Failure Traps) ---
    {
        "id": "CASE_17_ADV",
        "name": "Adversarial: 'The victim was unarmed'",
        "category": "Adversarial Negation",
        "narrative": "The victim was unarmed and walking peacefully home. Suddenly, the accused jumped from an alley, held a serrated knife at the victim's neck, and forcibly took his wallet containing Rs. 5,000.",
        "expected_ipc": "Section 392",
        "expected_bns": "Section 309(4)",
        "expected_charge": "Theft & Property Offences (Robbery)",
        "expected_tier": "Tier 3 (7 to 10 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_18_ADV",
        "name": "Adversarial: 'No prior enmity or planning'",
        "category": "Adversarial Negation",
        "narrative": "There was no prior enmity, no planning, and no long-standing animosity between the two neighbors. During a sudden altercation over a boundary pipe, the accused grabbed an iron rod lying at the spot and struck the victim once, causing death.",
        "expected_ipc": "Section 304 Part II",
        "expected_bns": "Section 105",
        "expected_charge": "Culpable Homicide (Sudden Fight)",
        "expected_tier": "Tier 3 (7 to 10 Years)",
        "should_abstain": False
    },
    {
        "id": "CASE_19_ADV",
        "name": "Adversarial: Murder with 'Falsely Implicated' Defense Plea",
        "category": "Adversarial Defense Plea",
        "narrative": "The accused ambushed the deceased and stabbed him repeatedly in the chest with a dagger in front of multiple eyewitnesses, causing instant death. In his section 313 statement, the accused claims he was falsely implicated due to village politics.",
        "expected_ipc": "Section 302",
        "expected_bns": "Section 103(1)",
        "expected_charge": "Murder & Culpable Homicide",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)",
        "should_abstain": False
    },
    {
        "id": "CASE_20_ADV",
        "name": "Adversarial: Cheating with 'Cash' & 'Money' Keywords",
        "category": "Adversarial Keyword Trap",
        "narrative": "The accused deceived thirty investors into handing over Rs. 85 lakhs in cash by promising 40% monthly returns on a cryptocurrency trading algorithm. He had no trading license and transferred the money directly to his personal offshore accounts.",
        "expected_ipc": "Section 420",
        "expected_bns": "Section 318(4)",
        "expected_charge": "Cheating & Financial Fraud",
        "expected_tier": "Tier 2 (3 to 7 Years)",
        "should_abstain": False
    },

    # --- 2 Out-of-Domain Abstention Cases ---
    {
        "id": "CASE_21_OOD",
        "name": "Out-of-Domain: Regional Monsoon Weather Forecast",
        "category": "Out-of-Domain Rejection",
        "narrative": "The meteorological center predicts heavy monsoon precipitation and thunderstorms across coastal districts over the next 48 hours. Maximum temperatures will hover around 31 degrees Celsius, with humidity levels exceeding 88 percent.",
        "expected_ipc": "Abstain",
        "expected_bns": "Abstain",
        "expected_charge": "None",
        "expected_tier": "None",
        "should_abstain": True
    },
    {
        "id": "CASE_22_OOD",
        "name": "Out-of-Domain: Corporate Quarterly Financial Disclosure",
        "category": "Out-of-Domain Rejection",
        "narrative": "Consolidated fiscal revenue increased 14 percent year-over-year, while EBITDA margins expanded by 220 basis points. The board of directors declared an interim dividend of Rs. 4 per equity share during the quarterly shareholders meeting.",
        "expected_ipc": "Abstain",
        "expected_bns": "Abstain",
        "expected_charge": "None",
        "expected_tier": "None",
        "should_abstain": True
    }
]
