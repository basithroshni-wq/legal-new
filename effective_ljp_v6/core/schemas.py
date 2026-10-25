"""
Pydantic Schemas and Dataclasses for Effective LJP V6.
Defines verified typing for extracted facts, retrieved candidates, predictions, and audit reports.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AtomicFacts(BaseModel):
    """Structured, verified atomic facts extracted from legal narrative."""
    is_out_of_domain: bool = Field(False, description="True if text is not a cognizable legal case narrative")
    out_of_domain_reason: str = Field("", description="Reason for out of domain classification")
    
    # Core Homicide & Physical Elements
    death_caused: bool = False
    injury_severity: str = "None"  # None, Simple, Grievous, Fatal
    weapon_used: bool = False
    weapon_type: str = "None"  # None, Blunt, Edged/Sharp (Knife/Axe), Firearm, Corrosive
    weapon_source: str = "None"  # Pre-arranged/Carried, Found at Spot, Unknown
    
    # Intent & Mental State (Mens Rea)
    intention_to_cause_death: bool = False
    has_premeditation: bool = False
    is_sudden_fight: bool = False
    heat_of_passion: bool = False
    is_provocation: bool = False
    
    # Property & Deception Elements
    is_theft: bool = False
    is_robbery: bool = False
    is_dacoity: bool = False
    force_or_violence_used: bool = False
    is_fraud_or_cheating: bool = False
    fraudulent_inducement_at_inception: bool = False
    is_forgery: bool = False
    is_breach_of_trust: bool = False
    is_breach_of_trust_clerk_servant: bool = False
    is_criminal_negligence: bool = False
    
    # Matrimonial & Special Categories
    is_matrimonial: bool = False
    is_dowry_death: bool = False
    marriage_years: Optional[float] = None
    is_sexual_offence: bool = False
    is_sexual_harassment: bool = False
    is_intimidation: bool = False
    is_criminal_trespass: bool = False
    is_defamation: bool = False
    is_housebreaking: bool = False
    is_theft_in_dwelling: bool = False
    is_robbery_with_hurt: bool = False
    is_corruption_or_bribery: bool = False
    is_suicide_abetment: bool = False
    is_ndps_narcotics: bool = False
    is_cheque_dishonour: bool = False
    is_pocso_child_abuse: bool = False
    is_extortion: bool = False
    is_acid_attack: bool = False
    is_kidnapping_ransom: bool = False
    is_cyber_phishing: bool = False
    is_hate_speech_153a: bool = False
    is_arms_act: bool = False
    is_cbt_public_servant_banker: bool = False
    is_arson_fire: bool = False
    is_kidnapping_lawful_guardian: bool = False
    is_stalking: bool = False
    is_destruction_of_evidence: bool = False
    is_counterfeit_currency: bool = False
    is_rioting: bool = False
    is_unlawful_assembly: bool = False
    is_wrongful_confinement: bool = False
    is_stolen_property_possession: bool = False
    is_cheating_personation: bool = False
    is_cruelty_to_animals: bool = False
    is_uapa_offence: bool = False
    is_wildlife_poaching: bool = False
    
    # Parties & Procedure
    accused_count: int = 1
    has_common_intention: bool = False
    is_criminal_conspiracy: bool = False
    is_commercial_civil_dispute: bool = False
    defense_plea_false_implication: bool = False
    
    # Dynamic extracted tokens for ingredient matching
    extracted_tokens: List[str] = Field(default_factory=list)


class CandidateKnowledge(BaseModel):
    """Retrieved statutory candidate with gating assessment."""
    id: str
    ipc_section: str
    bns_section: str
    statute_title: str
    charge_category: str
    statutory_ceiling_tier: str
    statutory_max_years: int
    lexical_bm25_score: float = 0.0
    dense_cosine_score: float = 0.0
    combined_relevance: float = 0.0
    ingredient_fulfillment: float = 0.0
    matched_ingredients: List[str] = Field(default_factory=list)
    missing_ingredients: List[str] = Field(default_factory=list)
    is_gated_in: bool = True
    rejection_reason: Optional[str] = None


class ArticlePrediction(BaseModel):
    """Predicted statutory provision with dual-code notation."""
    rank: int
    ipc_section: str
    bns_section: str
    display_name: str
    charge_category: str
    statutory_ceiling_tier: str
    calibrated_probability: float
    confidence_level: str


class ChargePrediction(BaseModel):
    """Predicted legal charge category."""
    rank: int
    charge_name: str
    probability: float


class PenaltyPrediction(BaseModel):
    """Dynamic penalty severity distribution."""
    predicted_tier: str
    statutory_ceiling_years: int
    tier_probabilities: Dict[str, float]
    is_bailable: bool
    reconciled_by_jcv: bool = False


class JudicialAuditReport(BaseModel):
    """Symbolic audit trail verifying compliance under CrPC 31 / BNSS 25."""
    initial_jci_score: float = 100.0
    final_jci_score: float = 100.0
    compliance_status: str = "COMPLIANT"
    deductions: List[Dict[str, Any]] = Field(default_factory=list)
    reconciliations: List[str] = Field(default_factory=list)
    is_statutorily_sound: bool = True


class LjpPredictionResult(BaseModel):
    """Complete prediction package from Effective LJP V6."""
    case_summary: str
    is_abstained: bool = False
    abstain_message: str = ""
    atomic_facts: AtomicFacts
    retrieved_statutes: List[CandidateKnowledge]
    filtered_out_candidates: List[CandidateKnowledge]
    top_articles: List[ArticlePrediction]
    top_charges: List[ChargePrediction]
    penalty_prediction: PenaltyPrediction
    judicial_audit: JudicialAuditReport
    ratio_decidendi: str
    landmark_precedents_cited: List[str]
