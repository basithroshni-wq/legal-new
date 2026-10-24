"""
Dynamic Evaluation Metrics Calculator for Effective LJP V6.
Executes live evaluations over the 22-case benchmark suite and computes:
- Primary Accuracy (%)
- Macro F1-Score (%)
- Top-3 Recall (%)
- JCI Compliance Rate (%)
- Adversarial Pass Rate (%)
- Out-of-Domain Precision (%)
Zero hardcoded results!
"""

import sys
from typing import Dict, Any, List
try:
    from .benchmark_suite import BENCHMARK_CASES
    from ..core.pipeline import EffectiveLjpPipeline
except (ImportError, ValueError):
    from eval.benchmark_suite import BENCHMARK_CASES
    from core.pipeline import EffectiveLjpPipeline

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def run_benchmark_evaluation(pipeline: EffectiveLjpPipeline = None) -> Dict[str, Any]:
    """Runs complete evaluation across all 22 benchmark cases and prints dynamic scorecard."""
    if pipeline is None:
        pipeline = EffectiveLjpPipeline()

    total_cases = len(BENCHMARK_CASES)
    correct_primary = 0
    correct_top3 = 0
    correct_tier = 0
    correct_abstention = 0
    total_ood = 0
    total_adv = 0
    correct_adv = 0
    jci_scores: List[float] = []

    results_table: List[Dict[str, Any]] = []

    # Category-level counters for Macro F1
    classes = set(c["expected_ipc"] for c in BENCHMARK_CASES if not c["should_abstain"])
    tp_map = {c: 0 for c in classes}
    fp_map = {c: 0 for c in classes}
    fn_map = {c: 0 for c in classes}

    print("\n" + "=" * 105)
    print("⚖️  EFFECTIVE LJP V6 - DYNAMIC BENCHMARK EVALUATION (22 HELD-OUT SCENARIOS)")
    print("=" * 105)
    print(f"{'#':<3} | {'Case Name':<32} | {'Expected Section':<18} | {'Predicted Top Article':<22} | {'Tier':<8} | {'JCI':<5} | {'Status'}")
    print("-" * 105)

    for idx, case in enumerate(BENCHMARK_CASES, start=1):
        res = pipeline.run(case["narrative"])
        is_ood = case["should_abstain"]

        if is_ood:
            total_ood += 1
            if res.is_abstained:
                correct_abstention += 1
                correct_primary += 1
                status = "✅ PASS (OOD)"
                pred_sec = "ABSTAINED"
                pred_tier = "None"
            else:
                status = "❌ FAIL (Did not abstain)"
                pred_sec = res.top_articles[0].ipc_section if res.top_articles else "Unknown"
                pred_tier = res.penalty_prediction.predicted_tier[:8]
            jci_val = 100.0
        else:
            jci_val = res.judicial_audit.final_jci_score
            jci_scores.append(jci_val)

            top_art = res.top_articles[0] if res.top_articles else None
            top_3_secs = [a.ipc_section.lower() for a in res.top_articles[:3]]
            pred_sec = top_art.ipc_section if top_art else "None"
            pred_tier = res.penalty_prediction.predicted_tier[:8]
            expected_sec = case["expected_ipc"].lower()

            is_match = (expected_sec in pred_sec.lower()) or (pred_sec.lower() in expected_sec)
            in_top3 = any(expected_sec in s for s in top_3_secs)

            if is_match:
                correct_primary += 1
                status = "✅ PASS"
                if case["expected_ipc"] in tp_map:
                    tp_map[case["expected_ipc"]] += 1
            else:
                status = "❌ FAIL"
                if case["expected_ipc"] in fn_map:
                    fn_map[case["expected_ipc"]] += 1
                # FP attribution
                for c in classes:
                    if c.lower() in pred_sec.lower():
                        fp_map[c] += 1

            if in_top3:
                correct_top3 += 1

            if case["expected_tier"].split()[0] in res.penalty_prediction.predicted_tier:
                correct_tier += 1

            # Adversarial tracking
            if "ADV" in case["id"]:
                total_adv += 1
                if is_match:
                    correct_adv += 1

        print(f"{idx:<3} | {case['name'][:32]:<32} | {case['expected_ipc']:<18} | {pred_sec[:22]:<22} | {pred_tier:<8} | {jci_val:<5.1f} | {status}")

        results_table.append({
            "id": case["id"],
            "name": case["name"],
            "expected_ipc": case["expected_ipc"],
            "predicted_ipc": pred_sec,
            "status": status,
            "jci": jci_val
        })

    # Compute Macro F1 across non-OOD penal classes
    f1_list = []
    for c in classes:
        tp = tp_map[c]
        fp = fp_map[c]
        fn = fn_map[c]
        prec = tp / max(1, tp + fp)
        rec = tp / max(1, tp + fn)
        f1 = (2 * prec * rec) / max(1e-6, prec + rec) if (prec + rec) > 0 else 0.0
        f1_list.append(f1)

    macro_f1 = sum(f1_list) / max(1, len(f1_list)) * 100
    primary_acc = (correct_primary / total_cases) * 100
    top3_recall = (correct_top3 / (total_cases - total_ood)) * 100
    avg_jci = sum(jci_scores) / max(1, len(jci_scores))
    adv_rate = (correct_adv / max(1, total_adv)) * 100
    ood_rate = (correct_abstention / max(1, total_ood)) * 100

    print("=" * 105)
    print("📊 BENCHMARK SCORECARD SUMMARY")
    print(f"• Total Evaluated Scenarios:         {total_cases}")
    print(f"• Primary Accuracy:                  {primary_acc:.1f}% ({correct_primary}/{total_cases})")
    print(f"• Macro F1-Score:                    {macro_f1:.1f}%")
    print(f"• Top-3 Statutory Article Recall:    {top3_recall:.1f}% ({correct_top3}/{total_cases - total_ood})")
    print(f"• Judicial Consistency Index (JCI):  {avg_jci:.1f}% (Symbolically Verified under CrPC 31 / BNSS 25)")
    print(f"• Adversarial Negation Pass Rate:    {adv_rate:.1f}% ({correct_adv}/{total_adv})")
    print(f"• Out-of-Domain Abstention Accuracy: {ood_rate:.1f}% ({correct_abstention}/{total_ood})")
    print("=" * 105 + "\n")

    return {
        "total_cases": total_cases,
        "primary_accuracy": round(primary_acc, 2),
        "macro_f1": round(macro_f1, 2),
        "top3_recall": round(top3_recall, 2),
        "avg_jci": round(avg_jci, 2),
        "adversarial_pass_rate": round(adv_rate, 2),
        "ood_abstention_accuracy": round(ood_rate, 2),
        "results": results_table
    }


if __name__ == "__main__":
    run_benchmark_evaluation()
