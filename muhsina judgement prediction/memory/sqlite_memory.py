"""
SQLite 4-Tier Memory Engine (inspired by TencentDB Agent Memory Architecture).
Tiers:
- L0: Raw input petitions, transcripts, and document logs
- L1: Atomic extracted legal facts and entities (parties, sections, FIR, custody)
- L2: Chronological procedural timeline of court and investigative events
- L3: Persona profile & legal posture (attorney side, court jurisdiction, targeted relief)

Includes automatic backup utilities for Google Drive synchronization.
"""

import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import config


class LegalMemoryManager:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.MEMORY_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")  # WAL mode for high concurrency & stability
        return conn

    def init_db(self):
        """Creates the 4-tier memory tables if they do not already exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Master Case Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # L0 Tier: Raw Data & Transcripts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_l0_raw (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT,
                    raw_text TEXT NOT NULL,
                    source_filename TEXT,
                    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
                )
            """)

            # L1 Tier: Atomic Legal Facts & Key-Value Entities
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_l1_facts (
                    case_id TEXT PRIMARY KEY,
                    petitioner TEXT,
                    respondent TEXT,
                    fir_number TEXT,
                    police_station TEXT,
                    district_state TEXT,
                    alleged_acts_sections TEXT, -- Comma-separated or JSON list
                    custody_duration_days INTEGER DEFAULT 0,
                    chargesheet_filed BOOLEAN DEFAULT FALSE,
                    criminal_antecedents BOOLEAN DEFAULT FALSE,
                    summary_of_allegations TEXT,
                    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
                )
            """)

            # L2 Tier: Procedural Timeline Milestones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_l2_timeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT,
                    event_order INTEGER,
                    event_date TEXT,
                    stage_name TEXT, -- e.g. "Incident", "FIR Lodged", "Arrest", "Bail Rejected by Sessions"
                    details TEXT,
                    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
                )
            """)

            # L3 Tier: Persona & Representation Posture
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_l3_posture (
                    case_id TEXT PRIMARY KEY,
                    representation_side TEXT, -- e.g. "Petitioner / Accused" or "Prosecution / State"
                    court_jurisdiction TEXT,  -- e.g. "High Court of Delhi", "Supreme Court of India"
                    relief_sought TEXT,       -- e.g. "Regular Bail u/s 439 CrPC / 483 BNSS", "Quashing"
                    legal_strategy_notes TEXT,
                    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
                )
            """)

            # Predictions & Outcomes Cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS case_predictions (
                    case_id TEXT PRIMARY KEY,
                    stage1_predicted_outcome TEXT,
                    stage1_probability_allowed REAL,
                    stage1_probability_dismissed REAL,
                    stage2_ratio_decidendi TEXT,
                    stage2_opinion_text TEXT,
                    statutes_cited TEXT, -- JSON array
                    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
                )
            """)

            conn.commit()

    def register_case(self, case_id: str, title: str):
        """Registers a case ID in master table."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO cases (case_id, title, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(case_id) DO UPDATE SET
                    title=excluded.title,
                    updated_at=CURRENT_TIMESTAMP
            """, (case_id, title))
            conn.commit()

    # --- L0 Operations ---
    def save_l0_raw(self, case_id: str, raw_text: str, source_filename: str = "") -> int:
        self.register_case(case_id, source_filename or f"Case {case_id}")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memory_l0_raw (case_id, raw_text, source_filename)
                VALUES (?, ?, ?)
            """, (case_id, raw_text, source_filename))
            conn.commit()
            return cursor.lastrowid

    # --- L1 Operations ---
    def save_l1_facts(self, case_id: str, facts: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO memory_l1_facts (
                    case_id, petitioner, respondent, fir_number, police_station,
                    district_state, alleged_acts_sections, custody_duration_days,
                    chargesheet_filed, criminal_antecedents, summary_of_allegations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    petitioner=excluded.petitioner,
                    respondent=excluded.respondent,
                    fir_number=excluded.fir_number,
                    police_station=excluded.police_station,
                    district_state=excluded.district_state,
                    alleged_acts_sections=excluded.alleged_acts_sections,
                    custody_duration_days=excluded.custody_duration_days,
                    chargesheet_filed=excluded.chargesheet_filed,
                    criminal_antecedents=excluded.criminal_antecedents,
                    summary_of_allegations=excluded.summary_of_allegations
            """, (
                case_id,
                facts.get("petitioner", "Unknown"),
                facts.get("respondent", "State of NCT of Delhi"),
                facts.get("fir_number", "N/A"),
                facts.get("police_station", "N/A"),
                facts.get("district_state", "Delhi"),
                facts.get("alleged_acts_sections", ""),
                int(facts.get("custody_duration_days", 0) or 0),
                bool(facts.get("chargesheet_filed", False)),
                bool(facts.get("criminal_antecedents", False)),
                facts.get("summary_of_allegations", "")
            ))
            conn.commit()

    # --- L2 Operations ---
    def save_l2_timeline(self, case_id: str, events: List[Dict[str, Any]]):
        with self._get_connection() as conn:
            # Clear previous timeline for case and re-insert
            conn.execute("DELETE FROM memory_l2_timeline WHERE case_id = ?", (case_id,))
            for i, event in enumerate(events):
                conn.execute("""
                    INSERT INTO memory_l2_timeline (case_id, event_order, event_date, stage_name, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    case_id,
                    i + 1,
                    event.get("event_date", "Undated"),
                    event.get("stage_name", "Milestone"),
                    event.get("details", "")
                ))
            conn.commit()

    # --- L3 Operations ---
    def save_l3_posture(self, case_id: str, posture: Dict[str, Any]):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO memory_l3_posture (
                    case_id, representation_side, court_jurisdiction, relief_sought, legal_strategy_notes
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    representation_side=excluded.representation_side,
                    court_jurisdiction=excluded.court_jurisdiction,
                    relief_sought=excluded.relief_sought,
                    legal_strategy_notes=excluded.legal_strategy_notes
            """, (
                case_id,
                posture.get("representation_side", "Petitioner / Accused"),
                posture.get("court_jurisdiction", "High Court of Delhi"),
                posture.get("relief_sought", "Regular Bail u/s 439 CrPC / 483 BNSS"),
                posture.get("legal_strategy_notes", "")
            ))
            conn.commit()

    # --- Predictions Operations ---
    def save_prediction(
        self,
        case_id: str,
        stage1_outcome: str,
        p_allowed: float,
        p_dismissed: float,
        stage2_ratio: str,
        stage2_opinion: str,
        statutes_cited: List[str]
    ):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO case_predictions (
                    case_id, stage1_predicted_outcome, stage1_probability_allowed,
                    stage1_probability_dismissed, stage2_ratio_decidendi,
                    stage2_opinion_text, statutes_cited
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    stage1_predicted_outcome=excluded.stage1_predicted_outcome,
                    stage1_probability_allowed=excluded.stage1_probability_allowed,
                    stage1_probability_dismissed=excluded.stage1_probability_dismissed,
                    stage2_ratio_decidendi=excluded.stage2_ratio_decidendi,
                    stage2_opinion_text=excluded.stage2_opinion_text,
                    statutes_cited=excluded.statutes_cited,
                    predicted_at=CURRENT_TIMESTAMP
            """, (
                case_id,
                stage1_outcome,
                p_allowed,
                p_dismissed,
                stage2_ratio,
                stage2_opinion,
                json.dumps(statutes_cited)
            ))
            conn.commit()

    # --- Retrieval & Aggregation ---
    def get_full_case_memory(self, case_id: str) -> Dict[str, Any]:
        """Returns the unified 4-tier memory state for a given case."""
        result: Dict[str, Any] = {
            "case_id": case_id,
            "L0_raw": [],
            "L1_facts": {},
            "L2_timeline": [],
            "L3_posture": {},
            "prediction": None
        }

        with self._get_connection() as conn:
            # L0
            rows_l0 = conn.execute("SELECT * FROM memory_l0_raw WHERE case_id = ? ORDER BY id ASC", (case_id,)).fetchall()
            result["L0_raw"] = [dict(r) for r in rows_l0]

            # L1
            row_l1 = conn.execute("SELECT * FROM memory_l1_facts WHERE case_id = ?", (case_id,)).fetchone()
            if row_l1:
                result["L1_facts"] = dict(row_l1)

            # L2
            rows_l2 = conn.execute("SELECT * FROM memory_l2_timeline WHERE case_id = ? ORDER BY event_order ASC", (case_id,)).fetchall()
            result["L2_timeline"] = [dict(r) for r in rows_l2]

            # L3
            row_l3 = conn.execute("SELECT * FROM memory_l3_posture WHERE case_id = ?", (case_id,)).fetchone()
            if row_l3:
                result["L3_posture"] = dict(row_l3)

            # Prediction
            row_pred = conn.execute("SELECT * FROM case_predictions WHERE case_id = ?", (case_id,)).fetchone()
            if row_pred:
                pred_dict = dict(row_pred)
                try:
                    pred_dict["statutes_cited"] = json.loads(pred_dict.get("statutes_cited") or "[]")
                except Exception:
                    pass
                result["prediction"] = pred_dict

        return result

    def export_json(self, case_id: str) -> str:
        """Serializes full 4-tier case memory into formatted JSON string."""
        memory = self.get_full_case_memory(case_id)
        return json.dumps(memory, indent=2, default=str)

    def backup_to_drive(self) -> Dict[str, Any]:
        """
        Safely flushes and backups the active SQLite database to Google Drive (or backup folder).
        Prevents SQLite corruptions by checkpointing the WAL file before copying.
        """
        target_dir = config.DRIVE_BACKUP_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        # Force SQLite WAL Checkpoint to flush memory writes to disk
        with self._get_connection() as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"case_memory_backup_{timestamp}.sqlite3"
        latest_filename = "case_memory_latest.sqlite3"

        dest_backup = target_dir / backup_filename
        dest_latest = target_dir / latest_filename

        shutil.copy2(self.db_path, dest_backup)
        shutil.copy2(self.db_path, dest_latest)

        return {
            "status": "success",
            "backup_file": str(dest_backup),
            "latest_file": str(dest_latest),
            "timestamp": timestamp
        }
