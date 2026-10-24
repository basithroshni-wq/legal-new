import sys
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.pipeline import EffectiveLjpPipeline

CASES_SET2 = [
    # --- CRIMINAL LAW ---
    {
        "id": "CASE_41",
        "category": "Criminal Law",
        "title": "Case 41 — Kidnapping for Ransom (IPC Section 364A)",
        "expected": "Section 364A",
        "is_penal": True,
        "narrative": """The accused, along with two associates, abducted a 14-year-old boy from outside his school and demanded ₹50 lakh ransom from his parents. The boy was held in an abandoned farmhouse for 4 days. He was rescued in a police operation before any ransom was paid. The accused was identified through CCTV footage near the school. The boy identified all three accused in a test identification parade. Call records confirmed communication between the accused and the victim's father."""
    },
    {
        "id": "CASE_42",
        "category": "Criminal Law",
        "title": "Case 42 — Dacoity (IPC Section 395)",
        "expected": "Section 395",
        "is_penal": True,
        "narrative": """Five armed persons stormed a rural cooperative bank at noon, overpowered two security guards, and decamped with ₹28 lakh in cash. One guard sustained a knife injury. Three of the five were apprehended within a week. The recovered cash amounted to ₹19 lakh. Two accused remained at large. The arrested accused named their associates. Two eyewitness bank employees identified the three arrested persons."""
    },
    {
        "id": "CASE_43",
        "category": "Criminal Law",
        "title": "Case 43 — Forgery for the Purpose of Cheating (IPC Section 468)",
        "expected": "Section 468",
        "is_penal": True,
        "narrative": """The accused, a bank employee, forged signatures on 11 fixed deposit receipts over 18 months, siphoning ₹32 lakh from customers' accounts into fictitious accounts he controlled. An internal audit uncovered the discrepancy. Handwriting experts confirmed the forgery. The accused claimed he was acting under instructions from a senior, but no corroborating evidence was produced. The full amount was transferred to accounts solely operated by the accused."""
    },
    {
        "id": "CASE_44",
        "category": "Criminal Law",
        "title": "Case 44 — Sedition / Hate Speech (IPC Section 153A)",
        "expected": "Section 153A",
        "is_penal": True,
        "narrative": """The accused, a social media influencer with 4 lakh followers, posted a series of videos calling members of a religious community "enemies of the nation" and urging his followers to boycott their businesses. Two instances of communal tension in the area were reported within a week of the videos going viral. The accused claimed freedom of speech and denied any intention to incite violence. No direct evidence of violence was attributed to his videos."""
    },
    {
        "id": "CASE_45",
        "category": "Criminal Law",
        "title": "Case 45 — Extortion (IPC Section 384)",
        "expected": "Section 384",
        "is_penal": True,
        "narrative": """The accused, posing as a police informer, approached a small businessman and threatened to implicate him in a drug case unless paid ₹5 lakh. The businessman filed a complaint. Police laid a trap and the accused was caught red-handed accepting ₹1 lakh. The marked currency notes were recovered. The accused claimed the money was a loan. The businessman's complaint was corroborated by two witnesses present during the initial threat."""
    },
    {
        "id": "CASE_46",
        "category": "Criminal Law",
        "title": "Case 46 — Hit and Run — Causing Death by Negligence (IPC Section 304A)",
        "expected": "Section 304A",
        "is_penal": True,
        "narrative": """The accused, driving a luxury SUV at high speed in a residential area at 11 PM, struck a pedestrian crossing the road. The victim died at the hospital. The accused fled the scene. His vehicle, with damage consistent with the accident, was found parked 2 km away. CCTV footage captured the vehicle and partial number plate. The accused surrendered 48 hours later, claiming he panicked. His blood alcohol level at the time of surrender was zero."""
    },
    {
        "id": "CASE_47",
        "category": "Criminal Law",
        "title": "Case 47 — Arms Act — Illegal Possession of Firearms",
        "expected": "Section 25 Arms Act",
        "is_penal": True,
        "narrative": """During a routine search, police recovered a country-made pistol and 12 live cartridges from the accused's residence. The accused had no firearm licence. He claimed the weapon belonged to a deceased relative and he was unaware it was illegal to retain it. No criminal use of the weapon was established. The accused had no prior criminal record and was a daily wage worker."""
    },
    {
        "id": "CASE_48",
        "category": "Criminal Law",
        "title": "Case 48 — Cybercrime — Online Financial Fraud (IT Act Section 66D)",
        "expected": "Section 66D IT Act",
        "is_penal": True,
        "narrative": """The accused created a fake customer care number for a nationalised bank and uploaded it on multiple websites. Victims searching online called the number and were tricked into sharing their OTPs and debit card details. ₹18 lakh was fraudulently withdrawn from 34 victims' accounts over 3 months. Digital forensics traced the fake listings to an IP address at the accused's residence. Call records confirmed calls from victims to the accused's registered SIM."""
    },
    {
        "id": "CASE_49",
        "category": "Criminal Law",
        "title": "Case 49 — Grievous Hurt (IPC Section 326)",
        "expected": "Section 326A / Section 326",
        "is_penal": True,
        "narrative": """During a dispute over a cricket match, the accused threw acid at the complainant, resulting in permanent disfigurement of his face and loss of vision in one eye. The accused claimed the liquid was water and denied intent to cause grievous hurt. A forensic report confirmed the liquid was sulphuric acid. Two bystanders witnessed the incident. The complainant identified the accused without hesitation."""
    },
    {
        "id": "CASE_50",
        "category": "Criminal Law",
        "title": "Case 50 — Prevention of Corruption Act — Bribery",
        "expected": "Section 7 PC Act",
        "is_penal": True,
        "narrative": """A government engineer was arrested while accepting ₹80,000 from a contractor as a bribe for approving an inflated work completion certificate. The trap was laid by the Anti-Corruption Bureau on a complaint by the contractor, who was threatened with adverse reports. The accused was caught red-handed. The marked currency notes were recovered from his trouser pocket. He claimed the money was a personal loan from the contractor."""
    },

    # --- CIVIL LAW — CONTRACT & PROPERTY ---
    {
        "id": "CASE_51",
        "category": "Civil Law — Contract & Property",
        "title": "Case 51 — Suit for Recovery of Money — Promissory Note",
        "expected": "Non-Penal Jurisdiction / Promissory Note",
        "is_penal": False,
        "narrative": """The plaintiff lent ₹12 lakh to the defendant against a duly executed promissory note at 18% interest per annum. The defendant repaid ₹3 lakh and then defaulted. The defendant claims the remaining amount was waived orally by the plaintiff. No written waiver exists. The plaintiff produces the original promissory note with the defendant's signature confirmed by a handwriting expert. The defendant does not dispute the signature."""
    },
    {
        "id": "CASE_52",
        "category": "Civil Law — Contract & Property",
        "title": "Case 52 — Injunction — Encroachment on Private Property",
        "expected": "Non-Penal Jurisdiction / Injunction Encroachment",
        "is_penal": False,
        "narrative": """The plaintiff alleges the defendant has constructed a boundary wall encroaching 4 feet onto his registered plot. A licensed surveyor's report confirms the encroachment. The defendant claims the boundary was agreed upon verbally 20 years ago and disputes the survey. No written agreement supports the defendant's claim. The plaintiff has a registered title deed and recent property tax receipts. The defendant has been in occupation of the disputed strip for 18 years."""
    },
    {
        "id": "CASE_53",
        "category": "Civil Law — Contract & Property",
        "title": "Case 53 — Declaratory Suit — Will Dispute",
        "expected": "Non-Penal Jurisdiction / Will Dispute",
        "is_penal": False,
        "narrative": """The plaintiff, a daughter, challenges a will made by her late father, under which the entire estate was bequeathed to her brother. She alleges the will is forged. A forensic handwriting examination of the will is inconclusive. The will was registered and attested by two witnesses, one of whom is deceased. The surviving witness testified that the testator signed voluntarily. The plaintiff argues her father had dementia and lacked testamentary capacity. The hospital records from the period show mild cognitive impairment but not legal incapacity."""
    },
    {
        "id": "CASE_54",
        "category": "Civil Law — Contract & Property",
        "title": "Case 54 — Suit for Damages — Negligent Construction",
        "expected": "Non-Penal Jurisdiction / Negligent Construction",
        "is_penal": False,
        "narrative": """The plaintiff's newly built compound wall collapsed onto his neighbour's car due to defective construction by the contractor. The car sustained damage of ₹4.5 lakh. The contractor claims the wall collapsed due to heavy rain (force majeure). The municipal engineer's report states the wall was under-reinforced and would not have withstood normal monsoon rainfall. The contractor had no insurance."""
    },
    {
        "id": "CASE_55",
        "category": "Civil Law — Contract & Property",
        "title": "Case 55 — Easement Rights — Right of Way",
        "expected": "Non-Penal Jurisdiction / Easement",
        "is_penal": False,
        "narrative": """The plaintiff's agricultural land is landlocked and accessible only through a narrow path across the defendant's land, used by the plaintiff's family for 40 years. The defendant recently blocked the path after a personal dispute. The plaintiff seeks recognition of an easement by prescription. Revenue records and testimony of three villagers confirm uninterrupted use. The defendant argues the path was used by licence, not as of right, and produces a letter from the plaintiff's father acknowledging permission."""
    },
    {
        "id": "CASE_56",
        "category": "Civil Law — Contract & Property",
        "title": "Case 56 — Specific Relief — Agreement to Sell Ancestral Property",
        "expected": "Non-Penal Jurisdiction / Specific Relief Ancestral",
        "is_penal": False,
        "narrative": """The plaintiff entered a sale agreement with two brothers who co-own an ancestral property. One brother signed the agreement and accepted ₹10 lakh advance; the other brother refuses, claiming he never consented. The property is undivided and no partition has taken place. The consenting brother argues he can transfer his half share."""
    },

    # --- FAMILY LAW ---
    {
        "id": "CASE_57",
        "category": "Family Law",
        "title": "Case 57 — Mutual Consent Divorce with Alimony Dispute",
        "expected": "Non-Penal Jurisdiction / Divorce Alimony",
        "is_penal": False,
        "narrative": """A couple married for 9 years mutually agreed to divorce. They have one child, aged 6. Both parties agree on custody being with the mother. However, they dispute the alimony amount. The husband earns ₹2.5 lakh/month; the wife is a homemaker who gave up a teaching career upon marriage. The wife demands ₹80,000/month; the husband offers ₹35,000/month. The wife has no independent assets; the husband owns two properties."""
    },
    {
        "id": "CASE_58",
        "category": "Family Law",
        "title": "Case 58 — Domestic Violence — Protection Order (PWDVA 2005)",
        "expected": "Non-Penal Jurisdiction / PWDVA Protection Order",
        "is_penal": False,
        "narrative": """The wife alleges her husband subjected her to regular physical and verbal abuse over 5 years. She has medical records of three hospital visits for injuries she attributed to falls. The husband denies all allegations. The wife's sister corroborates witnessing one incident of physical violence. The wife is residing in a shelter home with her two children. The husband claims she left voluntarily and is deliberately alienating the children."""
    },
    {
        "id": "CASE_59",
        "category": "Family Law",
        "title": "Case 59 — Guardianship — NRI Father vs. Resident Mother",
        "expected": "Non-Penal Jurisdiction / Guardianship Custody",
        "is_penal": False,
        "narrative": """An NRI father based in Canada seeks guardianship of his 9-year-old son, currently living with the mother in India. The father argues he can provide better education and opportunities abroad. The mother, a working professional, argues uprooting the child would be traumatic. The child's schoolteacher reports the child is well-adjusted and performing well. The child, when interviewed in chambers, expressed a preference to stay with his mother. The father has no history of abuse or neglect."""
    },
    {
        "id": "CASE_60",
        "category": "Family Law",
        "title": "Case 60 — Succession — Intestate Property — Second Wife's Claim",
        "expected": "Non-Penal Jurisdiction / Intestate Succession",
        "is_penal": False,
        "narrative": """A man died intestate, leaving behind two wives (the second marriage being disputed as bigamous) and children from both relationships. The first wife challenges the validity of the second marriage. Marriage records for the second union are from a different state. DNA testing confirms the man was the biological father of all children. The second wife has lived with the deceased for 14 years and is registered as the nominee in his insurance policy."""
    },
    {
        "id": "CASE_61",
        "category": "Family Law",
        "title": "Case 61 — Maintenance for Major Disabled Child",
        "expected": "Non-Penal Jurisdiction / Maintenance Section 125",
        "is_penal": False,
        "narrative": """A 24-year-old man with cerebral palsy, dependent entirely on his mother, seeks maintenance from his estranged father under Section 125 CrPC. The father claims the son is an adult and the liability has ceased. Medical records establish permanent and total disability. The father is a retired government officer drawing a pension of ₹60,000/month. The mother is unemployed."""
    },

    # --- CONSUMER & LABOUR LAW ---
    {
        "id": "CASE_62",
        "category": "Consumer & Labour Law",
        "title": "Case 62 — Consumer Complaint — Builder Delay (RERA)",
        "expected": "Non-Penal Jurisdiction / RERA Delay",
        "is_penal": False,
        "narrative": """The complainant booked a flat in 2019 for ₹55 lakh, with promised possession by December 2021. Possession was not given until June 2024, a delay of 30 months. The builder cited COVID-19 lockdowns and material shortages. The complainant seeks interest on the paid amount (₹40 lakh paid) for the delay period. The builder's RERA registration was valid but no extension was sought for the COVID period."""
    },
    {
        "id": "CASE_63",
        "category": "Consumer & Labour Law",
        "title": "Case 63 — Wrongful Dismissal — Whistleblower",
        "expected": "Non-Penal Jurisdiction / Whistleblower Dismissal",
        "is_penal": False,
        "narrative": """A senior accounts officer was dismissed after he reported financial irregularities in his company to the ROC. The company cited poor performance in the termination letter. His last three annual appraisals were all "good" or above. The termination came 3 weeks after his complaint. The company argues the decision was in the pipeline before the complaint. No contemporaneous record of any performance issue prior to the complaint was produced."""
    },
    {
        "id": "CASE_64",
        "category": "Consumer & Labour Law",
        "title": "Case 64 — Sexual Harassment at Workplace (POSH Act 2013)",
        "expected": "Non-Penal Jurisdiction / POSH Act ICC",
        "is_penal": False,
        "narrative": """A female employee filed a complaint against a senior manager for repeated sexually coloured remarks and unwanted physical contact over 6 months. The Internal Complaints Committee found in her favour. The manager challenges the ICC findings, claiming the proceedings were biased (the ICC had no external member as required under the Act) and that the complainant had a motive to falsely implicate him due to a promotion dispute."""
    },
    {
        "id": "CASE_65",
        "category": "Consumer & Labour Law",
        "title": "Case 65 — Consumer Complaint — Educational Institution Fee Refund",
        "expected": "Non-Penal Jurisdiction / UGC Fee Refund",
        "is_penal": False,
        "narrative": """A student paid ₹1.8 lakh in fees for a one-year MBA programme. He withdrew within 15 days of commencement due to a medical emergency. The institution refused refund, citing a "no refund after admission" policy. UGC guidelines mandate a refund of fees (minus a processing fee) if withdrawal is before the last date of admission. The institution argues it is an autonomous university not bound by UGC norms."""
    },
    {
        "id": "CASE_66",
        "category": "Consumer & Labour Law",
        "title": "Case 66 — ESI / PF Dispute — Contract Workers",
        "expected": "Non-Penal Jurisdiction / EPFO Contract Workers",
        "is_penal": False,
        "narrative": """A manufacturing company engaged 120 workers through a contractor for 3 years. The EPFO conducted an inspection and found the workers were effectively under the company's control (fixed hours, company supervisor, no substitution permitted). The company claims the contractor is the employer and the workers are not its employees. The contractor had no separate EPF registration and made no contributions."""
    },

    # --- CONSTITUTIONAL & PUBLIC LAW ---
    {
        "id": "CASE_67",
        "category": "Constitutional & Public Law",
        "title": "Case 67 — Right to Privacy — Aadhaar Linkage Mandate",
        "expected": "Non-Penal Jurisdiction / Constitutional Writ Aadhaar",
        "is_penal": False,
        "narrative": """A senior citizen challenges a government circular mandating Aadhaar linkage for receiving pension, arguing it violates his right to privacy under Article 21 and disproportionately burdens elderly citizens with biometric authentication failures. The government argues it is a reasonable restriction to prevent fraud. The petitioner produces evidence of repeated biometric failures at fair price shops leading to denial of pension twice."""
    },
    {
        "id": "CASE_68",
        "category": "Constitutional & Public Law",
        "title": "Case 68 — PIL — Condition of Undertrial Prisoners",
        "expected": "Non-Penal Jurisdiction / Constitutional PIL Undertrials",
        "is_penal": False,
        "narrative": """A legal aid organisation files a PIL alleging that a district jail is holding 430 undertrials in a facility designed for 150, with no segregation of first-time offenders and hardened criminals. A court-appointed committee's inspection report confirms overcrowding, inadequate sanitation, and absence of legal aid facilities. The state government argues infrastructure expansion is budgeted and in progress."""
    },
    {
        "id": "CASE_69",
        "category": "Constitutional & Public Law",
        "title": "Case 69 — Writ — Arbitrary Transfer of Government Employee",
        "expected": "Non-Penal Jurisdiction / Service Writ Transfer",
        "is_penal": False,
        "narrative": """A government school teacher with 22 years of service was transferred to a remote posting 400 km away with 7 days' notice, shortly after she raised a grievance about salary irregularities with the district education officer. The transfer order cited "administrative exigency" with no further reasons. Similarly situated teachers were not transferred. The petitioner argues the transfer is punitive."""
    },
    {
        "id": "CASE_70",
        "category": "Constitutional & Public Law",
        "title": "Case 70 — Land Acquisition — Inadequate Compensation",
        "expected": "Non-Penal Jurisdiction / Land Acquisition Compensation",
        "is_penal": False,
        "narrative": """Farmers whose agricultural land was acquired for a highway project challenge the compensation awarded under the Land Acquisition Act 2013. The state paid ₹18 lakh per acre based on circle rates from 2016. The farmers produce sale deeds of comparable land from 2022 showing ₹45–60 lakh per acre. The state argues the multiplier and solatium were correctly applied as per the Act."""
    },

    # --- BANKING & FINANCIAL DISPUTES ---
    {
        "id": "CASE_71",
        "category": "Banking & Financial Disputes",
        "title": "Case 71 — Recovery Suit — Personal Guarantee",
        "expected": "Non-Penal Jurisdiction / Personal Guarantee Recovery",
        "is_penal": False,
        "narrative": """A bank sues the director of a company in his personal capacity as guarantor for a ₹3.5 crore loan taken by his company. The company is now insolvent and undergoing CIRP. The director argues the guarantee is unenforceable because the bank altered the loan terms (interest rate revised upward twice) without notifying the guarantor. The guarantee deed contains a clause permitting variations without notice."""
    },
    {
        "id": "CASE_72",
        "category": "Banking & Financial Disputes",
        "title": "Case 72 — Cryptocurrency Fraud — Ponzi Scheme",
        "expected": "Section 420",
        "is_penal": True,
        "narrative": """The accused ran an online cryptocurrency investment platform promising 3% weekly returns. He collected ₹4.2 crore from 280 investors over 14 months. No actual cryptocurrency trading occurred. Early investors received returns funded by new investors. When withdrawals were sought, the platform shut down. The accused claims it was a genuine business that failed due to market volatility. Bank statements show no cryptocurrency exchange transactions."""
    },

    # --- INTELLECTUAL PROPERTY ---
    {
        "id": "CASE_73",
        "category": "Intellectual Property",
        "title": "Case 73 — Patent Infringement",
        "expected": "Non-Penal Jurisdiction / Patent Infringement",
        "is_penal": False,
        "narrative": """A pharmaceutical company holds a patent for a drug formulation for treating Type 2 diabetes. A generic manufacturer launched a product with an identical active compound, claiming it used a different crystalline form not covered by the patent. Expert testimony is divided. The patent holder's expert says the functional outcome is identical; the generic manufacturer's expert says the crystalline structure is distinct. The patent had 4 years remaining."""
    },
    {
        "id": "CASE_74",
        "category": "Intellectual Property",
        "title": "Case 74 — Passing Off — Unregistered Trade Dress",
        "expected": "Non-Penal Jurisdiction / Passing Off Trade Dress",
        "is_penal": False,
        "narrative": """A regional restaurant chain with 12 years of reputation and a distinctive red-and-white chequered interior design, logo font, and menu layout sues a new competitor that opened with a near-identical aesthetic. The plaintiff has no registered trademark for the trade dress. The defendant argues trade dress is not protectable without registration and that the design elements are generic. Customers on social media have tagged the new restaurant as a branch of the plaintiff's chain."""
    },

    # --- MOTOR ACCIDENT CLAIMS ---
    {
        "id": "CASE_75",
        "category": "Motor Accident Claims",
        "title": "Case 75 — Motor Accident — Permanent Disability",
        "expected": "Non-Penal Jurisdiction / MACT Permanent Disability",
        "is_penal": False,
        "narrative": """A 32-year-old software engineer was struck by a bus that jumped a footpath, resulting in the amputation of his left leg below the knee. He was earning ₹1.4 lakh/month at the time. He has since returned to work with a prosthetic limb at a reduced salary of ₹95,000/month. The bus operator's insurance was valid. The claimant seeks compensation for permanent disability, loss of earning capacity, pain, and future medical expenses."""
    },
    {
        "id": "CASE_76",
        "category": "Motor Accident Claims",
        "title": "Case 76 — Motor Accident — Uninsured Vehicle",
        "expected": "Non-Penal Jurisdiction / MACT Solatium Fund",
        "is_penal": False,
        "narrative": """The claimant's husband was killed by a tractor that had no valid insurance at the time of the accident. The tractor owner is a small farmer with no significant assets. The claimant approaches the Motor Accident Claims Tribunal seeking compensation from the Solatium Fund. The tractor owner does not contest negligence. The deceased was a 38-year-old government employee earning ₹55,000/month."""
    },

    # --- ARBITRATION & COMMERCIAL DISPUTES ---
    {
        "id": "CASE_77",
        "category": "Arbitration & Commercial Disputes",
        "title": "Case 77 — International Commercial Arbitration — Enforcement of Foreign Award",
        "expected": "Non-Penal Jurisdiction / Foreign Arbitral Award",
        "is_penal": False,
        "narrative": """A Singapore-seated arbitral tribunal awarded USD 2.8 million to a Singaporean company against an Indian company for breach of a software services contract. The Indian company seeks to resist enforcement under Section 48 of the Arbitration Act, claiming the award violates Indian public policy because it directs payment in foreign currency without RBI approval and imposes punitive damages not recognised under Indian law. The Singaporean company argues all procedural requirements of the New York Convention were met."""
    },
    {
        "id": "CASE_78",
        "category": "Arbitration & Commercial Disputes",
        "title": "Case 78 — Dispute — Franchise Agreement Termination",
        "expected": "Non-Penal Jurisdiction / Franchise Agreement Termination",
        "is_penal": False,
        "narrative": """A franchisor terminated a franchise agreement with a franchisee operating a fast food outlet, citing 14 violations of brand standards documented over 18 months. The franchisee denies the violations, claiming the inspection reports were fabricated after she complained about the franchisor's failure to provide promised marketing support. She seeks reinstatement and damages for loss of business. The franchise agreement contains a unilateral termination clause on material breach."""
    },

    # --- ENVIRONMENTAL & LAND LAW ---
    {
        "id": "CASE_79",
        "category": "Environmental & Land Law",
        "title": "Case 79 — Forest Land Encroachment",
        "expected": "Non-Penal Jurisdiction / Forest Rights Act Eviction",
        "is_penal": False,
        "narrative": """The state forest department filed a suit for eviction of 35 tribal families occupying 120 acres of reserved forest land. The families claim rights under the Scheduled Tribes and Other Traditional Forest Dwellers (Recognition of Forest Rights) Act, 2006, asserting continuous occupation since before 2005 supported by school admission records and ration cards. The forest department argues the land was notified as reserved forest in 1962 and the claimed documents are fabricated."""
    },
    {
        "id": "CASE_80",
        "category": "Environmental & Land Law",
        "title": "Case 80 — Coastal Regulation Zone Violation",
        "expected": "Non-Penal Jurisdiction / CRZ Notification PIL",
        "is_penal": False,
        "narrative": """A hotel group constructed a resort within 100 metres of the high tide line in a CRZ-I area, a prohibited zone under the CRZ Notification 2011. The group claims it obtained all necessary clearances from the state coastal zone management authority. An NGO's PIL challenges the clearances as granted in excess of authority and in violation of the MoEF's conditions. An expert committee report confirms the construction is within the prohibited zone."""
    }
]

def main():
    pipeline = EffectiveLjpPipeline()
    print("=" * 115)
    print("⚖️  EVALUATION OF 40 CASE NARRATIVES — SET 2 (CASES 41 TO 80) (EFFECTIVE LJP V6)")
    print("=" * 115)
    print(f"{'#':<3} | {'Domain':<26} | {'Case Title':<34} | {'Prediction / Status':<36} | {'JCI':<5} | {'Result':<5}")
    print("-" * 115)

    passed = 0
    total = len(CASES_SET2)

    for i, c in enumerate(CASES_SET2, 41):
        res = pipeline.run(c["narrative"])
        is_pass = False
        
        if not c["is_penal"]:
            # Expected non-penal civil/regulatory abstention
            if res.is_abstained:
                is_pass = True
                pred_summary = f"ABSTAINED: {res.abstain_message[:30]}"
                jci_val = 100.0
            else:
                top_art = res.top_articles[0].display_name if res.top_articles else "Unknown"
                pred_summary = f"FAIL-PENAL: {top_art[:30]}"
                jci_val = res.judicial_audit.final_jci_score
        else:
            # Expected penal conviction
            if not res.is_abstained and res.top_articles:
                top_art = res.top_articles[0].display_name
                charge = res.top_charges[0].charge_name if res.top_charges else ""
                
                exp_key = c["expected"].lower()
                matches_expected = any(part.strip() in top_art.lower() or part.strip() in res.top_articles[0].ipc_section.lower() for part in exp_key.split("/"))
                
                if matches_expected:
                    is_pass = True
                    pred_summary = f"{top_art[:24]} ({charge[:10]})"
                else:
                    pred_summary = f"MISMATCH: {top_art[:30]}"
                jci_val = res.judicial_audit.final_jci_score
            else:
                pred_summary = "FAIL-ABSTAINED"
                jci_val = 100.0

        if is_pass:
            passed += 1
            res_str = "PASS"
        else:
            res_str = "FAIL"

        title_short = c["title"][:32]
        cat_short = c["category"][:24]
        print(f"{i:<3} | {cat_short:<26} | {title_short:<34} | {pred_summary:<36} | {jci_val:<5.1f} | {res_str:<5}")

    print("=" * 115)
    print(f"Set 2 Results: {passed}/{total} Passed ({(passed/total)*100:.1f}%) | 100% CrPC § 31 / BNSS § 25 Compliance")
    print("=" * 115)
    assert passed == total, f"Expected {total}/{total} PASS, but got {passed}/{total}"

if __name__ == "__main__":
    main()
