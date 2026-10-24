"""
Evaluation Script for Roadside Extortion & Robbery Scenarios (Section 390 / Section 392 IPC & BNS 309(4)).
Tests cases where victims are stopped and forced to surrender property under threat of instant harm.
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
        "id": "CASE_USER_01",
        "title": "User Scenario: Road Stoppage & Belongings Surrender",
        "narrative": "The accused allegedly stopped the complainant on a public road and threatened to cause immediate physical harm unless the complainant handed over a mobile phone and wallet. Fearing the threat, the complainant surrendered the belongings. The accused escaped with the property, and the complainant subsequently reported the incident to the police.",
        "expected_ipc": "Section 392",
        "expected_bns": "Section 309(4)",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },
    {
        "id": "CASE_EXT_02",
        "title": "Night Alleyway Cash & Watch Extortion",
        "narrative": "The accused intercepted a pedestrian in an alleyway late at night and threatened immediate physical violence unless he surrendered his wallet containing Rs 4,500 and his gold watch. In fear of instant injury, the complainant handed over the valuables, and the accused fled into the dark.",
        "expected_ipc": "Section 392",
        "expected_bns": "Section 309(4)",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },
    {
        "id": "CASE_EXT_03",
        "title": "Highway Scooter Interception & Laptop Bag Robbery",
        "narrative": "While the victim was riding his two-wheeler along the national highway, the accused forced him to stop by blocking the road and threatened to cause immediate physical harm unless the rider surrendered his laptop bag and cash. Fearing imminent injury, the rider relinquished his bag, and the accused sped away on a motorcycle.",
        "expected_ipc": "Section 392",
        "expected_bns": "Section 309(4)",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },
    {
        "id": "CASE_EXT_04",
        "title": "ATM Vestibule Immediate Hurt Threat",
        "narrative": "Immediately after withdrawing cash from an ATM kiosk, the complainant was confronted by the accused who threatened immediate physical harm unless the cash was handed over. Due to fear of violence, the complainant gave up Rs 10,000, and the accused ran away with the money.",
        "expected_ipc": "Section 392",
        "expected_bns": "Section 309(4)",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },
    {
        "id": "CASE_EXT_05",
        "title": "Bus Stop Smartphone Stoppage",
        "narrative": "At an isolated suburban bus stop, the accused stopped a college student and threatened instant bodily hurt unless he surrendered his smartphone. Fearing immediate harm, the student parted with his mobile phone, and the accused made off with the property.",
        "expected_ipc": "Section 392",
        "expected_bns": "Section 309(4)",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },
    {
        "id": "CASE_EXT_06",
        "title": "Adversarial: Victim Unharmed & No Weapon",
        "narrative": "The accused stopped the complainant on a road and threatened to cause immediate physical harm unless the complainant handed over his leather purse. Fearing the threat, the complainant surrendered the purse. The accused escaped with the property. The complainant was completely unarmed and unharmed, and no weapon was recovered from the accused.",
        "expected_ipc": "Section 392",
        "expected_bns": "Section 309(4)",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },
    {
        "id": "CASE_EXT_07",
        "title": "Two Assailants Joint Roadside Extortion",
        "narrative": "Two accused persons stopped the complainant on a quiet street and threatened to inflict immediate physical harm unless he parted with his mobile phone and cash. Fearing violence, the complainant surrendered his phone and wallet to the assailants, who both fled the scene together with the property.",
        "expected_ipc": "Section 392",
        "expected_bns": "Section 309(4)",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    }
]

print("=" * 115)
print(f"{'#':<3} | {'Case Title':<46} | {'Predicted Provision':<24} | {'Conf':<8} | {'Tier':<14} | {'JCI':<5} | {'Status'}")
print("-" * 115)

for i, c in enumerate(test_cases, 1):
    res = pipeline.run(c["narrative"])
    top = res.top_articles[0] if res.top_articles else None
    pred_sec = top.ipc_section if top else "None"
    prob_str = f"{top.calibrated_probability*100:.1f}%" if top else "N/A"
    tier_str = res.penalty_prediction.predicted_tier[:14] if res.penalty_prediction else "N/A"
    jci_str = f"{res.judicial_audit.final_jci_score:.1f}"
    
    passed = (c["expected_ipc"].lower() in pred_sec.lower())
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{i:<3} | {c['title']:<46} | {pred_sec:<24} | {prob_str:<8} | {tier_str:<14} | {jci_str:<5} | {status}")

print("=" * 115)
