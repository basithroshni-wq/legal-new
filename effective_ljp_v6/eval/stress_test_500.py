"""
500-Case Comprehensive Multi-Category Benchmark & Stress Test for Effective LJP V6.
Evaluates the full neuro-symbolic pipeline across 20 distinct Indian Penal Jurisprudence categories:
1. Premeditated Murder (IPC 302 / BNS 103)
2. Sudden Fight Homicide (IPC 304 Part II / BNS 105)
3. Culpable Homicide Part I (IPC 304 Part I / BNS 105)
4. Attempt to Murder (IPC 307 / BNS 109)
5. Grievous Hurt by Dangerous Weapons (IPC 326 / BNS 118(2))
6. Simple Hurt by Dangerous Weapons (IPC 324 / BNS 118(1))
7. Simple Hurt Unarmed (IPC 323 / BNS 115(2))
8. Theft (IPC 379 / BNS 303(2))
9. Robbery (IPC 392 / BNS 309(4))
10. Dacoity (5+ persons) (IPC 395 / BNS 310(2))
11. Criminal Breach of Trust (IPC 406 / BNS 316(2))
12. Cheating & Financial Fraud (IPC 420 / BNS 318(4))
13. Forgery & Fabricated Documents (IPC 468/471 / BNS 336/340)
14. Rape & Sexual Offences (IPC 376 / BNS 64)
15. Matrimonial Cruelty (IPC 498A / BNS 85)
16. Dowry Death (IPC 304B / BNS 80)
17. Criminal Intimidation (IPC 506 / BNS 351)
18. Civil Commercial Dispute Quashing (Quashed u/s 482 CrPC / Section 528 BNSS)
19. Out-of-Domain Abstention (Non-Penal / External / OOD)
20. Adversarial Negation & Linguistic Edge Traps
"""

import sys
import os
import time
import json
from collections import defaultdict
from typing import List, Dict, Any

# Ensure parent directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from core.pipeline import EffectiveLjpPipeline


def generate_500_test_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    def add_c(cid: int, cat: str, exp: str, ood: bool, text: str):
        cases.append({
            "id": f"CASE_{cid:03d}",
            "category": cat,
            "expected_ipc": exp,
            "should_abstain": ood,
            "narrative": text.strip()
        })

    c_id = 1

    # =========================================================================
    # 1. Premeditated Murder (IPC 302 / BNS 103) (30 cases)
    # =========================================================================
    locs = ["Kozhikode", "Delhi", "Bengaluru", "Lucknow", "Jaipur", "Patna", "Kolkata", "Chennai", "Pune", "Bhopal"]
    for i in range(30):
        loc = locs[i % len(locs)]
        if i % 5 == 0:
            narr = f"In {loc}, nursing a decade-long land feud, the accused hid behind a concrete pillar with a sharp iron machete, ambushed the victim returning home at dusk, and hacked his neck multiple times, killing him on the spot."
        elif i % 5 == 1:
            narr = f"In {loc}, the accused hired two sharpshooters for Rs 5 lakhs. The shooters cornered the victim outside his commercial warehouse and pumped five bullets into his chest with country pistols, causing instant death."
        elif i % 5 == 2:
            narr = f"In {loc}, driven by an insurance conspiracy, the accused mixed lethal potassium cyanide into his uncle's bedtime tonic. The uncle consumed the poisoned beverage and died within minutes due to cardiac arrest."
        elif i % 5 == 3:
            narr = f"In an act of honor killing in {loc}, the father and brother strangled the 22-year-old victim with a nylon rope in her bedroom at midnight and disposed of her corpse in an open agricultural well."
        else:
            narr = f"In {loc}, harboring an old electoral grudge, the accused purchased a heavy iron crowbar, waited for the victim in an unlit alley, and crushed his skull with brutal repeated strikes, causing fatal craniocerebral damage."
        add_c(c_id, "Premeditated Murder", "Section 302", False, narr)
        c_id += 1

    # =========================================================================
    # 2. Sudden Fight Homicide (IPC 304 Part II / BNS 105) (30 cases)
    # =========================================================================
    venues = ["tea stall", "roadside dhaba", "bus terminus", "ration queue", "market square", "cricket ground"]
    for i in range(30):
        venue = venues[i % len(venues)]
        if i % 3 == 0:
            narr = f"A heated argument broke out at a {venue} over Rs 20 change. Without any premeditation, in a sudden fight, the accused picked up a wooden stick from a stall and struck the deceased once on the head, causing him to collapse and die later."
        elif i % 3 == 1:
            narr = f"During a card game in a village shed, a sudden quarrel erupted over cheating allegations. In the heat of passion without premeditation, the accused shoved the deceased hard into a stone pillar, causing a fatal skull injury."
        else:
            narr = f"At a local {venue}, a verbal brawl escalated between neighbors over parking space. Acting in the heat of the moment without prior grudge, the accused grabbed a bamboo stave and dealt a blow to the deceased's parietal region, resulting in death."
        add_c(c_id, "Sudden Fight Homicide (Exception 4)", "Section 304 Part II", False, narr)
        c_id += 1

    # =========================================================================
    # 3. Culpable Homicide Part I (IPC 304 Part I / BNS 105) (25 cases)
    # =========================================================================
    for i in range(25):
        if i % 2 == 0:
            narr = f"Returning home unexpectedly, the accused discovered his spouse in a compromising posture with another man. Deprived of self-control due to grave and sudden provocation, he snatched a scythe from the kitchen and inflicted lethal wounds on the intruder."
        else:
            narr = f"The complainant and his friends attacked the accused's brother with sticks. Under extreme provocation and exceeding his right of private defense, the accused grabbed an axe from the woodpile and struck the primary aggressor, causing fatal lacerations."
        add_c(c_id, "Culpable Homicide Part I (Provocation/Defense)", "Section 304 Part I", False, narr)
        c_id += 1

    # =========================================================================
    # 4. Attempt to Murder (IPC 307 / BNS 109) (30 cases)
    # =========================================================================
    for i in range(30):
        if i % 3 == 0:
            narr = f"Intending to murder his business rival, the accused pointed a loaded revolver at his chest from point-blank range and pulled the trigger. The bullet perforated the victim's left lung, but he survived following an emergency 8-hour cardiothoracic surgery."
        elif i % 3 == 1:
            narr = f"The assailant ambushed the victim in a staircase with intent to kill and slashed his throat with an open surgical razor. The victim collapsed in a pool of blood but survived after undergoing immediate emergency tracheostomy and blood transfusions."
        else:
            narr = f"With clear intention to murder, the accused pushed the victim off a third-floor residential terrace while shouting threats to finish him off. The victim sustained multiple spinal fractures and internal hemorrhaging but survived after intensive hospital care."
        add_c(c_id, "Attempt to Murder", "Section 307", False, narr)
        c_id += 1

    # =========================================================================
    # 5. Grievous Hurt by Dangerous Weapons (IPC 326 / BNS 118(2)) (30 cases)
    # =========================================================================
    for i in range(30):
        if i % 3 == 0:
            narr = f"During a boundary altercation, the accused attacked the victim with a heavy iron rod, repeatedly hitting his right forearm and knee, resulting in compound comminuted fractures of the ulna and permanent impairment of the limb."
        elif i % 3 == 1:
            narr = f"Following an altercation outside a cinema hall, the accused threw concentrated industrial sulphuric acid directly onto the victim's face, causing full-thickness third-degree chemical burns, loss of vision in the left eye, and permanent facial disfigurement."
        else:
            narr = f"The assailant pulled out a curved meat cleaver and chopped at the complainant's legs during a market dispute, fracturing both fibulae and severing the tibial tendon, leaving the victim permanently crippled."
        add_c(c_id, "Grievous Hurt by Dangerous Weapons", "Section 326", False, narr)
        c_id += 1

    # =========================================================================
    # 6. Simple Hurt by Dangerous Weapons (IPC 324 / BNS 118(1)) (25 cases)
    # =========================================================================
    for i in range(25):
        if i % 2 == 0:
            narr = f"During a minor altercation outside a tea stall, the accused swung a small penknife, causing a superficial 2 cm cut across the complainant's forearm. The injury was treated with topical dressing without bone involvement or grievous harm."
        else:
            narr = f"In a neighborhood spat, the accused threw an iron bicycle chain at the complainant, causing minor skin bruises and a superficial laceration on his shoulder without any fracture or permanent privation."
        add_c(c_id, "Simple Hurt by Dangerous Weapons", "Section 324", False, narr)
        c_id += 1

    # =========================================================================
    # 7. Simple Hurt Unarmed (IPC 323 / BNS 115(2)) (25 cases)
    # =========================================================================
    for i in range(25):
        if i % 2 == 0:
            narr = f"In a disagreement over bus ticketing, the passenger engaged in a heated argument with the conductor, repeatedly slapped him across the face, and kicked his shins, causing bodily pain and minor contusions without any weapons used."
        else:
            narr = f"During a verbal altercation in a residential housing society, the accused pushed the resident to the tarmac and delivered several fist blows to his shoulders, causing temporary soreness and swelling without any skeletal fracture."
        add_c(c_id, "Simple Hurt (Unarmed)", "Section 323", False, narr)
        c_id += 1

    # =========================================================================
    # 8. Theft (IPC 379 / BNS 303(2)) (30 cases)
    # =========================================================================
    items = ["leather wallet", "smart mobile phone", "gold necklace", "laptop backpack", "wrist watch"]
    for i in range(30):
        item = items[i % len(items)]
        if i % 3 == 0:
            narr = f"On a crowded suburban railway platform, the accused carefully slid his hand into the commuter's back pocket, slipped away with his {item} containing Rs 12,000 without consent, and vanished into the crowd without employing any force."
        elif i % 3 == 1:
            narr = f"While the shopkeeper was busy attending to customers, the accused quietly opened the glass showcase, took a {item} valued at Rs 45,000, concealed it in his jacket, and exited the store without making payment."
        else:
            narr = f"The complainant had parked his motorcycle outside a temple. The accused broke the handlebar lock with a master key, started the vehicle dishonestly, and drove away with the motorcycle without the owner's knowledge or consent."
        add_c(c_id, "Theft (IPC 379)", "Section 379", False, narr)
        c_id += 1

    # =========================================================================
    # 9. Robbery (IPC 392 / BNS 309(4)) (30 cases)
    # =========================================================================
    for i in range(30):
        if i % 3 == 0:
            narr = f"While the victim was walking home on an isolated service road at 10 PM, two men intercepted him on a motorbike. One held a sharp knife against his neck threatening to stab him while the other forcibly snatched his wallet, smartphone, and gold ring."
        elif i % 3 == 1:
            narr = f"Inside an isolated bank ATM kiosk, the accused grabbed the customer from behind, slammed his head against the glass partition, and forcibly took Rs 25,000 cash which the customer had just withdrawn, fleeing on a two-wheeler."
        else:
            narr = f"Three assailants cornered a commuter near a dark subway underpass. Threatening to slit his throat with an iron blade, they physically restrained him and forcefully stripped him of his wristwatch and cash bag before fleeing."
        add_c(c_id, "Robbery (IPC 392)", "Section 392", False, narr)
        c_id += 1

    # =========================================================================
    # 10. Dacoity (5+ persons) (IPC 395 / BNS 310(2)) (25 cases)
    # =========================================================================
    for i in range(25):
        if i % 2 == 0:
            narr = f"A gang of seven armed robbers stormed a nationalized bank branch in Muzaffarpur during morning business hours. Holding the cashier and customers at gunpoint with revolvers, they conjointly looted Rs 42 lakhs from the cash vault and escaped in a getaway van."
        else:
            narr = f"Six masked dacoits armed with country pistols and iron choppers intercepted a highway passenger bus in Morena. They conjointly threatened the driver, held the passengers hostage, and looted gold jewelry and cash worth Rs 15 lakhs from everyone on board."
        add_c(c_id, "Dacoity (IPC 395)", "Section 395", False, narr)
        c_id += 1

    # =========================================================================
    # 11. Criminal Breach of Trust (IPC 406 / BNS 316(2)) (25 cases)
    # =========================================================================
    for i in range(25):
        if i % 2 == 0:
            narr = f"The accused was appointed as the chief custodian of a commercial cold storage facility in Indore. Having been legally entrusted with 500 metric tons of imported spices worth Rs 3 crores, he dishonestly sold the goods to private merchants and misappropriated the funds."
        else:
            narr = f"The complainant entrusted Rs 15 lakhs in cash to his verified logistics dispatch manager for official custom duty clearance. The manager dishonestly converted the entire entrusted funds to his personal account and absconded."
        add_c(c_id, "Criminal Breach of Trust", "Section 406", False, narr)
        c_id += 1

    # =========================================================================
    # 12. Cheating & Financial Fraud (IPC 420 / BNS 318(4)) (30 cases)
    # =========================================================================
    for i in range(30):
        if i % 3 == 0:
            narr = f"The accused floated a bogus cryptocurrency arbitrage enterprise promising a guaranteed return of 25% per month. Displaying fabricated government approvals, he dishonestly induced 80 investors to deposit Rs 4.5 crores before shutting the website and absconding."
        elif i % 3 == 1:
            narr = f"Operating a fake overseas recruitment agency in Chandigarh, the accused collected Rs 2.5 lakhs each from 45 unemployed youths by providing bogus visa stamping and fabricated work permits for Canadian healthcare facilities, having had fraudulent intent from inception."
        else:
            narr = f"A rogue real estate builder created fake allotment brochures and booking receipts for a non-existent residential tower. He dishonestly induced 15 buyers to transfer Rs 2 crores as advance deposits and diverted the money to personal offshore shell entities."
        add_c(c_id, "Cheating & Financial Fraud", "Section 420", False, narr)
        c_id += 1

    # =========================================================================
    # 13. Forgery & Fabricated Documents (IPC 468 / BNS 336(3)) (25 cases)
    # =========================================================================
    for i in range(25):
        if i % 2 == 0:
            narr = f"To usurp prime commercial real estate, the accused fabricated a bogus registered deed of sale by forging the signatures of the rightful owner and appending counterfeit sub-registrar seals, using the forged document to fraudulently obtain a bank mortgage."
        else:
            narr = f"The accused forged the testamentary will of his late uncle, faking the signatures of two deceased attesting witnesses on non-judicial stamp paper, and dishonestly produced it before the revenue tehsildar to mutated property in his name."
        add_c(c_id, "Forgery & False Documents", "Section 468", False, narr)
        c_id += 1

    # =========================================================================
    # 14. Rape & Sexual Offences (IPC 376 / BNS 64) (20 cases)
    # =========================================================================
    for i in range(20):
        narr = f"The accused lured the victim to an isolated farmhouse on the pretext of offering an interview. He locked the entry doors, threatened her with physical harm, and forcibly subjected her to non-consensual sexual intercourse against her will."
        add_c(c_id, "Rape & Sexual Offences", "Section 376", False, narr)
        c_id += 1

    # =========================================================================
    # 15. Matrimonial Cruelty (IPC 498A / BNS 85) (25 cases)
    # =========================================================================
    for i in range(25):
        if i % 2 == 0:
            narr = f"Following three years of marriage, the husband and his parents continually subjected the complainant to physical thrashing and verbal torture, demanding an additional Rs 10 lakhs and a luxury sedan from her maternal relatives. No fatal injury occurred."
        else:
            narr = f"The in-laws and husband locked the complainant in an unventilated storeroom, denied her meals, and subjected her to relentless psychological and physical cruelty over unmet gold jewelry demands, driving her to severe mental depression."
        add_c(c_id, "Matrimonial Cruelty (IPC 498A)", "Section 498A", False, narr)
        c_id += 1

    # =========================================================================
    # 16. Dowry Death (IPC 304B / BNS 80) (25 cases)
    # =========================================================================
    years = [1, 2, 3, 4, 5]
    for i in range(25):
        yr = years[i % len(years)]
        if i % 2 == 0:
            narr = f"Within {yr} years of marriage, the 24-year-old victim died of extensive 90% kerosene burn injuries in her matrimonial home. The record proved that soon before her death, she was continuously harassed and assaulted by her husband for an unpaid dowry of Rs 5 lakhs."
        else:
            narr = f"The victim died under abnormal circumstances due to organophosphorus pesticide poisoning within {yr} years of marriage. Evidence revealed persistent physical violence and dowry demands for a four-wheeler by her husband and mother-in-law leading up to the tragedy."
        add_c(c_id, "Dowry Death (IPC 304B)", "Section 304B", False, narr)
        c_id += 1

    # =========================================================================
    # 17. Criminal Intimidation (IPC 506 / BNS 351) (20 cases)
    # =========================================================================
    for i in range(20):
        if i % 2 == 0:
            narr = f"The accused walked into the shopkeeper's premises, brandished an iron revolver, and issued direct death threats stating he would blow his head off if extortion protection money of Rs 50,000 was not handed over by morning, without inflicting any physical hurt."
        else:
            narr = f"Harboring enmity over an election loss, the accused intercepted the complainant on the street, hurled violent verbal abuses, and threatened to set his house on fire and kill his family members if he testified in court."
        add_c(c_id, "Criminal Intimidation (IPC 506)", "Section 506", False, narr)
        c_id += 1

    # =========================================================================
    # 18. Civil Commercial Dispute Quashing (Quashed u/s 482 CrPC) (20 cases)
    # =========================================================================
    for i in range(20):
        if i % 2 == 0:
            narr = f"The complainant company entered into an enterprise software service level agreement with the vendor. Due to delayed deployment of milestone modules, invoices worth Rs 18 lakhs remained unpaid. The complainant filed a criminal complaint of cheating under Section 420."
        else:
            narr = f"A tenancy lease agreement expired after 3 years. The tenant delayed vacating the premises by two months while rent reconciliation was underway. The landlord filed an FIR alleging criminal breach of trust and cheating."
        add_c(c_id, "Civil Dispute (Quashable)", "Quashed u/s 482 CrPC", False, narr)
        c_id += 1

    # =========================================================================
    # 19. Out-of-Domain Abstention (25 cases)
    # =========================================================================
    ood_texts = [
        "A deep depression over the east-central Bay of Bengal has intensified into a severe cyclonic storm with wind speeds touching 120 kmph. Heavy to very heavy rainfall is forecasted for coastal Odisha and Andhra Pradesh over the next 48 hours.",
        "The synthesis of chiral ruthenium complexes was performed using asymmetric hydrogenation catalysis. Spectroscopic NMR analysis confirmed enantiomeric excess exceeding 98% with optimal thermodynamic yield.",
        "The Indian national cricket team secured a thrilling four-wicket victory against Australia in the final over of the World Test Championship at Lord's, powered by a masterclass century.",
        "To bake a traditional sourdough loaf, mix 500g of unbleached bread flour with 350ml water and 100g of active levain. Allow autolyse for 45 minutes before folding and bulk fermentation.",
        "The quarterly financial report indicated a 14% year-on-year growth in net cloud revenues, driven by enterprise AI deployments and expanding data center infrastructure across the Asia-Pacific corridor."
    ]
    for i in range(25):
        txt = ood_texts[i % len(ood_texts)]
        add_c(c_id, "Out-of-Domain Abstention", "Out of Domain / Non-Penal", True, txt)
        c_id += 1

    # =========================================================================
    # 20. Adversarial Negations & Linguistic Stress Traps (35 cases)
    # =========================================================================
    traps = [
        # (narrative, expected_ipc)
        ("The accused was charged with murder, but the post-mortem report conclusively established that the victim died of natural myocardial infarction with no external marks of violence or poison.", "Quashed u/s 482 CrPC"),
        ("During a property partition dispute, the accused merely slapped his cousin once across the face. He did NOT use any weapon, did not cause any fracture, and did not intend to kill him.", "Section 323"),
        ("The victim sustained a grazing scratch on his forearm from a broken pocketknife during a street scuffle, without any bone involvement, fracture, or grievous injury.", "Section 324"),
        ("The accused slipped his hand into the victim's jacket pocket on a crowded bus and took his leather wallet, walking away quietly without using any force, weapon, or threats.", "Section 379"),
        ("The complainant alleged that the accused murdered his father, but the FIR and evidence reveal the accused merely forged a municipal title deed on stamp paper to mutate agricultural land.", "Section 468"),
        ("A sudden fight occurred in a tea stall over a sports bet without any premeditation or prior grudge, wherein the accused grabbed a wooden stool and struck the deceased once on the head.", "Section 304 Part II"),
        ("The husband and in-laws harassed the complainant for Rs 3 lakhs dowry over 4 years of marriage. She left the matrimonial home and lodged a complaint. No fatal injury occurred.", "Section 498A"),
        ("The accused pointed a country pistol at the businessman's chest and pulled the trigger with intent to kill. The victim sustained a perforated lung but survived following emergency cardiothoracic surgery.", "Section 307"),
        ("The accused struck the complainant with an iron crowbar during an argument, causing a compound fracture of both radius and ulna and permanent disability of the left arm.", "Section 326"),
        ("The accused threatened to shoot the shopkeeper if he did not pay Rs 50,000 monthly protection money. He fired no shots and inflicted zero physical injury.", "Section 506"),
    ]
    for i in range(35):
        t_narr, t_exp = traps[i % len(traps)]
        add_c(c_id, "Adversarial & Negation Stress Trap", t_exp, False, t_narr)
        c_id += 1

    return cases


def run_stress_test_500():
    print("=" * 105)
    print("🔥 EXECUTING 500-CASE COMPREHENSIVE MULTI-CATEGORY BENCHMARK (EFFECTIVE LJP V6)")
    print("=" * 105)

    pipeline = EffectiveLjpPipeline()
    cases = generate_500_test_cases()
    total = len(cases)

    category_stats = defaultdict(lambda: {"total": 0, "passed": 0})
    failures = []
    latencies = []

    t0 = time.time()

    for idx, c in enumerate(cases, 1):
        cat = c["category"]
        category_stats[cat]["total"] += 1

        case_start = time.perf_counter()
        res = pipeline.run(c["narrative"])
        case_dur = (time.perf_counter() - case_start) * 1000
        latencies.append(case_dur)

        is_passed = False

        if c["should_abstain"]:
            if res.is_abstained:
                is_passed = True
            else:
                failures.append({
                    "id": c["id"],
                    "category": cat,
                    "narrative": c["narrative"][:80] + "...",
                    "expected": "Out-of-Domain Abstention",
                    "predicted": res.top_articles[0].ipc_section if res.top_articles else "No Article",
                    "diagnostics": ["Failed to trigger out-of-domain classifier"]
                })
        else:
            if res.is_abstained:
                failures.append({
                    "id": c["id"],
                    "category": cat,
                    "narrative": c["narrative"][:80] + "...",
                    "expected": c["expected_ipc"],
                    "predicted": "ABSTAINED (False Positive)",
                    "diagnostics": [f"Pipeline falsely abstained: {res.abstain_message}"]
                })
            elif not res.top_articles:
                failures.append({
                    "id": c["id"],
                    "category": cat,
                    "narrative": c["narrative"][:80] + "...",
                    "expected": c["expected_ipc"],
                    "predicted": "NO PREDICTIONS",
                    "diagnostics": ["No articles survived gating and prediction"]
                })
            else:
                top_art = res.top_articles[0]
                pred_sec = top_art.ipc_section

                exp_clean = c["expected_ipc"].lower().replace("section ", "").strip()
                pred_clean = pred_sec.lower().replace("section ", "").strip()

                if exp_clean in pred_clean or pred_clean in exp_clean:
                    is_passed = True
                elif "quash" in exp_clean and "quash" in pred_clean:
                    is_passed = True
                elif "304 part i" in exp_clean and "304 part i" in pred_clean:
                    is_passed = True
                elif "304 part ii" in exp_clean and "304 part ii" in pred_clean:
                    is_passed = True
                elif ("468" in exp_clean or "471" in exp_clean) and ("468" in pred_clean or "471" in pred_clean):
                    is_passed = True
                else:
                    failures.append({
                        "id": c["id"],
                        "category": cat,
                        "narrative": c["narrative"][:80] + "...",
                        "expected": c["expected_ipc"],
                        "predicted": pred_sec,
                        "diagnostics": [f"Mismatch: Top article {pred_sec} did not match expected {c['expected_ipc']}"]
                    })

        if is_passed:
            category_stats[cat]["passed"] += 1

        if idx % 100 == 0 or idx == total:
            elapsed = time.time() - t0
            passed_so_far = sum(s["passed"] for s in category_stats.values())
            print(f"[{idx:>3}/{total}] Processed... Passed: {passed_so_far}/{idx} ({(passed_so_far/idx)*100:.1f}%) | Time: {elapsed:.2f}s")

    total_time = time.time() - t0
    passed_count = sum(s["passed"] for s in category_stats.values())
    accuracy = (passed_count / total) * 100
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    print("-" * 105)
    print("📊 500-CASE EVALUATION RESULTS:")
    print(f"• Total Evaluated Cases:   {total}")
    print(f"• Total Passed:            {passed_count}")
    print(f"• Total Failed:            {len(failures)}")
    print(f"• Overall Pass Rate:       {accuracy:.2f}%")
    print(f"• Total Evaluation Time:   {total_time:.2f} seconds")
    print(f"• Average Latency / Case:  {avg_latency:.2f} ms\n")

    print(f"{'Category':<44} | {'Total':<6} | {'Passed':<6} | {'Accuracy'}")
    print("-" * 75)
    for cat, stats in sorted(category_stats.items()):
        cat_acc = (stats["passed"] / max(1, stats["total"])) * 100
        print(f"{cat:<44} | {stats['total']:<6} | {stats['passed']:<6} | {cat_acc:.1f}%")

    if failures:
        print("\n" + "=" * 105)
        print(f"⚠️ DETAILED DIAGNOSTIC LOG OF FAILED CASES ({len(failures)} ISSUES FOUND):")
        print("=" * 105)
        for f in failures[:15]:
            print(f"[{f['id']}] {f['category']}")
            print(f"  Narrative: {f['narrative']}")
            print(f"  Expected:  {f['expected']}  -->  Predicted: {f['predicted']}")
            print(f"  Issues Identified: {', '.join(f['diagnostics'])}\n")
        if len(failures) > 15:
            print(f"... and {len(failures) - 15} more failures.")
    else:
        print("\n✅ PERFECT SCORE: 100.0% Pass Rate across all 500 cases in all categories!")

    return {
        "total": total,
        "passed": passed_count,
        "accuracy": accuracy,
        "failures": failures,
        "category_stats": dict(category_stats),
        "total_time": total_time,
        "avg_latency": avg_latency
    }


if __name__ == "__main__":
    run_stress_test_500()
