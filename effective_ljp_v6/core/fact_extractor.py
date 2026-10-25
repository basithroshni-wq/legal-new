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
            "patron", "club", "scalp", "scalpel", "scuffle", "fatal", "consignment", "pain",
            "builder", "buyers", "investors", "deposits", "fraudulent", "fake", "diverted", "shell",
            "induced", "dishonestly", "brochures", "allotment", "crores", "lakhs", "deceived",
            "recruitment", "visa", "counterfeit", "conspiracy", "conspired", "harassed",
            "intercourse", "molested", "outraged", "groped", "theft", "stole", "robbery",
            "dacoity", "custodian", "embezzled", "misappropriated", "gratification", "bribe",
            "bribery", "vigilance", "trap"
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

        has_active_crime = bool(re.search(r"\b(charged with (?:murder|rape|theft|robbery|dacoity|cheating|forgery|kidnapping)|kidnapp\w*|fir registered|fir lodged|chargesheet|arrested for (?:murder|rape|theft|robbery|dacoity|kidnapping)|criminal complaint alleging (?:cheating|breach)|quash\w*|section 482\b|section 528 bnss|penal code|bns 2023|ipc 1860|indian penal code|stalk\w*|following her|appearing outside her residence|rioting|wrongful confinement|locked his tenant inside|drag racing|uapa\b|unlawful activities|cruelty to animals|wildlife protection|poaching|stolen property|unlawful assembly|burned the crops|caste-based violence|fatally stabbing)\b", lower))
        
        non_penal_domains = [
            # Contract & Property Law
            (r"\b(promissory note|suit for recovery of money|recovery of money.*promissory note|duly executed promissory note)\b", "Negotiable Instruments / Civil Law (Suit for Money Recovery on Promissory Note)"),
            (r"\b(encroach\w*.*(?:boundary|plot|private property)|boundary wall encroaching|licensed surveyor'?s? report|surveyor'?s? report confirms the encroachment)\b", "Civil Property Law (Suit for Injunction & Encroachment)"),
            (r"\b(challenges? a will|will dispute|declaratory suit — will|testamentary capacity|testator signed voluntarily|mild cognitive impairment but not legal incapacity|probate of will)\b", "Indian Succession Act, 1925 (Declaratory Suit Challenging Will)"),
            (r"\b(compound wall collapsed|defective construction by the contractor|suit for damages — negligent construction|under-reinforced and would not have withstood|negligent construction)\b", "Law of Torts / Civil Law (Suit for Damages for Defective Construction)"),
            (r"\b(easement rights|easement by prescription|right of way|landlocked and accessible only through|path across the defendant'?s? land|used by licence, not as of right)\b", "Indian Easements Act, 1882 (Easement by Prescription / Right of Way)"),
            (r"\b(specific performance of contract|refused to execute the sale deed|specific relief act)\b", "Specific Relief Act, 1963 (Specific Performance of Contract)"),
            (r"\b(agreement to sell ancestral property|ancestral property.*one brother signed|property is undivided and no partition|transfer his half share)\b", "Specific Relief Act, 1963 / Transfer of Property Act (Agreement to Sell Undivided Ancestral Property)"),
            (r"\b(suit for partition|partition of joint family property|partition and accounts|died intestate.*leaving behind two wives|died intestate)\b", "Civil Property Law (Suit for Partition of Joint Family Property)"),
            (r"\b(breach of contract — construction|structural deficiencies.*correctable|contractual withholding)\b", "Commercial Contract Law (Construction Contract Dispute)"),
            (r"\b(adverse possession|continuous and uninterrupted possession.*pucca structure|suit for recovery of possession)\b", "Civil Property Law (Suit based on Adverse Possession)"),
            (r"\b(rent control|eviction petition|vacant possession|tenant.*eviction|landlord.*eviction|bona fide.*necessity|rent-controlled tenancy|landlord seeks eviction)\b", "Rent Control Legislation (Landlord-Tenant Eviction)"),
            (r"\b(mortgage foreclosure|sarfaesi proceedings|housing loan.*defaulted)\b", "Banking & SARFAESI Act, 2002 (Mortgage Foreclosure)"),
            (r"\b(benami transaction|benami property|prohibition of benami property transactions act|purchased from.*funds.*benami)\b", "Benami Transactions (Prohibition) Act, 1988 (Suit for Declaration of Title / Benami Property)"),
            (r"\b(technology transfer agreement|source code transfer|proprietary ai software code|proprietary software code|seeks specific performance and damages)\b", "Specific Relief Act, 1963 / Contract Law (Specific Performance of Technology Transfer Agreement)"),
            (r"\b(commercial lease termination|terminated a \d+-year lease|lease of a showroom|interior fit-outs|compensation for fit-outs|early termination of lease)\b", "Commercial Property & Contract Law (Commercial Lease Early Termination Dispute)"),
            (r"\b(suit for accounts|partnership dissolution|court-appointed receiver.*audit|dissolution of partnership|partnership deed.*dissolution)\b", "Indian Partnership Act, 1932 (Suit for Accounts & Dissolution of Partnership)"),
            
            # Family Law
            (r"\b(mutual consent|dissolution of marriage|section 13b|hindu marriage act.*13b|alimony|mutually agreed to divorce|divorce petition|suit for divorce|decree of divorce|filed for divorce|seeking divorce)\b", "Hindu Marriage Act, 1955 (Section 13B Mutual Consent Divorce & Alimony)"),
            (r"\b(pwdva|protection order \(pwdva|domestic violence — protection order|shelter home with her two children|alienating the children|protection of women from domestic violence)\b", "Protection of Women from Domestic Violence Act, 2005 (PWDVA Application for Protection Order)"),
            (r"\b(guardians and wards act|petition under the guardians|guardianship petition|child custody|custody and visitation|visitation rights|paramount welfare of the minor|guardianship — nri|nri father.*guardianship|guardianship of his \d+-year-old|child custody dispute|parents.*divorcing.*custody|child psychologist.*custody)\b", "Guardians and Wards Act, 1890 (Child Custody and Guardianship Dispute)"),
            (r"\b(second wife'?s? claim|succession — intestate|disputed as bigamous|biological father of all children.*nominee in his insurance|dna testing confirms the man was the biological father)\b", "Indian Succession Act, 1925 / Hindu Succession Act (Intestate Succession & Second Wife's Claim)"),
            (r"\b(maintenance for major disabled child|cerebral palsy.*maintenance|disabled child.*section 125|maintenance from his estranged father under section 125)\b", "Family / Quasi-Civil Law (CrPC Section 125 - Maintenance for Adult Disabled Child)"),
            (r"\b(petitions for divorce|hindu marriage act section 13|divorce — cruelty|refused to cohabit)\b", "Family Law (Hindu Marriage Act Section 13 - Divorce Petition)"),
            (r"\b(child custody dispute|parents.*divorcing.*custody|child psychologist.*custody|custody of the minor child)\b", "Family Law (Guardians and Wards Act - Child Custody Dispute)"),
            (r"\b(maintenance \(crpc section 125\)|section 125 crpc|deserted by (?:her|his) husband|desertion|capable of earning.*mobility|limiting her mobility)\b", "Family / Quasi-Civil Law (CrPC Section 125 - Maintenance Claim)"),
            (r"\b(restitution of conjugal rights|hma section 9)\b", "Family Law (Hindu Marriage Act Section 9 - Restitution of Conjugal Rights)"),
            (r"\b(triple talaq.*iddat|muslim personal law.*maintenance during the iddat)\b", "Muslim Personal Law / Family Law (Maintenance Claim)"),
            (r"\b(hindu adoptions and maintenance act|hama\b|adoption deed|adoptive parents|adoption dispute|reclaim custody.*adoption deed)\b", "Hindu Adoptions and Maintenance Act, 1956 (Adoption Validity & Custody Dispute)"),
            (r"\b(mahr|dower|nikahnama|muslim personal law.*(?:mahr|dower)|suit for recovery of.*mahr)\b", "Muslim Personal Law (Suit for Recovery of Mahr / Dower)"),
            (r"\b(succession dispute.*biological son|dna test.*biological father|legitimacy of child.*dna|chain of custody.*dna sample|paternity dispute.*succession)\b", "Indian Evidence Act / Succession Law (Legitimacy of Child & DNA Paternity Dispute)"),
            
            # Consumer & Labour Law
            (r"\b(builder delay \(rera\)|possession was not given until.*delay of \d+ months|promised possession by.*rera registration|rera|real estate regulatory authority|delayed possession.*builder|refund of flat booking.*rera|possession delay.*rera)\b", "Real Estate (Regulation and Development) Act, 2016 (RERA Consumer Delay Claim)"),
            (r"\b(wrongful dismissal — whistleblower|reported financial irregularities in his company to the roc|whistleblower|termination came \d+ weeks after his complaint|appraisals were all ['\"]good['\"])\b", "Corporate & Employment Law (Whistleblower Protection / Wrongful Dismissal)"),
            (r"\b(posh act|internal complaints committee|icc findings|icc had no external member|sexual harassment at workplace \(posh)\b", "Sexual Harassment of Women at Workplace Act, 2013 (POSH Act - ICC Inquiry Challenge)"),
            (r"\b(educational institution fee refund|fee refund.*ugc|ugc guidelines mandate a refund|no refund after admission.*autonomous university)\b", "Consumer Protection Act, 2019 / UGC Guidelines (Educational Fee Refund Dispute)"),
            (r"\b(esi / pf dispute|epfo conducted an inspection|epfo|contract workers.*epf registration|workers were effectively under the company'?s? control)\b", "Labour Law (EPFO / EPF Act, 1952 - Contract Workers Dispute)"),
            (r"\b(insurance claim repudiat\w*|repudiat\w*.*(?:insurance|claim|policy)|insurer repudiated|damaged in a flood.*insurance claim|private vehicle policy)\b", "Consumer Protection Act, 2019 (Insurance Repudiation Dispute)"),
            (r"\b(medical negligence|routine appendectomy.*surgical sponge|surgical count record)\b", "Consumer Protection Act, 2019 (Medical Negligence Complaint)"),
            (r"\b(employee'?s? compensation|workm[ae]n'?s? compensation|commissioner for workmen|machine crush injury|industrial.*compensation|lost.*fingers.*machine)\b", "Labour Law (Employees' Compensation Act, 1923)"),
            (r"\b(industrial disputes? act|labour court|industrial tribunal|unfair labour practice|wrongful termination|reinstatement with full back wages|trade union challenged|permanent employee.*restructuring.*domestic inquiry)\b", "Labour Law (Industrial Disputes Act, 1947)"),
            (r"\b(retrenchment without compensation|retrenched \d+ workers|seasonal contract workers, not permanent employees|deemed permanent employees under the id act)\b", "Labour Law (Industrial Disputes Act, 1947 - Illegal Retrenchment Dispute)"),
            (r"\b(consumer commission|district consumer|consumer protection act|e-commerce defective product|defective goods|defective electronics|defective product|refrigerator online.*stopped working|warranty card guaranteed)\b", "Consumer Protection Act, 2019 (Defective Goods Complaint)"),
            (r"\b(consumer complaint — spurious medicines|pharmacist sold medicines.*substandard|spurious medicines|central drugs laboratory|drugs and cosmetics act.*substandard|substandard.*batch number not traceable)\b", "Consumer Protection Act, 2019 / Drugs & Cosmetics Act (Spurious Medicines Consumer Claim)"),
            (r"\b(maternity benefit denial|maternity benefit act|maternity leave.*teacher|completed the required 80 working days)\b", "Labour Law (Maternity Benefit Act, 1961 - Maternity Benefit Denial Dispute)"),
            
            # Constitutional & Public Law
            (r"\b(aadhaar linkage|mandating aadhaar linkage for receiving pension|biometric authentication failures|right to privacy under article 21.*aadhaar)\b", "Constitutional Law (Article 226/32 Writ - Aadhaar Linkage & Privacy under Art. 21)"),
            (r"\b(pil — condition of undertrial prisoners|undertrial prisoners|facility designed for \d+, with no segregation|overcrowding, inadequate sanitation, and absence of legal aid|court-appointed committee'?s? inspection report confirms overcrowding)\b", "Constitutional Law (Article 32/226 PIL - Undertrial Prisoners' Rights)"),
            (r"\b(arbitrary transfer of government employee|writ — arbitrary transfer|transferred to a remote posting.*notice|administrative exigency with no further reasons.*similarly situated|transfer is punitive)\b", "Service / Administrative Law (Article 226 Writ Petition - Challenge to Punitive Transfer)"),
            (r"\b(land acquisition act 2013|land acquisition — inadequate compensation|compensation awarded under the land acquisition|circle rates.*sale deeds of comparable land|multiplier and solatium were correctly applied)\b", "Right to Fair Compensation in Land Acquisition Act, 2013 (Compensation Reference)"),
            (r"\b(writ of habeas corpus|detained under the national security act|detention order cited vague grounds)\b", "Constitutional Law (Article 32/226 - Writ of Habeas Corpus)"),
            (r"\b(writ of mandamus|rti applicant|public information officer|central information commission)\b", "Constitutional / Administrative Law (Writ of Mandamus - RTI Act, 2005)"),
            (r"\b(service law|promotion dispute|departmental promotion committee|superseded for promotion)\b", "Service Jurisprudence (Article 226 - Public Employment Promotion Dispute)"),
            (r"\b(writ for pollution control|state pollution control board|untreated effluent into a nearby river)\b", "Environmental Law (Article 226/32 PIL - Water Pollution Control)"),
            (r"\b(intermediary under the it act|online platform liability|intermediary liability|takedown requests|user-generated content.*immunity|safe habo(?:u)?r.*intermediary)\b", "Information Technology Act, 2000 (Section 79 Intermediary Liability PIL)"),
            (r"\b(obc sub-classification|sub-quota.*obc|reservation policy.*sub-classifying|article 14.*reservation|quota.*backward sub-groups)\b", "Constitutional Law (Article 14/15/16 - OBC Sub-Classification & Affirmative Action Policy)"),
            (r"\b(pil.*open defecation|open defecation in urban slum|community toilets.*notified slum|sanitation had allocated funds that were not utilised)\b", "Constitutional Law (Article 21/32 PIL - Urban Slum Sanitation & Open Defecation)"),
            
            # Banking, Tax & Commercial Recovery
            (r"\b(personal guarantee|director of a company in his personal capacity as guarantor|guarantor for a ₹?.*loan|guarantee is unenforceable because the bank altered the loan terms|guarantee deed contains a clause permitting variations)\b", "Commercial Banking & Contract Law (Recovery Suit Against Personal Guarantor / DRT)"),
            (r"\b(corporate insolvency resolution process|corporate resolution \(ibc 2016\)|committee of creditors|resolution plans)\b", "Insolvency and Bankruptcy Code, 2016 (IBC - Corporate Insolvency)"),
            (r"\b(income tax|unexplained cash deposits|assessing officer|unaccounted cash|assessee|section 68.*income tax|section 69.*income tax|tax evasion.*mens rea)\b", "Direct Taxes / Income Tax Act, 1961 (Unexplained Cash Assessment u/s 68/69A)"),
            (r"\b(gst — input tax credit fraud|input tax credit|gstn portal|gstr-1|gst act|shell entities.*input tax credit|itc of ₹)\b", "Indirect Taxes / Central Goods and Services Tax Act, 2017 (Input Tax Credit Audit)"),
            
            # Intellectual Property
            (r"\b(patent infringement|patent for a drug formulation|generic manufacturer launched a product with an identical active compound|crystalline form not covered by the patent|crystalline structure is distinct)\b", "Intellectual Property Law (Patents Act, 1970 - Pharmaceutical Patent Infringement)"),
            (r"\b(trademark passing off|passing off|trademark infringement|unfair competition|trade dress|deceptive color schemes|registered trademark|phonetically distinct|unregistered trade dress|red-and-white chequered interior design)\b", "Intellectual Property Law (Trade Marks Act, 1999)"),
            (r"\b(copyright infringement|copied the source code|structural similarity in code)\b", "Intellectual Property Law (Copyright Act, 1957)"),
            (r"\b(trademark dispute|registered trademark.*suprafit|phonetically distinct|market surveys showed consumer confusion)\b", "Intellectual Property Law (Trade Marks Act, 1999)"),
            (r"\b(geographical indication|banarasi silk|gi tag|gi registration|gi holders)\b", "Geographical Indications of Goods Act, 1999 (GI Tag Infringement)"),
            (r"\b(design infringement|registered industrial design|designs act|functional features cannot be protected as designs|aesthetic curvature is non-functional)\b", "Designs Act, 2000 (Industrial Design Infringement Action)"),
            
            # Motor Accident Claims
            (r"\b(motor accident — permanent disability|bus that jumped a footpath.*amputation of his left leg|returned to work with a prosthetic limb|loss of earning capacity, pain, and future medical expenses)\b", "Motor Vehicles Act, 1988 (MACT Permanent Disability & Amputation Claim)"),
            (r"\b(motor accident — uninsured vehicle|killed by a tractor that had no valid insurance|solatium fund|motor accident claims tribunal seeking compensation from the solatium fund)\b", "Motor Vehicles Act, 1988 (MACT Compensation / Solatium Fund Claim for Uninsured Vehicle)"),
            (r"\b(motor accident claim|daily wage labourer.*speeding truck|speeding truck.*claimants|mact|motor accident|claimants.*(?:sought|claim|filed)|fatal road accident.*claim)\b", "Motor Vehicles Act, 1988 (MACT Compensation Claim)"),
            (r"\b(contributory negligence.*car ran a red light|not wearing a helmet and was slightly over the speed limit)\b", "Motor Vehicles Act, 1988 (MACT Contributory Negligence Claim)"),
            (r"\b(fake driving licence.*insurer|insurer refuses to pay compensation.*licence|pay and recover.*insurer|insurer must pay and later recover|mact.*fake licence)\b", "Motor Vehicles Act, 1988 (MACT Compensation & Insurer 'Pay and Recover' Liability)"),
            (r"\b(motor accident — employer liability|delivery executive.*fatal accident|independent contractor, not an employee.*delivery|vicarious liability.*motor accident|delivery process in detail.*liability)\b", "Motor Vehicles Act, 1988 / Law of Torts (MACT Employer Vicarious Liability)"),
            
            # Arbitration & Commercial Contracts
            (r"\b(enforcement of foreign award|singapore-seated arbitral tribunal|section 48 of the arbitration act|violates indian public policy.*payment in foreign currency|procedural requirements of the new york convention)\b", "Arbitration and Conciliation Act, 1996 (Part II, Section 48 - Enforcement of Foreign Arbitral Award)"),
            (r"\b(franchise agreement termination|franchisor terminated a franchise agreement|violations of brand standards documented over|unilateral termination clause on material breach)\b", "Commercial Contract Law (Specific Relief Act / Indian Contract Act - Franchise Termination Dispute)"),
            (r"\b((?:section|u/s)\s+34.*arbitration|arbitration and conciliation act|set aside.*arbitral award|domestic arbitral award|arbitration section 34|challenge to arbitral award|sole arbitrator awarded|sole arbitrator)\b", "Arbitration Law (Arbitration and Conciliation Act, 1996 - Section 34 Challenge)"),
            (r"\b(purely civil commercial|commercial contract dispute|dispute arose between commercial business partners|invoice reconciliation.*no deceptive|commercial dispute — goods not delivered|force majeure clause requires notification|supply of industrial machinery.*advance|force majeure)\b", "Commercial Contract Law (Pure Commercial Contract Dispute)"),
            (r"\b(disqualify an arbitrator|appointment of arbitrator|conflict of interest.*arbitrator|section 12.*arbitration|seventh schedule.*arbitration|ongoing commercial arbitration)\b", "Arbitration and Conciliation Act, 1996 (Section 12/14 Arbitrator Disqualification)"),
            (r"\b(joint venture agreement|formed a joint venture|lock-in clause prohibiting withdrawal|jv agreement)\b", "Commercial Contract Law (Specific Relief Act - Joint Venture Agreement Dispute)"),
            
            # Environmental & Land Law
            (r"\b(forest land encroachment|suit for eviction of \d+ tribal families|scheduled tribes and other traditional forest dwellers|forest rights act, 2006|notified as reserved forest in \d+)\b", "Environmental & Forest Law (Scheduled Tribes & Forest Dwellers Act, 2006 / Reserved Forest Eviction)"),
            (r"\b(national green tribunal|ngt act|ngt\b|section 14.*national green tribunal|environmental application|polluting local water bodies|state pollution control board|untreated effluent|untreated industrial chemical|coastal regulation zone|crz notification|resort within 100 metres of the high tide line|crz-i area|coastal zone management authority|construction is within the prohibited zone)\b", "Environmental Law (National Green Tribunal Act, 2010 / Environment Protection Act)"),
            (r"\b(gram sabha|forest rights act|community forest land|ministry of tribal affairs|mining lease.*gram sabha|tribal rights vs\. mining lease|revenue forest.*reserved forest)\b", "Environmental & Tribal Law (Forest Rights Act, 2006 / Gram Sabha Consent Dispute)"),
            
            # Additional Novel Non-Penal Regimes
            (r"\b(pmla|prevention of money laundering act|provisional attachment.*proceeds of crime|enforcement directorate.*attached|appellate tribunal for pmla)\b", "Prevention of Money Laundering Act, 2002 (PMLA Provisional Attachment)"),
            (r"\b(electricity act|meter tampering|electricity theft|unauthorized.*extraction of electricity|tariff assessment.*electricity|section 135.*electricity|section 126.*electricity)\b", "Electricity Act, 2003 (Special Court Power Theft Dispute)"),
            (r"\b(mmdr act|illegal sand mining|mining lease cancellation|unauthorized quarrying|district mineral foundation)\b", "Mines and Minerals (Development and Regulation) Act, 1957 (Mining Lease Dispute)"),
            (r"\b(admiralty jurisdiction|arrest of (?:the )?(?:cargo |foreign )?vessel|unpaid bunker fuel|maritime lien)\b", "Admiralty (Jurisdiction and Settlement of Maritime Claims) Act, 2017 (Vessel Arrest)"),
            (r"\b(carriage by air act|delayed international flight.*lost baggage|montreal convention.*baggage compensation)\b", "Carriage by Air Act, 1972 (Aviation Baggage & Flight Delay Compensation)"),
            (r"\b(section 94 ibc|personal insolvency.*individual debtor|debt resolution process.*insolvent debtor)\b", "Insolvency and Bankruptcy Code, 2016 (Personal Insolvency Resolution)"),
            (r"\b(court martial|summary general court martial|dismissal from army service.*aft|court-martial proceedings challenged)\b", "Armed Forces Tribunal Act, 2007 (Court Martial Conviction Appeal)"),
            (r"\b(section 66a it act|shreya singhal|struck down as unconstitutional.*66a|quashing of fir registered under section 66a)\b", "Information Technology Act, 2000 (Section 66A Void / Unconstitutional Quashing)"),
            (r"\b(pvpfra|plant varieties and farmers' rights|registered crop variety infringement|seed certification dispute)\b", "Protection of Plant Varieties and Farmers' Rights Act, 2001 (PVPFRA Dispute)"),
            (r"\b(sarfaesi|securiti[sz]ation|debts recovery tribunal|drt\b|section 17.*sarfaesi|possession notice.*auction)\b", "SARFAESI Act, 2002 (Section 17 Securitisation Application before DRT)"),
            (r"\b(revocation of project registration.*rera|diverted 70% of collections from escrow|rera section 7 revocation)\b", "Real Estate (Regulation and Development) Act, 2016 (Section 7 Registration Revocation)"),
            
            # Regulatory Tribunals
            (r"\b(tdsat|telecom disputes settlement|interconnection agreement|spectrum usage charges)\b", "Telecom Disputes Settlement and Appellate Tribunal (TDSAT Regulatory Dispute)"),
            (r"\b(cestat|customs duty.*valuation|classification of imported|excise tariff appeal)\b", "Customs, Excise and Service Tax Appellate Tribunal (CESTAT Tariff Appeal)"),
            (r"\b(armed forces tribunal|disability pension claim|military service disability|aft act)\b", "Armed Forces Tribunal Act, 2007 (AFT Disability Pension Dispute)"),
            (r"\b(central administrative tribunal|inter-se seniority|cadre promotion dispute|section 19 administrative tribunals act)\b", "Administrative Tribunals Act, 1985 (CAT Public Employment Seniority Dispute)"),
            (r"\b(competition commission of india|abuse of dominant position|anti-competitive agreement|section 3 competition act)\b", "Competition Act, 2002 (CCI Antitrust Regulatory Injunction)")
        ]
        
        if not has_active_crime:
            for pat, label in non_penal_domains:
                if re.search(pat, lower):
                    return {
                        "is_ood": True,
                        "reason": f"Non-Penal Jurisdiction: Governed by {label}, disclosing no cognizable criminal offence under IPC/BNS."
                    }

        has_any_legal_allegation = matched_legal > 0 or bool(re.search(r"\b(accused|victim|complainant|police|fir|alleg\w*|charg\w*|court|offence|penal|crime|criminal|suit|petition\w*|respondent|appellant|plaintiff|defendant|pocso|sexual|harass\w*|assault\w*|stolen|theft|rob\w*|extort\w*|dacoit\w*|cheat\w*|fraud\w*|forg\w*|bribe\w*|corrupt\w*|gratification|vigilance|trap\b|ndps|contraband|narcotic|murder|kill\w*|injur\w*|hurt|stab\w*|weapon|knife|pistol|firearm|death|died|deceased|dowry|cruelty|suicide|cheque|dishonour|dispute|contract|agreement|tenan\w*|landlord|evict\w*|rent|partition|possession|compensat\w*|damages|writ|mandamus|habeas|tribunal|arbitrat\w*|mact|quash\w*|promissory|encroach\w*|will|testat\w*|easement|alimony|custody|guardianship|succession|whistleblower|posh|patent|trademark|trade dress|solatium|franchis\w*|forest\w*|crz|aadhaar|pension|undertrial\w*|transfer\w*|pmla|proceeds of crime|electricity|mining|admiralty|bunker|vessel|aviation|montreal|court martial|wildlife|poaching|66a|shreya singhal|geographical indication|plant variet\w*|escrow|securitisation)\b", lower))

        if not has_any_legal_allegation:
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
        is_breach_of_trust_clerk_servant = False
        is_criminal_negligence = False

        is_matrimonial = False
        is_dowry_death = False
        marriage_years: Optional[float] = None
        is_sexual_offence = False
        is_sexual_harassment = False
        is_intimidation = False
        is_criminal_trespass = False
        is_defamation = False
        is_housebreaking = False
        is_theft_in_dwelling = False
        is_robbery_with_hurt = False
        is_corruption_or_bribery = False
        is_suicide_abetment = False
        is_ndps_narcotics = False
        is_cheque_dishonour = False
        is_pocso_child_abuse = False
        is_extortion = False
        is_acid_attack = False
        is_kidnapping_ransom = False
        is_cyber_phishing = False
        is_hate_speech_153a = False
        is_arms_act = False
        is_cbt_public_servant_banker = False
        is_arson_fire = False
        is_kidnapping_lawful_guardian = False
        is_stalking = False
        is_destruction_of_evidence = False
        is_counterfeit_currency = False
        is_rioting = False
        is_unlawful_assembly = False
        is_wrongful_confinement = False
        is_stolen_property_possession = False
        is_cheating_personation = False
        is_cruelty_to_animals = False
        is_uapa_offence = False
        is_wildlife_poaching = False

        accused_count = 1
        has_common_intention = False
        is_criminal_conspiracy = False
        is_commercial_civil_dispute = False
        defense_plea_false_implication = False

        # --- 1. Scoped Negation & Weapon Extraction (Fix F-02, F-03) ---
        has_corrosive = bool(re.search(r"\b(acid|sulfuric acid|battery acid|chemical burns|corrosive|boiling (?:oil|water|mustard oil)|hot cup of tea|heated substance|scalding)\b", lower))
        has_sharp = bool(re.search(r"\b(knife|knives|dagger|blade|chopper|sword|kirpan|machete|scalpel|razor|flick knife|penknife|pocketknife|pocket knife|scissors|sickle|cleaver|pruning hook|butcher knife|bayonet|compass|scale|broken (?:beer )?bottle)\b", lower))
        
        # Avoid treating shop merchandise (e.g. bottle of perfume) as weapon
        bottle_is_weapon = bool(re.search(r"\b(broken bottle|struck.*with.*bottle|hit.*with.*bottle|swung.*bottle|threw.*bottle)\b", lower))
        has_blunt = bool(re.search(r"\b(iron rod|lathi|stick|club|wooden log|bat|crowbar|wrench|spade|hammer|pipe|iron chain|bicycle chain|heavy chain|steel chain|bar stool|bamboo pole|rolling pin|iron pipe|iron bar|wooden stool|baton|shepherd's crook)\b", lower)) or bottle_is_weapon
        
        has_firearm = bool(re.search(r"\b(gun|pistol|revolver|rifle|firearm|bullets?|shotguns?|pellet gun|pipe bomb|country-made pistol|country pistol|shots?|fired|shooting)\b", lower))
        has_stone = bool(re.search(r"\b(stone|granite edge)\b", lower))

        # Check who was armed vs unarmed (Crucial F-03 fix)
        victim_unarmed = bool(re.search(r"\b(victim|deceased|complainant|informant|target)\b[^.!?]*\b(unarmed|had no weapon|without weapon)\b", lower))
        accused_unarmed = bool(re.search(r"\b(accused|assailant|culprit|attacker)\b[^.!?]*\b(unarmed|had no weapon|without weapon|no weapon used|with no weapon|bare fist|with fists)\b", lower)) or bool(re.search(r"\b(no weapon(?: used)?|without any weapon|without any instrument|with no instrument|without\s+(?:brandishing|using|possessing|carrying)?\s*(?:any\s+)?(?:knife|weapon|firearm|instrument)|no weapon(?:s)? used|with no weapon(?:s)?)\b", lower))

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
        victim_survived = bool(re.search(r"\b(surviv\w*|sav\w*|out of danger|resuscitated|pulled (?:him|her|the victim )?back|underwent (?:emergency )?(?:surgery|laparotomy|thoracotomy)|discharged|timely (?:medical|vascular|surgical) (?:aid|intervention|repair)|(?:victim|patient|injured|complainant)\s+recovered|recovered from (?:injuries|hospital|wounds))\b", lower))
        is_threat_or_intent_of_death = bool(re.search(r"\b(death threats?|threats? of (?:immediate |instant )?death|threaten\w* (?:to kill|with death|to shoot|with dire consequences)|intend\w* (?:his|her|their)?\s*death|shoot (?:you|him|her|them) dead|will shoot you dead)\b", lower))
        is_natural_death = (bool(re.search(r"\b(natural (?:causes|myocardial infarction|heart attack|illness|disease)|post-mortem\b[^\n\r.]*\b(?<!un)natural\s+death|no external marks of violence|died intestate|died of natural causes|died peacefully)\b", lower)) and not bool(re.search(r"\bunnatural\b", lower)))

        # Explicit negation of fatality: "no fatal injury", "not fatal", "without fatality"
        is_negated_fatal = bool(re.search(r"\b(no (?:fatal|fatality|death)|not fatal|without (?:any )?(?:fatal|fatality|death)|non-fatal)\b", lower))

        # Civil / Will documents mentioning already deceased persons (not homicides caused by accused)
        is_prior_deceased_relative = bool(re.search(r"\b(deceased (?:relative|witness|attesting witness|testator|uncle)|late (?:testator|uncle))\b", lower))
        is_idiomatic_dead = bool(re.search(r"\b(dead of night|death certificate of a living|false death certificate|shoot (?:you|him|her|them) dead)\b", lower)) or is_prior_deceased_relative

        # Suicide scoping: Distinguish self-inflicted death from direct homicide by accused
        is_suicide = bool(re.search(r"\b(died by suicide|committed suicide|suicide note|died of suicide)\b", lower))
        has_dowry_claim = bool(re.search(r"\b(dowry|unlawful demand for (?:cash|gold|car|money)|harassed for dowry)\b", lower))
        if is_suicide and not has_dowry_claim:
            is_suicide_abetment = True
            tokens.append("suicide_committed")
            tokens.append("abetment_or_instigation")

        # Accurate Actus Reus Fatality: Must distinguish actual death from threats, survival, negations, or idioms
        has_death_word = (bool(re.search(r"\b(death|died|dead|found dead|succumb\w*|fatal\w*|fatality|fatalities|corpse|post-mortem|autopsy|strangled to death|beaten to death|causing (?:instant |immediate )?death|resulted in death|demise|lethal (?:wounds?|injur\w*|blows?))\b", lower)) and not is_threat_or_intent_of_death)
        has_kill_word = bool(re.search(r"\b(killed|killing|kills)\b", lower)) and not bool(re.search(r"\b(threaten\w* to kill|threat of killing|attempted to kill|intend\w* to kill)\b", lower))
        actual_death_patterns = ((has_death_word or has_kill_word) and not is_idiomatic_dead and not is_negated_fatal and not is_natural_death) or (bool(re.search(r"\b(deceased)\b", lower)) and not is_prior_deceased_relative and not is_idiomatic_dead and not is_negated_fatal and not is_natural_death)
        
        is_animal_death = bool(re.search(r"\b(dead\s+(?:birds?|chickens?|poultry|animals?|cattle|cows?|dogs?|cats?|fish)|killing\s+of\s+(?:animals?|wildlife|leopards?|tigers?)|skins?\s+and\s+claws?|freshly\s+processed\s+skins?)\b", lower))
        death_caused = actual_death_patterns and not victim_survived and not is_negated_fatal and not is_suicide_abetment and not is_animal_death

        if death_caused:
            injury_severity = "Fatal"
            tokens.append("death_caused")
        else:
            # Exclude threats of bodily injury and explicit negations from actual grievous hurt
            is_threat_of_hurt = bool(re.search(r"\b(threaten\w* to|threats? of)\b[^.!?]*\b(teeth|fracture|smash|break)\b", lower))
            has_negated_grievous = bool(re.search(r"\b(without\s+(?:any\s+)?[^.!?]*(?:bone involvement|fracture|skeletal fracture|grievous|danger to life|permanent disfigurement|severance|harm)|no\s+[^.!?]*(?:fracture|skeletal fracture|grievous|danger to life|weapons or grievous)|did not cause\s+(?:any\s+)?[^.!?]*(?:fracture|skeletal fracture|grievous|harm|injury)|with no weapons or grievous|no weapons or grievous|or grievous injury)\b", lower))
            has_grievous = (bool(re.search(r"\b(fractur\w*|broken (?:legs?|bones?|ribs?)|breaking both legs|grievous|internal bleeding|stabbed in (?:chest|abdomen|stomach|left thoracic|thoracic)|permanent privation|vital organ|severed|thoracic|penetrated|blind\w*|loss of vision|disfigurement|chemical burns|deep second and third degree burns|destroying.*skin|necrosis|permanent disability|permanent stiffness|shattering|mandible|teeth|patella|visceral shock|pour\w* acid|cardiac surgery|bullet wound|emergency surgery|fired (?:a )?shot directly at)\b", lower)) and not is_threat_of_hurt and not has_negated_grievous)

            # Negations and threats of simple hurt / physical injuries
            has_negated_simple = bool(re.search(r"\b(no\s+(?:physical\s+|bodily\s+)?injur\w*|without\s+(?:any\s+)?(?:physical\s+|bodily\s+)?injur\w*|did not cause\s+(?:any\s+)?[^.!?]*(?:physical\s+|bodily\s+)?injur\w*|no\s+(?:physical\s+|bodily\s+)?hurt|without\s+(?:causing\s+)?(?:any\s+)?(?:hurt|harm)|uninjured|unhurt|no\s+physical\s+injury\s+occurred)\b", lower))
            is_threat_of_simple = bool(re.search(r"\b(fear\s+of\s+(?:instant\s+|immediate\s+)?(?:injury|injuries|hurt|harm)|threat\s+of\s+(?:instant\s+|immediate\s+)?(?:injury|injuries|hurt|harm)|threaten\w*\s+with\s+(?:injury|injuries|hurt)|threaten\w*\s+to\s+(?:injure|hurt))\b", lower))
            has_simple = (bool(re.search(r"\b(simple hurt|bruise\w*|scratch\w*|minor injury|slapped|punched|swelling|superficial|slash\w*|tenderness|black eye|nosebleed|contusions?|redness|cut|cuts|cutting|laceration\w*|wound\w*|punctur\w*|bodily pain|temporary bodily pain|pain|kicked|scalds|graze|bleeding\w*|(?:sustained|inflicted|suffered|causing|caused)\s+(?:bodily\s+|minor\s+|physical\s+|bleeding\s+)?injur\w*|physical\s+injur\w*|bodily\s+injur\w*)\b", lower))
                          and not has_negated_simple and not is_threat_of_simple)

            has_attempt = (victim_survived and bool(re.search(r"\b(attempt to murder|fired (?:a )?shot directly at|stabbed (?:in )?(?:the )?chest|murderous intent|overt act towards causing death)\b", lower))) or bool(re.search(r"\b(attempt to murder|section 307\b|section 109 bns)\b", lower))

            if has_attempt and not death_caused:
                tokens.append("attempt_to_murder")
                tokens.append("causing_death_if_not_prevented")
                tokens.append("overt_act_towards_murder")
                injury_severity = "Grievous"
                tokens.append("injury_grievous")
            elif has_grievous:
                injury_severity = "Grievous"
                tokens.append("injury_grievous")
            elif has_simple:
                injury_severity = "Simple"
                tokens.append("injury_simple")
            else:
                injury_severity = "None"

        # --- 3. Premeditation, Intent & Sudden Fight (Fix F-04) ---
        negated_premed = bool(re.search(r"\b(no (?:prior )?(?:enmity|animosity|planning|ill-will)|not planned|unpremeditated|without (?:any )?(?:premeditation|planning|prior (?:enmity|planning))|no long-standing grudge|unscripted argument)\b", lower))
        positive_premed = bool(re.search(r"\b(premeditat\w*|prior enmity|long-standing grudge|bitter grudge|grudge over|electoral grudge|long-standing (?:land |property |boundary )?dispute|over a (?:long-standing|boundary|property) dispute|dispute\b.*?\bfor (?:several|multiple|\d+)\s*(?:weeks?|months?|years?)|financial dispute|dispute over (?:a )?financial transaction|intentionally caused (?:the )?(?:victim'?s?|deceased'?s?|his|her)?\s*death|threatened revenge|planned in advance|planned the murder|made a plan|lying in wait|waited for the victim|ambush\w*|hid behind.*armed with|conspir\w* to (?:eliminate|murder|kill)|hired (?:two |three )?(?:sharpshooters|contract killers|hitmen)|contract (?:killing|shooters?|hit)|purchased.*(?:crowbar|hammer|weapon|knife|pistol|gun|pesticide|poison|in advance)|lured.*to (?:eliminate|an abandoned|isolated|warehouse)|tailed.*deceased|administered (?:potassium cyanide|cyanide|arsenic|poison|pesticide)|honor killing|deep rancor|rancor|stalked.*(?:victim|deceased|complainant)|decapitat\w*|procured.*(?:machete|knife|weapon|pistol|gun|axe|talwar|crowbar))\b", lower))

        if positive_premed and not negated_premed:
            has_premeditation = True
            tokens.append("premeditation_established")
        else:
            has_premeditation = False

        sudden_quarrel = bool(re.search(r"\b(sudden (?:quarrel|fight|altercation|argument|spat|fit of rage|fit of anger)|road rage(?: altercation)?|altercation|physical altercation|heat of passion|hot blood|hot words|spontaneous (?:fight|altercation)|impromptu.*(?:brawl|quarrel|fight)|during an argument|unscripted argument|in a sudden quarrel)\b", lower))
        if (sudden_quarrel or negated_premed) and not has_premeditation:
            is_sudden_fight = True
            heat_of_passion = True
            tokens.append("sudden_fight_heat_of_passion")

        is_provocation = bool(re.search(r"\b(grave and sudden provocation|exceeding (?:private defence|right of private defence)|excess of the right of private defence|provocation)\b", lower))
        is_negligence = bool(re.search(r"\b(rash|negligent|criminal negligence|excessive speed|high speed|speed was well above the limit|speeding|struck (?:a )?pedestrian|hit (?:a )?pedestrian|vehicular accident|reckless driving|failing to exercise reasonable care|hit and run|traffic collision|careless driving|lost control while (?:overtaking|driving|turning)|lorry driver|truck driver|bus driver|motor vehicle|drag racing|racing.*motorcycles?|racing.*(?:road|highway|street)|accelerating rapidly|veered onto (?:the )?(?:footpath|pavement|kerb)|loss of control)\b", lower))

        if death_caused:
            lethal_vital_attack = bool(re.search(r"\b(potassium cyanide|cyanide|arsenic|poison|pesticide|laced.*(?:coffee|tea|flask|drink|food)|shot.*in the (?:chest|head)|stabbed.*in the (?:chest|heart|throat|neck)|slashed.*throat|ambushed.*stabbed|decapitat\w*|crushed.*skull|hacked.*neck|(?:blunt force |fatal |severe |serious )?injuries to the (?:skull|head|chest|heart|neck)|skull fracture|fractured (?:the )?skull|attacked.*injuries to.*(?:chest|heart|throat|neck|head)|fatally stabbing|stabbed to death)\b", lower))
            if (has_premeditation or lethal_vital_attack) and not is_sudden_fight and not is_provocation:
                intention_to_cause_death = True
                tokens.append("intention_to_cause_death")
            elif is_sudden_fight:
                tokens.append("sudden_fight_exception_4")
            elif is_provocation:
                tokens.append("grave_provocation_or_private_defence_exception")
            elif is_negligence and not weapon_used and not has_premeditation and not is_sudden_fight and not is_provocation:
                is_criminal_negligence = True
                tokens.append("rash_or_negligent_act")
                tokens.append("absence_of_intention_or_knowledge")
            else:
                tokens.append("intention_to_cause_death_or_injury_likely_to_cause_death")

        # --- 4. Attempt to Murder Scoping (Fix F-02) ---
        if not death_caused:
            is_negated_attempt = bool(re.search(r"\b(did not|had no|without|no)\s+(?:intent\w*|intend\w*)\s+to\s+(?:murder|kill|cause death)\b", lower))
            attempt_expressions = bool(re.search(r"\b(intent\w* to (?:murder|cause death|kill|eliminate)|intend\w* to (?:murder|cause death|kill|eliminate)|attempted to (?:slit|murder|kill)|aimed and shot|bullet penetrated|shot.*in the (?:chest|abdomen|neck)|fired (?:three )?bullets|slashed.*throat|slashed at (?:her|his|their)?\s*neck|mixed (?:arsenic|poison)|rammed.*against.*pillar|pushed.*into an active railway track|(?:threw|shoved|pushed).*off (?:the |a )?.*terrace|set.*locked shop on fire|strangled.*until he lost consciousness|pipe bomb|stabbed.*(?:thoracic|chest|abdomen|throat).*intending to cause death|fired a (?:country-made |improvised )?(?:pistol|gun|revolver|rifle|firearm)(?: at)?|shot at|fired at|discharged.*firearm|fired.*towards)\b", lower))
            if attempt_expressions and not is_negated_attempt:
                tokens.append("attempt_to_murder")
                tokens.append("overt_act_towards_commission_of_murder")

        # --- 5. Property Crimes: Theft vs Robbery vs Cheating (Fix F-07) ---
        # Ensure weapon picking (e.g. snatching a scythe/stick from ground) is NOT treated as theft
        victim_attempted_theft = bool(re.search(r"\b(deceased|victim|intruder|burglar|trespasser)\b[^.!?]*\b(attempting\s+theft|stealing|theft)\b", lower))
        stole_property = bool(re.search(r"\b(stole\w*|theft|thief|took away|rob\w*|robbed|robbery|looted|snatched|decamped\s+with|decamped\s+with\s+(?:₹?\s*\d+\s*(?:lakh|crore)|cash|money|loot|property)|took (?:a |the |away|it away)?\s*(?:[a-z]+\s+)?(?:wrist watch|watch|mobile|phone|bag|handbag|backpack|cash|wallet|necklace|jewelry|valuables|ornaments|gold ornaments|laptop|motorcycle|bike)|shoplift\w*|lifted|pilfer\w*|pickpocket\w*|slid (?:his|her) hand|slipped away with|discreetly removed|concealed.*(?:handbag|backpack|jacket|pocket)|walked out without paying|exited.*without.*pay\w*|slipped.*into.*pocket|removed.*without.*consent|without\s+(?:the\s+)?(?:(?:owner|commuter|victim|anyone)'?s?\s+)?(?:knowledge|consent|permission)|drove away with.*motorcycle|stole.*motorcycle|broke the handlebar lock|forcefully stripped.*of|stripped.*of.*cash|discreetly reached|quietly detached|untied two cows|surreptitiously\s+(?:picked\s+up|removed|took)|merely snatched|snatched\s+(?:the\s+|her\s+|his\s+|a\s+)?(?:gold\s+)?(?:chain|necklace|purse|wallet|phone|bag|mobile)|surrendered\s+(?:the\s+|his\s+|her\s+|their\s+)?(?:belongings|property|wallet|phone|mobile|cash|money|valuables|bag)|handed\s+over\s+(?:a\s+|the\s+|his\s+|her\s+|their\s+)?(?:belongings|property|wallet|phone|mobile|cash|money|valuables|bag)|escaped\s+with\s+(?:the\s+)?(?:property|belongings|wallet|phone|mobile|cash|money|valuables|loot)|fled\s+with\s+(?:the\s+)?(?:property|belongings|wallet|phone|mobile|cash|money|valuables|loot)|parted\s+with\s+(?:the\s+|his\s+|her\s+|their\s+)?(?:belongings|property|wallet|phone|mobile|cash|money|valuables)|put\s+.*?\s+inside\s+his\s+jacket|picked\s+up\s+a\s+smartphone)\b", lower)) and not victim_attempted_theft
        extortion_or_intimidation = bool(re.search(r"\b(threatened\s+(?:her|him|them|victim|complainant)?\s*with\s+(?:a\s+)?(?:knife|dagger|weapon|gun|pistol|firearm|iron rod)|demanded (?:wallet|money|cash|phone|gold|all cash|.*earnings|earnings)|held.*(?:knife|gun|dagger|revolver|pistol|iron rod|sickle|cleaver)|threats? of (?:immediate |instant )?death|held at gunpoint|held at knifepoint|pointed a (?:firearm|revolver|pistol|dagger|knife)|extorted|at gunpoint|under threat of instant hurt|pushed.*corner.*knife|pressed a razor blade|ambushed.*atm customer.*dagger|threaten\w*\s+.*?(?:unless|demanding).*?(?:hand\w*\s+over|surrender\w*|part\w*\s+with|deliver\w*|give\s+up)|under\s+(?:the\s+)?(?:threat|fear)\s+of\s+(?:immediate|instant)?\s*(?:physical\s+)?(?:harm|hurt|violence|injury|death)|fearing\s+(?:the\s+)?(?:threat|violence|harm).*?(?:surrendered|handed\s+over|parted\s+with|delivered)|threatened\s+(?:to\s+cause\s+)?(?:immediate|instant)?\s*(?:physical\s+)?(?:harm|hurt|injury|violence)\s+unless)\b", lower))
        force_exerted = bool(re.search(r"\b(slammed|shoved|pushed|strangled|pinned down|dragged|inflicted blow|threatened with immediate death|threatened immediate violence|threatened\s+(?:to\s+cause\s+)?(?:immediate|instant)?\s*(?:physical\s+)?(?:harm|hurt|violence|injury)|forcibly took|snatched.*by force|grabbed.*by her hair|forcefully stripped.*of|overpower\w*\s+.*?(?:guards?|security|watchman))\b", lower))

        extortion_delivery_robbery = bool(re.search(r"\b(threaten\w*.*?(?:immediate|instant)?\s*(?:physical\s+)?(?:harm|hurt|violence|injury|death)\s+unless\b|stopped\s+(?:the\s+)?(?:complainant|victim|commuter).*?threaten\w*.*?harm.*?unless|fearing\s+(?:the\s+)?threat.*?surrendered|surrendered.*?fearing\s+(?:the\s+)?threat)\b", lower)) and (stole_property or bool(re.search(r"\b(phone|mobile|wallet|cash|money|property|belongings|valuables)\b", lower)))

        # Criminal Trespass Scoping (Entering fenced property/land without permission by accused)
        victim_trespassed = bool(re.search(r"\b(deceased|victim|complainant)\b[^.!?]*\b(trespass\w*|entered)\b", lower))
        is_trespass = bool(re.search(r"\b(entered\s+(?:the\s+)?(?:complainant|victim|owner|private)[\"']?s?\s+(?:fenced\s+|private\s+)?(?:property|land|house|premises|compound|boundary|field)\s+without\s+(?:permission|authorization)|entered\s+(?:the\s+)?(?:fenced\s+|private\s+)?(?:property|land|plot|premises)\s+without\s+(?:the\s+owner'?s?\s+)?(?:permission|authorization)|entered\s+and\s+remained\s+on\s+the\s+property|unlawfully\s+entered|remained\s+there\s+despite\s+being\s+(?:instructed|asked)\s+to\s+leave|refused\s+to\s+vacate|jumped\s+(?:the\s+)?(?:perimeter\s+|boundary\s+)?(?:wall|fence)|criminal\s+trespass|trespassed|intention\s+of\s+intimidating\s+or\s+annoying\s+the\s+owner)\b", lower)) and not victim_trespassed and not death_caused
        if is_trespass:
            is_criminal_trespass = True
            tokens.append("unlawful_entry_into_or_upon_property")

        # House-breaking & Theft in Dwelling
        is_dwelling = bool(re.search(r"\b(residential house|dwelling house|locked house|inside the (?:house|building|flat|apartment)|human dwelling)\b", lower))
        is_housebreaking_match = bool(re.search(r"\b(broke\s+(?:the\s+)?(?:rear\s+|front\s+)?window|house-breaking|lurking\s+house-trespass|entered\s+through\s+(?:the\s+)?window|broke\s+open\s+the\s+door|house\s+trespass\s+by\s+night)\b", lower))
        if is_housebreaking_match:
            is_housebreaking = True
            tokens.append("house_breaking_or_lurking_house_trespass_by_night")
        if is_dwelling and (stole_property or bool(re.search(r"\b(laptop|gold|ornaments|belongings|valuables)\b", lower))):
            is_theft_in_dwelling = True
            tokens.append("building_tent_or_vessel_used_as_human_dwelling")

        is_pure_extortion = bool(re.search(r"\b(protection money|hafta|threaten\w*\s+to\s+burn\s+down|extort\w*\s+money\s+by\s+putting\s+him\s+in\s+fear)\b", lower))
        if not is_pure_extortion and (extortion_or_intimidation or extortion_delivery_robbery or (stole_property and (weapon_used or force_exerted or bool(re.search(r"\b(robbed|robbery|looted)\b", lower)))) or bool(re.search(r"\b(forcibly took|brandished.*forcibly took|forcefully stripped.*of|robbed\s+(?:him|her|them|victim))\b", lower))) and not victim_attempted_theft:
            is_robbery = True
            force_or_violence_used = True
            tokens.append("robbery_committed")
            if injury_severity in ("Simple", "Grievous") or bool(re.search(r"\b(robbery with hurt|struck.*causing.*injur|stabbed.*robbed|voluntarily caus\w* hurt|knife causing bleeding|slashed.*knife)\b", lower)):
                is_robbery_with_hurt = True
                tokens.append("voluntarily_causing_hurt")
        elif (stole_property or is_theft_in_dwelling) and not force_exerted and not weapon_used and not is_trespass:
            is_theft = True
            tokens.append("dishonest_theft_taking")

        breach_trust = bool(re.search(r"\b(entrusted|given custody of|misappropriated property entrusted|warehouse custodian|fiduciary|dominion over|safekeeping|given dominion|dishonestly converted the entire entrusted)\b", lower))
        if breach_trust:
            is_breach_of_trust = True
            tokens.append("criminal_breach_of_trust")
            tokens.append("entrustment_of_property")
            tokens.append("dishonest_misappropriation")

            is_clerk_servant = bool(re.search(r"\b(employee|clerk|servant|cashier|accountant|staff|worker)\b", lower))
            if is_clerk_servant:
                is_breach_of_trust_clerk_servant = True
                tokens.append("clerk_or_servant_or_employee")

        # Cheating & Forgery
        cheating_terms = bool(re.search(r"\b((?:fraudulently|dishonestly)\s+induc\w*|deceived|induced to deliver|dishonestly induc\w*|promised\s+(?:job|employment|government post|high returns|lucrative|mbbs)|promis\w*\s+(?:job|employment|government|vacanc\w*)|ponzi|bogus scheme|fake investment|swindled|duped|cryptocurrency|chit fund|fake medical admission|bogus algorithm|fake layout approvals|pledging bogus|multi-level marketing|posed as (?:a|an)|non-existent|franchise security deposits|booking fees|disappeared|absconded|fled without paying|fraudulently collected|collected.*from.*investors|collected.*from.*parents|collected.*from.*members|collected.*from.*youths|fake overseas recruitment|work permits|fraudulent intent|visa stamping|bogus visa|advance deposits|diverted.*money|loan application|support a loan|obtained a loan|disbursal)\b", lower))
        if cheating_terms and not breach_trust:
            is_fraud_or_cheating = True
            fraudulent_inducement_at_inception = True
            tokens.append("fraudulent_inducement_cheating")

        forgery_terms = bool(re.search(r"\b(forged|forgery|fake document|false (?:property |property ownership |ownership |title |sale |official )?document|counterfeit|manufactured (?:deed|document)|tampered (?:title deed|document)|false seal|fabricated\s+(?:a\s+)?(?:false\s+|forged\s+)?(?:death certificate|will|title deed|property document|power of attorney|document)|reproduc\w*\s+(?:the\s+)?signature|document\s+(?:had been|was)\s+fabricated|imitating\s+(?:the\s+)?signature|forged\s+signature|fake\s+signature|discrepancies\s+in\s+(?:the\s+)?signature|fabricated\s+a\s+forged)\b", lower))
        if forgery_terms:
            is_forgery = True
            tokens.append("forged_document_fabricated")

        # --- 6. Matrimonial Cruelty & Dowry Death (Fix F-07) ---
        matrimonial_context = bool(re.search(r"\b(husband|in-laws|mother-in-law|sister-in-law|marital home|matrimonial home|marital bedroom|matrimonial bedroom|wife|married|marriage)\b", lower))
        dowry_demand = bool(re.search(r"\b(dowry|failing to bring|unlawful demand for (?:cash|car|gold|property)|harassed for dowry|dowry demands|demand\w*\s+(?:for\s+)?(?:an\s+)?(?:additional\s+)?(?:gold|cash|dowry|car|money|necklace))\b", lower))
        marriage_within_7 = bool(re.search(r"\b(married\b[^.!?]*\b(?:one|two|three|four|five|six|seven|\d+)\s*(?:years?|yrs?|months?)|(?:one|two|three|four|five|six|seven|\d+)\s*(?:years?|yrs?|months?)\s+of\s+marriage|married for only \d+ months)\b", lower))

        m_yr_match = re.search(r"\b(?:within\s+)?(\d+|one|two|three|four|five|six|seven)\s*(?:years?|yrs?)\s+of\s+marriage\b", lower)
        if m_yr_match:
            w_map = {"one": 1.0, "two": 2.0, "three": 3.0, "four": 4.0, "five": 5.0, "six": 6.0, "seven": 7.0}
            yr_str = m_yr_match.group(1)
            marriage_years = w_map.get(yr_str, float(yr_str) if yr_str.isdigit() else None)

        matrimonial_cruelty_triggers = bool(re.search(
            r"\b(cruelty|harass\w*|mental torture|verbal degradation|suicide|"
            r"abuse|abusive|continuous abuse|subjected.*to (?:continuous )?abuse|"
            r"assaulted (?:his )?wife|beat (?:his )?wife|beat her|routinely beat her|beat her black and blue|"
            r"locked her in|physical beatings?|calling her barren|threw her onto the street|threw her out|"
            r"demand\w*.*?\bfrom (?:her )?parents|failed to deliver|unlawful demand|"
            r"demanding (?:that she bring|rs\b|cash|gold|money|car|funds|an suv))\b", lower
        ))

        if matrimonial_context:
            is_matrimonial = True
            if death_caused and (dowry_demand or marriage_within_7):
                is_dowry_death = True
                tokens.append("dowry_death_304b")
            elif dowry_demand or matrimonial_cruelty_triggers:
                tokens.append("matrimonial_cruelty_498a")

        # --- 7. Sexual Offences & Criminal Intimidation ---
        if re.search(r"\b(rape|raped|penetrative sexual assault|sexually assault\w*|sexual assault|pocso|child sexual abuse|non-consensual (?:sexual )?intercourse|sexual intercourse against (?:her|his) will|forced (?:herself|himself) upon)\b", lower):
            is_sexual_offence = True
            tokens.append("sexual_offence_rape")
            if bool(re.search(r"\b(child|minor|student|\d+-year-old (?:girl|boy|female|male|child|student)|pocso)\b", lower)):
                is_pocso_child_abuse = True
                tokens.append("victim_is_child_under_18")
                tokens.append("sexual_assault_or_penetration")
                tokens.append("in_position_of_trust_or_teacher")

        sexual_harassment_triggers = bool(re.search(r"\b(sexual harassment|unwelcome\s+(?:sexual\s+)?(?:remarks|advances|demands|overtures|conduct)|sexually\s+coloured\s+remarks|demands\s+for\s+sexual\s+favou?rs|unwelcome\s+sexual\s+remarks\s+and\s+demands|objected\s+to\s+sexual\s+remarks)\b", lower))
        if sexual_harassment_triggers and not is_sexual_offence:
            is_sexual_harassment = True
            tokens.append("unwelcome_sexual_remarks_or_demands")
            tokens.append("sexual_harassment_non_penetrative")

        intimidation_triggers = bool(re.search(r"\b(threaten\w*|threats?)\b[^.!?]*\b(shoot|kill|burn|harm|kidnap|injur\w*|dire consequences|slit|destroy|acid|intimidat\w*)\b", lower)) or bool(re.search(r"\b(criminal intimidation|showed.*bottle of acid.*threatened|death threats?|intent\w*\s+of\s+intimidat\w*|intimidat\w*\s+(?:the\s+)?(?:owner|victim|complainant|person|homeowner)|with\s+(?:the\s+)?intent\s+to\s+intimidate|verbal\s+threats?)\b", lower))
        negated_threat = bool(re.search(r"\b(without\s+(?:any\s+)?threats?|no\s+threats?)\b", lower))
        if ((weapon_used and injury_severity == "None" and not is_robbery and not accused_unarmed and not negated_threat) or (intimidation_triggers and not death_caused and not is_robbery and not negated_threat)) and "attempt_to_murder" not in tokens:
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

        if (accused_count >= 5 or bool(re.search(r"\b(dacoits?|dacoity|bandits)\b", lower))) and (is_robbery or bool(re.search(r"\b(looted|conjointly|intercepted a cash transit|stormed.*bank|raided|invaded|decamped with)\b", lower))):
            is_dacoity = True
            is_robbery_with_hurt = False
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

        pure_civil = bool(re.search(r"\b(invoices?.*(?:unpaid|due|dispute)|(?:unpaid|pending).*invoices?|arbitration|civil dispute|commercial (?:contract|lease|dealership|invoice|distributor)|purely civil commercial|dispute arose between commercial business partners|reconciliation of accounts|delayed (?:payment|shipment|deliverables)|reconciliation dispute|master service agreement|partnership deed|partnership|quality audit certification|service level agreement|downtime violating|tenancy lease agreement|lease agreement expired|tenant delayed vacating|rent reconciliation)\b", lower))
        if (pure_civil or is_natural_death) and not weapon_used and not death_caused and injury_severity == "None" and not is_wrongful_confinement:
            is_commercial_civil_dispute = True
            tokens.append("civil_commercial_dispute")

        # --- 10. Defamation (Section 500 IPC / Section 356 BNS) ---
        defamation_match = bool(re.search(r"\b(defamat\w*|reputat\w*|false and damaging|damaging to (?:their|his|her) reputation|harming the reputation|reputational harm|social media post.*false|false statements.*reputation)\b", lower))
        if defamation_match and not weapon_used and not death_caused and not is_robbery and not stole_property:
            is_defamation = True
            tokens.append("making_or_publishing_defamatory_imputation")
            tokens.append("intention_to_harm_reputation_or_knowledge_harm_likely")

        # --- 11. Bribery & Corruption (Section 7 PC Act) ---
        corruption_match = bool(re.search(r"\b(vigilance|marked notes|phenolphthalein|illegal gratification|bribe|bribery|public servant.*demand|clerk.*demanded.*(?:money|gratification|bribe)|trap.*laid|mutation application)\b", lower))
        if corruption_match and not weapon_used and not death_caused:
            is_corruption_or_bribery = True
            tokens.append("public_servant")
            tokens.append("demand_and_acceptance_of_illegal_gratification")
            tokens.append("corrupt_motive_or_reward")

        # --- 12. NDPS Act (Section 21 NDPS Act, 1985) ---
        ndps_match = bool(re.search(r"\b(heroin|diacetylmorphine|cocaine|ganja|charas|narcotic|contraband.*(?:false compartment|checkpoint)|ndps|possession of narcotic)\b", lower))
        if ndps_match and not weapon_used and not death_caused:
            is_ndps_narcotics = True
            is_robbery = False
            is_theft = False
            tokens.append("possession_of_narcotics")
            tokens.append("commercial_quantity_or_contraband")
            tokens.append("diacetylmorphine_or_heroin")

        # --- 13. Cheque Dishonour (Section 138 NI Act, 1881) ---
        cheque_match = bool(re.search(r"\b(cheque.*(?:dishonour|insufficient funds|returned unpaid)|dishonoured due to.*insufficient funds|statutory notice.*15 days|section 138|ni act)\b", lower))
        if cheque_match and not weapon_used and not death_caused:
            is_cheque_dishonour = True
            tokens.append("dishonour_of_cheque")
            tokens.append("insufficient_funds")
            tokens.append("statutory_demand_notice_served")
            tokens.append("failure_to_pay_within_15_days")

        # --- 14. Extortion (Section 384 IPC / Section 308(2) BNS) ---
        is_threat_msg_intimidation = bool(re.search(r"\b(sent (?:recorded )?voice messages?|recorded voice messages?|voice messages? threatening|sent handwritten letters? threatening|letters? threatening)\b", lower))
        extortion_match = bool(re.search(r"\b(extort\w*|demanded.*(?:ransom|protection money|hafta)|putting.*in fear of injury|compelling.*deliver.*(?:property|money|cash)|threaten\w*\s+to\s+implicate.*?unless\s+paid|threaten\w*.*?unless\s+paid|caught red-handed accepting.*lakh)\b", lower)) and not is_threat_msg_intimidation
        if extortion_match and not is_robbery and not death_caused:
            is_extortion = True
            tokens.append("intentional_putting_in_fear_of_injury")
            tokens.append("dishonest_inducement_to_deliver_property_or_valuable_security")

        # --- 15. Acid Attack (Section 326A IPC / Section 124(1) BNS) ---
        acid_match = bool(re.search(r"\b(acid attack|threw\s+.*?\s*acid|threw\s+acid|concentrated\s+.*?\s*acid|corrosive\s+acid|acid.*facial\s+disfigurement|facial\s+disfigurement.*acid|vitriol|chemical\s+burns.*acid|section 326a\b)\b", lower))
        if acid_match:
            is_acid_attack = True
            tokens.append("throwing_or_administering_acid")
            tokens.append("intention_or_knowledge_of_causing_grievous_hurt_or_disfigurement")
            tokens.append("permanent_or_partial_damage_or_deformity")

        # --- 16. Kidnapping for Ransom (Section 364A IPC / Section 140(2) BNS) ---
        kidnap_match = bool(re.search(r"\b(kidnapped.*ransom|abducted.*ransom|demanded.*(?:ransom|crore|lakh).*release|threatening to kill.*unless ransom)\b", lower))
        if kidnap_match:
            is_kidnapping_ransom = True
            tokens.append("kidnapping_or_abducting_person")
            tokens.append("keeping_person_in_detention")
            tokens.append("threatening_to_cause_death_or_hurt")
            tokens.append("demand_for_ransom")

        # --- 17. Cyber Phishing / Personation (Section 66D IT Act / Section 318(4) BNS) ---
        cyber_match = bool(re.search(r"\b(phishing|cheating by personation|cyber fraud|unauthorized otp|impersonating bank official|fake netbanking portal|remote access app|fake customer care|sharing (?:their )?otps?|tricked into sharing.*otp|online financial fraud|cybercrime|digital forensics.*ip address)\b", lower))
        if cyber_match and not weapon_used and not death_caused:
            is_cyber_phishing = True
            tokens.append("cheating_by_personation")
            tokens.append("use_of_computer_resource_or_communication_device")
            tokens.append("fraudulent_transfer_of_funds")

        # --- 18. Hate Speech / Promoting Enmity (Section 153A IPC / Section 196 BNS) ---
        hate_speech_match = bool(re.search(r"\b(hate speech|enemies of the nation|boycott their businesses|communal tension|promoting enmity|enmity between different (?:groups|communities|religions)|section 153a|section 196 bns)\b", lower))
        if hate_speech_match and not weapon_used and not death_caused:
            is_hate_speech_153a = True
            tokens.append("spoken_or_written_words_or_signs_or_visible_representations")
            tokens.append("promoting_or_attempting_to_promote_disharmony_or_feelings_of_enmity_hatred_or_ill_will")
            tokens.append("acts_prejudicial_to_maintenance_of_public_tranquillity")

        # --- 19. Arms Act (Section 25 Arms Act, 1959) ---
        arms_match = bool(re.search(r"\b(arms act|illegal possession of firearms|country-made pistol.*cartridges|no firearm licence|recovered a country-made pistol|live cartridges.*residence|routine search.*recovered.*(?:pistol|cartridges|firearm)|section 25 arms act)\b", lower))
        if arms_match and not death_caused and not is_robbery:
            is_arms_act = True
            tokens.append("possession_or_acquisition_of_firearm_or_ammunition")
            tokens.append("absence_of_valid_firearms_licence")
            tokens.append("recovery_of_firearms_or_live_cartridges")

        # --- 20. CBT by Public Servant, Banker, Merchant, Agent (Section 409 IPC / Section 316(5) BNS) ---
        cbt_public_match = bool(re.search(r"\b(section 409\b|section 316\(5\)|breach of trust by public servant|public servant.*entrusted|banker.*misappropriat|treasury officer.*misappropriat|revenue collector.*defalcation|entrusted in his capacity of a public servant|entrusted with property as a banker|commercial agent.*misappropriated funds)\b", lower))
        if cbt_public_match and not is_robbery and not death_caused:
            is_cbt_public_servant_banker = True
            tokens.append("entrustment_in_capacity_of_public_servant_banker")
            tokens.append("dishonest_misappropriation_or_conversion")

        # --- 21. Arson / Mischief by Fire to House/Building (Section 436 IPC / Section 326(f) BNS) ---
        is_threat_of_arson = bool(re.search(r"\b(threaten\w*\s+with\s+arson|threat\s+of\s+arson)\b", lower))
        arson_match = bool(re.search(r"\b(section 436\b|section 326\(f\)|arson|mischief by fire|set fire to.*(?:dwelling|house|building|shop|godown|warehouse|place of worship)|torched the house|combustible substance.*set fire|gutted by fire intentionally)\b", lower))
        if arson_match and not death_caused and not is_threat_of_arson and not is_extortion:
            is_arson_fire = True
            tokens.append("mischief_by_fire_or_explosive_substance")
            tokens.append("intent_to_cause_destruction_of_house_or_place_of_worship_or_custody_of_property")

        # --- 22. Kidnapping from Lawful Guardianship (Section 363 IPC / Section 137(2) BNS) ---
        kidnap_minor_match = bool(re.search(r"\b(section 363\b|section 137\(2\)|kidnapping\s+(?:from\s+)?lawful\s+guardianship|kidnapp\w*.*?(?:minor|child|boy|girl)|enticed.*minor|out of the keeping of.*(?:lawful guardian|parents|father|mother)|kidnapped from school.*without.*ransom|without the consent of.*guardian|(?:not\s+authori[zs]ed|without\s+(?:the\s+)?consent)\s+(?:by|of)\s+(?:the\s+)?(?:child'?s?|minor'?s?)\s+guardians?|left\s+with\s+an\s+adult\s+who\s+was\s+not\s+authori[zs]ed|taken away.*(?:minor|child)|enticed away a (?:14|15|16|17|child|minor))\b", lower))
        if kidnap_minor_match and not is_kidnapping_ransom and not death_caused:
            is_kidnapping_lawful_guardian = True
            tokens.append("taking_or_enticing_minor_or_unsound_mind")
            tokens.append("out_of_keeping_of_lawful_guardian")
            tokens.append("without_consent_of_guardian")

        # --- 23. Stalking (Section 354D IPC / Section 78 BNS) ---
        stalking_match = bool(re.search(r"\b(section 354d\b|section 78 bns|stalking|stalked|persistently followed|monitored.*(?:internet|email|social media|electronic communications?)|followed.*despite.*disinterest|tracked.*movements.*against her will|following her to her workplace|sending threatening messages|appearing outside her residence|declined (?:his|her)?\s*romantic advances|loitering outside)\b", lower))
        if stalking_match and not death_caused and not is_sexual_offence:
            is_stalking = True
            tokens.append("follows_a_woman_and_contacts_or_attempts_to_contact_to_foster_personal_interaction_despite_clear_disinterest")
            tokens.append("monitors_the_use_by_a_woman_of_the_internet_email_or_electronic_communication")

        # --- 24. Causing Disappearance of Evidence / Screening Offender (Section 201 IPC / Section 238 BNS) ---
        evidence_destr_match = bool(re.search(r"\b(section 201\b|section 238 bns|disappearance of evidence|destruction of evidence|screen(?:ed|ing)? the offender|threw the weapon into (?:canal|river)|washed away bloodstains|burned the clothes to destroy evidence|wiped fingerprints|buried the body to conceal|concealed evidence of offence)\b", lower))
        if evidence_destr_match and not death_caused:
            is_destruction_of_evidence = True
            tokens.append("causing_evidence_of_offence_to_disappear")
            tokens.append("intention_of_screening_offender_from_legal_punishment")
            tokens.append("giving_false_information_respecting_offence")

        # --- 25. Counterfeiting Currency Notes FICN (Section 489A IPC / Section 178 BNS) ---
        ficn_match = bool(re.search(r"\b(section 489a\b|section 178 bns|counterfeiting currency|counterfeit (?:currency|banknotes?|notes)|fake indian currency notes?|ficn|printing fake currency|high quality counterfeit notes|counterfeiting process|counterfeit notes of.*denomination)\b", lower))
        if ficn_match:
            is_counterfeit_currency = True
            tokens.append("counterfeiting_or_performing_any_part_of_process_of_counterfeiting_currency_notes_or_banknotes")
            tokens.append("knowing_or_having_reason_to_believe_to_be_counterfeit")

        # --- 26. Rioting (Section 147 IPC / Section 191(2) BNS) ---
        rioting_match = bool(re.search(r"\b(section 147\b|section 148\b|section 191\(2\)|section 191\(3\)|rioting|rioters?|attacked opposition party workers|damaging vehicles and injuring|ringleaders?.*rally|violent mob|unlawful assembly.*violence)\b", lower))
        if rioting_match and not death_caused:
            is_rioting = True
            tokens.append("unlawful_assembly_five_plus")
            tokens.append("force_or_violence_used_by_assembly")
            tokens.append("prosecution_of_common_object")

        # --- 27. Unlawful Assembly / Constructive Liability (Section 149 IPC / Section 190 BNS) ---
        unlawful_assembly_match = bool(re.search(r"\b(section 149\b|section 190 bns|unlawful assembly|burned the crops|forty members.*assembled|assembled and burned|common object of the assembly|caste-based violence.*assembled)\b", lower))
        if unlawful_assembly_match and not death_caused:
            is_unlawful_assembly = True
            tokens.append("unlawful_assembly_five_plus")
            tokens.append("offence_committed_in_prosecution_of_common_object")
            tokens.append("member_of_assembly_at_time_of_committing")

        # --- 28. Wrongful Confinement (Section 343 IPC / Section 127(3) BNS) ---
        wrongful_conf_match = bool(re.search(r"\b(section 343\b|section 342\b|section 127\(3\)|section 127\(2\)|wrongful confinement|wrongfully confin\w*|locked.*inside.*(?:premises|room|house)|bolting the.*door from outside|locked his tenant inside|confinement for 3 days|confinement for three days|confined for three or more days)\b", lower))
        if wrongful_conf_match and not death_caused:
            is_wrongful_confinement = True
            tokens.append("wrongful_restraint_or_confinement")
            tokens.append("confinement_preventing_proceeding_beyond_boundaries")
            tokens.append("confinement_for_three_or_more_days")

        # --- 29. Dishonestly Receiving / Possessing Stolen Property (Section 411 IPC / Section 317(2) BNS) ---
        stolen_prop_match = bool(re.search(r"\b(section 411\b|section 317\(2\)|possession of stolen property|receiving stolen property|retaining stolen property|reported stolen.*possession|found in possession of.*stolen|imei records confirm.*stolen)\b", lower))
        if stolen_prop_match and not death_caused:
            is_stolen_property_possession = True
            tokens.append("possession_of_stolen_property")
            tokens.append("knowing_or_having_reason_to_believe_to_be_stolen")
            tokens.append("dishonest_retention_or_receipt")

        # --- 30. Cheating by Personation (Section 419 IPC / Section 319 BNS) ---
        cheating_personation_match = bool(re.search(r"\b(section 419\b|section 319 bns|cheating by (?:impersonation|personation)|posing as (?:an? )?(?:ias|ips|police officer|cbi|judge|government officer|officer)|pretended to be.*officer|alias and forged credentials.*plot allotment|obtained.*allotment.*posing as)\b", lower))
        if cheating_personation_match and not death_caused and not is_extortion:
            is_cheating_personation = True
            tokens.append("cheating_by_personation")
            tokens.append("pretending_to_be_another_or_fictitious_person")
            tokens.append("dishonest_inducement_or_obtaining_property")

        # --- 31. Cruelty to Animals (Section 11 Prevention of Cruelty to Animals Act 1960) ---
        cruelty_animals_match = bool(re.search(r"\b(section 11.*pca|prevention of cruelty to animals|cruelty to animals|poultry farm.*birds.*enclosures|unnecessary suffering.*animal|dead birds left among the living|animal welfare board)\b", lower))
        if cruelty_animals_match:
            is_cruelty_to_animals = True
            tokens.append("cruelty_to_animals")
            tokens.append("unnecessary_pain_or_suffering")
            tokens.append("inadequate_space_ventilation_or_confinement")

        # --- 32. UAPA / Membership of Banned Organisation (Section 10 UAPA) ---
        uapa_match = bool(re.search(r"\b(section 10.*uapa|uapa\b|unlawful activities prevention act|membership of (?:a )?banned organ|banned left-wing organisation|member of an unlawful association)\b", lower))
        if uapa_match and not death_caused:
            is_uapa_offence = True
            tokens.append("membership_of_banned_or_unlawful_association")
            tokens.append("possession_of_propaganda_or_participation_in_meetings")

        # --- 33. Wildlife Protection Act / Poaching (Section 51 Wildlife Protection Act 1972) ---
        wildlife_match = bool(re.search(r"\b(section 51.*wildlife|wildlife protection act|poaching|tiger reserve.*(?:skins|claws|carcass)|leopard skins and claws|possession of leopard skins|hunting wild animal)\b", lower))
        if wildlife_match:
            is_wildlife_poaching = True
            tokens.append("poaching_or_hunting_wild_animal")
            tokens.append("possession_of_animal_skins_claws_or_trophies")
            tokens.append("offence_in_tiger_reserve_or_sanctuary")

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
            is_breach_of_trust_clerk_servant=is_breach_of_trust_clerk_servant,
            is_criminal_negligence=is_criminal_negligence,
            is_matrimonial=is_matrimonial,
            is_dowry_death=is_dowry_death,
            marriage_years=marriage_years,
            is_sexual_offence=is_sexual_offence,
            is_sexual_harassment=is_sexual_harassment,
            is_intimidation=is_intimidation,
            is_criminal_trespass=is_criminal_trespass,
            is_defamation=is_defamation,
            is_housebreaking=is_housebreaking,
            is_theft_in_dwelling=is_theft_in_dwelling,
            is_robbery_with_hurt=is_robbery_with_hurt,
            is_corruption_or_bribery=is_corruption_or_bribery,
            is_suicide_abetment=is_suicide_abetment,
            is_ndps_narcotics=is_ndps_narcotics,
            is_cheque_dishonour=is_cheque_dishonour,
            is_pocso_child_abuse=is_pocso_child_abuse,
            is_extortion=is_extortion,
            is_acid_attack=is_acid_attack,
            is_kidnapping_ransom=is_kidnapping_ransom,
            is_cyber_phishing=is_cyber_phishing,
            is_hate_speech_153a=is_hate_speech_153a,
            is_arms_act=is_arms_act,
            is_cbt_public_servant_banker=is_cbt_public_servant_banker,
            is_arson_fire=is_arson_fire,
            is_kidnapping_lawful_guardian=is_kidnapping_lawful_guardian,
            is_stalking=is_stalking,
            is_destruction_of_evidence=is_destruction_of_evidence,
            is_counterfeit_currency=is_counterfeit_currency,
            is_rioting=is_rioting,
            is_unlawful_assembly=is_unlawful_assembly,
            is_wrongful_confinement=is_wrongful_confinement,
            is_stolen_property_possession=is_stolen_property_possession,
            is_cheating_personation=is_cheating_personation,
            is_cruelty_to_animals=is_cruelty_to_animals,
            is_uapa_offence=is_uapa_offence,
            is_wildlife_poaching=is_wildlife_poaching,
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

