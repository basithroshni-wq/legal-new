"""
Comprehensive 8-Domain Accuracy & Judicial Consistency Benchmark Suite for DLKR-LJP.
Validates all 20 configured IPC 1860 & BNS 2023 criminal sections across:
1. Homicide: Murder (302) vs Culpable Homicide Exception 4 (304 Part II)
2. Attempt & Grievous Assault: Attempt to Murder (307) vs Grievous Weapon Hurt (326)
3. Bodily Hurt: Dangerous Weapon Hurt (324) vs Simple Hurt (323)
4. Property & Force: Theft (379) vs Robbery (392) vs Criminal Breach of Trust (406)
5. Financial Fraud & Forgery: Cheating (420) vs Forged Valuable Security (467) vs Civil Quashing u/s 482
6. Offences Against Women: Matrimonial Cruelty (498A) vs Dowry Death (304B)
7. Criminal Intimidation: Death Threats (506 Part II)
8. Sexual Offences: Rape & Sexual Assault (376)
"""

import unittest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import DynamicLjpPipeline


class TestAllSectionsAccuracy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pipeline = DynamicLjpPipeline(load_transformer=False)

    def test_domain_1_premeditated_murder(self):
        """Domain 1A: Premeditated cold-blooded murder -> IPC 302 / Tier 4."""
        facts = "The accused harbored a long-standing property grudge, armed himself with an axe beforehand, ambushed the victim alone at night, and hacked him to death on the spot."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]
        jcv = res["predictions"]["judicial_consistency_audit"]

        self.assertIn("302", top_art)
        self.assertIn("Murder", top_chg)
        self.assertIn("Tier 4", primary_tier)
        self.assertEqual(jcv["audit_status"], "STATUTORILY COMPLIANT")

    def test_domain_1_culpable_homicide_exception_4(self):
        """Domain 1B: Sudden fight upon sudden quarrel with casual weapon -> IPC 304 Part II / Tier 3."""
        facts = "During a sudden quarrel over wages, the contractor picked up an iron rod lying nearby and struck once on the labourer's head in the heat of passion. The labourer died next morning. No prior animosity or planning."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("304 Part II", top_art)
        self.assertNotIn("302", top_art)
        self.assertIn("Culpable Homicide", top_chg)
        self.assertIn("Tier 3", primary_tier)

    def test_domain_2_attempt_to_murder(self):
        """Domain 2: Firing gunshot intending death, victim survived -> IPC 307 / Tier 3."""
        facts = "The accused fired two pistol shots point blank aiming at the victim's chest with intent to kill. The victim received emergency surgical treatment and survived the murderous attack."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("307", top_art)
        self.assertNotIn("302", top_art)
        self.assertIn("Attempt to Murder", top_chg)
        self.assertIn("Tier 3", primary_tier)

    def test_domain_3_dangerous_weapon_hurt_vs_simple(self):
        """Domain 3A: Stabbing forearm with sharp knife causing laceration -> IPC 324 / Tier 1."""
        facts = "The accused attacked the victim with a sharp knife causing a deep bleeding laceration on the forearm. The victim was treated with stitches and discharged from hospital as injuries were non-fatal and non-grievous."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("324", top_art)
        self.assertIn("Tier 1", primary_tier)

    def test_domain_3_simple_hurt_unarmed(self):
        """Domain 3B: Unarmed slapping and fist blows -> IPC 323 / Tier 1."""
        facts = "The accused slapped the complainant and beat him with bare fists causing simple bruises and contusions on the face. No weapon was used and no bones were fractured."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("323", top_art)
        self.assertIn("Tier 1", primary_tier)

    def test_domain_4_theft_unarmed(self):
        """Domain 4A: Dishonest theft of movable property without force -> IPC 379 / Tier 1."""
        facts = "The accused dishonestly stole a gold necklace from the passenger's handbag without consent while traveling on an interstate bus, moving the property away quietly."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("379", top_art)
        self.assertNotIn("392", top_art)
        self.assertIn("Theft", top_chg)
        self.assertIn("Tier 1", primary_tier)

    def test_domain_4_robbery_at_knifepoint(self):
        """Domain 4B: Theft accompanied by brandishing deadly weapon / threat of death -> IPC 392 / Tier 3."""
        facts = "The accused accosted the commuter on an isolated street, brandished a large knife at his throat, and forcibly extorted his wallet, cash, and smartphone under threat of instant death."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("392", top_art)
        self.assertIn("Theft & Dacoity", top_chg)
        self.assertIn("Tier 3", primary_tier)

    def test_domain_4_criminal_breach_of_trust(self):
        """Domain 4C: Lawful entrustment followed by dishonest conversion -> IPC 406 / Tier 1."""
        facts = "The company entrusted funds amounting to ten lakhs to the accounts manager for tax deposit. The manager dishonestly converted the money to his personal bank account and misappropriated the entire sum."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("406", top_art)
        self.assertIn("Tier 1", primary_tier)

    def test_domain_5_cheating_financial_fraud(self):
        """Domain 5A: Fraudulent deception inducing investment -> IPC 420 / Tier 2."""
        facts = "The accused induced innocent victims to invest 50 lakhs in a fictitious real estate scheme with dishonest intention from the very inception, absconding after receiving the funds."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("420", top_art)
        self.assertIn("Cheating", top_chg)
        self.assertIn("Tier 2", primary_tier)

    def test_domain_5_forged_valuable_security(self):
        """Domain 5B: Forgery of valuable security / will / title deed -> IPC 467 / Tier 3."""
        facts = "The accused fabricated a forged will and valuable security by placing counterfeit signatures of the deceased landowner to usurp ancestral agricultural property."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("467", top_art)
        self.assertIn("Tier 3", primary_tier)

    def test_domain_5_civil_quashing(self):
        """Domain 5C: Pure commercial breach without fraud -> Quashing u/s 482 / No Penal Provision."""
        facts = "The complainant filed a criminal complaint over unpaid consulting invoices and delay in delivery of software source code. The dispute was purely civil and breach of contract only with no criminal offence made out."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        self.assertTrue(res["predictions"]["is_exculpatory"])
        self.assertIn("Civil", top_art)
        self.assertIn("No Criminal Offence", top_chg)

    def test_domain_6_matrimonial_cruelty_vs_dowry_death(self):
        """Domain 6A: Matrimonial cruelty without fatal death -> IPC 498A / Tier 1."""
        facts = "The husband and mother-in-law subjected the woman to continuous physical harassment and cruelty demanding two lakhs in additional dowry. The victim approached the police for protection."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("498A", top_art)
        self.assertIn("Matrimonial Cruelty", top_chg)
        self.assertIn("Tier 1", primary_tier)

    def test_domain_6_dowry_death(self):
        """Domain 6B: Unnatural death within 7 years of marriage linked to dowry -> IPC 304B / Tier 3."""
        facts = "Within three years of marriage, the young bride died of severe burn injuries under abnormal circumstances at her matrimonial home soon after persistent harassment and torture for dowry."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("304B", top_art)
        self.assertIn("Dowry Death", top_chg)
        self.assertIn("Tier 3", primary_tier)

    def test_domain_7_criminal_intimidation(self):
        """Domain 7: Death threat to witness -> IPC 506 Part II / Tier 2."""
        facts = "The accused confronted the eyewitness outside the courtroom, brandished an iron knuckle, and threatened to kill him and murder his entire family if he testified in court."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("506", top_art)
        self.assertIn("Criminal Intimidation", top_chg)
        self.assertIn("Tier 2", primary_tier)

    def test_domain_8_sexual_offence_rape(self):
        """Domain 8: Penetrative sexual assault without consent -> IPC 376 / Tier 4."""
        facts = "The accused physically overpowered the victim in an isolated building and committed non-consensual penetrative sexual assault and rape against her will."
        res = self.pipeline.run(facts)
        top_art = res["predictions"]["head1_articles"][0]["display_name"]
        top_chg = res["predictions"]["head2_charges"][0]["charge_name"]
        primary_tier = res["predictions"]["primary_penalty"]["tier"]

        self.assertIn("376", top_art)
        self.assertIn("Sexual Offences", top_chg)
        self.assertIn("Tier 4", primary_tier)


if __name__ == "__main__":
    unittest.main()
