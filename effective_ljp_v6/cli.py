"""
Command-Line Interface (CLI) for Effective LJP V6.
Usage:
    python cli.py --benchmark
    python cli.py --predict "Narrative text..."
    python cli.py --ui [--share] [--port 7860]
"""

import argparse
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure package directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.pipeline import EffectiveLjpPipeline
from eval.metrics import run_benchmark_evaluation
from ui.app import launch_dashboard


def main():
    parser = argparse.ArgumentParser(description="Effective LJP V6: Neuro-Symbolic Legal Judgment Prediction Engine")
    parser.add_argument("--benchmark", action="store_true", help="Execute 22-case held-out benchmark and report live metrics")
    parser.add_argument("--predict", type=str, help="Adjudicate a case narrative from command line")
    parser.add_argument("--ui", action="store_true", help="Launch interactive Gradio web dashboard")
    parser.add_argument("--share", action="store_true", help="Create public shareable Gradio tunnel URL")
    parser.add_argument("--port", type=int, default=7860, help="Server port for Gradio dashboard (default: 7860)")

    args = parser.parse_args()

    if args.benchmark:
        run_benchmark_evaluation()
    elif args.predict:
        pipeline = EffectiveLjpPipeline()
        res = pipeline.run(args.predict)
        print("\n" + "=" * 80)
        print("⚖️  EFFECTIVE LJP V6 ADJUDICATION REPORT")
        print("=" * 80)
        if res.is_abstained:
            print(f"STATUS: {res.abstain_message}")
        else:
            top_art = res.top_articles[0]
            print(f"TOP LAW PROVISION:      {top_art.display_name}")
            print(f"CALIBRATED PROBABILITY: {top_art.calibrated_probability * 100:.1f}% ({top_art.confidence_level})")
            print(f"PRIMARY CHARGE HEAD:    {res.top_charges[0].charge_name} ({res.top_charges[0].probability * 100:.1f}%)")
            print(f"PENALTY SEVERITY TIER:  {res.penalty_prediction.predicted_tier} (Max {res.penalty_prediction.statutory_ceiling_years} Years)")
            print(f"JUDICIAL CONSISTENCY:   {res.judicial_audit.final_jci_score:.1f}% ({res.judicial_audit.compliance_status})")
            print(f"RATIO DECIDENDI:        {res.ratio_decidendi}")
            if res.landmark_precedents_cited:
                print(f"LANDMARK PRECEDENTS:    {', '.join(res.landmark_precedents_cited)}")
        print("=" * 80 + "\n")
    elif args.ui:
        launch_dashboard(share=args.share, server_port=args.port)
    else:
        # Default behavior: run benchmark
        print("[Effective LJP V6] No arguments specified. Running benchmark suite...\n")
        run_benchmark_evaluation()


if __name__ == "__main__":
    main()
