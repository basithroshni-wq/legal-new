"""
Dedicated Verification Suite for User Scenarios:
1. Loan Application Document Forgery & False Presentation (IPC 468, 471, 420 / BNS 336(3), 340(2), 318(4))
2. Fenced Boundary Intrusion & Criminal Trespass with Intimidation (IPC 447, 506 / BNS 329(3), 351)
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

cases = [
    {
        "id": "CASE_FORGERY_01",
        "title": "Scenario 1: Loan Application False Document & Forged Signature",
        "narrative": "The accused allegedly created a false property document by imitating the signature of the lawful owner. The document was subsequently presented to a financial institution to support a loan application. During verification, the institution discovered discrepancies in the signature and contacted the property owner, who denied signing the document.",
        "expected_ipc": "Section 468",
        "expected_bns": "Section 336(3)",
        "expected_charge": "Forgery & Counterfeiting"
    },
    {
        "id": "CASE_TRESPASS_02",
        "title": "Scenario 2: Fenced Boundary Intrusion & Criminal Intimidation",
        "narrative": "The accused allegedly entered the complainant's fenced property without permission and remained there despite being instructed to leave. Evidence from witnesses indicated that the accused had entered the property with the intention of intimidating the owner during an ongoing boundary dispute. The owner subsequently filed a police complaint.",
        "expected_ipc": "Section 447",
        "expected_bns": "Section 329(3)",
        "expected_charge": "Criminal Trespass & Intimidation"
    },
    {
        "id": "CASE_FORGERY_02",
        "title": "Variant 1B: Fabricated Deed Used as Genuine for Bank Credit",
        "narrative": "The accused manufactured a fabricated sale deed by forging the signatures of the true title holder and submitted the counterfeit deed to a cooperative bank as collateral to secure a business credit line. The fraud was uncovered before disbursement.",
        "expected_ipc": "Section 468",
        "expected_bns": "Section 336(3)",
        "expected_charge": "Forgery & Counterfeiting"
    },
    {
        "id": "CASE_TRESPASS_03",
        "title": "Variant 2B: Unlawful Compound Trespass to Threaten Owner",
        "narrative": "During a contentious property line dispute, the accused jumped the perimeter wall of the complainant's residential compound without authorization and refused to vacate, issuing verbal threats to intimidate the homeowner into surrendering land.",
        "expected_ipc": "Section 447",
        "expected_bns": "Section 329(3)",
        "expected_charge": "Criminal Trespass & Intimidation"
    },
    {
        "id": "CASE_CBT_CLERK_04",
        "title": "Scenario 3: Employee Customer Payments CBT",
        "narrative": "An employee of a commercial establishment was entrusted with collecting payments from customers and depositing the amounts into the company's bank account. An internal audit allegedly revealed that some collected payments had been transferred to the employee's personal account. The company submitted financial records and transaction statements to the police.",
        "expected_ipc": "Section 408",
        "expected_bns": "Section 316(4)",
        "expected_charge": "Criminal Breach of Trust by Clerk or Servant"
    },
    {
        "id": "CASE_NEGLIGENT_DEATH_05",
        "title": "Scenario 4: Excessive Speed Driver Pedestrian Death",
        "narrative": "A driver allegedly drove a vehicle at excessive speed in a crowded area and struck a pedestrian while failing to exercise reasonable care. The pedestrian sustained serious injuries and later died in hospital. Witness statements and vehicle inspection records were collected to determine whether the driver's conduct amounted to criminal negligence.",
        "expected_ipc": "Section 304A",
        "expected_bns": "Section 106",
        "expected_charge": "Causing Death by Negligence"
    },
    {
        "id": "CASE_SEXUAL_HARASSMENT_06",
        "title": "Scenario 5: Colleague Unwelcome Sexual Remarks & Demands",
        "narrative": "A woman alleged that a colleague repeatedly made unwelcome sexual remarks and demands despite her objections. She submitted messages and identified witnesses who had observed some of the incidents. The complaint was investigated to determine whether the alleged conduct satisfied the legal definition of sexual harassment.",
        "expected_ipc": "Section 354A",
        "expected_bns": "Section 75",
        "expected_charge": "Sexual Harassment"
    }
]

print("=" * 115)
print(f"{'#':<3} | {'Case Title':<46} | {'Top Article':<22} | {'Charge Head':<24} | {'JCI':<5} | {'Status'}")
print("-" * 115)

for i, c in enumerate(cases, 1):
    res = pipeline.run(c["narrative"])
    top = res.top_articles[0] if res.top_articles else None
    pred_sec = top.ipc_section if top else "None"
    charge_str = res.top_charges[0].charge_name[:24] if res.top_charges else "None"
    jci_str = f"{res.judicial_audit.final_jci_score:.1f}"
    
    passed = (c["expected_ipc"].lower() in pred_sec.lower()) or (top and "471" in top.ipc_section and "468" in c["expected_ipc"])
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{i:<3} | {c['title']:<46} | {pred_sec:<22} | {charge_str:<24} | {jci_str:<5} | {status}")

print("=" * 115)
