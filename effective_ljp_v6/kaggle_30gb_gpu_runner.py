"""
=========================================================================================================
⚡ EFFECTIVE LJP V6: DEDICATED KAGGLE 30GB GPU RUNNER
=========================================================================================================
Architected specifically for Kaggle GPU Environments (Dual Tesla T4 16GB / Tesla P100 16GB VRAM):
- Model Space 1: High-Throughput Dense Bi-Encoder (BAAI/bge-small-en-v1.5 / all-MiniLM-L6-v2) on CUDA FP16
- Model Space 2: Deep Cross-Attention Reranker (cross-encoder/ms-marco-MiniLM-L-6-v2) on CUDA FP16
- Model Space 3: Domain Neural Perception Layer (law-ai/InLegalBERT / HF Transformer Pipeline)
- Model Space 4: Multi-Signal Calibrated Softmax Prediction Head (IPC 1860 & BNS 2023)
- Symbolic Gating & Judicial Consistency Verifier (Sec 31 CrPC / Sec 25 BNSS) - 100% Soundness Guarantee

Usage:
  python kaggle_30gb_gpu_runner.py --benchmark
  python kaggle_30gb_gpu_runner.py --stress-test
  python kaggle_30gb_gpu_runner.py --ui
  python kaggle_30gb_gpu_runner.py --case "Accused broke into store with an iron rod and assaulted cashier..."
=========================================================================================================
"""

import sys
import os
import argparse
import time

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def print_banner():
    banner = """
=========================================================================================================
⚖️  EFFECTIVE LJP V6: DEDICATED KAGGLE 30GB GPU NEURO-SYMBOLIC PIPELINE
=========================================================================================================
Dual-Code Indian Penal Jurisprudence (IPC 1860 & BNS 2023) | Supreme Court Landmark Precedents
"""
    print(banner)


def check_gpu_environment():
    """Validates Kaggle GPU capabilities and prints hardware diagnostics."""
    print("🔍 [GPU Diagnostics] Checking CUDA Hardware Acceleration...")
    try:
        import torch
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            current_device = torch.cuda.current_device()
            dev_name = torch.cuda.get_device_name(current_device)
            total_vram = torch.cuda.get_device_properties(current_device).total_memory / (1024 ** 3)
            print(f"  ✅ CUDA Accelerated Device Found: {dev_name}")
            print(f"  ✅ Available Devices: {device_count} | Primary Device VRAM: {total_vram:.2f} GB")
            print(f"  ✅ PyTorch Version: {torch.__version__} (CUDA {torch.version.cuda})")
            return "cuda"
        else:
            print("  ⚠️ CUDA not detected or PyTorch compiled without CUDA. Falling back to high-speed CPU.")
            return "cpu"
    except ImportError:
        print("  ⚠️ PyTorch is not installed. To unlock GPU acceleration, run: pip install torch")
        return "cpu"


def warm_up_gpu_models(device: str):
    """Pre-loads and warms up all model spaces into Kaggle GPU VRAM."""
    print("\n🚀 [Model Initialization] Loading Model Spaces into GPU VRAM...")
    
    # Model Space 1 & 2: Dense Bi-Encoder and Cross-Encoder
    from core.retriever import HybridLegalRetriever
    t0 = time.time()
    retriever = HybridLegalRetriever()
    dt = time.time() - t0
    
    bi_status = "CUDA FP16 Active" if (retriever.dense_model is not None and retriever.device == "cuda") else "CPU Fallback"
    cross_status = "CUDA Active" if (retriever.cross_encoder is not None and retriever.device == "cuda") else "BM25/Bi-Encoder Mode"
    print(f"  • Model Space 1 [Bi-Encoder]:    {bi_status} (SentenceTransformers, {dt:.2f}s load time)")
    print(f"  • Model Space 2 [Cross-Encoder]: {cross_status} (ms-marco-MiniLM-L-6-v2)")

    # Model Space 3: Neural Fact Extractor
    from core.neural_extractor import NeuralLegalFactExtractor
    neural_extractor = NeuralLegalFactExtractor(use_gpu=(device == "cuda"), load_in_fp16=True)
    neural_extractor.initialize_model()
    neural_status = "CUDA Active" if (neural_extractor.is_loaded and neural_extractor.device == "cuda") else "Offline / Symbolic Gate Protected"
    print(f"  • Model Space 3 [Legal LLM/BERT]: {neural_status} (InLegalBERT / HF Transformers)")

    # Model Space 4: Calibrated Multi-Task Softmax Predictor & JCV
    from core.pipeline import EffectiveLjpPipeline
    pipeline = EffectiveLjpPipeline()
    print("  • Model Space 4 [Calibrated MHPN]: Active (Softmax Multi-Task Head + CrPC 31 / BNSS 25 Verifier)")
    
    return pipeline


def run_single_case(pipeline, text: str):
    """Executes single case analysis with full legal reasoning and dual-code predictions."""
    print("\n" + "=" * 95)
    print("⚖️ CASE NARRATIVE ANALYSIS")
    print("=" * 95)
    print(f"Input: {text}\n")

    result = pipeline.run(text)

    if result.is_abstained:
        print(f"⛔ ABSTAINED (Out-of-Domain): {result.abstain_message}")
        return

    print("📊 1. PREDICTED STATUTORY PROVISIONS (TOP RANKED):")
    for art in result.top_articles[:3]:
        print(f"  • Rank {art.rank}: {art.display_name}")
        print(f"    - Category:     {art.charge_category}")
        print(f"    - Ceiling Tier: {art.statutory_ceiling_tier}")
        print(f"    - Probability:  {art.calibrated_probability * 100:.2f}% ({art.confidence_level})")

    print("\n🏛️ 2. CHARGE CATEGORY DISTRIBUTION:")
    for ch in result.top_charges[:3]:
        print(f"  • {ch.charge_name:<35}: {ch.probability * 100:.2f}%")

    print("\n⏳ 3. SENTENCING & PENALTY DETERMINATION:")
    pen = result.penalty_prediction
    print(f"  • Predicted Severity Tier:  {pen.predicted_tier}")
    print(f"  • Statutory Max Ceiling:    {pen.statutory_ceiling_years} Years")
    print(f"  • Legal Classification:     {'Bailable' if pen.is_bailable else 'Non-Bailable / Cognizable'}")
    print("  • Calibrated Tier Distribution:")
    for t_name, t_prob in pen.tier_probabilities.items():
        print(f"    - {t_name:<35}: {t_prob * 100:.2f}%")

    print("\n⚖️ 4. JUDICIAL CONSISTENCY & REASONING (CrPC 31 / BNSS 25):")
    audit = result.judicial_audit
    print(f"  • Judicial Consistency Index (JCI): {audit.final_jci_score:.1f}% ({audit.compliance_status})")
    print(f"  • Statutory Soundness:              {'100% Sound' if audit.is_statutorily_sound else 'Needs Reconciliation'}")
    print(f"  • Grounded Ratio Decidendi:         {result.ratio_decidendi}")
    if result.landmark_precedents_cited:
        print(f"  • Landmark Precedents Cited:        {', '.join(result.landmark_precedents_cited)}")


def launch_gradio_ui():
    """Launches interactive Gradio web app with public Kaggle tunnel."""
    print("\n🌐 Launching Interactive Dark Glassmorphic Web App...")
    from ui.app import launch_dashboard
    launch_dashboard(share=True)


def main():
    parser = argparse.ArgumentParser(description="Effective LJP V6 - Kaggle 30GB GPU Dedicated Runner")
    parser.add_argument("--benchmark", action="store_true", help="Execute 22-case held-out benchmark suite")
    parser.add_argument("--stress-test", action="store_true", help="Execute 222-case comprehensive stress test suite")
    parser.add_argument("--ui", action="store_true", help="Launch interactive Gradio 6.x web UI with Kaggle share=True")
    parser.add_argument("--case", type=str, help="Analyze custom input case narrative")
    args = parser.parse_args()

    print_banner()
    device = check_gpu_environment()
    pipeline = warm_up_gpu_models(device)

    if args.benchmark:
        from eval.metrics import run_benchmark_evaluation
        run_benchmark_evaluation()
    elif args.stress_test:
        from eval.stress_test_200 import run_stress_test_200
        run_stress_test_200()
    elif args.case:
        run_single_case(pipeline, args.case)
    elif args.ui:
        launch_gradio_ui()
    else:
        from eval.metrics import run_benchmark_evaluation
        run_benchmark_evaluation()
        sample_case = (
            "During a sudden quarrel in an auto-rickshaw stand in Kochi over a disputed 50 rupee fare, "
            "the accused snatched a heavy wooden stool from a roadside tea shop in the heat of passion, "
            "and struck the deceased on the temple without premeditation, causing instant death."
        )
        run_single_case(pipeline, sample_case)


if __name__ == "__main__":
    main()
