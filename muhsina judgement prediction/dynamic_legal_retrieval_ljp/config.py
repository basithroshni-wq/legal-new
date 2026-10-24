"""
Configuration for Dynamic Legal Knowledge Retrieval for Judgment Prediction (DLKR-LJP).
Implements the paper abstract architecture adapted to the Indian Criminal Legal System (IPC & BNS).
"""

import os
import sys
from pathlib import Path

# Environment Detection
IS_COLAB = "google.colab" in sys.modules or os.path.exists("/content")

if IS_COLAB:
    BASE_DIR = Path("/content/dlkr_ljp_runtime")
    PERSIST_DIR = Path("/content/drive/MyDrive/DLKR_LJP_Indian_Law")
else:
    BASE_DIR = Path(__file__).resolve().parent / "runtime_data"
    PERSIST_DIR = BASE_DIR / "checkpoints"

BASE_DIR.mkdir(parents=True, exist_ok=True)
PERSIST_DIR.mkdir(parents=True, exist_ok=True)

CHROMA_DIR = BASE_DIR / "chroma_legal_kb"

# Model Backbones
BACKBONE_MODEL_NAME = "law-ai/InLegalBERT"
TRANSFORMER_MODEL_NAME = BACKBONE_MODEL_NAME
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Dynamic Relevance & Confidence Gate Hyperparameters
SIMILARITY_THRESHOLD_TAU = 0.40     # Calibrated Cosine cutoff for semantic relevance
MIN_CONFIDENCE_FLOOR = 0.35         # Absolute floor below which items are classified as spurious noise
TOP_K_RETRIEVAL = 6                 # Raw candidate pool size from external KB
MAX_GATED_KNOWLEDGE_ITEMS = 3       # Maximum verified items fused into prefix layer
ENABLE_ADAPTIVE_GATING = True       # Adapts gating threshold to relative top-k margin

# Head 1: Law Articles Vocabulary (Mapped across IPC 1860 & BNS 2023)
LAW_ARTICLES = [
    "IPC_302_BNS_103",   # Murder
    "IPC_304_PART2_BNS_105",   # Culpable Homicide not amounting to murder (Part II - Sudden Quarrel/Single Blow)
    "IPC_304_PART1_BNS_105",   # Culpable Homicide not amounting to murder (Part I - Bodily Injury likely to cause death)
    "IPC_307_BNS_109",   # Attempt to Murder
    "IPC_304B_BNS_80",   # Dowry Death
    "IPC_376_BNS_64",    # Rape / Sexual Offences
    "IPC_420_BNS_318",   # Cheating & Dishonestly Inducing Delivery
    "IPC_406_BNS_316",   # Criminal Breach of Trust
    "IPC_467_BNS_338",   # Forgery of Valuable Security
    "IPC_468_BNS_336",   # Forgery for Purpose of Cheating
    "IPC_471_BNS_340",   # Using Forged Document as Genuine
    "IPC_498A_BNS_85",   # Cruelty by Husband or Relatives
    "IPC_323_BNS_115",   # Voluntarily Causing Hurt
    "IPC_324_BNS_117",   # Causing Hurt by Dangerous Weapons
    "IPC_326_BNS_118",   # Voluntarily Causing Grievous Hurt
    "IPC_379_BNS_303",   # Theft
    "IPC_392_BNS_309",   # Robbery
    "IPC_506_BNS_351",   # Criminal Intimidation
    "IPC_120B_BNS_61",   # Criminal Conspiracy
    "IPC_34_BNS_3"       # Common Intention
]

# Head 2: Criminal Charge Categories
CRIMINAL_CHARGES = [
    "Murder & Culpable Homicide",
    "Culpable Homicide (Sudden Fight / Heat of Passion)",
    "Attempt to Murder",
    "Sexual Offences & Assault",
    "Cheating & Financial Fraud",
    "Forgery & Counterfeiting",
    "Criminal Breach of Trust",
    "Matrimonial Cruelty & Harassment",
    "Dowry Death",
    "Assault & Grievous Hurt",
    "Theft & Dacoity",
    "Criminal Conspiracy",
    "Criminal Intimidation"
]

# Head 3: Term of Penalty & Statutory Sentencing Tiers
PENALTY_TIERS = [
    "Tier 1: Up to 3 Years (Bailable / Minor Misdemeanor)",
    "Tier 2: 3 to 7 Years (Arnesh Kumar Threshold / Medium Penalty)",
    "Tier 3: 7 to 10 Years (Serious Offence / Substantial Imprisonment)",
    "Tier 4: Life Imprisonment / Capital Sentence (Heinous Offence)"
]
