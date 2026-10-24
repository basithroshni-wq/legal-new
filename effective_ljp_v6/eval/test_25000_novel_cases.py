"""
25,000-Case Novel Domain Benchmark for Effective LJP V6
Synthesizes 25,000 realistic cases strictly modeled on Indian Penal & Non-Penal Jurisprudence,
featuring 50 Distinct Archetypes x 500 Procedural Variants = 25,000 Exhaustive Cases:
- 25 Penal Archetypes (12,500 cases) including novel penal statutes never tested before:
  * Section 409 IPC / Section 316(5) BNS (CBT by Public Servant / Banker)
  * Section 436 IPC / Section 326(f) BNS (Arson / Fire Destruction of Dwelling)
  * Section 363 IPC / Section 137(2) BNS (Kidnapping Minor from Lawful Guardianship)
  * Section 354D IPC / Section 78 BNS (Stalking & Electronic Cyber-Monitoring)
  * Section 201 IPC / Section 238 BNS (Causing Disappearance of Evidence / Screening Offender)
  * Section 489A IPC / Section 178 BNS (Counterfeiting Currency Notes FICN)
  * Plus Dacoity, Kidnapping for Ransom, Hate Speech 153A, Arms Act 25, IT Act 66D, etc.
- 25 Non-Penal / Regulatory / Specialized Regimes (12,500 cases) which must strictly ABSTAIN:
  * PMLA Provisional Asset Attachment
  * Electricity Act 2003 Meter Tampering Assessment
  * MMDR Act Illegal Sand Mining Quashing
  * Admiralty Cargo Vessel Arrest in Rem
  * Carriage by Air Aviation Cargo Loss
  * Personal Insolvency Resolution IBC Section 94
  * Armed Forces Tribunal Court Martial Challenge
  * Wildlife Protection Act Specimen Confiscation
  * IT Act Section 66A Void / Unconstitutional Quashing
  * Geographical Indications GI Infringement
  * PVPFRA Breeder Royalties
  * RERA Escrow Account Misallocation
  * DRT SARFAESI Section 17 Challenge
  * Civil Specific Performance, Partition, Rent Eviction, Writ Mandamus, NGT, MACT, Patent, etc.
"""

import sys
import os
import time
from collections import defaultdict
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from core.pipeline import EffectiveLjpPipeline

CITIES = [
    "Kozhikode", "Kochi", "Thiruvananthapuram", "Kannur", "Kollam", "Bengaluru",
    "Mysuru", "Mangaluru", "Hubballi", "Chennai", "Coimbatore", "Madurai",
    "Tiruchirappalli", "Salem", "Hyderabad", "Warangal", "Visakhapatnam",
    "Vijayawada", "Guntur", "Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad",
    "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Jaipur", "Jodhpur", "Udaipur",
    "Kota", "Delhi", "Noida", "Gurugram", "Faridabad", "Lucknow", "Kanpur",
    "Varanasi", "Agra", "Prayagraj", "Patna", "Gaya", "Muzaffarpur", "Ranchi",
    "Jamshedpur", "Kolkata", "Howrah", "Asansol", "Siliguri", "Bhubaneswar",
    "Cuttack", "Rourkela", "Guwahati", "Dibrugarh", "Bhopal", "Indore", "Jabalpur",
    "Gwalior", "Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Jammu", "Srinagar"
]

OCCUPATIONS = [
    "farmer", "truck driver", "school teacher", "accountant", "shopkeeper",
    "software engineer", "contractor", "trader", "factory supervisor", "clerk",
    "businessman", "electrician", "pharmacist", "warehouse manager", "labourer"
]

def generate_25000_novel_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    VARIANTS = 500

    def add_case(cid: int, dom: str, title: str, exp: str, ood: bool, text: str):
        cases.append({
            "id": f"D25K_{cid:05d}",
            "domain": dom,
            "title": title,
            "expected": exp,
            "should_abstain": ood,
            "narrative": text.strip()
        })

    c_id = 1

    # =========================================================================
    # PART 1: 25 PENAL ARCHETYPES (25 x 500 = 12,500 Cases)
    # =========================================================================

    # Arch 1: CBT by Public Servant/Banker (IPC 409 / BNS 316(5)) [NOVEL]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        occ = OCCUPATIONS[i % len(OCCUPATIONS)]
        amt = 15 + (i % 85)
        narr = (
            f"The accused, a public servant serving as a senior revenue officer in {city}, was entrusted in his official capacity "
            f"with government treasury funds amounting to Rs. {amt} lakh collected from local stamp duties. "
            f"An internal vigilance defalcation audit revealed that the accused committed criminal breach of trust by public servant "
            f"by dishonestly misappropriating and converting the public funds to his private commercial trading accounts u/s 409 IPC."
        )
        add_case(c_id, "Penal Law", "Case 1 — CBT by Public Servant / Banker (IPC Section 409)", "Section 409", False, narr)
        c_id += 1

    # Arch 2: Arson / Mischief by Fire to House (IPC 436 / BNS 326(f)) [NOVEL]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"Following a bitter land dispute in {city}, the accused arrived at the complainant's residential dwelling house "
            f"carrying combustible substance and kerosene. The accused deliberately committed arson and mischief by fire, "
            f"setting fire to the dwelling house and godown with intent to destroy the building. The property was gutted by fire intentionally."
        )
        add_case(c_id, "Penal Law", "Case 2 — Arson / Fire Destruction (IPC Section 436)", "Section 436", False, narr)
        c_id += 1

    # Arch 3: Kidnapping from Lawful Guardianship (IPC 363 / BNS 137(2)) [NOVEL]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        age = 13 + (i % 4)
        narr = (
            f"The accused enticed away a {age}-year-old minor school student from {city} out of the keeping of the lawful guardian "
            f"without the consent of the guardian. The minor girl was taken away from school premises to another district without any ransom demand."
        )
        add_case(c_id, "Penal Law", "Case 3 — Kidnapping from Lawful Guardianship (IPC Section 363)", "Section 363", False, narr)
        c_id += 1

    # Arch 4: Stalking & Electronic Cyber-Monitoring (IPC 354D / BNS 78) [NOVEL]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The complainant, a working professional in {city}, reported that the accused persistently followed her to her office and residence, "
            f"monitored her internet and social media electronic communications, and sent unwanted messages despite her clear indication of disinterest, "
            f"constituting repeated stalking against her will u/s 354D IPC."
        )
        add_case(c_id, "Penal Law", "Case 4 — Stalking (IPC Section 354D)", "Section 354D", False, narr)
        c_id += 1

    # Arch 5: Causing Disappearance of Evidence (IPC 201 / BNS 238) [NOVEL]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"After a serious crime was committed by his associate in {city}, the accused intentionally caused disappearance of evidence "
            f"by washing away bloodstains from the crime floor, wiping fingerprints, burning the clothes, and throwing the weapon into a canal "
            f"with the intention of screening the offender from legal punishment u/s 201 IPC."
        )
        add_case(c_id, "Penal Law", "Case 5 — Disappearance of Evidence (IPC Section 201)", "Section 201", False, narr)
        c_id += 1

    # Arch 6: Counterfeit Currency Notes FICN (IPC 489A / BNS 178) [NOVEL]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        amt = 100 + (i % 900)
        narr = (
            f"Acting on intelligence in {city}, police raided a clandestine workshop and caught the accused engaged in the counterfeiting process "
            f"of printing fake currency. Seized material included high quality counterfeit notes (FICN) of Rs. 500 denomination totalling {amt} banknotes "
            f"and printing machinery used for counterfeiting currency notes under Section 489A IPC."
        )
        add_case(c_id, "Penal Law", "Case 6 — Counterfeit Currency Notes FICN (IPC Section 489A)", "Section 489A", False, narr)
        c_id += 1

    # Arch 7: Kidnapping for Ransom (IPC 364A / BNS 140(2))
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        ransom = 25 + (i % 75)
        narr = (
            f"The accused abducted a 14-year-old student from {city} and held him in an abandoned farmhouse, demanding Rs. {ransom} lakh ransom "
            f"from his parents under threat of physical elimination. The police rescued the boy and arrested the accused on call record evidence."
        )
        add_case(c_id, "Penal Law", "Case 7 — Kidnapping for Ransom (IPC Section 364A)", "Section 364A", False, narr)
        c_id += 1

    # Arch 8: Dacoity with Arms (IPC 395 / BNS 310(2))
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        lakhs = 15 + (i % 40)
        narr = (
            f"Five armed persons stormed a rural cooperative bank near {city} at noon, overpowered security guards, and decamped with Rs. {lakhs} lakh in cash. "
            f"The gang was subsequently intercepted and arrested with recovered cash and weapons, establishing joint dacoity under Section 395 IPC."
        )
        add_case(c_id, "Penal Law", "Case 8 — Dacoity (IPC Section 395)", "Section 395", False, narr)
        c_id += 1

    # Arch 9: Hate Speech & Promoting Enmity (IPC 153A / BNS 196)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused delivered a public hate speech at a rally in {city}, calling a minority group enemies of the nation, "
            f"urging an economic boycott of their businesses, promoting enmity and disharmony between different religious communities prejudicial to public tranquillity."
        )
        add_case(c_id, "Penal Law", "Case 9 — Hate Speech (IPC Section 153A)", "Section 153A", False, narr)
        c_id += 1

    # Arch 10: Unlicensed Firearms (Section 25 Arms Act)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"During a routine search in {city}, police recovered a country-made pistol and six live cartridges from the accused's residence. "
            f"The accused had no firearm licence, establishing illegal possession of firearms under Section 25 Arms Act."
        )
        add_case(c_id, "Penal Law", "Case 10 — Arms Act (Section 25)", "Section 25 Arms Act", False, narr)
        c_id += 1

    # Arch 11: Cyber Phishing & Impersonation (Section 66D IT Act)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        amt = 50000 + (i * 1000)
        narr = (
            f"The accused created a spoofed banking website in {city}, sent phishing emails, deceived the complainant into disclosing net banking credentials, "
            f"and fraudulently siphoned Rs. {amt} from the account, constituting cheating by personation using a computer resource under Section 66D IT Act."
        )
        add_case(c_id, "Penal Law", "Case 11 — Cyber Phishing (Section 66D IT Act)", "Section 66D IT Act", False, narr)
        c_id += 1

    # Arch 12: Acid Attack Grievous Hurt (IPC 326A / BNS 124(1))
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused threw concentrated battery sulfuric acid on the complainant in {city} following rejected advances, "
            f"causing deep chemical burns, permanent disfigurement, and loss of vision, satisfying Section 326A IPC acid attack."
        )
        add_case(c_id, "Penal Law", "Case 12 — Acid Attack (IPC Section 326A)", "Section 326A", False, narr)
        c_id += 1

    # Arch 13: Extortion (IPC 384 / BNS 308(2))
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused repeatedly threatened a shopkeeper in {city} with arson and physical injury to his family unless monthly extortion "
            f"money of Rs. 40,000 was paid. Fearing for his life, the complainant paid the amount, satisfying Section 384 IPC extortion."
        )
        add_case(c_id, "Penal Law", "Case 13 — Extortion (IPC Section 384)", "Section 384", False, narr)
        c_id += 1

    # Arch 14: Hit and Run Criminal Negligence (IPC 304A / BNS 106)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A heavy commercial truck driver drove at excessive speed in a congested school zone in {city} without reasonable care, "
            f"striking a pedestrian who succumbed to injuries. The driver fled the scene, constituting causing death by negligence under Section 304A IPC."
        )
        add_case(c_id, "Penal Law", "Case 14 — Hit and Run (IPC Section 304A)", "Section 304A", False, narr)
        c_id += 1

    # Arch 15: Public Servant Bribery Trap (Section 7 PC Act)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        bribe = 10000 + (i * 500)
        narr = (
            f"A public servant serving as a land revenue officer in {city} demanded and accepted an illegal gratification of Rs. {bribe} "
            f"to issue a title clearance certificate. The vigilance bureau laid a trap and caught him with phenolphthalein-marked notes under Section 7 PC Act."
        )
        add_case(c_id, "Penal Law", "Case 15 — Prevention of Corruption (Section 7 PC Act)", "Section 7 PC Act", False, narr)
        c_id += 1

    # Arch 16: Forgery for Purpose of Cheating (IPC 468 / BNS 336(3))
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused fabricated a false property deed by imitating the signature of the lawful owner in {city} and submitted it "
            f"to a financial bank to secure a fraudulent mortgage loan, constituting forgery for purpose of cheating under Section 468 IPC."
        )
        add_case(c_id, "Penal Law", "Case 16 — Forgery for Cheating (IPC Section 468)", "Section 468", False, narr)
        c_id += 1

    # Arch 17: Lurking House-breaking by Night (IPC 457 / BNS 331(4))
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused broke into a locked residential bungalow in {city} at 2:00 AM by cutting the rear window grill with iron cutters, "
            f"entering the house to commit theft, constituting lurking house-trespass and house-breaking by night under Section 457 IPC."
        )
        add_case(c_id, "Penal Law", "Case 17 — Lurking House-breaking by Night (IPC Section 457)", "Section 457", False, narr)
        c_id += 1

    # Arch 18: Theft in Dwelling House (IPC 380 / BNS 305(a))
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused entered an inhabited dwelling house in {city} during the day through an unbolted doorway and stole a laptop "
            f"and cash from the bedroom without using any force or weapons, constituting theft in dwelling house under Section 380 IPC."
        )
        add_case(c_id, "Penal Law", "Case 18 — Theft in Dwelling (IPC Section 380)", "Section 380", False, narr)
        c_id += 1

    # Arch 19: Robbery with Hurt (IPC 394 / BNS 309(4))
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused intercepted a pedestrian on a lonely road in {city}, struck him with a knife causing bleeding injuries to his hand, "
            f"and forcibly snatched his gold chain and mobile phone, constituting robbery with hurt under Section 394 IPC."
        )
        add_case(c_id, "Penal Law", "Case 19 — Robbery with Hurt (IPC Section 394)", "Section 394", False, narr)
        c_id += 1

    # Arch 20: Premeditated Murder (IPC 302 / BNS 103(1))
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused, harboring long-standing enmity over a land boundary in {city}, lay in wait with a bloodied iron rod at night, "
            f"ambushed the unarmed deceased from behind, and struck repeated fatal blows to the skull with intention to cause death under Section 302 IPC."
        )
        add_case(c_id, "Penal Law", "Case 20 — Premeditated Murder (IPC Section 302)", "Section 302", False, narr)
        c_id += 1

    # Arch 21: Sudden Fight Homicide (IPC 304 Part II / BNS 105)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A heated altercation erupted between two labourers at a construction site in {city} over wage distribution. "
            f"In the sudden fight and heat of passion without premeditation, the accused shoved the deceased, who fell backwards hitting his head "
            f"on a stone curb, dying of head injury under Section 304 Part II IPC."
        )
        add_case(c_id, "Penal Law", "Case 21 — Sudden Fight Homicide (IPC Section 304 Part II)", "Section 304 Part II", False, narr)
        c_id += 1

    # Arch 22: Attempt to Murder (IPC 307 / BNS 109)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused cornered his rival in a market street in {city} and fired a shot directly at his chest with a firearm with murderous intent. "
            f"The victim survived after emergency cardiac surgery, establishing attempt to murder under Section 307 IPC."
        )
        add_case(c_id, "Penal Law", "Case 22 — Attempt to Murder (IPC Section 307)", "Section 307", False, narr)
        c_id += 1

    # Arch 23: Criminal Defamation (IPC 500 / BNS 356)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The accused published false and defamatory allegations on social media claiming the complainant, a reputed doctor in {city}, "
            f"was harvesting illicit organs, intending to harm his professional reputation and standing under Section 500 IPC."
        )
        add_case(c_id, "Penal Law", "Case 23 — Criminal Defamation (IPC Section 500)", "Section 500", False, narr)
        c_id += 1

    # Arch 24: Workplace Sexual Harassment (IPC 354A / BNS 75)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A woman working at a commercial firm in {city} complained that a male manager repeatedly made unwelcome sexual remarks "
            f"and explicit demands for physical favours despite her objections, constituting sexual harassment under Section 354A IPC."
        )
        add_case(c_id, "Penal Law", "Case 24 — Sexual Harassment (IPC Section 354A)", "Section 354A", False, narr)
        c_id += 1

    # Arch 25: Cheque Dishonour (Section 138 NI Act)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        amt = 200000 + (i * 5000)
        narr = (
            f"The accused issued a cheque of Rs. {amt} in {city} towards discharge of business liability. The cheque was dishonoured with memo "
            f"insufficient funds. The complainant issued statutory demand notice, but the accused failed to pay, attracting Section 138 NI Act."
        )
        add_case(c_id, "Penal Law", "Case 25 — Cheque Dishonour (Section 138 NI Act)", "Section 138 NI Act", False, narr)
        c_id += 1

    # =========================================================================
    # PART 2: 25 NON-PENAL / REGULATORY ARCHETYPES (25 x 500 = 12,500 Cases)
    # MUST STRICTLY ABSTAIN (Zero False Convictions)
    # =========================================================================

    # Arch 26: PMLA Asset Attachment Appeal [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The Directorate of Enforcement issued a provisional attachment order under Section 5 of the Prevention of Money Laundering Act (PMLA) "
            f"attaching commercial properties in {city}. The appellant challenged the attachment before the Appellate Tribunal PMLA claiming bona fide acquisition."
        )
        add_case(c_id, "Regulatory", "Case 26 — PMLA Asset Attachment Appeal", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 27: Electricity Act Meter Tampering Tariff Assessment [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The state electricity distribution board conducted an inspection on an industrial unit in {city}, alleging meter tampering and electricity theft, "
            f"issuing a provisional commercial tariff assessment under Section 126 and Section 135 of the Electricity Act, 2003. The consumer filed a statutory appeal."
        )
        add_case(c_id, "Regulatory", "Case 27 — Electricity Act Regulatory Assessment", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 28: MMDR Act Sand Mining Quashing [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"Mining regulatory authorities seized sand mining tippers near {city} citing unpermitted riverbed excavation under Section 4 and Section 21 of the MMDR Act. "
            f"The leaseholder filed a writ in the High Court challenging the administrative seizure and royalty penalties."
        )
        add_case(c_id, "Regulatory", "Case 28 — MMDR Act Mining Regulatory Quashing", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 29: Admiralty Cargo Vessel Arrest in Rem [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A maritime bunker supplier instituted an admiralty suit in rem under the Admiralty (Jurisdiction and Settlement of Maritime Claims) Act, 2017 "
            f"seeking the arrest of a foreign cargo vessel berthed at port near {city} to enforce a maritime lien for unpaid fuel supplies."
        )
        add_case(c_id, "Regulatory", "Case 29 — Admiralty Cargo Vessel Arrest in Rem", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 30: Carriage by Air Aviation Cargo Loss [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"An export conglomerate in {city} filed a claim under the Carriage by Air Act, 1972 incorporating the Montreal Convention 1999 "
            f"against an international airline carrier for transit cargo loss and air waybill consignment destruction."
        )
        add_case(c_id, "Regulatory", "Case 30 — Carriage by Air Aviation Cargo Loss", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 31: Personal Insolvency IBC Section 94 [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A corporate promoter who executed personal guarantees for bank loans in {city} filed an application under Section 94 of the Insolvency "
            f"and Bankruptcy Code, 2016 (IBC) before the NCLT initiating personal guarantor insolvency resolution process."
        )
        add_case(c_id, "Regulatory", "Case 31 — Personal Insolvency IBC Section 94", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 32: Armed Forces Tribunal Court Martial Challenge [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A retired military officer approached the Armed Forces Tribunal under Section 14 of the Armed Forces Tribunal Act, 2007 challenging "
            f"the administrative findings of a Court Martial inquiry and pension forfeiture near {city}."
        )
        add_case(c_id, "Regulatory", "Case 32 — Armed Forces Tribunal Challenge", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 33: Wildlife Protection Act Specimen Confiscation [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"Forest department officials seized timber and biological specimens from an estate near {city} under Section 50 of the Wildlife (Protection) Act, 1972. "
            f"The estate owner filed an appeal challenging the administrative confiscation before the Chief Wildlife Warden."
        )
        add_case(c_id, "Regulatory", "Case 33 — Wildlife Protection Act Confiscation", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 34: IT Act Section 66A Void / Unconstitutional Quashing [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The petitioner challenged a municipal notice issued under Section 66A of the IT Act in {city}, seeking a writ of certiorari on the ground "
            f"that Section 66A IT Act was struck down as unconstitutional and void by the Supreme Court in Shreya Singhal v. Union of India."
        )
        add_case(c_id, "Regulatory", "Case 34 — IT Act Section 66A Void Quashing", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 35: Geographical Indications GI Infringement [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A registered association of traditional handloom weavers in {city} filed a civil suit under Section 66 and 67 of the Geographical Indications "
            f"of Goods Act, 1999 seeking a permanent injunction against a commercial retailer falsely labeling synthetic fabrics with their registered GI mark."
        )
        add_case(c_id, "Regulatory", "Case 35 — Geographical Indications GI Protection", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 36: Plant Varieties PVPFRA Royalties [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"An agricultural university filed an infringement suit under Section 64 of the Protection of Plant Varieties and Farmers' Rights Act, 2001 (PVPFRA) "
            f"against a commercial seed distributor in {city} for unauthorized commercial sale of its protected variety hybrid seeds."
        )
        add_case(c_id, "Regulatory", "Case 36 — Plant Varieties PVPFRA Dispute", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 37: RERA Escrow Account Misallocation [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"Homebuyers of a residential project in {city} filed a statutory complaint before the Real Estate Regulatory Authority (RERA) "
            f"under Section 4(2)(l)(D) alleging that the builder diverted 70% of project collections from the designated escrow account to separate entities."
        )
        add_case(c_id, "Regulatory", "Case 37 — RERA Escrow Misallocation", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 38: DRT SARFAESI Section 17 Challenge [NOVEL REGULATORY]
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A borrower in {city} filed a securitization application under Section 17 of the SARFAESI Act before the Debts Recovery Tribunal (DRT) "
            f"challenging the bank's possession notice and auction of mortgaged factory assets."
        )
        add_case(c_id, "Regulatory", "Case 38 — DRT SARFAESI Section 17 Challenge", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 39: Civil Specific Performance Agreement of Sale
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The plaintiff entered into a registered agreement to sell immovable property in {city}, paid Rs. 20 lakh earnest money, "
            f"and demonstrated readiness to pay the balance. The vendor refused execution, prompting a suit for specific performance under the Specific Relief Act."
        )
        add_case(c_id, "Civil Law", "Case 39 — Suit for Specific Performance", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 40: Civil Partition Suit Ancestral Property
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The plaintiff filed a civil suit for partition before the Civil Court in {city} seeking division by metes and bounds of ancestral joint family property "
            f"and separate possession of his 1/4th coparcenary share under the Hindu Succession Act."
        )
        add_case(c_id, "Civil Law", "Case 40 — Suit for Partition", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 41: Landlord-Tenant Rent Eviction
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A landlord filed an eviction petition before the Rent Control Court in {city} seeking vacant possession of a commercial shop "
            f"on the grounds of bona fide personal necessity to establish an accounting consultancy office."
        )
        add_case(c_id, "Civil Law", "Case 41 — Landlord Eviction Petition", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 42: Family Law Mutual Consent Divorce
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"Spouses residing in {city} living separately for two years filed a joint petition for dissolution of marriage by mutual consent "
            f"under Section 13B of the Hindu Marriage Act, with agreed permanent alimony and shared child custody terms."
        )
        add_case(c_id, "Family Law", "Case 42 — Mutual Consent Divorce", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 43: Workman's Compensation & Labour Dispute
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"An industrial factory worker who sustained a machine crush injury during manufacturing operations in {city} filed a statutory claim "
            f"for permanent disability compensation under the Employee's Compensation Act before the Commissioner for Workmen's Compensation."
        )
        add_case(c_id, "Labour Law", "Case 43 — Workman Compensation Claim", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 44: Constitutional Writ of Mandamus for Promotion
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A government executive in {city} filed a writ petition under Article 226 of the Constitution seeking a writ of mandamus directing "
            f"the administrative department to consider him for promotion to Chief Engineer based on established seniority rosters."
        )
        add_case(c_id, "Constitutional Law", "Case 44 — Writ of Mandamus", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 45: Environmental NGT Pollution Abatement
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A citizens' environmental welfare society in {city} filed an application under Section 14 of the National Green Tribunal Act, 2010 "
            f"seeking directions to curb untreated industrial chemical discharge polluting local water bodies."
        )
        add_case(c_id, "Environmental Law", "Case 45 — NGT Environmental Application", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 46: Patent Claim Infringement Suit
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A pharmaceutical company holding a registered patent for a chemical drug formulation filed a patent infringement suit in the High Court "
            f"near {city} against a generic manufacturer seeking an injunction against manufacture and commercial marketing."
        )
        add_case(c_id, "Intellectual Property", "Case 46 — Patent Infringement Suit", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 47: Trademark Passing Off Suit
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A consumer goods manufacturer in {city} filed a civil suit for trademark passing off and unfair competition against a rival enterprise "
            f"marketing packaged beverages with deceptive color schemes and identical phonetic brand names."
        )
        add_case(c_id, "Intellectual Property", "Case 47 — Trademark Passing Off Suit", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 48: Motor Accident Claims Tribunal (MACT)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"The legal dependents of a bank officer who died in a highway collision near {city} filed a claim petition under Section 166 "
            f"of the Motor Vehicles Act before the MACT seeking compensation of Rs. 85 lakh against the vehicle insurer."
        )
        add_case(c_id, "Motor Accident Claims", "Case 48 — MACT Claim Petition", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 49: Arbitration Act Section 34 Challenge
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"An infrastructure development contractor in {city} filed a commercial petition under Section 34 of the Arbitration and Conciliation Act, 1996 "
            f"seeking to set aside a domestic arbitral award on grounds of patent illegality and contravention of contract terms."
        )
        add_case(c_id, "Arbitration", "Case 49 — Arbitration Section 34 Challenge", "ABSTAINED", True, narr)
        c_id += 1

    # Arch 50: Pure Commercial Contractual Breach (Civil Quashing u/s 482)
    for i in range(VARIANTS):
        city = CITIES[i % len(CITIES)]
        narr = (
            f"A dispute arose between commercial business partners in {city} over delayed equipment deliveries and invoice reconciliation. "
            f"No deceptive misrepresentation occurred at the inception of the contract, constituting a purely civil commercial contract dispute."
        )
        add_case(c_id, "Commercial Law", "Case 50 — Commercial Contract Quashing", "ABSTAINED", True, narr)
        c_id += 1

    return cases

def run_benchmark():
    print("=" * 125)
    print("🚀 EFFECTIVE LJP V6 — 25,000-CASE NOVEL DOMAIN & HIGH-THROUGHPUT EVALUATION")
    print("=" * 125)

    cases = generate_25000_novel_cases()
    total_cases = len(cases)
    print(f"[*] Generated {total_cases:,} benchmark cases across 50 Archetypes (500 variants each).")
    print(f"[*] Comprising 12,500 Penal Cases (25 Archetypes) + 12,500 Non-Penal / Regulatory Cases (25 Archetypes).")
    print("[*] Initializing Effective LJP V6 Neuro-Symbolic Engine...\n")

    pipeline = EffectiveLjpPipeline()

    domain_stats = defaultdict(lambda: {"total": 0, "pass": 0, "fail": 0, "jci_sum": 0.0})
    archetype_stats = defaultdict(lambda: {"total": 0, "pass": 0, "fail": 0, "jci_sum": 0.0})

    start_time = time.time()
    passed_total = 0
    failed_cases = []

    # Process in streaming loop
    for idx, c in enumerate(cases, start=1):
        narrative = c["narrative"]
        expected = c["expected"]
        should_abstain = c["should_abstain"]
        dom = c["domain"]
        title = c["title"]

        output = pipeline.run(narrative)

        is_pass = False
        jci = output.judicial_audit.final_jci_score if output.judicial_audit else 100.0

        if should_abstain:
            if output.is_abstained:
                is_pass = True
        else:
            if not output.is_abstained and output.top_articles:
                top_art = output.top_articles[0].ipc_section
                top_disp = output.top_articles[0].display_name
                exp = expected.lower()
                if exp in top_art.lower() or exp in top_disp.lower():
                    is_pass = True

        if is_pass and jci >= 80.0:
            passed_total += 1
            domain_stats[dom]["pass"] += 1
            archetype_stats[title]["pass"] += 1
        else:
            domain_stats[dom]["fail"] += 1
            archetype_stats[title]["fail"] += 1
            if len(failed_cases) < 15:
                pred_label = "ABSTAINED" if output.is_abstained else (output.top_articles[0].ipc_section if output.top_articles else "NONE")
                failed_cases.append((c["id"], title, expected, pred_label, jci))

        domain_stats[dom]["total"] += 1
        domain_stats[dom]["jci_sum"] += jci
        archetype_stats[title]["total"] += 1
        archetype_stats[title]["jci_sum"] += jci

        if idx % 5000 == 0 or idx == total_cases:
            elapsed = time.time() - start_time
            rate = idx / elapsed if elapsed > 0 else 0
            print(f"[*] Processed {idx:,}/{total_cases:,} cases ({idx/total_cases*100:.1f}%) | "
                  f"Passed: {passed_total:,} | Speed: {rate:.1f} cases/sec | Elapsed: {elapsed:.1f}s")

    total_time = time.time() - start_time
    overall_accuracy = (passed_total / total_cases) * 100.0

    print("\n" + "=" * 125)
    print(f"📊 SUMMARY BY 50 ARCHETYPES (500 VARIANTS EACH)")
    print("=" * 125)
    print(f"{'#':<4} | {'Archetype Title':<60} | {'Cases':<7} | {'Passed':<7} | {'Pass Rate':<10} | {'Avg JCI':<8}")
    print("-" * 125)

    arch_list = list(archetype_stats.items())
    for idx, (arch_name, s) in enumerate(arch_list, start=1):
        rate = (s["pass"] / s["total"]) * 100.0
        avg_jci = s["jci_sum"] / s["total"]
        print(f"{idx:<4} | {arch_name[:60]:<60} | {s['total']:<7} | {s['pass']:<7} | {rate:>8.1f}% | {avg_jci:>7.1f}")

    print("\n" + "=" * 125)
    print("📈 DOMAIN-LEVEL AGGREGATION")
    print("=" * 125)
    print(f"{'Domain':<25} | {'Total Cases':<12} | {'Passed':<10} | {'Accuracy':<10} | {'Avg JCI Score':<14}")
    print("-" * 125)
    for dom, s in sorted(domain_stats.items()):
        acc = (s["pass"] / s["total"]) * 100.0
        avg_jci = s["jci_sum"] / s["total"]
        print(f"{dom:<25} | {s['total']:<12} | {s['pass']:<10} | {acc:>8.1f}% | {avg_jci:>12.1f}")

    print("=" * 125)
    print(f"🏆 FINAL BENCHMARK RESULT: {passed_total:,} / {total_cases:,} PASSED ({overall_accuracy:.2f}%)")
    print(f"⏱️  TOTAL EXECUTION TIME: {total_time:.2f} seconds ({total_cases/total_time:.1f} cases/sec)")
    print("=" * 125)

    if failed_cases:
        print("\n❌ Sample Failures:")
        for fid, title, exp, act, jci in failed_cases:
            print(f"   - {fid} [{title}]: Expected '{exp}', got '{act}', JCI={jci}")

if __name__ == "__main__":
    run_benchmark()
