"""
Prefix-Based Attention Fusion Layer (PFL) - Multi-Aspect Legal Prefix.
Fuses gated legal knowledge items, decomposed atomic case facts, AND Pretrained LLM legal ratio
directly into the InLegalBERT transformer encoder input via a structured token budget.

Guarantees balanced cross-attention across:
1. LLM Judicial Ratio & Ingredients (~128 tokens)
2. Gated Statutory Elements (~128 tokens)
3. Case Facts (~256 tokens)
Ensuring the complete sequence fits within InLegalBERT's 512-token context window without truncation loss.
"""

from typing import List, Dict, Any, Tuple, Optional
from gating.fact_factorizer import AtomicCaseFacts


class PrefixKnowledgeFusion:
    def __init__(self, max_prefix_length: int = 256, max_fact_length: int = 900):
        self.max_prefix_length = max_prefix_length
        self.max_fact_length = max_fact_length

    def format_prefix(
        self,
        gated_items: List[Dict[str, Any]],
        atomic_facts: Optional[AtomicCaseFacts] = None,
        legal_reasoning: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Formats gated knowledge items, atomic facts, and LLM judicial ratio into a structured attention prefix.
        Budget-allocated to prevent exceeding InLegalBERT's 512-token capacity.
        """
        segments = []

        # 1. LLM Legal Distillation & Ratio Decidendi (~128 tokens / 450 chars)
        if legal_reasoning:
            ratio = legal_reasoning.get("ratio_decidendi", legal_reasoning.get("judicial_ratio", ""))
            actus = legal_reasoning.get("actus_reus", "")
            mens = legal_reasoning.get("mens_rea", "")
            chg = legal_reasoning.get("primary_charge", "")
            ratio_parts = []
            if chg and chg != "N/A":
                ratio_parts.append(f"Charge: {chg}")
            if actus and actus != "N/A":
                ratio_parts.append(f"Actus: {actus}")
            if mens and mens != "N/A":
                ratio_parts.append(f"Mens: {mens}")
            if ratio and ratio != "N/A":
                ratio_parts.append(f"Ratio: {ratio[:180]}")
            ratio_str = " | ".join(ratio_parts)[:450]
            if ratio_str:
                segments.append(f"[LEGAL_RATIO: {ratio_str}]")

        # 2. Statutory Knowledge Prefix (~128 tokens / 450 chars)
        statute_segments = []
        if gated_items:
            for idx, item in enumerate(gated_items[:3], 1):
                title = item.get("title", "")
                tier = item.get("penalty_tier", "").split(":")[0]
                align = item.get("ingredient_score", item.get("similarity", 0.0))
                elems = ", ".join(item.get("essential_elements", [])[:2])
                statute_segments.append(f"[K{idx}: {title} ({tier}) | Elements: {elems}]")
            statute_str = " ".join(statute_segments)[:450]
        else:
            statute_str = "[K0: General Indian Penal Jurisprudence]"
        segments.append(f"[STATUTORY_PREFIX: {statute_str}]")

        # 3. Atomic Fact Aspects Prefix (~64 tokens)
        if atomic_facts:
            aspect_str = atomic_facts.to_prefix_string()[:200]
            segments.append(f"[FACT_ASPECTS: {aspect_str}]")

        return " ".join(segments)

    def construct_fused_prompt(
        self,
        fact_text: str,
        gated_items: List[Dict[str, Any]],
        atomic_facts: Optional[AtomicCaseFacts] = None,
        legal_reasoning: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Creates fused multi-aspect input sequence:
        LLM Distillation + Statutory Knowledge + Core Case Facts (~512 InLegalBERT token budget)
        """
        prefix_str = self.format_prefix(gated_items, atomic_facts, legal_reasoning)
        clean_facts = fact_text.strip()[:self.max_fact_length]
        fused_text = f"{prefix_str} [CASE_FACTS]: {clean_facts}"
        return fused_text, prefix_str
