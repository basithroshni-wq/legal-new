"""
Configuration for Indian Legal Judgment Prediction & 4-Tier Memory Engine.
Supports automatic adaptation between Google Colab (with T4 GPU & Drive) and local workstation environments.
"""

import os
import sys
from pathlib import Path

# Environment Detection
IS_COLAB = "google.colab" in sys.modules or os.path.exists("/content")

# Base Working & Persistence Directories
if IS_COLAB:
    # Use fast local NVMe on Colab for active DBs to avoid FUSE SQLite lock errors
    BASE_DIR = Path("/content/legal_runtime")
    DRIVE_BACKUP_DIR = Path("/content/drive/MyDrive/Indian_Legal_Judgment_Engine")
else:
    BASE_DIR = Path(__file__).resolve().parent / "runtime_data"
    DRIVE_BACKUP_DIR = BASE_DIR / "backups"

# Ensure directories exist
BASE_DIR.mkdir(parents=True, exist_ok=True)
DRIVE_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Database Paths
MEMORY_DB_PATH = BASE_DIR / "case_memory.sqlite3"
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"

# AI Model Identifiers
# Stage 1: Fast deterministic classifier for binary outcome prediction (Allowed vs Dismissed)
STAGE1_CLASSIFIER_MODEL = "law-ai/InLegalBERT"

# Stage 2: Generative judicial reasoning and ratio decidendi model
# Raazi29/Nyaya-Llama-3.1-8B-Indian-Legal is fine-tuned specifically on Indian Supreme Court & High Court judgments
STAGE2_REASONING_MODEL = "Raazi29/Nyaya-Llama-3.1-8B-Indian-Legal"

# Embedding model for Statutory RAG
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Quantization & Inference Settings
USE_4BIT = True
MAX_NEW_TOKENS = 768
TEMPERATURE = 0.2
TOP_P = 0.9

# Memory Layer Tiers
TIER_L0_RAW = "L0_RAW"               # Full transcripts, raw petition text
TIER_L1_FACTS = "L1_ATOMIC_FACTS"    # Key-value legal entities (parties, sections, FIR)
TIER_L2_TIMELINE = "L2_TIMELINE"     # Chronological procedural milestones
TIER_L3_PERSONA = "L3_CASE_POSTURE"  # Representation posture (Defense/Prosecution, Jurisdiction)

# Outcome Classes
OUTCOME_ALLOWED = "PETITION ALLOWED"
OUTCOME_DISMISSED = "PETITION DISMISSED"
