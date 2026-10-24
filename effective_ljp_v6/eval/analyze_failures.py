import sys
import os
import json
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.stress_test_200 import generate_200_test_cases
from core.pipeline import EffectiveLjpPipeline

def analyze():
    pipeline = EffectiveLjpPipeline()
    cases = generate_200_test_cases()
    
    cat_stats = defaultdict(lambda: {"total": 0, "passed": 0})
    issue_by_component = defaultdict(list)
    failures = []
    
    for c in cases:
        cat = c["category"]
        cat_stats[cat]["total"] += 1
        res = pipeline.run(c["narrative"])
        
        passed = False
        pred_sec = ""
        
        if c["should_abstain"]:
            if res.is_abstained:
                passed = True
                pred_sec = "ABSTAINED"
            else:
                pred_sec = res.top_articles[0].ipc_section if res.top_articles else "Unknown"
                issue_by_component["Out-of-Domain Screening"].append((c["id"], cat, "Failed to abstain", pred_sec, c["narrative"][:60]))
        else:
            if res.is_abstained:
                passed = False
                pred_sec = "ABSTAINED (False Rejection)"
                issue_by_component["Out-of-Domain Screening"].append((c["id"], cat, "Erroneously abstained on legal fact", c["expected_ipc"], c["narrative"][:60]))
            else:
                top_art = res.top_articles[0] if res.top_articles else None
                pred_sec = top_art.ipc_section if top_art else "None"
                exp_sec = c["expected_ipc"].lower()
                
                if exp_sec in pred_sec.lower() or pred_sec.lower() in exp_sec or ("406" in exp_sec and "408" in pred_sec.lower()) or ("408" in exp_sec and "406" in pred_sec.lower()):
                    passed = True
                else:
                    passed = False
                    # Diagnose component
                    facts = res.atomic_facts
                    reasons = []
                    
                    # 1. FactExtractor checks
                    if "302" in exp_sec and not facts.death_caused:
                        reasons.append("FactExtractor: death_caused=False")
                        issue_by_component["FactExtractor"].append((c["id"], "Murder death_caused=False", c["narrative"][:60]))
                    if "302" in exp_sec and facts.death_caused and not facts.has_premeditation and not facts.weapon_used:
                        reasons.append("FactExtractor: no premeditation/weapon_used caused 302 to drop")
                        issue_by_component["FactExtractor"].append((c["id"], "Murder lacked premeditation signal", c["narrative"][:60]))
                    if "304 part ii" in exp_sec and not facts.is_sudden_fight:
                        reasons.append("FactExtractor: sudden_fight=False")
                        issue_by_component["FactExtractor"].append((c["id"], "Exception 4 sudden_fight=False", c["narrative"][:60]))
                    if "392" in exp_sec and not facts.is_robbery:
                        reasons.append("FactExtractor: is_robbery=False")
                        issue_by_component["FactExtractor"].append((c["id"], "Robbery is_robbery=False", c["narrative"][:60]))
                    if "395" in exp_sec and not facts.is_dacoity:
                        reasons.append("FactExtractor: is_dacoity=False")
                        issue_by_component["FactExtractor"].append((c["id"], "Dacoity accused_count < 5", c["narrative"][:60]))
                    if "406" in exp_sec and not facts.is_breach_of_trust:
                        reasons.append("FactExtractor: is_breach_of_trust=False")
                        issue_by_component["FactExtractor"].append((c["id"], "Breach of trust=False", c["narrative"][:60]))
                    
                    # 2. Gating checks
                    gated_ids = [cand.id for cand in res.retrieved_statutes]
                    expected_id_prefix = exp_sec.replace("section 304 part i", "stat_304_p1").replace("section 304 part ii", "stat_304_p2").replace("section ", "stat_").replace("quashed u/s 482", "stat_civil_482").upper()
                    matched_in_gate = any(expected_id_prefix in gid for gid in gated_ids)
                    if not matched_in_gate:
                        reasons.append("Gating: Expected statute filtered out")
                        # check rejection reason
                        filt_reason = "Not retrieved"
                        for cand in res.filtered_out_candidates:
                            if expected_id_prefix in cand.id:
                                filt_reason = cand.rejection_reason
                        issue_by_component["Gating"].append((c["id"], exp_sec, filt_reason, c["narrative"][:60]))
                    else:
                        # 3. Predictor / Ranker checks
                        top3_secs = [a.ipc_section for a in res.top_articles[:3]]
                        reasons.append(f"Predictor/Ranker: Precedence order error. Got {pred_sec}, Expected {c['expected_ipc']}")
                        issue_by_component["Predictor/Ranker"].append((c["id"], c["expected_ipc"], pred_sec, top3_secs, c["narrative"][:60]))
                    
                    failures.append({
                        "id": c["id"],
                        "category": cat,
                        "expected": c["expected_ipc"],
                        "predicted": pred_sec,
                        "reasons": reasons
                    })
        if passed:
            cat_stats[cat]["passed"] += 1
            
    print("=" * 80)
    print("CATEGORY PERFORMANCE BREAKDOWN:")
    print("=" * 80)
    total_cases = len(cases)
    total_passed = sum(s["passed"] for s in cat_stats.values())
    for cat, s in sorted(cat_stats.items()):
        pct = (s["passed"] / s["total"]) * 100
        print(f"{cat:36} : {s['passed']:2d}/{s['total']:2d} ({pct:5.1f}%)")
    print("-" * 80)
    print(f"OVERALL: {total_passed}/{total_cases} ({total_passed/total_cases*100:.1f}%)")
    print("=" * 80)
    print("\nISSUES BY PIPELINE COMPONENT:")
    print("=" * 80)
    for comp, items in issue_by_component.items():
        print(f"\n[{comp}] ({len(items)} issues):")
        for it in items[:10]:
            print(f"  • {it}")
        if len(items) > 10:
            print(f"  ... and {len(items)-10} more.")

if __name__ == "__main__":
    analyze()
