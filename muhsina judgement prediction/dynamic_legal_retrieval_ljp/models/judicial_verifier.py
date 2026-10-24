import copy
"""
Judicial Consistency Verifier (JCV) Module for DLKR-LJP.
A post-inference architectural validation and reconciliation layer that:
1. Audits cross-head statutory consistency between Articles (Head 1), Charges (Head 2), and Sentencing Tiers (Head 3).
2. Enforces statutory sentencing ceilings and floors under the Indian Penal Code (IPC 1860) and Bharatiya Nyaya Sanhita (BNS 2023) across all 20 sections.
3. Anchors primary penalties to highest verified offense while providing compound sentence guidance under Section 31 CrPC / Section 25 BNSS.
4. Produces a calibrated Judicial Consistency Index (JCI) and auditable reconciliation log.
"""

from typing import Dict, List, Any, Tuple, Optional
import config
from gating.fact_factorizer import AtomicCaseFacts


# Statutory Maximum Sentencing Ceiling & Authorized Tiers Map for ALL 20 sections
STATUTORY_PENALTY_BOUNDS: Dict[str, Dict[str, Any]] = {
    # 1. Homicide & Violent Offences
    "IPC_302_BNS_103": {
        "max_imprisonment": "Death or Life Imprisonment",
        "authorized_tiers": ["Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"],
        "statutory_floor": "Life Imprisonment (Mandatory minimum unless exceptional)",
        "statutory_ceiling": "Death Penalty"
    },
    "IPC_304_PART1_BNS_105": {
        "max_imprisonment": "Imprisonment for life or up to 10 years",
        "authorized_tiers": [
            "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
            "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Life Imprisonment / 10 Years"
    },
    "IPC_304_PART2_BNS_105": {
        "max_imprisonment": "10 Years Imprisonment",
        "authorized_tiers": [
            "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Strict 10-Year Statutory Ceiling"
    },
    "IPC_307_BNS_109": {
        "max_imprisonment": "10 Years (or Life if hurt is caused)",
        "authorized_tiers": [
            "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
            "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
            "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "10-Year Baseline / Life if hurt caused (Tier 3/4)"
    },
    "IPC_326_BNS_118": {
        "max_imprisonment": "10 Years Imprisonment or Life Imprisonment",
        "authorized_tiers": [
            "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
            "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
            "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Life / 10-Year Statutory Ceiling"
    },
    "IPC_324_BNS_117": {
        "max_imprisonment": "3 Years Imprisonment",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Strict 3-Year Ceiling (Tier 1)"
    },
    "IPC_324_BNS_118": {
        "max_imprisonment": "3 Years Imprisonment (BNS 118(1))",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Strict 3-Year Ceiling (Tier 1)"
    },
    "IPC_323_BNS_115": {
        "max_imprisonment": "1 Year Imprisonment",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Strict 1-Year Ceiling (Tier 1)"
    },

    # 2. Property & Theft / Robbery
    "IPC_379_BNS_303": {
        "max_imprisonment": "3 Years Imprisonment",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Strict 3-Year Ceiling (Tier 1)"
    },
    "IPC_392_BNS_309": {
        "max_imprisonment": "10 Years Imprisonment (14 Years on Highway)",
        "authorized_tiers": [
            "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "10-Year Statutory Ceiling (Tier 3)"
    },
    "IPC_406_BNS_316": {
        "max_imprisonment": "3 Years Imprisonment",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Strict 3-Year Ceiling (Tier 1)"
    },

    # 3. Commercial & Document Fraud
    "IPC_420_BNS_318": {
        "max_imprisonment": "7 Years Imprisonment",
        "authorized_tiers": [
            "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Strict 7-Year Ceiling (Arnesh Kumar Notice Mandatory)"
    },
    "IPC_467_BNS_338": {
        "max_imprisonment": "10 Years or Life Imprisonment",
        "authorized_tiers": [
            "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
            "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
            "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Life / 10 Years Ceiling"
    },
    "IPC_468_BNS_336": {
        "max_imprisonment": "7 Years Imprisonment",
        "authorized_tiers": [
            "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Strict 7-Year Ceiling (Tier 2)"
    },
    "IPC_471_BNS_340": {
        "max_imprisonment": "Same as Forgery (2 to 7 Years)",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
            "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Punishment as Forged Document"
    },

    # 4. Offences Against Women & Sexual
    "IPC_498A_BNS_85": {
        "max_imprisonment": "3 Years Imprisonment",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Strict 3-Year Ceiling (Arnesh Kumar Guidelines Apply)"
    },
    "IPC_304B_BNS_80": {
        "max_imprisonment": "Life Imprisonment (Minimum 7 Years)",
        "authorized_tiers": [
            "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
            "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"
        ],
        "statutory_floor": "Strict Mandatory Minimum of 7 Years",
        "statutory_ceiling": "Life Imprisonment"
    },
    "IPC_376_BNS_64": {
        "max_imprisonment": "Life Imprisonment (Minimum 10 Years)",
        "authorized_tiers": [
            "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"
        ],
        "statutory_floor": "Strict Mandatory Minimum of 10 Years",
        "statutory_ceiling": "Life Imprisonment / Death"
    },

    # 5. Intimidation & Inchoate / Conspiracy
    "IPC_506_BNS_351": {
        "max_imprisonment": "2 Years (Part I) / 7 Years (Part II - Threat to Cause Death)",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
            "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "7-Year Ceiling for Death Threat (Tier 2)"
    },
    "IPC_120B_BNS_61": {
        "max_imprisonment": "Tracks Principal Offence Conspired",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
            "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
            "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
            "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Principal Offence Maximum"
    },
    "IPC_34_BNS_3": {
        "max_imprisonment": "Tracks Principal Offence in Furtherance of Common Intention",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
            "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
            "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
            "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"
        ],
        "statutory_floor": "None",
        "statutory_ceiling": "Principal Offence Maximum"
    },

    # Civil / Exculpatory Quashing
    "NONE_CIVIL_DISPUTE": {
        "max_imprisonment": "0 Years (No Penal Provision Attracted / Quashed u/s 482)",
        "authorized_tiers": [
            "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)"
        ],
        "statutory_floor": "0 Days (Discharge / Acquittal)",
        "statutory_ceiling": "No Penal Deprivation Permitted"
    }
}


TIER_LEVEL_ORDINAL = {
    "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)": 1,
    "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)": 2,
    "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)": 3,
    "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)": 4,
}

class JudicialConsistencyVerifier:
    """
    Audits predictions from all 3 heads for statutory legality,
    detects ceiling violations, and reconciles contradictions.
    """

    def __init__(self):
        self.bounds_map = STATUTORY_PENALTY_BOUNDS

    def verify_and_reconcile(
        self,
        predictions: Dict[str, Any],
        atomic_facts: Optional[AtomicCaseFacts] = None
    ) -> Dict[str, Any]:
        """
        Runs complete statutory audit (F-10, F-11, F-06):
        1. Audits primary penalty tier against statutory ceiling using ordinal tiers.
        2. Detects Exception 4 and reconciles Head 1, Head 2, and Head 3 simultaneously.
        3. Uses deep copies to protect caller state.
        4. Re-sorts all updated heads descending by probability.
        5. Computes dynamic calibrated Judicial Consistency Index (JCI).
        """
        head1_articles = copy.deepcopy(predictions.get("head1_articles", []))
        head2_charges = copy.deepcopy(predictions.get("head2_charges", []))
        head3_tiers = copy.deepcopy(predictions.get("head3_penalty_tiers", []))
        primary_penalty = copy.deepcopy(predictions.get("primary_penalty", {}))

        # Check for Out of Domain
        if predictions.get("is_out_of_domain") or (atomic_facts and atomic_facts.is_out_of_domain):
            return {
                "head1_articles": head1_articles,
                "head2_charges": head2_charges,
                "head3_penalty_tiers": head3_tiers,
                "primary_penalty": primary_penalty,
                "backbone": predictions.get("backbone", config.BACKBONE_MODEL_NAME),
                "is_exculpatory": False,
                "is_out_of_domain": True,
                "atomic_facts": atomic_facts or predictions.get("atomic_facts"),
                "judicial_consistency_audit": {
                    "audit_status": "OUT OF DOMAIN / NON-COGNIZABLE",
                    "conflicts_detected": [],
                    "judicial_consistency_index": 100.0,
                    "penalty_ceiling_status": "N/A (No Penal Provision Attracted)",
                    "actions_taken": ["Abstained from criminal adjudication on non-cognizable narrative."]
                },
                "is_statutorily_valid": True,
                "judicial_consistency_index": 100.0,
                "reconciliation_applied": False,
                "audit_log": []
            }

        top_article_item = head1_articles[0] if head1_articles else None
        top_art_id = top_article_item["article_id"] if top_article_item else "UNKNOWN"
        top_charge_item = head2_charges[0] if head2_charges else None
        top_charge_name = top_charge_item["charge_name"] if top_charge_item else "UNKNOWN"
        predicted_tier = primary_penalty.get("tier", "")

        audit_log: List[Dict[str, Any]] = []
        is_reconciled = False
        reconciled_tier = predicted_tier
        penalty_ceiling_status = "COMPLIANT"

        # ---------------- AUDIT 1: STATUTORY PENALTY CEILING ENFORCEMENT (Ordinal Comparison) ----------------
        bounds = self.bounds_map.get(top_art_id)
        if bounds:
            authorized_tiers = bounds["authorized_tiers"]
            stat_ceiling = bounds["statutory_ceiling"]
            stat_floor = bounds.get("statutory_floor", "None")

            auth_levels = [TIER_LEVEL_ORDINAL.get(t, 0) for t in authorized_tiers if t in TIER_LEVEL_ORDINAL]
            max_auth_level = max(auth_levels) if auth_levels else 4
            min_auth_level = min(auth_levels) if auth_levels else 1
            pred_level = TIER_LEVEL_ORDINAL.get(predicted_tier, 0)

            if pred_level > max_auth_level:
                # Exceeds statutory ceiling -> reconcile to highest authorized tier
                is_reconciled = True
                valid_tiers_sorted = sorted(authorized_tiers, key=lambda t: TIER_LEVEL_ORDINAL.get(t, 0), reverse=True)
                reconciled_tier = valid_tiers_sorted[0]
                penalty_ceiling_status = "RECONCILED_CEILING_EXCEEDED"
                audit_log.append({
                    "rule": "STATUTORY_CEILING_ENFORCEMENT",
                    "severity": "CRITICAL",
                    "finding": f"Predicted penalty '{predicted_tier}' exceeds statutory ceiling for {top_art_id} ({stat_ceiling}).",
                    "action": f"Reconciled primary penalty downward to authorized statutory tier: '{reconciled_tier}'."
                })
            elif pred_level < min_auth_level and stat_floor != "None":
                # Falls below statutory mandatory floor -> reconcile upward
                is_reconciled = True
                valid_tiers_sorted = sorted(authorized_tiers, key=lambda t: TIER_LEVEL_ORDINAL.get(t, 0))
                reconciled_tier = valid_tiers_sorted[0]
                penalty_ceiling_status = "RECONCILED_FLOOR_VIOLATION"
                audit_log.append({
                    "rule": "STATUTORY_FLOOR_ENFORCEMENT",
                    "severity": "CRITICAL",
                    "finding": f"Predicted penalty '{predicted_tier}' falls below mandatory statutory floor for {top_art_id} ({stat_floor}).",
                    "action": f"Reconciled primary penalty upward to authorized statutory tier: '{reconciled_tier}'."
                })
            else:
                audit_log.append({
                    "rule": "STATUTORY_CEILING_ENFORCEMENT",
                    "severity": "VERIFIED",
                    "finding": f"Predicted tier '{predicted_tier}' is statutorily authorized under {top_art_id} (Ceiling: {stat_ceiling}).",
                    "action": "Preserved predicted tier as legally compliant."
                })
        else:
            if top_art_id not in ["NONE_CIVIL_DISPUTE", "NONE_OUT_OF_DOMAIN"]:
                audit_log.append({
                    "rule": "ARTICLE_BOUND_CHECK",
                    "severity": "WARNING",
                    "finding": f"Article identifier '{top_art_id}' not explicitly mapped in statutory bounds table.",
                    "action": "Applied general penal code safeguards."
                })

        # ---------------- AUDIT 2: MULTI-OFFENCE COMPOUND SENTENCING (CrPC 31 / BNSS 25) ----------------
        if len(head1_articles) > 1:
            secondary_articles = [a for a in head1_articles[1:3] if a.get("probability", 0) >= 0.65]
            if secondary_articles:
                sec_names = [s.get("display_name", s.get("article_id", "")) for s in secondary_articles]
                audit_log.append({
                    "rule": "COMPOUND_SENTENCING_GUIDANCE (CrPC 31 / BNSS 25)",
                    "severity": "INFORMATIVE",
                    "finding": f"Concomitant offences detected: {', '.join(sec_names)}.",
                    "action": f"Primary penalty anchored to highest verified offence ({reconciled_tier}). Sentences may run concurrently or consecutively under judicial discretion."
                })

        # ---------------- AUDIT 3: EXCEPTION 4 SUDDEN FIGHT CHECK ----------------
        if atomic_facts and (atomic_facts.is_heat_of_passion or (atomic_facts.is_sudden_fight and (atomic_facts.single_blow or atomic_facts.weapon_source == "Found at Spot / Casual"))):
            if "302" in top_art_id and not "304" in top_art_id:
                is_reconciled = True
                top_art_id = "IPC_304_PART2_BNS_105"
                reconciled_tier = "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)"
                audit_log.append({
                    "rule": "EXCEPTION_4_CONVERSION",
                    "severity": "CRITICAL",
                    "finding": "Sudden fight / heat of passion without premeditation precludes Section 302 Murder.",
                    "action": "Converted primary offence to Section 304 Part II (Tier 3: 7 to 10 Years)."
                })

                # Re-rank Head 1 articles to place 304 Part II at the top
                exc4_art = None
                for a in head1_articles:
                    if "304_PART2" in a.get("article_id", ""):
                        exc4_art = a
                        break
                if exc4_art:
                    exc4_art["probability"] = 0.9400
                else:
                    head1_articles.append({
                        "article_id": "IPC_304_PART2_BNS_105",
                        "display_name": "IPC 304 Part II | BNS 105",
                        "probability": 0.9400,
                        "gated_evidence": True,
                        "alignment_score": 0.95
                    })
                # Lower Section 302 probability
                for a in head1_articles:
                    if "302" in a.get("article_id", "") and "304" not in a.get("article_id", ""):
                        a["probability"] = 0.3500
                head1_articles.sort(key=lambda x: x["probability"], reverse=True)

                # Re-rank Head 2 charges
                for c in head2_charges:
                    if "Sudden Fight" in c.get("charge_name", ""):
                        c["probability"] = 0.9400
                head2_charges.sort(key=lambda x: x["probability"], reverse=True)

        # ---------------- AUDIT 4: CALCULATE JUDICIAL CONSISTENCY INDEX (JCI) ----------------
        jci_score = 100.0
        critical_count = sum(1 for a in audit_log if a["severity"] == "CRITICAL")
        warning_count = sum(1 for a in audit_log if a["severity"] == "WARNING")
        
        if is_reconciled:
            # Reconciled violations incur a slight index adjustment
            jci_score = max(70.0, 100.0 - (critical_count * 5.0) - (warning_count * 2.0))
        elif critical_count > 0:
            jci_score = max(50.0, 100.0 - (critical_count * 20.0) - (warning_count * 5.0))
        else:
            jci_score = max(90.0, 100.0 - (warning_count * 3.0))

        reconciled_primary_penalty = {
            "tier": reconciled_tier,
            "probability": primary_penalty.get("probability", 0.85) if not is_reconciled else 0.8800
        }

        # Update Head 3 distribution if reconciled (F-10: deep copy and re-sort)
        reconciled_head3 = copy.deepcopy(head3_tiers)
        if is_reconciled:
            for t in reconciled_head3:
                if t["tier"] == reconciled_tier:
                    t["probability"] = 0.8800
                else:
                    t["probability"] = 0.0400
            tot = sum(t["probability"] for t in reconciled_head3)
            for t in reconciled_head3:
                t["probability"] = round(t["probability"] / tot, 4)

        # Ensure Head 3 is always sorted descending by probability
        reconciled_head3.sort(key=lambda x: x["probability"], reverse=True)

        conflicts_list = [a["finding"] for a in audit_log if a["severity"] == "CRITICAL"]
        audit_status = "RECONCILED BY JCV" if is_reconciled else "STATUTORILY COMPLIANT"

        audit_payload = {
            "audit_status": audit_status,
            "conflicts_detected": conflicts_list,
            "judicial_consistency_index": round(jci_score, 1),
            "penalty_ceiling_status": penalty_ceiling_status,
            "actions_taken": [a["action"] for a in audit_log]
        }

        return {
            "head1_articles": head1_articles,
            "head2_charges": head2_charges,
            "head3_penalty_tiers": reconciled_head3,
            "primary_penalty": reconciled_primary_penalty,
            "backbone": predictions.get("backbone", config.BACKBONE_MODEL_NAME),
            "is_exculpatory": predictions.get("is_exculpatory", False),
            "is_out_of_domain": predictions.get("is_out_of_domain", False),
            "atomic_facts": atomic_facts or predictions.get("atomic_facts"),
            "judicial_consistency_audit": audit_payload,
            "is_statutorily_valid": True,
            "judicial_consistency_index": round(jci_score, 1),
            "reconciliation_applied": is_reconciled,
            "audit_log": audit_log,
            "reconciled_predictions": {
                "head1_articles": head1_articles,
                "head2_charges": head2_charges,
                "head3_penalty_tiers": reconciled_head3,
                "primary_penalty": reconciled_primary_penalty
            }
        }
