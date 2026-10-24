import sys
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.pipeline import EffectiveLjpPipeline

CASES = [
    # --- CRIMINAL LAW ---
    {
        "id": "CASE_01",
        "category": "Criminal Law",
        "title": "Case 1 — Murder (IPC Section 302)",
        "expected": "Section 302",
        "narrative": """The accused, a 34-year-old farmer, was alleged to have killed his neighbour over a long-standing land boundary dispute. On the night of 14 March 2023, witnesses reported hearing a heated argument. The deceased was found dead the following morning with blunt force injuries to the skull. The accused was found in possession of a bloodied iron rod. Forensic evidence confirmed the victim's blood on the rod. The accused pleaded that he acted in self-defence, claiming the deceased attacked him first with a sickle. However, the post-mortem report showed no injuries on the accused's body consistent with an attack. Three eyewitnesses corroborated the prosecution's version."""
    },
    {
        "id": "CASE_02",
        "category": "Criminal Law",
        "title": "Case 2 — Culpable Homicide Not Amounting to Murder (IPC Section 304)",
        "expected": "Section 304",
        "narrative": """The accused, a 28-year-old truck driver, struck the deceased during a road rage altercation. He pushed the deceased, who fell and struck his head on a kerb stone, resulting in death. The accused had no prior criminal record. CCTV footage showed the deceased had initiated the physical altercation. Medical evidence indicated death was caused by a single fall injury. The accused immediately called for an ambulance."""
    },
    {
        "id": "CASE_03",
        "category": "Criminal Law",
        "title": "Case 3 — Attempt to Murder (IPC Section 307)",
        "expected": "Section 307",
        "narrative": """The accused fired a country-made pistol at the complainant during an election-related dispute in a rural village. The bullet grazed the complainant's arm. The accused was apprehended at the scene. Two witnesses identified him. The accused claimed the gun discharged accidentally. Forensic examination of the weapon showed it was in functional condition and had been recently fired. No history of prior enmity was conclusively established."""
    },
    {
        "id": "CASE_04",
        "category": "Criminal Law",
        "title": "Case 4 — Rape (IPC Section 376)",
        "expected": "Section 376",
        "narrative": """The complainant, a 22-year-old woman, alleged that the accused, her supervisor at a private firm, raped her in the office after hours on 5 July 2022. She reported the incident to the police 48 hours later. Medical examination confirmed injuries consistent with sexual assault. The accused claimed the act was consensual. Digital evidence (WhatsApp messages) showed the accused had previously made unwanted advances that were clearly rebuffed. No prior consensual relationship was established."""
    },
    {
        "id": "CASE_05",
        "category": "Criminal Law",
        "title": "Case 5 — Dowry Death (IPC Section 304B)",
        "expected": "Section 304B",
        "narrative": """The deceased, married for 11 months, died of severe burn injuries at her matrimonial home. The husband and in-laws claimed it was a kitchen accident. The deceased's parents produced letters she had written describing constant harassment for additional dowry. Neighbours testified to hearing frequent quarrels. The post-mortem showed burns inconsistent with an accidental kitchen fire (no singeing of eyebrows or eyelashes). The accused failed to provide any plausible explanation for the nature of injuries."""
    },
    {
        "id": "CASE_06",
        "category": "Criminal Law",
        "title": "Case 6 — Theft (IPC Section 379)",
        "expected": "Section 379",
        "narrative": """The accused, a 19-year-old, was caught on CCTV stealing a mobile phone from an unattended table at a café. He was apprehended within 30 minutes with the phone still in his possession. He had one prior minor theft conviction two years ago. The accused expressed remorse and offered to return the phone. The phone's value was ₹12,000."""
    },
    {
        "id": "CASE_07",
        "category": "Criminal Law",
        "title": "Case 7 — Robbery (IPC Section 392)",
        "expected": "Section 392",
        "narrative": """Three accused persons intercepted a motorcyclist at night, threatened him with knives, and snatched his gold chain and wallet containing ₹8,000. A bystander noted the registration number of their vehicle. All three were arrested the following day. The stolen items were recovered from their possession. The victim identified all three in a test identification parade."""
    },
    {
        "id": "CASE_08",
        "category": "Criminal Law",
        "title": "Case 8 — Cheating (IPC Section 420)",
        "expected": "Section 420",
        "narrative": """The accused, representing himself as a registered real estate developer, collected ₹45 lakh from 12 buyers for flats in a project that never existed. The accused used forged approval documents. No construction was initiated. Victims filed complaints after two years of delays. Bank statements traced deposits to the accused's account. He was arrested while attempting to flee to another state."""
    },
    {
        "id": "CASE_09",
        "category": "Criminal Law",
        "title": "Case 9 — NDPS Act — Possession of Narcotic Drugs",
        "expected": "NDPS Act",
        "narrative": """The accused was intercepted at a state highway checkpoint. A search of his vehicle revealed 3 kg of heroin concealed in a false compartment. The accused claimed ignorance, saying he was only transporting the vehicle for a friend. The seizure was conducted in the presence of independent witnesses. Forensic analysis confirmed the substance as diacetylmorphine (heroin). The accused had no prior criminal record."""
    },
    {
        "id": "CASE_10",
        "category": "Criminal Law",
        "title": "Case 10 — Domestic Violence / Abetment of Suicide (IPC Section 306)",
        "expected": "Section 306 / Section 498A",
        "narrative": """The deceased, a 26-year-old woman, died by suicide. She left a note naming her husband and mother-in-law, stating she could no longer endure daily mental and physical torture. Neighbours testified to frequent arguments. Medical records showed the deceased had been treated for depression and injuries on two prior occasions. The husband and mother-in-law denied all allegations. No direct act of abetment was proven beyond the note."""
    },

    # --- CIVIL LAW — PROPERTY & CONTRACT ---
    {
        "id": "CASE_11",
        "category": "Civil Law — Property & Contract",
        "title": "Case 11 — Specific Performance of Contract",
        "expected": "Civil Dispute / Specific Relief Act",
        "narrative": """The plaintiff entered into a registered sale agreement with the defendant for a residential plot for ₹22 lakh, paying ₹5 lakh as advance. The defendant later refused to execute the sale deed, claiming the price had risen. The agreement had a clear timeline and penalty clause. The plaintiff was ready and willing to pay the remaining amount. The defendant had no legal encumbrances on the property."""
    },
    {
        "id": "CASE_12",
        "category": "Civil Law — Property & Contract",
        "title": "Case 12 — Suit for Partition of Joint Family Property",
        "expected": "Civil Dispute / Partition",
        "narrative": """Three brothers jointly inherited an agricultural land of 12 acres from their father, who died intestate. The eldest brother has been in exclusive possession for 15 years, collecting rental income without sharing it. The younger brothers filed for partition and accounts. The eldest claimed the others had orally surrendered their shares. No documentary evidence of surrender was produced."""
    },
    {
        "id": "CASE_13",
        "category": "Civil Law — Property & Contract",
        "title": "Case 13 — Breach of Contract — Construction",
        "expected": "Civil Dispute / Commercial",
        "narrative": """A contractor was hired to construct a commercial building within 18 months for ₹80 lakh. Work stopped after 14 months when 60% of construction was complete. The contractor claimed the owner had withheld milestone payments; the owner claimed defective workmanship. An independent engineer's report confirmed 3 structural deficiencies but assessed them as correctable. The owner had withheld ₹12 lakh beyond the contractual withholding limit."""
    },
    {
        "id": "CASE_14",
        "category": "Civil Law — Property & Contract",
        "title": "Case 14 — Adverse Possession",
        "expected": "Civil Dispute / Adverse Possession",
        "narrative": """The plaintiff claims title over a 2,000 sq ft plot on the basis of 25 years of open, continuous, and uninterrupted possession. He has a pucca structure on it, pays property tax, and his neighbours corroborate his possession. The original title holder's legal heirs filed a suit for recovery of possession 3 years ago. The plaintiff cannot produce a title deed."""
    },
    {
        "id": "CASE_15",
        "category": "Civil Law — Property & Contract",
        "title": "Case 15 — Landlord-Tenant Eviction (Rent Act)",
        "expected": "Civil Dispute / Rent Control",
        "narrative": """A landlord seeks eviction of a tenant who has been in possession for 22 years under a rent-controlled tenancy. The tenant pays ₹800/month (the original rent from 2001). The landlord claims personal necessity — his son needs the premises for a business. The tenant argues the landlord already owns two other commercial properties. The rent control legislation requires genuine personal necessity."""
    },
    {
        "id": "CASE_16",
        "category": "Civil Law — Property & Contract",
        "title": "Case 16 — Mortgage Foreclosure",
        "expected": "Civil Dispute / Banking & SARFAESI",
        "narrative": """A borrower took a housing loan of ₹40 lakh from a bank. He defaulted after 3 years, with outstanding dues of ₹38 lakh. The bank initiated SARFAESI proceedings. The borrower challenged the action, claiming the bank had not followed proper notice procedures. Bank records show notices were sent by registered post. The borrower claims he never received them and was undergoing medical treatment."""
    },

    # --- FAMILY LAW ---
    {
        "id": "CASE_17",
        "category": "Family Law",
        "title": "Case 17 — Divorce — Cruelty (HMA Section 13)",
        "expected": "Family Law / HMA Section 13",
        "narrative": """The husband petitions for divorce on grounds of cruelty. He alleges his wife made false complaints to police twice, resulting in his arrest and subsequent acquittal. He further alleges she refused to cohabit for 3 years and publicly humiliated him at family gatherings. The wife denies cruelty, claiming the complaints were genuine. Both complaints resulted in acquittals for lack of evidence."""
    },
    {
        "id": "CASE_18",
        "category": "Family Law",
        "title": "Case 18 — Child Custody Dispute",
        "expected": "Family Law / Guardianship & Custody",
        "narrative": """The parents of a 7-year-old girl are divorcing. The mother, a homemaker, seeks custody. The father, an IT professional working 14-hour days, also seeks custody, offering better financial resources and private schooling. The child psychologist's report indicates the child is emotionally closer to the mother. The mother lives with her parents, providing a stable family environment."""
    },
    {
        "id": "CASE_19",
        "category": "Family Law",
        "title": "Case 19 — Maintenance (CrPC Section 125)",
        "expected": "CrPC Section 125 / Maintenance",
        "narrative": """A 45-year-old woman with no independent income was deserted by her husband of 18 years. The husband earns ₹1.2 lakh/month. He claims she left voluntarily and is capable of earning. The wife produces medical records showing she suffers from rheumatoid arthritis limiting her mobility. They have no children."""
    },
    {
        "id": "CASE_20",
        "category": "Family Law",
        "title": "Case 20 — Restitution of Conjugal Rights (HMA Section 9)",
        "expected": "Family Law / HMA Section 9",
        "narrative": """The wife left the matrimonial home 8 months ago following a dispute with her mother-in-law. She is living at her parents' house and has a stable job. The husband files for restitution of conjugal rights. The wife contends that her husband actively encouraged his mother's hostility. No divorce petition has been filed by either side."""
    },
    {
        "id": "CASE_21",
        "category": "Family Law",
        "title": "Case 21 — Muslim Personal Law — Triple Talaq / Maintenance",
        "expected": "Family Law / Triple Talaq Act 2019",
        "narrative": """A Muslim woman was given triple talaq via a WhatsApp message in 2021 (post the Muslim Women Protection of Rights on Marriage Act, 2019). The husband claims it was said in anger and was not intentional. The wife seeks maintenance during the iddat period and thereafter. Two witnesses confirmed the talaq message."""
    },

    # --- CONSUMER & LABOUR LAW ---
    {
        "id": "CASE_22",
        "category": "Consumer & Labour Law",
        "title": "Case 22 — Medical Negligence",
        "expected": "Consumer Protection Act / Medical Negligence",
        "narrative": """A patient underwent a routine appendectomy. A surgical sponge was inadvertently left in the abdominal cavity, discovered 6 months later during a follow-up CT scan. A second surgery was required for removal. The hospital denied negligence, claiming the patient had a pre-existing condition. The surgical count record was incomplete."""
    },
    {
        "id": "CASE_23",
        "category": "Consumer & Labour Law",
        "title": "Case 23 — Insurance Claim Repudiation",
        "expected": "Consumer Protection Act / Insurance Dispute",
        "narrative": """The complainant's car was damaged in a flood. He filed an insurance claim of ₹3.2 lakh. The insurer repudiated it, alleging the car was being used as a taxi (commercial use) contrary to the private vehicle policy. The complainant produced evidence that his car was never registered as a taxi. A neighbour had briefly borrowed the car once."""
    },
    {
        "id": "CASE_24",
        "category": "Consumer & Labour Law",
        "title": "Case 24 — Workman's Compensation — Industrial Accident",
        "expected": "Labour Law / Employees Compensation Act",
        "narrative": """A factory worker lost three fingers of his right hand in a machine accident. The factory owner claimed the worker had bypassed a safety guard in violation of standing orders. Co-workers testified that the safety guard was frequently non-functional and management was aware. The factory's maintenance log showed the guard had been reported faulty twice in the preceding month."""
    },
    {
        "id": "CASE_25",
        "category": "Consumer & Labour Law",
        "title": "Case 25 — Unfair Labour Practice — Wrongful Termination",
        "expected": "Industrial Disputes Act / Labour Law",
        "narrative": """A permanent employee of 12 years was terminated via a letter citing "restructuring." No domestic inquiry was conducted. The employer claimed the post was abolished. The employee proved that a contractual worker was immediately hired for the same duties. The employee had no disciplinary record."""
    },
    {
        "id": "CASE_26",
        "category": "Consumer & Labour Law",
        "title": "Case 26 — E-Commerce Defective Product",
        "expected": "Consumer Protection Act / Defective Goods",
        "narrative": """The complainant purchased a refrigerator online for ₹42,000. It stopped working after 3 months. The service centre visited twice but could not repair it. The company refused a replacement, offering only repeated repairs. The warranty card guaranteed repairs or replacement within 30 days for manufacturing defects. The defect was confirmed as a manufacturing defect by the service engineer's report."""
    },

    # --- CONSTITUTIONAL & PUBLIC LAW ---
    {
        "id": "CASE_27",
        "category": "Constitutional & Public Law",
        "title": "Case 27 — Writ of Habeas Corpus",
        "expected": "Constitutional Law / Article 32/226 Habeas Corpus",
        "narrative": """A political activist was detained under the National Security Act (NSA) without trial for 9 months. The detention order cited vague grounds of "disturbing public order." The detainee's lawyer challenged the detention as lacking specific material. The government filed a counter-affidavit but failed to disclose the specific acts leading to detention."""
    },
    {
        "id": "CASE_28",
        "category": "Constitutional & Public Law",
        "title": "Case 28 — Writ of Mandamus — Right to Information",
        "expected": "Constitutional Law / Mandamus / RTI Act",
        "narrative": """An RTI applicant sought copies of government contracts awarded to a private company. The Public Information Officer denied the request citing trade secrets. The applicant argued the contracts involved public funds and no specific commercial harm was demonstrated. The CIC had already ordered disclosure."""
    },
    {
        "id": "CASE_29",
        "category": "Constitutional & Public Law",
        "title": "Case 29 — Service Law — Promotion Dispute",
        "expected": "Service Jurisprudence / Article 226",
        "narrative": """A government officer was superseded for promotion despite having a better ACR record than the junior officer promoted. The Departmental Promotion Committee cited "overall profile." The officer had no adverse entries. The junior officer had a political connection which the petitioner alleged influenced the DPC decision. No documentary proof of political interference was produced."""
    },
    {
        "id": "CASE_30",
        "category": "Constitutional & Public Law",
        "title": "Case 30 — Environmental Law — Writ for Pollution Control",
        "expected": "Environmental Law / Article 226/32 PIL",
        "narrative": """Residents of an industrial area filed a PIL alleging that a chemical factory was discharging untreated effluent into a nearby river. The State Pollution Control Board had issued two show-cause notices but took no further action. Water samples showed toxic metal concentrations beyond permissible limits. The factory claimed it had installed an Effluent Treatment Plant (ETP)."""
    },

    # --- BANKING & FINANCIAL FRAUD ---
    {
        "id": "CASE_31",
        "category": "Banking & Financial Fraud",
        "title": "Case 31 — Cheque Dishonour (NI Act Section 138)",
        "expected": "Section 138 NI Act",
        "narrative": """The accused issued a post-dated cheque of ₹8 lakh to the complainant towards discharge of a loan. The cheque was dishonoured due to "insufficient funds." The complainant sent a statutory notice, which was duly received by the accused. No payment was made within 15 days. The accused claimed the loan was already repaid in cash and the cheque was issued as security only. No receipt for cash payment was produced."""
    },
    {
        "id": "CASE_32",
        "category": "Banking & Financial Fraud",
        "title": "Case 32 — Bank Fraud — Loan Fraud",
        "expected": "Section 420 IPC / Bank Fraud",
        "narrative": """A businessman obtained a term loan of ₹2 crore from a nationalised bank by submitting inflated stock statements and forged GST returns. The loan was declared NPA within 18 months. Forensic audit confirmed the collateral was overvalued by 60%. The accused transferred funds to shell companies immediately after disbursement. He was charged under IPC §420 and the Prevention of Money Laundering Act."""
    },

    # --- INTELLECTUAL PROPERTY ---
    {
        "id": "CASE_33",
        "category": "Intellectual Property",
        "title": "Case 33 — Copyright Infringement",
        "expected": "IPR / Copyright Act, 1957",
        "narrative": """A software company filed suit against a competitor claiming the competitor had copied the source code of its proprietary CRM software. The plaintiff produced an expert's report showing 68% structural similarity in code. The defendant claimed independent development and produced development logs. However, the logs had metadata anomalies suggesting backdating. The defendant's product was released just 4 months after the plaintiff's."""
    },
    {
        "id": "CASE_34",
        "category": "Intellectual Property",
        "title": "Case 34 — Trademark Dispute",
        "expected": "IPR / Trade Marks Act, 1999",
        "narrative": """The plaintiff, owner of a registered trademark "SUPRAFIT" for health supplements, sued the defendant for using the mark "SUPRFIT" on similar products. The defendant argued the marks were visually and phonetically distinct. Market surveys showed consumer confusion. The defendant's registration application was still pending."""
    },

    # --- MOTOR ACCIDENT CLAIMS ---
    {
        "id": "CASE_35",
        "category": "Motor Accident Claims",
        "title": "Case 35 — Motor Accident Claim — Death of Breadwinner",
        "expected": "Motor Vehicles Act / MACT Section 166",
        "narrative": """A 40-year-old daily wage labourer earning ₹600/day was killed by a speeding truck. He is survived by his wife and three minor children. The truck driver was negligent (driving under the influence; confirmed by blood alcohol test). The truck owner's insurance was valid. The claimants sought ₹50 lakh."""
    },
    {
        "id": "CASE_36",
        "category": "Motor Accident Claims",
        "title": "Case 36 — Motor Accident Claim — Contributory Negligence",
        "expected": "Motor Vehicles Act / MACT Contributory Negligence",
        "narrative": """A motorcyclist was injured when a car ran a red light. However, the motorcyclist was not wearing a helmet and was slightly over the speed limit. The car driver had a clean record. Both parties claim the other was at fault. CCTV footage confirms the car jumped the signal but the motorcyclist was also speeding."""
    },

    # --- ARBITRATION & COMMERCIAL DISPUTES ---
    {
        "id": "CASE_37",
        "category": "Arbitration & Commercial Disputes",
        "title": "Case 37 — Challenge to Arbitral Award",
        "expected": "Arbitration and Conciliation Act Section 34",
        "narrative": """An arbitral award directed the petitioner company to pay ₹1.8 crore to the respondent for breach of a supply contract. The petitioner challenges the award under §34, alleging the arbitrator failed to consider key documents submitted during proceedings and that the award is patently illegal. The arbitrator's reasoned award does reference the documents but in summary form. No fraud or bias is alleged."""
    },
    {
        "id": "CASE_38",
        "category": "Arbitration & Commercial Disputes",
        "title": "Case 38 — Commercial Dispute — Goods Not Delivered",
        "expected": "Commercial Dispute / Sale of Goods / Contract Act",
        "narrative": """The plaintiff paid ₹15 lakh in advance to the defendant for supply of industrial machinery within 60 days. No delivery was made. The defendant claims global supply chain disruptions (post-COVID reference) caused delays and that a force majeure clause applies. The contract's force majeure clause requires notification within 7 days of the event; notification was given only after 3 months."""
    },

    # --- JUVENILE & SPECIAL LEGISLATION ---
    {
        "id": "CASE_39",
        "category": "Juvenile & Special Legislation",
        "title": "Case 39 — POCSO Act — Child Sexual Abuse",
        "expected": "POCSO Act / Section 376 IPC",
        "narrative": """The accused, a 38-year-old school teacher, was charged with sexually assaulting a 10-year-old female student over a period of 6 months. The child's statement was recorded before a magistrate under §164 CrPC. Medical examination supported the allegation. The accused denied the charges and claimed the child was tutored by a rival teacher. The child's testimony was consistent across three rounds of questioning."""
    },
    {
        "id": "CASE_40",
        "category": "Juvenile & Special Legislation",
        "title": "Case 40 — Insolvency — Corporate Resolution (IBC 2016)",
        "expected": "Insolvency and Bankruptcy Code (IBC 2016)",
        "narrative": """A mid-sized manufacturing company with outstanding debt of ₹120 crore was admitted to the Corporate Insolvency Resolution Process (CIRP) under IBC. The Resolution Professional received two resolution plans. Plan A offered ₹55 crore recovery; Plan B offered ₹42 crore. The Committee of Creditors approved Plan A with 71% voting. A dissenting financial creditor challenged the plan, claiming it violated the waterfall mechanism and undervalued liquidation assets. The liquidation value was assessed at ₹48 crore."""
    }
]

def main():
    pipeline = EffectiveLjpPipeline()
    print("=" * 110)
    print("⚖️  EVALUATION OF 40 CASE NARRATIVES ACROSS LEGAL DOMAINS (EFFECTIVE LJP V6)")
    print("=" * 110)
    print(f"{'#':<3} | {'Domain':<24} | {'Case Title':<32} | {'Prediction / Status':<28} | {'JCI':<5}")
    print("-" * 110)

    for i, c in enumerate(CASES, 1):
        res = pipeline.run(c["narrative"])
        if res.is_abstained:
            pred_summary = f"ABSTAINED: {res.abstain_message[:24]}"
            jci_val = 100.0
        else:
            top_art = res.top_articles[0].display_name if res.top_articles else "No Article"
            charge = res.top_charges[0].charge_name if res.top_charges else "No Charge"
            pred_summary = f"{top_art} ({charge[:14]})"
            jci_val = res.judicial_audit.final_jci_score

        title_short = c["title"][:30]
        cat_short = c["category"][:22]
        print(f"{i:<3} | {cat_short:<24} | {title_short:<32} | {pred_summary:<28} | {jci_val:<5.1f}")

    print("=" * 110)

if __name__ == "__main__":
    main()
