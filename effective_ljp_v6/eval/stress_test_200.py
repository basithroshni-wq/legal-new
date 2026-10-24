"""
200-Case Large-Scale Stress Test & Failure Diagnostics for Effective LJP V6.
Tests all pipeline components:
1. Fact Extractor (Negation, Entity Scoping, Injury Grading, Accused Counts, Defense Pleas)
2. Hybrid BM25 + Dense Retriever (Vocabulary Bleed, Lexical Collisions)
3. Relevance & Confidence Gate (Disqualifications, Negative Exceptions)
4. Calibrated Multi-Task Predictor (Softmax Distribution, Precedence Rules)
5. Judicial Consistency Verifier (CrPC 31 / BNSS 25 Sentencing Ceilings, Exception 4)
6. Out-of-Domain Classifier (Abstention Precision)
"""

import sys
import os
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


def generate_200_test_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []

    def add_c(cid, cat, exp, ood, text):
        cases.append({
            "id": f"CASE_{cid:03d}",
            "category": cat,
            "expected_ipc": exp,
            "should_abstain": ood,
            "narrative": text.strip()
        })

    c_id = 1

    # --- 1. Premeditated Murder (IPC 302 / BNS 103) (15 cases) ---
    murder_templates = [
        ("Nursing a 5-year boundary wall dispute, the accused concealed a sharp sickle, ambushed the victim returning from his field, and slashed his throat, killing him on the spot.", "Section 302"),
        ("The accused hired two contract killers and supplied them with country pistols. Lying in wait outside the victim's factory, they shot him four times in the head, causing instant death.", "Section 302"),
        ("Driven by jealousy, the accused administered potassium cyanide into his brother's evening milk drink. The brother consumed it and died within minutes due to poisoning.", "Section 302"),
        ("The accused, having planned the murder a week prior, followed the victim into an isolated alley and stabbed him six times in the chest with a butcher knife, killing him on the spot.", "Section 302"),
        ("In an act of premeditated honor killing, the father and uncle strangled the victim with a nylon rope in her bedroom and dumped her corpse in the canal.", "Section 302"),
        ("The accused harbored a bitter grudge over property partition. He waited outside the victim's home at dawn and severed his jugular vein with a talwar, causing death instantly.", "Section 302"),
        ("The accused purchased an iron hammer specifically to eliminate his business partner. While the partner was sleeping in the office, the accused crushed his skull, killing him.", "Section 302"),
        ("The assailant tailed the deceased for three miles, cornered him behind a warehouse, and stabbed him in the heart with a dagger, causing instant fatality.", "Section 302"),
        ("To eliminate an eyewitness, the accused waited near the railway crossing and repeatedly stabbed the deceased in the neck with an ice-pick, resulting in death.", "Section 302"),
        ("The accused premeditated the murder over unpaid election dues, armed himself with a loaded shotgun, and fired two point-blank blasts into the victim's face, killing him.", "Section 302"),
        ("The accused conspired to murder his landlord. He lured him to an abandoned construction basement and bludgeoned him to death with a concrete slab.", "Section 302"),
        ("With clear premeditation and motive to claim insurance, the accused pushed the victim off a 200-foot cliff. The victim sustained fatal trauma and died on the spot.", "Section 302"),
        ("The accused hid behind a bus shelter armed with a meat chopper and hacked the deceased four times on the cervical spine upon arrival, causing immediate death.", "Section 302"),
        ("The accused ambushed his rival outside court premises and pumped five bullets into his torso with a revolver, causing fatal hemorrhage and instant death.", "Section 302"),
        ("Having threatened revenge months earlier, the accused attacked the sleeping victim with an axe, severing his head from his torso, killing him instantly.", "Section 302"),
    ]
    for text, exp in murder_templates:
        add_c(c_id, "Premeditated Murder", exp, False, text); c_id += 1

    # --- 2. Culpable Homicide - Sudden Fight / Exception 4 (IPC 304 Part II) (15 cases) ---
    sudden_templates = [
        ("A sudden quarrel broke out over overtaking at a traffic intersection. In the heat of passion, the driver grabbed a steering lock from his dashboard and struck the motorcyclist once, who died of skull fracture. There was no prior enmity.", "Section 304 Part II"),
        ("During a casual card game at a tea stall, hot words were exchanged. The accused grabbed a glass bottle lying on the table, broke it, and struck the victim's temple, causing fatal injuries. No planning was present.", "Section 304 Part II"),
        ("Two colleagues argued violently over office air conditioning. In sudden anger without premeditation, the accused pushed the victim down the stairwell, resulting in fatal head injuries.", "Section 304 Part II"),
        ("A sudden fight flared up between neighbors during Holi festivities. The accused picked up a bamboo pole lying nearby and struck a single fatal blow on the victim's cranium.", "Section 304 Part II"),
        ("While waiting in a bank queue, a heated scuffle ensued. The accused shoved the elderly victim hard, causing him to hit a granite edge and succumb to head trauma. There was no intent to kill.", "Section 304 Part II"),
        ("During a cricket match argument, the batsman hit the bowler on the neck with his bat in the heat of passion, causing sudden death. The parties had no prior animosity.", "Section 304 Part II"),
        ("A sudden fight occurred at a wedding buffet over food service. The accused threw a heavy steel utensil at the victim, causing blunt cranial trauma leading to death.", "Section 304 Part II"),
        ("An impromptu bar room brawl escalated when hot words were exchanged. The accused struck the victim with a bar stool, causing fatal cerebral hemorrhage without any premeditation.", "Section 304 Part II"),
        ("Two rickshaw drivers fought over a passenger. In sudden passion, the accused picked up a stone from the roadside and smashed it on the victim's skull, killing him.", "Section 304 Part II"),
        ("During a family dinner argument over television channels, the accused grabbed a wooden rolling pin from the kitchen counter and delivered a fatal blow to his brother in sudden anger.", "Section 304 Part II"),
        ("In an unscripted argument over stray dog feeding, the accused struck the victim once with an umbrella handle on a vital point, causing sudden death without prior enmity.", "Section 304 Part II"),
        ("A spontaneous altercation between tenants over water motor operation led the accused to punch the victim hard in the larynx in heat of passion, resulting in asphyxia and death.", "Section 304 Part II"),
        ("During a sudden verbal spat between bus passengers, the accused struck the complainant with an iron rod lying on the bus floor, who succumbed to injuries without prior enmity.", "Section 304 Part II"),
        ("A sudden quarrel broke out at a car wash. The accused swung a water pipe in hot blood, hitting the victim's head and causing fatal intracranial hemorrhage.", "Section 304 Part II"),
        ("In a sudden quarrel over grazing cattle on an uncultivated plot, the accused struck the victim with a shepherd's crook without prior planning, causing death from head injury.", "Section 304 Part II"),
    ]
    for text, exp in sudden_templates:
        add_c(c_id, "Sudden Fight Homicide (Exception 4)", exp, False, text); c_id += 1

    # --- 3. Culpable Homicide - Intention / Grave Provocation (IPC 304 Part I) (12 cases) ---
    p1_templates = [
        ("Four village assailants surrounded the victim and beat his ribs and legs severely with lathis to teach him a lesson, intending severe bodily injury likely to cause death, and he succumbed.", "Section 304 Part I"),
        ("Finding the deceased trespassing inside his bedroom at midnight attempting theft, the homeowner lost self-control and repeatedly beat him with an iron bar, exceeding private defence and causing death.", "Section 304 Part I"),
        ("Upon discovering his wife in a compromising position with the victim, the accused was subjected to grave and sudden provocation, and struck the victim repeatedly with a wooden stool, causing death.", "Section 304 Part I"),
        ("Three co-accused armed with iron rods attacked the victim in the bazaar in broad daylight, inflicting multiple fractures to his skull and limbs with intent to cause life-threatening injury, leading to death.", "Section 304 Part I"),
        ("The accused, reacting to violent physical assault by the deceased, picked up a pruning hook and struck the deceased across the torso with knowledge that it was likely to cause death, causing death.", "Section 304 Part I"),
        ("A group of five villagers caught a suspected cattle thief and tied him to a pole, thrashing him with belts and sticks for two hours until he succumbed to visceral shock.", "Section 304 Part I"),
        ("In a clash between two labor factions, the accused swung a heavy iron wrench at the opposing leader's head with intent to inflict life-threatening injury, causing fatal hemorrhage.", "Section 304 Part I"),
        ("The accused inflicted multiple deep knife gashes on the victim's thighs and chest during an escalated land clash, causing exsanguination and death in hospital.", "Section 304 Part I"),
        ("Two bouncers dragged an unruly patron out of a club and beat him with batons, intending serious bodily injury likely to cause death, leading to his demise the next morning.", "Section 304 Part I"),
        ("Acting in excess of the right of private defence against stone-pelters, the shopkeeper fired his licensed rifle into the crowd, hitting and killing a protester.", "Section 304 Part I"),
        ("During a gang altercation, the accused stabbed the victim in the flank with a dagger, intending severe bodily harm likely to cause death, resulting in fatal peritonitis.", "Section 304 Part I"),
        ("Three brothers beat their uncle with lathis over an irrigation channel, inflicting broken ribs and ruptured liver that resulted in death 12 hours later.", "Section 304 Part I"),
    ]
    for text, exp in p1_templates:
        add_c(c_id, "Culpable Homicide Not Murder (Part I)", exp, False, text); c_id += 1

    # --- 4. Attempt to Murder (IPC 307 / BNS 109) (12 cases) ---
    attempt_templates = [
        ("With the intention to murder, the accused shot the victim in the chest with a country-made pistol at point-blank range. The bullet penetrated the lung, but the victim survived emergency surgery.", "Section 307"),
        ("The accused slashed the victim's throat with a surgical scalpel with intent to kill him. Timely vascular repair by surgeons saved the victim's life.", "Section 307"),
        ("The assailant fired three bullets at the political leader's car, striking him in the abdomen and neck. The victim survived after ten days in the intensive care unit.", "Section 307"),
        ("The accused mixed arsenic into the complainant's breakfast porridge intending to kill him. The complainant consumed it, suffered severe toxicity, but survived stomach pumping.", "Section 307"),
        ("To kill his rival, the accused intentionally accelerated his SUV and rammed the pedestrian against a concrete pillar at 60 km/h. The victim suffered pelvic trauma but survived.", "Section 307"),
        ("The accused pushed the victim into an active railway track just as a train approached, intending his death. Bystanders pulled the victim back, saving him with minor injuries.", "Section 307"),
        ("With intent to eliminate his competitor, the accused set the victim's locked shop on fire while he was inside. Firefighters broke in and rescued the victim with 30% burns, who survived.", "Section 307"),
        ("The accused stabbed the victim four times in the left thoracic cavity with a dagger, intending to cause death. The victim underwent emergency thoracotomy and survived.", "Section 307"),
        ("The accused threw the victim off the terrace of a three-story building intending to murder him. The victim landed on an awning, breaking both legs, but survived.", "Section 307"),
        ("The attacker placed a ticking pipe bomb under the victim's car seat. It detonated prematurely, injuring the victim's limbs, who survived emergency surgery.", "Section 307"),
        ("With intent to kill, the accused pinned the victim down and strangled him with a wire until he lost consciousness. Police arrived and resuscitated the victim, who survived.", "Section 307"),
        ("The accused shot the complainant in the neck with a revolver intending his death. The bullet missed the carotid artery by millimeters, and the complainant survived.", "Section 307"),
    ]
    for text, exp in attempt_templates:
        add_c(c_id, "Attempt to Murder", exp, False, text); c_id += 1

    # --- 5. Voluntarily Causing Grievous Hurt by Dangerous Weapons (IPC 326) (12 cases) ---
    g_hurt_templates = [
        ("The accused threw sulfuric acid on the complainant's face and arms, causing permanent disfigurement, blindness in one eye, and severe chemical burns.", "Section 326"),
        ("During a market brawl, the accused took a butcher knife and chopped off the victim's left hand at the wrist, causing permanent privation of a limb.", "Section 326"),
        ("The accused struck the complainant across the jaw with an iron crowbar, fracturing the mandible and knocking out five teeth, requiring 25 days of hospitalization.", "Section 326"),
        ("The assailant drove a motorcycle past the victim and slashed his face with a razor blade, severing facial nerves and causing permanent facial disfigurement.", "Section 326"),
        ("The accused stabbed the complainant in the stomach with a bayonet, puncturing the intestine and causing acute internal bleeding requiring emergency laparotomy.", "Section 326"),
        ("The accused struck the victim's knee with an iron rod, shattering the patella into fragments and causing permanent stiffness and disability.", "Section 326"),
        ("During an argument, the accused poured boiling mustard oil over the victim's chest and back, causing deep second and third degree burns requiring skin grafting.", "Section 326"),
        ("The accused struck the victim with a sword on his forearm, completely severing the extensor tendons and causing permanent privation of fingers.", "Section 326"),
        ("The assailant fired a pellet gun into the victim's face, puncturing the retina and causing permanent loss of vision in the right eye.", "Section 326"),
        ("The accused struck the complainant's temple with an iron wrench, causing a depressed skull fracture with cranial bone displacement, though the victim survived.", "Section 326"),
        ("The accused used a heavy garden spade to chop the victim's ankle, severing the Achilles tendon and fracturing the tibia, causing permanent limping.", "Section 326"),
        ("The accused threw corrosive battery acid into the victim's lap, causing severe deep tissue necrosis and permanent disability.", "Section 326"),
    ]
    for text, exp in g_hurt_templates:
        add_c(c_id, "Grievous Hurt by Dangerous Weapons", exp, False, text); c_id += 1

    # --- 6. Voluntarily Causing Simple Hurt by Dangerous Weapons (IPC 324) (10 cases) ---
    s_hurt_templates = [
        ("During a dispute at a tea stall, the accused took out a small penknife and inflicted a superficial two-inch skin laceration on the complainant's arm.", "Section 324"),
        ("The accused swung a broken beer bottle during an argument, scratching the victim's shoulder and causing a superficial cut requiring three stitches without fracture.", "Section 324"),
        ("The accused brandished a pocket knife and slashed the victim's forearm, causing simple hurt without permanent disfigurement or danger to life.", "Section 324"),
        ("The accused threw a hot cup of tea at the complainant's face, causing minor first-degree superficial scalds that healed within four days.", "Section 324"),
        ("During an altercation, the accused took a safety razor blade and slashed the complainant's palm, inflicting a simple bleeding cut without fracture.", "Section 324"),
        ("The accused threw a sharp metal compass at the victim, puncturing the skin of his forearm and causing simple hurt without danger to life.", "Section 324"),
        ("The accused used a pair of tailoring scissors to poke the complainant in the thigh, causing a superficial puncture wound certified as simple hurt.", "Section 324"),
        ("The accused hit the victim across the back with a thin bicycle chain, causing bruises and skin abrasions certified as simple hurt by dangerous means.", "Section 324"),
        ("During a scuffle, the accused struck the complainant's wrist with a sharp wooden scale, causing a superficial bleeding cut with no fracture.", "Section 324"),
        ("The accused brandished a pocket blade and cut the complainant's coat and arm, causing a superficial 1-inch laceration with minor bleeding.", "Section 324"),
    ]
    for text, exp in s_hurt_templates:
        add_c(c_id, "Simple Hurt by Dangerous Weapons", exp, False, text); c_id += 1

    # --- 7. Simple Hurt Unarmed (IPC 323) (8 cases) ---
    simple_templates = [
        ("During a verbal argument over a parking spot, the accused slapped the complainant twice on the face and pushed him onto the grass, causing minor pain and bruises.", "Section 323"),
        ("The accused punched his neighbor in the eye during a heated exchange over garbage disposal, causing swelling and a black eye without any weapon.", "Section 323"),
        ("During an altercation at a movie theater, the accused kicked the complainant in the shins and twisted his arm, causing temporary bodily pain without fracture.", "Section 323"),
        ("The accused slapped the waiter across the ear because the soup was cold, causing minor tenderness and swelling without any instrument used.", "Section 323"),
        ("Two commuters shoved each other in a metro coach; the accused landed a bare fist punch on the complainant's nose, causing a brief nosebleed without fracture.", "Section 323"),
        ("The accused dragged the complainant by his collar and struck him with fists on his back and shoulders, causing minor contusions with no weapon.", "Section 323"),
        ("In an argument between students in a hostel, the accused delivered three slaps and kicked the complainant, causing minor bruises with no instrument.", "Section 323"),
        ("The landlord shoved the tenant against the wooden door during a rent dispute, causing back soreness and minor skin scratches with no weapon used.", "Section 323"),
    ]
    for text, exp in simple_templates:
        add_c(c_id, "Simple Hurt (Unarmed)", exp, False, text); c_id += 1

    # --- 8. Theft (IPC 379 / BNS 303(2)) (14 cases) ---
    theft_templates = [
        ("The accused boarded a crowded train, unzipped an unattended backpack on the luggage rack, and removed a Dell laptop worth Rs. 60,000 without the owner's consent or force.", "Section 379"),
        ("The accused discreetly stole an unlocked Royal Enfield motorcycle parked outside a temple in the dead of night and rode it away without the owner's knowledge.", "Section 379"),
        ("At a shopping mall, the accused concealed three branded leather jackets inside her handbag and walked out past the checkout counter without paying.", "Section 379"),
        ("The accused crept into an agricultural field at night, untied two cows valued at Rs. 80,000, and loaded them onto a pickup truck without using force or weapons.", "Section 379"),
        ("While the victim was swimming at a public pool, the accused lifted his smartphone and wallet from the changing locker and fled unnoticed.", "Section 379"),
        ("The accused pickpocketed an elderly commuter on a city bus, taking his leather purse containing Rs. 12,000 cash and debit cards without any violence.", "Section 379"),
        ("The accused stole 50 meters of copper wire from a construction yard after workers had departed for the evening, using no force or threats.", "Section 379"),
        ("The accused entered an unlocked jewelry showroom during lunch break and quietly slipped a diamond necklace into his coat pocket before exiting peacefully.", "Section 379"),
        ("While the shopkeeper was looking away, the customer picked up a bottle of imported perfume from the shelf and walked out without paying.", "Section 379"),
        ("The accused removed a parked bicycle from outside a school gate and rode it away with dishonest intention without the owner's consent.", "Section 379"),
        ("The accused quietly detached an electricity meter from an unoccupied commercial building and took it away without anyone's permission.", "Section 379"),
        ("At a library, the accused put two rare reference books inside his bag and exited past the turnstiles without permission or using any force.", "Section 379"),
        ("The accused reached into an open car window parked on the roadside and took away a lady's handbag lying on the passenger seat.", "Section 379"),
        ("The accused stole an external air conditioning compressor unit from outside an office building at night without using force or violence.", "Section 379"),
    ]
    for text, exp in theft_templates:
        add_c(c_id, "Theft (IPC 379)", exp, False, text); c_id += 1

    # --- 9. Robbery (IPC 392 / BNS 309(4)) (14 cases) ---
    robbery_templates = [
        ("The accused intercepted a pedestrian on a deserted road after sunset, pointed a curved dagger at his throat, and extorted his smartphone and Rs. 5,000 cash.", "Section 392"),
        ("Two motorcycle-borne youth rode alongside a walking woman, brandished a knife, snatched her gold mangalsutra by force, and sped away under threat of instant hurt.", "Section 392"),
        ("The accused entered a medical store, pointed a country pistol at the chemist's forehead, and forcibly took Rs. 25,000 from the cash drawer under threat of immediate death.", "Section 392"),
        ("While a commuter was waiting at an isolated bus stop at night, the accused held an iron rod to his ribs, threatened to smash his teeth, and forcibly took his wallet.", "Section 392"),
        ("The accused cornered a delivery boy in a dark alley, held a knife to his neck, and forcibly took his delivery bag containing cash collections and parcels.", "Section 392"),
        ("The accused boarded a late-night auto-rickshaw as a passenger, held a knife at the driver's chest on the highway, and forcibly took his day's earnings and mobile phone.", "Section 392"),
        ("The accused grabbed a schoolteacher by her hair on the highway, pressed a razor blade against her cheek, and forced her to hand over her gold earrings.", "Section 392"),
        ("The accused held a revolver at the petrol pump attendant's chest and demanded the day's cash collection under threat of instant death, taking Rs. 40,000.", "Section 392"),
        ("The accused ambushed an ATM customer inside the kiosk with a dagger, threatened to stab him if he screamed, and forcibly took Rs. 10,000 just withdrawn.", "Section 392"),
        ("The accused shoved a cyclist off his bicycle on an isolated stretch, held a sickle at his throat, and rode away with the bicycle and his purse.", "Section 392"),
        ("The accused intercepted a jeweler on a state highway after dusk, pointed a firearm at him, and forcibly took his leather briefcase containing silver ornaments.", "Section 392"),
        ("The accused pushed the victim into an elevator corner, pulled out a flick knife, and forcibly took his Rolex watch and wallet under fear of instant injury.", "Section 392"),
        ("The accused threatened a cab driver with a meat cleaver held against his neck and took away his mobile phone and Rs. 8,000 cash before pushing him out.", "Section 392"),
        ("Two men on a scooter blocked a pedestrian, brandished an iron pipe, threatened immediate violence, and forcibly took his gold bracelet and wallet.", "Section 392"),
    ]
    for text, exp in robbery_templates:
        add_c(c_id, "Robbery (IPC 392)", exp, False, text); c_id += 1

    # --- 10. Dacoity (IPC 395 / BNS 310(2)) (10 cases) ---
    dacoity_templates = [
        ("A gang of seven armed men stormed a bank branch at gunpoint, tied up the security guards, looted Rs. 80 lakhs from the cash vault, and fled in two SUVs.", "Section 395"),
        ("Six masked dacoits armed with country pistols and iron rods intercepted a cash delivery van on the national highway and conjointly looted Rs. 1.2 crores.", "Section 395"),
        ("A gang of five armed assailants entered a jewelry showroom, threatened customers with shotguns, broke display cases with hammers, and looted gold ornaments.", "Section 395"),
        ("Eight men armed with knives and lathis raided a wealthy farmer's farmhouse at midnight, held the family hostage under threat of death, and looted cash and gold.", "Section 395"),
        ("A gang of six armed robbers stopped a train by pulling the emergency chain in an unpopulated tract, brandished weapons, and looted valuables from three coaches.", "Section 395"),
        ("Seven dacoits carrying swords and firearms ambushed a bullion merchant's vehicle on the bypass road and conjointly looted 5 kg of gold bars.", "Section 395"),
        ("A gang of five masked men carrying shotguns broke into a toll plaza booth, overpowered the guards, and looted Rs. 15 lakhs from the cash safe.", "Section 395"),
        ("Nine armed bandits intercepted three transport trucks on a state highway at night, threatened the drivers with axes, and looted all the cargo.", "Section 395"),
        ("A gang of six men armed with pistols invaded a wedding banquet hall, held the guests at gunpoint, and looted all jewelry and cash shagun envelopes.", "Section 395"),
        ("Five armed men broke into a corporate headquarters overnight, tied up the night watchman with ropes, and looted the payroll cash safe.", "Section 395"),
    ]
    for text, exp in dacoity_templates:
        add_c(c_id, "Dacoity (IPC 395)", exp, False, text); c_id += 1

    # --- 11. Cheating & Fraud (IPC 420 / BNS 318(4)) (14 cases) ---
    cheating_templates = [
        ("The accused ran an unauthorized employment agency and dishonestly induced 25 job seekers to pay Rs. 50 lakhs by promising guaranteed government clerk appointments.", "Section 420"),
        ("The accused floated a fake multi-level marketing investment scheme promising 30% monthly returns, collected Rs. 1.5 crores from 80 investors, and fled without paying.", "Section 420"),
        ("The accused posed as an overseas visa consultant, issued fake Canadian work visas, and duped twelve applicants of Rs. 48 lakhs in cash advances.", "Section 420"),
        ("The accused deceived a businessman into transferring Rs. 30 lakhs as an advance for a government timber auction, having no authorization or tender rights.", "Section 420"),
        ("The accused ran a fake medical admission racket, fraudulently promising MBBS seats in state medical colleges, and collected Rs. 85 lakhs from five parents.", "Section 420"),
        ("The accused promised lucrative cryptocurrency returns on a bogus algorithm, dishonestly inducing thirty investors to transfer Rs. 70 lakhs into his personal account.", "Section 420"),
        ("The accused posed as a senior bank loan officer and charged Rs. 5 lakhs as loan processing fees for non-existent subsidized agricultural loans, duping ten farmers.", "Section 420"),
        ("The accused sold three residential plots to multiple buyers simultaneously by showing fake layout approvals, dishonestly cheating buyers of Rs. 90 lakhs.", "Section 420"),
        ("The accused induced a cooperative bank to disburse a loan of Rs. 40 lakhs by pledging bogus non-existent gold jewelry containing brass fillings.", "Section 420"),
        ("The accused posed as a franchise manager of a global fast-food brand and collected Rs. 25 lakhs as franchise security deposits from three entrepreneurs.", "Section 420"),
        ("The accused advertised subsidized government housing flats on social media, collected Rs. 20 lakhs in booking fees from low-income families, and disappeared.", "Section 420"),
        ("The accused deceived an exporter by posing as a foreign buyer's agent, taking delivery of garment consignments worth Rs. 35 lakhs with no intent to pay.", "Section 420"),
        ("The accused ran an unauthorized chit fund, collected monthly contributions of Rs. 60 lakhs from 200 members, and abruptly shut down operations and absconded.", "Section 420"),
        ("The accused duped a buyer into paying Rs. 15 lakhs for a second-hand excavator by concealing that it was already mortgaged and subject to court attachment.", "Section 420"),
    ]
    for text, exp in cheating_templates:
        add_c(c_id, "Cheating & Financial Fraud", exp, False, text); c_id += 1

    # --- 12. Forgery (IPC 468 / 471) (10 cases) ---
    forgery_templates = [
        ("The accused fabricated a forged will bearing forged signatures of his deceased uncle in order to fraudulently mutate ancestral land worth Rs. 2 crores in his name.", "Section 468"),
        ("The accused manufactured a fake university degree certificate and forged marksheets to secure employment as a lecturer in a government-aided college.", "Section 468"),
        ("The accused prepared a forged gift deed with counterfeit registrar stamps and seals to illegally mortgage a widow's property to a commercial bank.", "Section 468"),
        ("The accused forged the signature of the managing director on a bank cheque leaf for Rs. 25 lakhs and presented it at the bank counter for encashment.", "Section 468"),
        ("The accused fabricated a false death certificate of a living landowner in order to fraudulently claim title and sell the plot to third parties.", "Section 468"),
        ("The accused prepared counterfeit government non-judicial stamp papers and used them to create bogus lease deeds for commercial properties.", "Section 468"),
        ("The accused forged customs clearance certificates and import invoices to evade customs duty on imported machinery worth Rs. 80 lakhs.", "Section 468"),
        ("The accused manufactured a forged power of attorney from an NRI property owner and used it to execute a sale deed of a residential villa.", "Section 468"),
        ("The accused fabricated a counterfeit court decree to get an illegal mutation entered in the municipal tax records in collusion with revenue clerks.", "Section 468"),
        ("The accused created a fake driving license and forged voter ID card to open multiple bogus bank accounts for routing unauthorized funds.", "Section 468"),
    ]
    for text, exp in forgery_templates:
        add_c(c_id, "Forgery & False Documents", exp, False, text); c_id += 1

    # --- 13. Criminal Breach of Trust (IPC 406 / BNS 316) (10 cases) ---
    cbt_templates = [
        ("The accused was appointed custodian of a company warehouse with dominion over stock, but dishonestly misappropriated 50 air conditioners and sold them.", "Section 406"),
        ("The accused, as cashier of a cooperative society, was entrusted with daily cash collections of Rs. 14 lakhs, which he converted to his own personal use.", "Section 406"),
        ("The complainant entrusted 500 grams of gold bullion to the accused jeweler for crafting ornaments; the accused dishonestly pledged the gold to a private lender.", "Section 406"),
        ("The accused transport contractor was entrusted with a shipment of 200 bags of basmati rice for delivery to Chennai; he dishonestly diverted and sold the truckload.", "Section 406"),
        ("The accused was entrusted with the key and management of an NRI's residential bungalow; he dishonestly converted it into a commercial paying guest hostel.", "Section 406"),
        ("The accused, as treasurer of a charitable trust, was entrusted with donation funds of Rs. 30 lakhs, which he transferred to his personal savings account.", "Section 406"),
        ("The accused was given dominion over a friend's luxury car for safekeeping while the friend was abroad; the accused sold the vehicle using false papers.", "Section 406"),
        ("The accused logistics manager was entrusted with electronic gadgets worth Rs. 40 lakhs for distribution; he diverted the consignments to his brother's shop.", "Section 406"),
        ("The accused payroll clerk was entrusted with workers' provident fund deductions of Rs. 18 lakhs, which he misappropriated and converted to personal use.", "Section 406"),
        ("The accused partner in a firm was entrusted with partnership bank accounts, from which he withdrew Rs. 25 lakhs for personal gambling debts.", "Section 406"),
    ]
    for text, exp in cbt_templates:
        add_c(c_id, "Criminal Breach of Trust", exp, False, text); c_id += 1

    # --- 14. Matrimonial Cruelty (IPC 498A / BNS 85) (10 cases) ---
    matrimonial_templates = [
        ("The complainant married the accused three years ago. The husband and mother-in-law subjected her to continuous physical beatings and cruelty demanding an SUV as dowry.", "Section 498A"),
        ("The accused husband and his parents continuously taunted and starved the complainant, demanding Rs. 5 lakhs cash and gold from her maternal home as dowry.", "Section 498A"),
        ("The complainant's husband locked her in a room, beat her with a belt, and threatened to divorce her unless her father transferred a residential plot to his name.", "Section 498A"),
        ("The husband and in-laws harassed the complainant mentally and physically, driving her to attempt suicide over non-fulfillment of demands for a luxury car as dowry.", "Section 498A"),
        ("The accused husband repeatedly assaulted his wife in an intoxicated state, demanding that she bring Rs. 10 lakhs from her parents to fund his business.", "Section 498A"),
        ("The in-laws confiscated the complainant's jewelry, denied her medical treatment during illness, and subjected her to mental cruelty over insufficient dowry.", "Section 498A"),
        ("The husband and sister-in-law subjected the woman to continuous abuse, calling her barren and demanding Rs. 8 lakhs from her parents to permit her to stay.", "Section 498A"),
        ("The complainant was married for five years; her husband routinely beat her black and blue and threw her onto the street when her parents failed to deliver gold coins.", "Section 498A"),
        ("The accused husband inflicted physical cruelty and mental torture on his wife, demanding that her father liquidate his agricultural land to pay off his debts.", "Section 498A"),
        ("The in-laws constantly subjected the complainant to verbal humiliation, forced manual labor, and physical beatings for bringing inadequate dowry at the wedding.", "Section 498A"),
    ]
    for text, exp in matrimonial_templates:
        add_c(c_id, "Matrimonial Cruelty (IPC 498A)", exp, False, text); c_id += 1

    # --- 15. Dowry Death (IPC 304B / BNS 80) (10 cases) ---
    dowry_death_templates = [
        ("A 22-year-old woman was married to the accused for two years. Soon before her death, she was beaten for failing to bring a car; she was found dead with 90% burn injuries.", "Section 304B"),
        ("The deceased was married 18 months prior. Her in-laws continuously harassed her for Rs. 5 lakhs dowry; she was found hanging from a ceiling fan under unnatural circumstances.", "Section 304B"),
        ("Within four years of marriage, the victim died of organophosphate pesticide poisoning in her matrimonial home following continuous cruelty by her husband for dowry.", "Section 304B"),
        ("Married for three years, the woman was admitted to hospital with deep head injuries and subdural hemorrhage inflicted by her husband over dowry demands, and succumbed.", "Section 304B"),
        ("The victim died of unnatural burn injuries in her husband's kitchen within five years of marriage, with documented police complaints of dowry harassment soon before death.", "Section 304B"),
        ("The deceased woman, married two years ago, was found drowned in a farm well near the matrimonial house following repeated physical abuse by in-laws for cash dowry.", "Section 304B"),
        ("Within six years of marriage, the victim succumbed to blunt chest trauma inside the matrimonial home following an assault by her husband over unpaid dowry installments.", "Section 304B"),
        ("The deceased married the accused three years prior. She was found dead under suspicious circumstances with ligature marks on her neck after ongoing dowry torture.", "Section 304B"),
        ("A woman married for only 10 months was found dead in her marital bedroom with severe contusions and asphyxia following demands for a motorcycle by her husband.", "Section 304B"),
        ("Within four years of marriage, the woman was discovered charred to death in her matrimonial home following persistent cruelty by her in-laws demanding gold bangles.", "Section 304B"),
    ]
    for text, exp in dowry_death_templates:
        add_c(c_id, "Dowry Death (IPC 304B)", exp, False, text); c_id += 1

    # --- 16. Criminal Intimidation (IPC 506 / BNS 351) (10 cases) ---
    intimidation_templates = [
        ("The accused called the complainant repeatedly from an unknown number, threatening: 'Drop the lawsuit or I will shoot you dead and burn your house.' No hurt was caused.", "Section 506"),
        ("During a property dispute, the accused brandished an unlicensed revolver, pointed it at the complainant, and threatened to eliminate him if he fenced the plot.", "Section 506"),
        ("The accused sent handwritten letters to the school principal threatening: 'If you fail my son, your family will face acid attacks.' No physical act was committed.", "Section 506"),
        ("The accused stood outside the victim's shop waving a wooden club and shouted that he would break his limbs if he opened the shop tomorrow, causing grave alarm.", "Section 506"),
        ("The accused confronted a witness outside court, pulled a knife from his coat, and threatened: 'If you testify against me, you will not return home alive.'", "Section 506"),
        ("The accused sent recorded voice messages threatening to kidnap the complainant's daughter unless an extortion payment of Rs. 10 lakhs was transferred.", "Section 506"),
        ("The accused cornered a shopkeeper, showed him a bottle of acid, and threatened to disfigure his face if he demanded repayment of the grocery credit.", "Section 506"),
        ("During a heated municipality meeting, the councilor banged the table, produced a country pistol, and threatened to shoot the municipal engineer.", "Section 506"),
        ("The accused threatened an investigative journalist over telephone with dire consequences and physical elimination if he published an expository article.", "Section 506"),
        ("The accused blocked the path of the complainant's car, brandished an iron rod, and threatened to crush his skull if he did not withdraw his police complaint.", "Section 506"),
    ]
    for text, exp in intimidation_templates:
        add_c(c_id, "Criminal Intimidation (IPC 506)", exp, False, text); c_id += 1

    # --- 17. Civil Disputes / Quashable u/s 482 (10 cases) ---
    civil_templates = [
        ("A consulting firm filed an FIR alleging cheating because the client failed to pay three monthly software maintenance invoices totaling Rs. 15 lakhs under an arbitration clause.", "Quashed u/s 482"),
        ("The dispute arises out of a commercial lease agreement where the landlord refused to refund an advance security deposit of Rs. 8 lakhs following early termination.", "Quashed u/s 482"),
        ("A supplier filed a criminal complaint against a retailer for delayed payment of apparel consignments where the parties have an ongoing reconciliation of accounts.", "Quashed u/s 482"),
        ("The parties entered into a master service agreement for web development; when deliverables were delayed, the client lodged an FIR alleging criminal breach of contract.", "Quashed u/s 482"),
        ("A commercial distributor filed an FIR alleging fraud after the manufacturer terminated their dealership agreement in accordance with the 60-day notice clause.", "Quashed u/s 482"),
        ("A buyer filed an FIR alleging cheating when a batch of automotive spares delivered under warranty turned out to be defective, with ongoing commercial replacement talks.", "Quashed u/s 482"),
        ("Two business partners dissolved their partnership firm; partner A filed an FIR alleging partner B did not share book profits according to the partnership deed.", "Quashed u/s 482"),
        ("An enterprise customer lodged a criminal complaint because cloud software experienced server downtime violating the service level agreement credits.", "Quashed u/s 482"),
        ("A contractor filed an FIR alleging cheating after the real estate developer withheld milestone payment pending quality audit certification under the construction contract.", "Quashed u/s 482"),
        ("A vendor filed a criminal case alleging cheating when the buyer claimed an offset for damaged goods and deducted Rs. 5 lakhs from the final commercial invoice.", "Quashed u/s 482"),
    ]
    for text, exp in civil_templates:
        add_c(c_id, "Civil Dispute (Quashable)", exp, False, text); c_id += 1

    # --- 18. Adversarial & Negation Stress Traps (16 cases) ---
    adv_templates = [
        ("The victim was unarmed and walking home. Suddenly the accused jumped out, held a knife to his neck, and forcibly took his wallet.", "Section 392"),
        ("There was no prior enmity, no planning, and no long-standing grudge. During an argument, the accused struck the victim once with an iron pipe, causing death.", "Section 304 Part II"),
        ("The accused ambushed the deceased and stabbed him four times in the chest with a dagger in front of witnesses; the accused claims he was falsely implicated due to politics.", "Section 302"),
        ("The accused deceived twenty investors into handing over Rs. 95 lakhs in cash by promising 50% monthly returns on a cryptocurrency scheme.", "Section 420"),
        ("The complainant was armed with a walking stick, but the accused pulled a loaded pistol and shot him in the chest with intent to kill. The complainant survived emergency surgery.", "Section 307"),
        ("The victim suffered a knife cut certified by the medical officer as simple hurt without fracture or permanent privation.", "Section 324"),
        ("The accused picked up a smartphone lying on the counter without permission, but did not use any force, weapon, or threats during the taking.", "Section 379"),
        ("The accused held a revolver at the cashier's face, demanding all cash, but did not fire any shots and caused no physical hurt.", "Section 392"),
        ("Four men armed with lathis and clubs surrounded the victim and beat him severely, causing fatal fractures in furtherance of common intention.", "Section 304 Part I"),
        ("A woman married for two years was found dead with 80% burn injuries; soon before death, she was beaten for failing to bring a car as dowry.", "Section 304B"),
        ("The accused pointed a firearm at the victim shouting threats of immediate death unless he handed over his motorcycle, which the accused then took.", "Section 392"),
        ("The dispute between the software company and client involves unpaid invoices totaling Rs. 20 lakhs under a contract containing an arbitration clause.", "Quashed u/s 482"),
        ("The accused poured acid on the victim's face, permanently blinding him in both eyes and destroying his facial skin.", "Section 326"),
        ("The accused slapped the security guard across the face after an argument with no weapon used, causing minor redness and pain.", "Section 323"),
        ("A gang of seven armed bandits intercepted a transport truck on the highway, held the driver at gunpoint, and looted goods worth Rs. 50 lakhs.", "Section 395"),
        ("The accused fabricated a forged title deed to illegally sell a deceased owner's land to an innocent buyer for Rs. 40 lakhs.", "Section 468"),
    ]
    for text, exp in adv_templates:
        add_c(c_id, "Adversarial & Negation Stress Trap", exp, False, text); c_id += 1

    # --- 19. Out-of-Domain Non-Legal Rejections (10 cases) ---
    ood_templates = [
        ("The meteorological department forecasts heavy monsoon showers and thunderous squalls across coastal districts with temperatures near 32 celsius and humidity at 90%.", "Abstain"),
        ("Consolidated quarterly EBITDA margins expanded by 240 basis points, while net profit grew 18% year-over-year. The board declared an interim dividend of Rs. 5 per share.", "Abstain"),
        ("The national cricket team defeated their opponents by six wickets in the championship final, with the opening batsman scoring an unbeaten century off 85 deliveries.", "Abstain"),
        ("Preheat the oven to 180 degrees celsius. In a large mixing bowl, whisk together the flour, sugar, baking powder, and unsalted butter until smooth, then bake for 30 minutes.", "Abstain"),
        ("Quantum entanglement demonstrates non-local correlations between entangled photon pairs, violating Bell inequalities and serving as the foundation for quantum computing.", "Abstain"),
        ("Patients suffering from acute seasonal rhinitis exhibited marked symptom relief following once-daily administration of second-generation oral antihistamines in clinical trials.", "Abstain"),
        ("The smartphone features a 6.7-inch AMOLED display with a 120Hz refresh rate, powered by a 4nm octa-core processor and a 5000mAh battery supporting 65W fast charging.", "Abstain"),
        ("To install the package, execute npm install --save-dev in your terminal, configure the webpack build pipeline, and specify the output directory in tsconfig.json.", "Abstain"),
        ("The documentary explores the migratory patterns of humpback whales across Antarctic waters during early spring, highlighting polar navigation techniques.", "Abstain"),
        ("The museum exhibition features impressionist oil paintings from nineteenth-century Parisian artists, emphasizing post-impressionist brushwork and light capture.", "Abstain"),
    ]
    for text, exp in ood_templates:
        add_c(c_id, "Out-of-Domain Abstention", exp, True, text); c_id += 1

    return cases


def run_stress_test_200():
    pipeline = EffectiveLjpPipeline()
    cases = generate_200_test_cases()
    total = len(cases)

    print("\n" + "=" * 105)
    print(f"🔥 EXECUTING 200-CASE COMPREHENSIVE STRESS TEST ON EFFECTIVE LJP V6")
    print("=" * 105)

    passed_count = 0
    failures: List[Dict[str, Any]] = []
    category_stats = defaultdict(lambda: {"total": 0, "passed": 0})
    component_issue_log = defaultdict(list)

    for idx, c in enumerate(cases, start=1):
        res = pipeline.run(c["narrative"])
        cat = c["category"]
        category_stats[cat]["total"] += 1

        is_passed = False
        pred_sec = ""

        if c["should_abstain"]:
            if res.is_abstained:
                is_passed = True
                pred_sec = "ABSTAINED"
            else:
                pred_sec = res.top_articles[0].ipc_section if res.top_articles else "Unknown"
                component_issue_log["Out-of-Domain Screening"].append({
                    "id": c["id"],
                    "case": c["name"] if "name" in c else c["narrative"][:60],
                    "issue": "Failed to abstain on non-penal input",
                    "got": pred_sec
                })
        else:
            if res.is_abstained:
                is_passed = False
                pred_sec = "ABSTAINED (False Rejection)"
                component_issue_log["Out-of-Domain Screening"].append({
                    "id": c["id"],
                    "case": c["narrative"][:60],
                    "issue": "Erroneously abstained on valid legal narrative",
                    "expected": c["expected_ipc"]
                })
            else:
                top_art = res.top_articles[0] if res.top_articles else None
                pred_sec = top_art.ipc_section if top_art else "None"
                exp_sec = c["expected_ipc"].lower()

                if exp_sec in pred_sec.lower() or pred_sec.lower() in exp_sec:
                    is_passed = True
                else:
                    is_passed = False
                    # Diagnostic analysis of which part failed
                    facts = res.atomic_facts
                    reasons = []

                    # Fact extraction check
                    if "302" in exp_sec and not facts.death_caused:
                        reasons.append("FactExtractor: death_caused was False for Murder")
                    if "304 part ii" in exp_sec and not facts.is_sudden_fight:
                        reasons.append("FactExtractor: sudden_fight was False for Exception 4")
                    if "392" in exp_sec and not facts.is_robbery:
                        reasons.append("FactExtractor: is_robbery was False for Robbery")
                    if "307" in exp_sec and "attempt_to_murder" not in facts.extracted_tokens:
                        reasons.append("FactExtractor: attempt_to_murder was not in extracted_tokens")
                    if "406" in exp_sec and not facts.is_breach_of_trust:
                        reasons.append("FactExtractor: is_breach_of_trust was False")
                    if "395" in exp_sec and not facts.is_dacoity:
                        reasons.append("FactExtractor: is_dacoity was False (accused_count < 5)")

                    # Gating check
                    gated_ids = [cand.id for cand in res.retrieved_statutes]
                    expected_id_prefix = exp_sec.replace("section ", "stat_").replace("quashed u/s 482", "stat_civil_482").upper()
                    matched_in_gate = any(expected_id_prefix in gid for gid in gated_ids)
                    if not matched_in_gate:
                        reasons.append("Gating/Retriever: Expected statute was filtered out by Gate or missed by Retriever")
                        for cand in res.filtered_out_candidates:
                            if expected_id_prefix in cand.id:
                                reasons.append(f"Gating Rejection: {cand.rejection_reason}")

                    # Predictor check
                    if matched_in_gate:
                        top3_secs = [a.ipc_section for a in res.top_articles[:3]]
                        reasons.append(f"Predictor/Ranker: Precedence order placed {pred_sec} above {c['expected_ipc']} (Top 3: {top3_secs})")

                    failure_entry = {
                        "id": c["id"],
                        "category": cat,
                        "narrative": c["narrative"][:80] + "...",
                        "expected": c["expected_ipc"],
                        "predicted": pred_sec,
                        "diagnostics": reasons if reasons else ["Ranker scoring overlap"]
                    }
                    failures.append(failure_entry)
                    component_issue_log[cat].append(failure_entry)

        if is_passed:
            passed_count += 1
            category_stats[cat]["passed"] += 1

    accuracy = (passed_count / total) * 100

    print("-" * 105)
    print(f"📊 200-CASE EVALUATION RESULTS:")
    print(f"• Total Evaluated Cases:   {total}")
    print(f"• Total Passed:            {passed_count}")
    print(f"• Total Failed:            {len(failures)}")
    print(f"• Overall Pass Rate:       {accuracy:.1f}%\n")

    print(f"{'Category':<38} | {'Total':<6} | {'Passed':<6} | {'Accuracy'}")
    print("-" * 70)
    for cat, stats in sorted(category_stats.items()):
        cat_acc = (stats["passed"] / max(1, stats["total"])) * 100
        print(f"{cat:<38} | {stats['total']:<6} | {stats['passed']:<6} | {cat_acc:.1f}%")

    if failures:
        print("\n" + "=" * 105)
        print(f"⚠️ DETAILED DIAGNOSTIC LOG OF FAILED CASES ({len(failures)} ISSUES FOUND):")
        print("=" * 105)
        for f in failures:
            print(f"[{f['id']}] {f['category']}")
            print(f"  Narrative: {f['narrative']}")
            print(f"  Expected:  {f['expected']}  -->  Predicted: {f['predicted']}")
            print(f"  Issues Identified: {', '.join(f['diagnostics'])}\n")
    else:
        print("\n✅ Zero failures detected across all 200 cases!")

    return {
        "total": total,
        "passed": passed_count,
        "accuracy": accuracy,
        "failures": failures,
        "category_stats": dict(category_stats)
    }


if __name__ == "__main__":
    run_stress_test_200()
