"""
Evaluation Script for All User Provided Batch Cases
"""
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import EffectiveLjpPipeline

pipeline = EffectiveLjpPipeline()

test_cases = [
    {
        "id": "WIFEY_SEXUAL_HARASSMENT",
        "title": "Sexual Harassment (Colleague Remarks)",
        "narrative": "A woman alleged that a colleague repeatedly made unwelcome sexual remarks and demands despite her objections. She submitted messages and identified witnesses who had observed some of the incidents. The complaint was investigated to determine whether the alleged conduct satisfied the legal definition of sexual harassment.",
        "expected_ipc": "Section 354A",
        "expected_bns": "Section 75",
        "expected_charge": "Sexual Harassment"
    },
    {
        "id": "WIFEY_DEFAMATION",
        "title": "Criminal Defamation (Social Media Post)",
        "narrative": "The accused allegedly published a social media post containing statements about the complainant that the complainant claimed were false and damaging to their reputation. The complainant submitted screenshots of the post and statements from individuals who had seen it. Investigators examined the content, publication, alleged reputational harm, and whether any statutory exception applied.",
        "expected_ipc": "Section 500",
        "expected_bns": "Section 356",
        "expected_charge": "Defamation"
    },
    {
        "id": "CASE_KAKKANAD_HOMICIDE",
        "title": "Kakkanad Unpaid Wage Quarrel Rod Strike",
        "narrative": "On 12 August 2024, at about 9:40 pm, a building contractor argued with a daily-wage labourer over three weeks of unpaid wages at a construction site in Kakkanad, Kerala. The labourer shoved him during the argument, and the contractor picked up an iron rod lying nearby and struck the labourer once on the head. The labourer collapsed and died at the hospital the next morning. Witnesses confirmed there was no prior animosity or planning, and the contractor surrendered at the police station that night.",
        "expected_ipc": "Section 304",
        "expected_bns": "Section 105",
        "expected_charge": "Culpable Homicide"
    },
    {
        "id": "CASE_THRISSUR_THEFT",
        "title": "Thrissur Bus Pocket Lift Phone Theft",
        "narrative": "A night-shift tea-stall owner in Thrissur noticed a passenger's phone sticking out of a bag on a bus on 3 March 2025 at about 7:15 pm. He lifted it unnoticed while the passenger was boarding and left the bus at the next stop. The passenger raised an alarm, and the stall owner was caught by co-passengers with the phone in his pocket. He had no previous record.",
        "expected_ipc": "Section 379",
        "expected_bns": "Section 303(2)",
        "expected_charge": "Theft"
    },
    {
        "id": "CASE_ALUVA_RASH_DRIVING",
        "title": "Aluva Wet Road Lorry Pedestrian Death",
        "narrative": "On 21 November 2024, at about 6:30 am, a lorry driver was driving at high speed on a wet road near Aluva despite warnings from his helper. He lost control while overtaking and hit a pedestrian walking on the shoulder. The pedestrian died on the spot. Traffic camera footage showed the speed was well above the limit. The driver stopped, called an ambulance and cooperated with the police.",
        "expected_ipc": "Section 304A",
        "expected_bns": "Section 106",
        "expected_charge": "Causing Death by Negligence"
    },
    {
        "id": "CASE_KOZHIKODE_RECRUITMENT",
        "title": "Kozhikode Overseas Job Forgery & Cheating",
        "narrative": "Between January and April 2025, a self-styled recruitment consultant in Kozhikode advertised overseas hospital jobs and collected Rs 4,00,000 in total from three candidates as 'processing fees'. He issued forged offer letters and visa copies. No jobs existed, and he switched off his phone when the candidates demanded refunds. Bank records traced the money to his personal account.",
        "expected_ipc": "Section 420",
        "expected_bns": "Section 318(4)",
        "expected_charge": "Cheating"
    },
    {
        "id": "CASE_KOLLAM_KNIFE_GRIEVOUS",
        "title": "Kollam Boundary Quarrel Knife Stab",
        "narrative": "On 14 June 2024 at about 11 pm, two neighbours in Kollam quarrelled over a boundary wall that had been disputed for years. The accused went home, took a kitchen knife and returned to the spot. He stabbed the complainant twice in the thigh and arm, causing deep wounds and a fractured forearm. The complainant was hospitalised for 22 days. The accused was arrested the next morning.",
        "expected_ipc": "Section 326",
        "expected_bns": "Section 118(2)",
        "expected_charge": "Grievous Hurt"
    },
    {
        "id": "CASE_KOCHI_POISON_MURDER",
        "title": "Kochi Laced Coffee Partner Premeditated Murder",
        "narrative": "A partner in a small Kochi export firm discovered in September 2024 that his co-partner had diverted Rs 30 lakh to a personal account. Over the next two months the accused made a plan. On 9 December 2024 he laced a flask of coffee with a pesticide purchased in advance and handed it to the partner during a meeting. The partner died within hours. Purchase receipts, call records and a handwritten note were recovered by the police.",
        "expected_ipc": "Section 302",
        "expected_bns": "Section 103(1)",
        "expected_charge": "Murder"
    },
    {
        "id": "CASE_ALAPPUZHA_SHOP_HURT",
        "title": "Alappuzha Shop Refund Altercation Slap",
        "narrative": "On 5 January 2025, at about 10:30 pm, a shopkeeper in Alappuzha was closing his store when a customer demanded a refund for a defective item. The shopkeeper refused, and the customer abused him in front of other buyers. The shopkeeper slapped the customer and pushed him out of the shop. The customer fell, suffered a minor bruise on the elbow and left. No weapon was used, and the customer was treated as an outpatient.",
        "expected_ipc": "Section 323",
        "expected_bns": "Section 115(2)",
        "expected_charge": "Voluntarily Causing Hurt"
    },
    {
        "id": "CASE_ERNAKULAM_HOUSEBREAKING",
        "title": "Ernakulam Night House-breaking & Theft",
        "narrative": "On 18 July 2024, at about 2:15 am, a man in Ernakulam broke the rear window of a locked house while the family was away on a pilgrimage. He entered through the window, took gold ornaments and a laptop, and left through the back door. Neighbours saw him leaving with a bag and informed the police. Part of the stolen property was recovered from his rented room. He had two earlier convictions for theft.",
        "expected_ipc": "Section 380", # or 457 or 379
        "expected_bns": "Section 305(a)",
        "expected_charge": "Theft"
    },
    {
        "id": "CASE_PALAKKAD_ROBBERY_HURT",
        "title": "Palakkad Lonely Road Knife Chain Snatch Robbery",
        "narrative": "On 27 September 2024, at about 8 pm, a man in Palakkad stopped a woman on a lonely road while she was returning from work. He threatened her with a knife and snatched her gold chain. She resisted, and he cut her hand while escaping. The chain was recovered from a pawn shop, and she identified him at the identification parade.",
        "expected_ipc": "Section 392", # or 394
        "expected_bns": "Section 309(4)",
        "expected_charge": "Robbery"
    },
    {
        "id": "CASE_KOTTAYAM_VIGILANCE_TRAP",
        "title": "Kottayam Vigilance Trap Govt Clerk Bribery",
        "narrative": "In February 2025, a government clerk in Kottayam demanded Rs 15,000 from a landowner to process a mutation application. The landowner complained to the vigilance unit, and officers laid a trap on 11 February 2025. The clerk accepted marked notes at his office and was caught with the money in his drawer. The phenolphthalein test on his fingers was positive.",
        "expected_ipc": "Section 7 PC Act",
        "expected_bns": "PC Act",
        "expected_charge": "Public Servant Bribery"
    },
    {
        "id": "CASE_KANNUR_DOWRY_DEATH",
        "title": "Kannur 6-Year Matrimonial Cruelty Dowry Hanging",
        "narrative": "On 2 May 2025, a husband in Kannur, married for six years, began harassing his wife for additional dowry of Rs 5 lakh. Over four months he and his mother beat her and denied her food. On 10 September 2025 she was found hanging at home. Her family produced messages and a medical record of earlier injuries. The post-mortem confirmed hanging, and the family complained of cruelty before her death.",
        "expected_ipc": "Section 304B",
        "expected_bns": "Section 80",
        "expected_charge": "Dowry Death"
    },
    {
        "id": "TEST001_THEFT",
        "title": "Sample 1: Entered House Stolen Laptop & Gold",
        "narrative": "The accused allegedly entered a residential house while the owner was away and removed a laptop and gold ornaments without the owner's permission. The owner discovered the missing items upon returning home and filed a complaint with the police. During the investigation, the police recovered some of the stolen property from the accused. The prosecution alleged that the accused had dishonestly taken the property belonging to the complainant.",
        "expected_ipc": "Section 379",
        "expected_bns": "Section 303",
        "expected_charge": "Theft"
    },
    {
        "id": "TEST002_CHEATING",
        "title": "Sample 2: Land Sale Advance Inducement",
        "narrative": "The accused allegedly approached the complainant with a proposal to sell a piece of land and represented that the accused had the legal authority to complete the transaction. Believing these representations, the complainant transferred money to the accused as an advance payment. The accused subsequently failed to complete the sale and stopped responding to the complainant. The complainant alleged that the representations were false from the beginning and that the accused had dishonestly induced the payment.",
        "expected_ipc": "Section 420",
        "expected_bns": "Section 318",
        "expected_charge": "Cheating"
    },
    {
        "id": "TEST003_CBT",
        "title": "Sample 3: Construction Material Funds CBT",
        "narrative": "The accused was entrusted with money by the complainant for the specific purpose of purchasing construction materials for a building project. Instead of using the money for the agreed purpose, the accused allegedly transferred the amount to a personal account and refused to return it. The complainant submitted financial records and communications to the police. The prosecution alleged that the accused had dishonestly misappropriated property entrusted to them.",
        "expected_ipc": "Section 406",
        "expected_bns": "Section 316",
        "expected_charge": "Criminal Breach of Trust"
    },
    {
        "id": "TEST004_HURT",
        "title": "Sample 4: Public Altercation Struck with Hand",
        "narrative": "Following an argument at a public place, the accused allegedly struck the complainant with their hand, causing physical injuries. The complainant received medical treatment and subsequently lodged a police complaint. A medical report documented the injuries, and witnesses provided statements regarding the incident. The prosecution alleged that the accused had intentionally caused bodily pain to the complainant.",
        "expected_ipc": "Section 323",
        "expected_bns": "Section 115",
        "expected_charge": "Voluntarily Causing Hurt"
    },
    {
        "id": "TEST005_INTIMIDATION",
        "title": "Sample 5: Financial Dispute Serious Harm Threats",
        "narrative": "The accused allegedly threatened the complainant with serious physical harm during a dispute over a financial transaction. The complainant claimed that the threats were intended to create fear and prevent them from pursuing legal action to recover the money. The complainant submitted messages containing the alleged threats to the police. The prosecution alleged that the accused had threatened injury to the complainant's person with the intention of causing alarm.",
        "expected_ipc": "Section 506",
        "expected_bns": "Section 351",
        "expected_charge": "Criminal Intimidation"
    }
]

print("=" * 135)
print(f"{'#':<3} | {'Case Title':<46} | {'Top Article':<22} | {'Charge Head':<24} | {'JCI':<5} | {'Term':<16}")
print("-" * 135)

for i, c in enumerate(test_cases, 1):
    res = pipeline.run(c["narrative"])
    top = res.top_articles[0] if res.top_articles else None
    pred_sec = top.ipc_section if top else "None"
    charge_str = res.top_charges[0].charge_name[:24] if res.top_charges else "None"
    jci_str = f"{res.judicial_audit.final_jci_score:.1f}"
    term_str = res.penalty_prediction.predicted_tier[:16] if res.penalty_prediction else "None"
    
    print(f"{i:<3} | {c['title']:<46} | {pred_sec:<22} | {charge_str:<24} | {jci_str:<5} | {term_str:<16}")

print("=" * 135)
