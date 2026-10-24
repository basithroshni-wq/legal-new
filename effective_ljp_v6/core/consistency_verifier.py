"""
Judicial Consistency Verifier (JCV) for Effective LJP V6.
Enforces statutory sentencing ceilings under Section 31 CrPC / Section 25 BNSS,
applies Exception 4 sudden fight mitigation (reconciling Sec 302 to Sec 304 Part II),
and performs non-mutating deep-copy audits with dynamic JCI score calculation.
Fixes F-10.
"""

import copy
from typing import List, Dict, Any, Tuple
from .schemas import (
    ArticlePrediction,
    ChargePrediction,
    PenaltyPrediction,
    JudicialAuditReport,
    AtomicFacts
)


class JudicialConsistencyVerifier:
    """Symbolic legal guardrail auditing statutory ceilings, floors, and Exception 4 reconciliations."""

    def __init__(self):
        self.tier_hierarchy = {
            "Quashed (No Penal Term)": 0,
            "Tier 1 (Up to 3 Years)": 3,
            "Tier 2 (3 to 7 Years)": 7,
            "Tier 3 (7 to 10 Years)": 10,
            "Tier 4 (Life Imprisonment / Capital)": 99
        }

    def verify_and_reconcile(
        self,
        articles: List[ArticlePrediction],
        charges: List[ChargePrediction],
        penalty: PenaltyPrediction,
        facts: AtomicFacts
    ) -> Tuple[List[ArticlePrediction], List[ChargePrediction], PenaltyPrediction, JudicialAuditReport]:
        """
        Audits predictions for statutory validity without mutating caller objects.
        Returns:
            (reconciled_articles, reconciled_charges, reconciled_penalty, audit_report)
        """
        # Non-mutating deep copies (F-10 fix)
        rec_articles = copy.deepcopy(articles)
        rec_charges = copy.deepcopy(charges)
        rec_penalty = copy.deepcopy(penalty)

        jci_score = 100.0
        deductions: List[Dict[str, Any]] = []
        reconciliations: List[str] = []

        if not rec_articles:
            report = JudicialAuditReport(
                initial_jci_score=100.0,
                final_jci_score=100.0,
                compliance_status="ABSTAINED",
                deductions=[],
                reconciliations=["No penal provisions attracted; proceeding quashed or abstained."],
                is_statutorily_sound=True
            )
            return rec_articles, rec_charges, rec_penalty, report

        top_article = rec_articles[0]

        # --- Audit 1: Exception 4 Sudden Fight Homicide Reconciliation ---
        # If sudden fight / heat of passion without premeditation, Section 302 MUST be converted to Section 304 Part II
        if facts.death_caused and facts.is_sudden_fight and not facts.has_premeditation:
            if "302" in top_article.ipc_section:
                deductions.append({
                    "type": "Exception 4 Violation",
                    "penalty": 10.0,
                    "description": "Section 302 IPC assigned despite verified absence of premeditation in sudden quarrel."
                })
                jci_score -= 10.0

                # Reconcile Head 1
                top_article.ipc_section = "Section 304 Part II"
                top_article.bns_section = "Section 105"
                top_article.display_name = "Section 304 Part II | Section 105 (Culpable Homicide - Sudden Fight)"
                top_article.charge_category = "Culpable Homicide (Sudden Fight)"
                top_article.statutory_ceiling_tier = "Tier 3 (7 to 10 Years)"

                reconciliations.append(
                    "Reconciled Section 302 to Section 304 Part II under Exception 4 to Section 300 IPC (Pulicherla Nagaraju principle)."
                )

                # Reconcile Head 2 charges
                if rec_charges:
                    rec_charges[0].charge_name = "Culpable Homicide (Sudden Fight)"

                # Reconcile Head 3 penalty
                if "Tier 4" in rec_penalty.predicted_tier:
                    rec_penalty.predicted_tier = "Tier 3 (7 to 10 Years)"
                    rec_penalty.statutory_ceiling_years = 10
                    rec_penalty.reconciled_by_jcv = True
                    reconciliations.append(
                        "Lowered statutory sentencing ceiling from Tier 4 (Life) to Tier 3 (10 Years) under Section 304 Part II."
                    )

        # --- Audit 2: Statutory Ceiling Audit (CrPC 31 / BNSS 25) ---
        authorized_ceiling_years = self._get_statutory_max_years(top_article.ipc_section)
        pred_tier_years = self.tier_hierarchy.get(rec_penalty.predicted_tier, 0)
        authorized_tier = self._years_to_tier(authorized_ceiling_years)
        authorized_tier_years = self.tier_hierarchy.get(authorized_tier, 0)

        if pred_tier_years > authorized_tier_years and authorized_tier_years > 0:
            deductions.append({
                "type": "Statutory Ceiling Breach",
                "penalty": 20.0,
                "description": f"Predicted penalty '{rec_penalty.predicted_tier}' exceeds statutory maximum ({authorized_ceiling_years} years) for {top_article.ipc_section}."
            })
            jci_score -= 20.0

            # Reconcile penalty tier down to the statutory maximum
            rec_penalty.predicted_tier = authorized_tier
            rec_penalty.statutory_ceiling_years = authorized_ceiling_years
            rec_penalty.reconciled_by_jcv = True
            reconciliations.append(
                f"Statutory ceiling enforced under Section 31 CrPC / Section 25 BNSS: penalty capped at {authorized_tier}."
            )

        if "304a" in top_article.ipc_section.lower() or "354a" in top_article.ipc_section.lower() or "500" in top_article.ipc_section.lower():
            rec_penalty.is_bailable = True

        # Re-sort Head 3 tier probabilities cleanly
        # Ensure consistency flag
        is_sound = (jci_score >= 80.0)
        status = "COMPLIANT" if jci_score == 100.0 else "RECONCILED" if reconciliations else "NON-COMPLIANT"

        report = JudicialAuditReport(
            initial_jci_score=round(jci_score + sum(d["penalty"] for d in deductions), 1),
            final_jci_score=round(max(0.0, min(100.0, jci_score)), 1),
            compliance_status=status,
            deductions=deductions,
            reconciliations=reconciliations,
            is_statutorily_sound=is_sound
        )

        return rec_articles, rec_charges, rec_penalty, report

    def _get_statutory_max_years(self, ipc_section: str) -> int:
        """Returns statutory maximum years allowed under statute."""
        sec = ipc_section.lower()
        if "302" in sec or "376" in sec or "304b" in sec or "395" in sec or "326" in sec or "307" in sec or "394" in sec or "pocso" in sec or "364a" in sec or "304 part i" in sec or "304_p1" in sec or "409" in sec or "436" in sec or "489a" in sec:
            return 99  # Life imprisonment
        if "ndps" in sec:
            return 20
        if "457" in sec:
            return 14
        if "304 part ii" in sec or "392" in sec or "306" in sec:
            return 10
        if "420" in sec or "468" in sec or "471" in sec or "408" in sec or "304a" in sec or "380" in sec or "pc act" in sec or "corruption" in sec or "arms" in sec or "363" in sec or "201" in sec:
            return 7
        if "379" in sec or "406" in sec or "498a" in sec or "324" in sec or "354a" in sec or "384" in sec or "66d" in sec or "153a" in sec or "354d" in sec:
            return 3
        if "506" in sec or "500" in sec or "138" in sec:
            return 2
        if "323" in sec or "447" in sec:
            return 1
        if "482" in sec or "civil" in sec:
            return 0
        return 7

    def _years_to_tier(self, years: int) -> str:
        """Maps max years to canonical penalty tier string."""
        if years >= 20:
            return "Tier 4 (Life Imprisonment / Capital)"
        if years >= 10:
            return "Tier 3 (7 to 10 Years)"
        if years >= 7:
            return "Tier 2 (3 to 7 Years)"
        if years >= 1:
            return "Tier 1 (Up to 3 Years)"
        return "Quashed (No Penal Term)"
