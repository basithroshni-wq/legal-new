"""
=========================================================================================================
⚖️ 35-CASE RIGOROUS ACCURACY EVALUATION SUITE FOR EFFECTIVE LJP V6
=========================================================================================================
Evaluates 35 distinct statutory, adversarial, property, violent, matrimonial, and civil scenarios:
- 1-2:   Theft (IPC 379 / BNS 303)
- 3-4:   Robbery (IPC 392 / BNS 309)
- 5-6:   Dacoity (IPC 395 / BNS 310)
- 7-9:   Premeditated Murder (IPC 302 / BNS 103(1))
- 10-12: Sudden Fight Homicide - Exception 4 (IPC 304 Part II / BNS 105)
- 13-14: Culpable Homicide Not Murder - Part I (IPC 304 Part I / BNS 105)
- 15-16: Attempt to Murder (IPC 307 / BNS 109)
- 17-18: Grievous Hurt by Dangerous Weapons (IPC 326 / BNS 118(2))
- 19-20: Simple Hurt by Dangerous Weapons (IPC 324 / BNS 118(1))
- 21-22: Simple Hurt Unarmed (IPC 323 / BNS 115)
- 23-24: Cheating & Financial Fraud (IPC 420 / BNS 318)
- 25-26: Forgery & Fake Documents (IPC 468 / BNS 336)
- 27-28: Criminal Breach of Trust (IPC 406 / BNS 316)
- 29-30: Dowry Death (IPC 304B / BNS 80)
- 31-32: Matrimonial Cruelty (IPC 498A / BNS 85)
- 33-34: Criminal Intimidation (IPC 506 / BNS 351)
- 35:    Civil Dispute Quashing (Quashed u/s 482 CrPC / s.528 BNSS)
=========================================================================================================
"""

import sys
import os
import time
from typing import List, Dict, Any

# Ensure UTF-8 printing on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.pipeline import EffectiveLjpPipeline

CASES_35 = [
    # 1-2: Simple Theft (IPC 379 / BNS 303)
    {
        "id": "CASE_01",
        "category": "Theft",
        "name": "Suburban Train Pickpocketing",
        "narrative": "A commuter was traveling on a crowded suburban train in Thrissur when the accused secretly slid his hand into the victim's trouser pocket and slipped away with his leather wallet containing Rs 8,500 in cash without the commuter's knowledge or consent. No weapon was brandished and no physical violence was exerted.",
        "expected_section": "Section 379",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },
    {
        "id": "CASE_02",
        "category": "Theft",
        "name": "Electronics Store Shoplifting",
        "narrative": "The accused entered an electronics retail store as a customer, discreetly removed two high-end wireless headphones from the display shelf, concealed them inside his backpack, and walked out without paying. No store staff were confronted, and no force or threats were used.",
        "expected_section": "Section 379",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },

    # 3-4: Robbery (IPC 392 / BNS 309)
    {
        "id": "CASE_03",
        "category": "Robbery",
        "name": "Knifepoint Highway Extortion",
        "narrative": "The accused intercepted a lone motorcyclist on a dark bypass road near Aluva at midnight, held a sharp dagger against the victim's throat, and demanded all his cash and gold ring under threat of instant death. The victim handed over Rs 12,000 out of acute fear.",
        "expected_section": "Section 392",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },
    {
        "id": "CASE_04",
        "category": "Robbery",
        "name": "ATM Cabin Violent Mugging",
        "narrative": "As a customer was withdrawing cash inside an ATM kiosk, the assailant barged in armed with an iron wrench, slammed the victim against the glass wall, pinned him down by the neck, and forcibly took the Rs 20,000 withdrawn from the cash dispenser before fleeing.",
        "expected_section": "Section 392",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },

    # 5-6: Dacoity (IPC 395 / BNS 310)
    {
        "id": "CASE_05",
        "category": "Dacoity",
        "name": "Highway Cash Transit Heist",
        "narrative": "A gang of six masked dacoits armed with iron rods, country revolvers, and swords intercepted a bank cash transit vehicle on the interstate highway, overpowered the security guards at gunpoint, broke the rear lock, and looted Rs 45 lakhs in currency notes conjointly.",
        "expected_section": "Section 395",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },
    {
        "id": "CASE_06",
        "category": "Dacoity",
        "name": "Jewelry Showroom Gang Raid",
        "narrative": "Seven armed robbers stormed a jewelry showroom in Kozhikode wielding pistols and machetes. While two men held the staff hostage at gunpoint, the other five smashed the glass showcases and conjointly looted gold ornaments worth over Rs 80 lakhs before escaping in an SUV.",
        "expected_section": "Section 395",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },

    # 7-9: Premeditated Murder (IPC 302 / BNS 103(1))
    {
        "id": "CASE_07",
        "category": "Premeditated Murder",
        "name": "Lying-in-Wait Ambush Axe Murder",
        "narrative": "Due to a bitter and long-standing ancestral boundary grudge, the accused purchased a heavy iron axe in advance, hid behind a thick rubber plantation near the deceased's usual path, and ambushed him from behind, inflicting five repeated deep chopping wounds to the neck and head until he died instantly.",
        "expected_section": "Section 302",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },
    {
        "id": "CASE_08",
        "category": "Premeditated Murder",
        "name": "Contract Shooting at Point-Blank Range",
        "narrative": "With premeditated malice to eliminate his business rival, the accused hired a shooter who brought an illegal country pistol, tailed the deceased into an underground parking lot, and fired three bullets directly into his chest and temple, causing instant demise. Autopsy confirmed fatal vital organ perforation.",
        "expected_section": "Section 302",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },
    {
        "id": "CASE_09",
        "category": "Premeditated Murder",
        "name": "Lethal Cyanide Poisoning",
        "narrative": "The accused planned the murder of his business partner to pocket company assets. He obtained potassium cyanide, lured the deceased to a hotel room under pretext of contract signing, and secretly mixed the lethal poison into his beverage. The deceased suffered convulsions and died within minutes.",
        "expected_section": "Section 302",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },

    # 10-12: Sudden Fight Homicide - Exception 4 (IPC 304 Part II / BNS 105)
    {
        "id": "CASE_10",
        "category": "Sudden Fight Homicide",
        "name": "Tea Stall Fare Quarrel",
        "narrative": "During a sudden unscripted argument in a roadside tea stall in Kakkanad over a 50 rupee auto fare dispute, hot words were exchanged. In the heat of passion, the accused grabbed a wooden stool lying on the dirt floor and struck the deceased once on the temple without premeditation. The deceased collapsed and succumbed to head trauma.",
        "expected_section": "Section 304 Part II",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },
    {
        "id": "CASE_11",
        "category": "Sudden Fight Homicide",
        "name": "Bar Room Impromptu Scuffle",
        "narrative": "Two patrons who had no prior enmity or animosity began shouting at each other after an accidental nudge in a crowded restaurant. In the sudden brawl that ensued in the heat of passion, the accused picked up an empty glass bottle from a nearby table and hit the deceased on the parietal skull, resulting in fatal intracranial hemorrhage.",
        "expected_section": "Section 304 Part II",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },
    {
        "id": "CASE_12",
        "category": "Sudden Fight Homicide",
        "name": "Village Well Irrigation Spat",
        "narrative": "While drawing water from a shared village well, an impromptu quarrel broke out between two farmers. Without any premeditation or prior planning, the accused in a sudden fit of rage pushed the deceased hard, causing his head to hit against the jagged concrete edge of the well. The victim died shortly after.",
        "expected_section": "Section 304 Part II",
        "expected_tier": "Tier 3 (7 to 10 Years)"
    },

    # 13-14: Culpable Homicide Not Murder - Part I (IPC 304 Part I / BNS 105)
    {
        "id": "CASE_13",
        "category": "Culpable Homicide Part I",
        "name": "Grave Provocation Private Defense Excess",
        "narrative": "The deceased aggressively trespassed into the accused's courtyard armed with a heavy stick and struck the accused's mother. In grave and sudden provocation and in excess of the right of private defence, the accused retaliated with a heavy lathi, inflicting severe blows that caused the deceased's death.",
        "expected_section": "Section 304 Part I",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },
    {
        "id": "CASE_14",
        "category": "Culpable Homicide Part I",
        "name": "Group Thrashing without Lethal Weapons",
        "narrative": "Three villagers caught a trespasser inside their orchard. Instead of calling police, they subjected him to a prolonged thrashing with bare hands and thin bamboo canes. Although there was no prior plan to kill him, the cumulative bodily trauma resulted in visceral shock and demise.",
        "expected_section": "Section 304 Part I",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },

    # 15-16: Attempt to Murder (IPC 307 / BNS 109)
    {
        "id": "CASE_15",
        "category": "Attempt to Murder",
        "name": "Vital Chest Gunshot (Victim Survived)",
        "narrative": "The accused aimed a loaded country revolver directly at the complainant's chest intending to cause his death and fired a shot. The bullet penetrated the left thoracic cavity, causing massive hemorrhage. The victim survived solely due to emergency open-heart surgery and vascular intervention at the medical college.",
        "expected_section": "Section 307",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },
    {
        "id": "CASE_16",
        "category": "Attempt to Murder",
        "name": "Terrace Push with Slit Attempt",
        "narrative": "The assailant ambushed the victim on a third-floor rooftop, slashed at her neck with a surgical scalpel while shouting death threats, and then forcibly shoved her off the terrace edge intending to kill her. The victim fell onto a lower sunshade, suffering multiple fractures and surviving through timely surgical resuscitation.",
        "expected_section": "Section 307",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },

    # 17-18: Grievous Hurt by Dangerous Weapons (IPC 326 / BNS 118(2))
    {
        "id": "CASE_17",
        "category": "Grievous Hurt Dangerous Weapons",
        "name": "Iron Rod Skull Compound Fracture",
        "narrative": "The accused armed with a heavy solid iron rod accosted the victim in a lane and struck him repeatedly on both legs and the forehead, causing compound fractures of both tibia bones and permanent disfigurement. The victim survived after orthopaedic surgery with permanent limb stiffness.",
        "expected_section": "Section 326",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },
    {
        "id": "CASE_18",
        "category": "Grievous Hurt Dangerous Weapons",
        "name": "Corrosive Acid Vitriolage Attack",
        "narrative": "The accused threw a jar of concentrated sulfuric acid onto the complainant's face and upper chest, causing deep third-degree chemical burns, complete destruction of facial tissue, permanent loss of vision in one eye, and severe permanent disfigurement. The victim survived after extensive skin grafting.",
        "expected_section": "Section 326",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },

    # 19-20: Simple Hurt by Dangerous Weapons (IPC 324 / BNS 118(1))
    {
        "id": "CASE_19",
        "category": "Simple Hurt Dangerous Weapons",
        "name": "Superficial Razor Forearm Slash",
        "narrative": "During an altercation in a market, the accused took out a razor blade and inflicted a superficial horizontal cut across the victim's left forearm. The wound caused bleeding but no fracture, tendon damage, or danger to life. The victim received three stitches and was discharged the same hour.",
        "expected_section": "Section 324",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },
    {
        "id": "CASE_20",
        "category": "Simple Hurt Dangerous Weapons",
        "name": "Pocketknife Graze on Thigh",
        "narrative": "In an argument outside a cinema hall, the accused brandished a small penknife and slashed at the victim, causing an incised minor skin wound on his outer thigh. Medical examination confirmed superficial tissue incision without any bone involvement or grievous injury.",
        "expected_section": "Section 324",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },

    # 21-22: Simple Hurt Unarmed (IPC 323 / BNS 115)
    {
        "id": "CASE_21",
        "category": "Simple Hurt Unarmed",
        "name": "Unarmed Street Slaps and Punches",
        "narrative": "The accused had no weapon and attacked the complainant with bare fists during a disagreement over parking. He delivered multiple slaps and punches to the victim's face and torso, causing localized facial swelling, a black eye, and bodily pain. No fracture or bleeding occurred.",
        "expected_section": "Section 323",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },
    {
        "id": "CASE_22",
        "category": "Simple Hurt Unarmed",
        "name": "Bus Conductor Assault",
        "narrative": "A passenger refused to purchase a ticket and pushed the bus conductor, kicking him in the shin and punching him in the ribs with his bare hands. The victim suffered contusions and temporary pain without any dangerous instrument or bone breakage.",
        "expected_section": "Section 323",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },

    # 23-24: Cheating & Financial Fraud (IPC 420 / BNS 318)
    {
        "id": "CASE_23",
        "category": "Cheating & Financial Fraud",
        "name": "Bogus Overseas Nursing Job Scam",
        "narrative": "The accused set up a fictitious overseas recruitment agency in Ernakulam, dishonestly induced 35 nursing graduates by promising guaranteed NHS hospital appointments in the United Kingdom, fraudulently collected Rs 4.5 lakhs in cash from each candidate at inception, and subsequently shuttered the office and absconded with Rs 1.57 crores.",
        "expected_section": "Section 420",
        "expected_tier": "Tier 2 (3 to 7 Years)"
    },
    {
        "id": "CASE_24",
        "category": "Cheating & Financial Fraud",
        "name": "Cryptocurrency Ponzi Racket",
        "narrative": "The accused launched a fraudulent multi-level marketing platform promising guaranteed 40% monthly returns through a proprietary trading algorithm. Having deceptive inducement from the inception, they collected over Rs 3 crores from retail investors and abruptly shut down the website, diverting all deposits into shell entities.",
        "expected_section": "Section 420",
        "expected_tier": "Tier 2 (3 to 7 Years)"
    },

    # 25-26: Forgery & Fake Documents (IPC 468 / BNS 336)
    {
        "id": "CASE_25",
        "category": "Forgery & Fake Documents",
        "name": "Ancestral Land Title Deed Forgery",
        "narrative": "The accused manufactured a forged registered partition deed by fabricating the seal of the Sub-Registrar and copying the signatures of his deceased uncle, specifically with the intent to cheat prospective buyers by claiming absolute ownership over 2.5 acres of ancestral prime real estate.",
        "expected_section": "Section 468",
        "expected_tier": "Tier 2 (3 to 7 Years)"
    },
    {
        "id": "CASE_26",
        "category": "Forgery & Fake Documents",
        "name": "Fabricated Testamentary Will",
        "narrative": "To usurp his late brother's bank accounts, the accused fabricated a false registered will, forging the signatures of two deceased attesting witnesses and using a fake notary seal, subsequently presenting the forged will before the probate court to misappropriate Rs 40 lakhs.",
        "expected_section": "Section 468",
        "expected_tier": "Tier 2 (3 to 7 Years)"
    },

    # 27-28: Criminal Breach of Trust (IPC 406 / BNS 316)
    {
        "id": "CASE_27",
        "category": "Criminal Breach of Trust",
        "name": "Warehouse Cargo Custodian Misappropriation",
        "narrative": "The accused was the appointed warehouse manager entrusted with custody and dominion over 500 metric tons of imported raw cashew nuts stored for safekeeping by a trading firm. In violation of his fiduciary duties, he dishonestly misappropriated and sold 150 metric tons to local processors for personal profit.",
        "expected_section": "Section 406",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },
    {
        "id": "CASE_28",
        "category": "Criminal Breach of Trust",
        "name": "Logistics Dispatch Embezzlement",
        "narrative": "A transport fleet contractor was entrusted with the conveyance of a shipment of 800 electronic tablets for delivery to a state school board. The contractor diverted the transport truck, unloaded the electronic devices into an unauthorized private godown, and converted them to his own use.",
        "expected_section": "Section 406",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },

    # 29-30: Dowry Death (IPC 304B / BNS 80)
    {
        "id": "CASE_29",
        "category": "Dowry Death",
        "name": "Kerosene Burn Dowry Death (2 Years of Marriage)",
        "narrative": "The victim was married for only two years. Throughout the marital period, her husband and mother-in-law subjected her to severe harassment and cruelty demanding an additional dowry of Rs 5 lakhs and a luxury car. Within two years of marriage, the victim was found dead inside the matrimonial kitchen with 90% kerosene burn injuries.",
        "expected_section": "Section 304B",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },
    {
        "id": "CASE_30",
        "category": "Dowry Death",
        "name": "Poisoning within 3 Years of Marriage",
        "narrative": "A woman married for three years was subjected to persistent physical torture by her husband on account of failing to bring 50 sovereigns of gold as dowry. Following a final altercation over dowry demands, she was found dead under unnatural circumstances due to organophosphate poisoning.",
        "expected_section": "Section 304B",
        "expected_tier": "Tier 4 (Life Imprisonment / Capital)"
    },

    # 31-32: Matrimonial Cruelty (IPC 498A / BNS 85)
    {
        "id": "CASE_31",
        "category": "Matrimonial Cruelty",
        "name": "Ongoing Matrimonial Abuse (Victim Alive)",
        "narrative": "The complainant lodged an FIR against her husband and in-laws stating that she has been subjected to constant verbal degradation, denial of food, and systematic physical battery over the past four years for not bringing cash from her maternal home. The victim survived and sought protection.",
        "expected_section": "Section 498A",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },
    {
        "id": "CASE_32",
        "category": "Matrimonial Cruelty",
        "name": "In-Laws Dowry Harassment",
        "narrative": "A married woman was constantly taunted and subjected to mental cruelty by her husband and sister-in-law demanding that her parents transfer a residential plot to their name. She was beaten and expelled from the marital home late at night. No fatal injury occurred.",
        "expected_section": "Section 498A",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },

    # 33-34: Criminal Intimidation (IPC 506 / BNS 351)
    {
        "id": "CASE_33",
        "category": "Criminal Intimidation",
        "name": "Brandishing Firearm with Threat to Kill (No Hurt)",
        "narrative": "During an argument over tenancy eviction, the landlord pulled out a licensed revolver, pointed it directly at the tenant's chest, and threatened to shoot him dead if he did not vacate within 24 hours. No shots were fired and no physical injury of any kind was caused.",
        "expected_section": "Section 506",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },
    {
        "id": "CASE_34",
        "category": "Criminal Intimidation",
        "name": "Threatening Acid Attack",
        "narrative": "The accused accosted a college student near the bus stand, held up a bottle of chemical liquid claiming it was acid, and loudly threatened to disfigure her face if she refused to withdraw a civil petition. The accused then fled without touching her or pouring the liquid.",
        "expected_section": "Section 506",
        "expected_tier": "Tier 1 (Up to 3 Years)"
    },

    # 35: Commercial Civil Dispute Quashing (Quashed u/s 482 CrPC / s.528 BNSS)
    {
        "id": "CASE_35",
        "category": "Civil Dispute Quashing",
        "name": "Corporate Software Invoices Dispute",
        "narrative": "A software vendor filed a criminal complaint alleging cheating against an enterprise client because three monthly milestone invoices totaling Rs 18 lakhs remained unpaid following a reconciliation dispute over service level uptime. There was no deception at the inception of the contract, no weapon, and no physical altercation.",
        "expected_section": "Quashed u/s 482 CrPC",
        "expected_tier": "Quashed (No Penal Term)"
    }
]


def run_35_cases_benchmark():
    print("=" * 105)
    print("⚖️ EXECUTING COMPREHENSIVE 35-CASE RIGOROUS ACCURACY EVALUATION (EFFECTIVE LJP V6)")
    print("=" * 105)

    pipeline = EffectiveLjpPipeline()

    passed_count = 0
    total = len(CASES_35)
    results = []

    print(f"{'#':<3} | {'Case Name':<32} | {'Expected Section':<20} | {'Predicted Top Article':<22} | {'Tier':<8} | {'JCI':<5} | Status")
    print("-" * 105)

    category_stats = {}

    for idx, c in enumerate(CASES_35, start=1):
        cat = c["category"]
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "passed": 0}
        category_stats[cat]["total"] += 1

        t0 = time.time()
        res = pipeline.run(c["narrative"])
        elapsed = time.time() - t0

        if res.is_abstained:
            pred_section = "ABSTAINED"
            pred_tier = "None"
            jci = 100.0
            is_pass = (c["expected_section"] == "Abstain")
        else:
            top_art = res.top_articles[0]
            pred_section = top_art.ipc_section
            pred_tier = res.penalty_prediction.predicted_tier
            jci = res.judicial_audit.final_jci_score
            is_pass = (pred_section == c["expected_section"])

        if is_pass:
            passed_count += 1
            category_stats[cat]["passed"] += 1
            status_str = "✅ PASS"
        else:
            status_str = f"❌ FAIL (Got: {pred_section})"

        results.append({
            "idx": idx,
            "id": c["id"],
            "name": c["name"],
            "category": cat,
            "expected": c["expected_section"],
            "predicted": pred_section,
            "tier": pred_tier,
            "jci": jci,
            "passed": is_pass,
            "latency_ms": round(elapsed * 1000, 1)
        })

        print(f"{idx:<3} | {c['name'][:32]:<32} | {c['expected_section']:<20} | {pred_section:<22} | {pred_tier[:8]:<8} | {jci:<5.1f} | {status_str}")

    accuracy = (passed_count / total) * 100.0

    print("=" * 105)
    print("📊 35-CASE EVALUATION RESULTS:")
    print(f"• Total Evaluated Cases:   {total}")
    print(f"• Total Passed:            {passed_count}")
    print(f"• Total Failed:            {total - passed_count}")
    print(f"• Overall Pass Rate:       {accuracy:.1f}%\n")

    print(f"{'Category':<38} | {'Total':<6} | {'Passed':<6} | Accuracy")
    print("-" * 70)
    for cat, stats in sorted(category_stats.items()):
        c_acc = (stats['passed'] / stats['total']) * 100.0
        print(f"{cat:<38} | {stats['total']:<6} | {stats['passed']:<6} | {c_acc:.1f}%")

    print("=" * 105)
    return {
        "total": total,
        "passed": passed_count,
        "accuracy": accuracy,
        "results": results,
        "category_stats": category_stats
    }


if __name__ == "__main__":
    run_35_cases_benchmark()
