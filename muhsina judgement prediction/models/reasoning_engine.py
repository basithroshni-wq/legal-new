"""
Stage 2 Judicial Reasoning and Ratio Decidendi Engine.
Wraps `Raazi29/Nyaya-Llama-3.1-8B-Indian-Legal` (4-bit quantized)
to synthesize extracted 4-tier memory, retrieved statutory provisions,
and Stage 1 outcome classification into an authoritative judicial opinion.
"""

from typing import Dict, List, Any, Optional
import config


JUDICIAL_REASONING_PROMPT = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an eminent Judge of the High Court of Judicature in India.
Draft a comprehensive, formal, and authoritative Judicial Opinion and Ratio Decidendi based on the case facts, procedural timeline, retrieved statutory provisions, and the determined disposition.

Your draft MUST follow this judicial structure:
1. TITLE OF THE COURT & CAUSE TITLE
2. FACTUAL MATRIX & PROCEDURAL CHRONOLOGY
3. CONTENTIONS OF THE RESPECTIVE PARTIES
4. STATUTORY INTERPRETATION & LEGAL PRECEDENTS (Address both pre-2024 and post-2024 provisions)
5. RATIO DECIDENDI (The binding legal principle applied to these facts)
6. OPERATIVE DISPOSITION & FINAL ORDER (Aligned strictly with: {pred_outcome})
<|eot_id|><|start_header_id|>user<|end_header_id|>
CASE PARTICULARS:
- Petitioner: {petitioner}
- Respondent: {respondent}
- FIR No.: {fir_no}, P.S. {police_station}
- Alleged Sections: {sections}
- Custody Period: {custody_days} days
- Chargesheet Status: {chargesheet}
- Prior Antecedents: {antecedents}
- Relief Sought: {relief_sought}
- Forum: {jurisdiction}

PROCEDURAL TIMELINE:
{timeline_summary}

STAGE 1 DETERMINED DISPOSITION:
- Predicted Outcome: {pred_outcome} (Confidence: {confidence}%)

RETRIEVED STATUTORY PROVISIONS & CONCORDANCE:
{statutory_corpus}

Draft the complete formal High Court Judgment and Ratio Decidendi now.
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""


class Stage2ReasoningEngine:
    def __init__(self, model_name: str = config.STAGE2_REASONING_MODEL, device: Optional[str] = None):
        self.model_name = model_name
        self.device = device
        self.tokenizer = None
        self.model = None
        self.is_loaded = False

    def load_model(self):
        """Loads Nyaya-Llama-3.1-8B with 4-bit quantization on GPU."""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

            if self.device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"

            if self.device != "cuda":
                print("[Stage 2 Notice] CUDA GPU not detected. Using structured legal opinion synthesizer.")
                return

            print(f"[Stage 2] Loading 4-bit {self.model_name} on {self.device}...")

            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            )

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True
            )
            self.is_loaded = True
            print(f"[Stage 2] Successfully loaded {self.model_name} in 4-bit mode (~5.0 GB VRAM).")
        except Exception as e:
            print(f"[Stage 2 Notice] LLM loading deferred or unavailable ({e}). Structured legal synthesis active.")
            self.is_loaded = False

    def generate_opinion(
        self,
        case_memory: Dict[str, Any],
        retrieved_statutes: List[Dict[str, Any]],
        stage1_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Drafts judicial opinion using Nyaya-LLaMA if loaded,
        or structured jurisprudential synthesis engine.
        """
        l1 = case_memory.get("L1_facts", {})
        l2 = case_memory.get("L2_timeline", [])
        l3 = case_memory.get("L3_posture", {})

        pred_outcome = stage1_result.get("outcome", config.OUTCOME_ALLOWED)
        confidence = int(stage1_result.get("confidence", 0.85) * 100)

        # Format timeline
        timeline_lines = []
        for event in l2:
            timeline_lines.append(f"- [{event.get('event_date', 'Undated')}] {event.get('stage_name')}: {event.get('details')}")
        timeline_str = "\n".join(timeline_lines) if timeline_lines else "- Procedural stages in accordance with trial record."

        # Format statutes
        statute_lines = []
        cited_sections = []
        for item in retrieved_statutes:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            concordance = item.get("concordance")
            cited_sections.append(title)

            equiv_str = ""
            if concordance:
                equiv_str = f" [Cross-Reference: {concordance.get('new_law', concordance.get('old_law', ''))}]"
            statute_lines.append(f"• {title}{equiv_str}: {snippet}")

        statutes_str = "\n\n".join(statute_lines) if statute_lines else "• General principles of criminal jurisprudence."

        # Attempt GPU LLM Generation
        if self.is_loaded and self.tokenizer and self.model:
            try:
                import torch
                prompt = JUDICIAL_REASONING_PROMPT.format(
                    petitioner=l1.get("petitioner", "Applicant"),
                    respondent=l1.get("respondent", "State"),
                    fir_no=l1.get("fir_number", "N/A"),
                    police_station=l1.get("police_station", "N/A"),
                    sections=l1.get("alleged_acts_sections", "IPC Provisions"),
                    custody_days=l1.get("custody_duration_days", 0),
                    chargesheet="Filed" if l1.get("chargesheet_filed") else "Pending",
                    antecedents="Yes" if l1.get("criminal_antecedents") else "Clean Record",
                    relief_sought=l3.get("relief_sought", "Bail"),
                    jurisdiction=l3.get("court_jurisdiction", "High Court of Delhi"),
                    timeline_summary=timeline_str,
                    pred_outcome=pred_outcome,
                    confidence=confidence,
                    statutory_corpus=statutes_str
                )

                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=config.MAX_NEW_TOKENS,
                        temperature=config.TEMPERATURE,
                        top_p=config.TOP_P,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )

                response_text = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

                # Extract Ratio Decidendi segment
                ratio = self._extract_ratio(response_text)

                return {
                    "opinion_text": response_text.strip(),
                    "ratio_decidendi": ratio,
                    "statutes_cited": cited_sections,
                    "generator": f"Nyaya-Llama-3.1-8B-Indian-Legal (4-bit GPU)"
                }
            except Exception as e:
                print(f"[Warning] Nyaya-Llama generation failed: {e}. Falling back to structured synthesis.")

        # Structured Jurisprudential Synthesizer Fallback
        return self._synthesize_opinion(l1, l2, l3, retrieved_statutes, stage1_result)

    def _extract_ratio(self, text: str) -> str:
        import re
        match = re.search(r"(?:RATIO\s+DECIDENDI|Ratio\s+Decidendi)[\s\:\-]+([^\n\r]+(?:\n[^\n\r]+){1,4})", text)
        if match:
            return match.group(1).strip()
        return "The individual liberty of an undertrial prisoner cannot be curtailed indefinitely where investigation is complete and trial will take substantial time."

    def _synthesize_opinion(
        self,
        l1: Dict[str, Any],
        l2: List[Dict[str, Any]],
        l3: Dict[str, Any],
        statutes: List[Dict[str, Any]],
        stage1: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesizes high-grade Indian High Court judicial judgment draft."""
        petitioner = l1.get("petitioner", "The Applicant")
        respondent = l1.get("respondent", "State (NCT of Delhi)")
        fir = l1.get("fir_number", "N/A")
        ps = l1.get("police_station", "N/A")
        sections = l1.get("alleged_acts_sections", "Relevant Provisions")
        custody = l1.get("custody_duration_days", 90)
        court = l3.get("court_jurisdiction", "HIGH COURT OF DELHI AT NEW DELHI")
        relief = l3.get("relief_sought", "Regular Bail")
        outcome = stage1.get("outcome", config.OUTCOME_ALLOWED)
        prob = int(stage1.get("probability_allowed" if outcome == config.OUTCOME_ALLOWED else "probability_dismissed", 0.85) * 100)

        is_allowed = (outcome == config.OUTCOME_ALLOWED)

        if is_allowed:
            ratio = (
                f"Where the accused has suffered substantial pre-trial incarceration ({custody} days), "
                f"the investigation stands concluded with the filing of the chargesheet, and the evidence is predominantly "
                f"documentary, continued detention serves no penal or investigative purpose. Personal liberty enshrined "
                f"under Article 21 of the Constitution must supersede speculative apprehension."
            )
            disposition_block = (
                f"1. The present petition is hereby ALLOWED.\n"
                f"2. The Petitioner ({petitioner}) is directed to be admitted to regular bail upon furnishing a personal bond "
                f"in the sum of Rs. 50,000/- with one surety of the like amount to the satisfaction of the Learned Trial Court.\n"
                f"3. The Petitioner shall surrender their passport, shall not leave the National Capital Region without prior permission, "
                f"and shall not attempt to influence or tamper with any prosecution witnesses.\n"
                f"4. Any observation made herein is confined solely to the adjudication of bail and shall not influence the merits of the trial."
            )
        else:
            ratio = (
                f"Having regard to the gravity and heinous nature of the allegations under {sections}, the specific overt role "
                f"attributed to the applicant, and the nascent stage of the prosecution, there exists a prima facie case. "
                f"The societal interest and apprehension of witness intimidation outweigh individual liberty at this stage."
            )
            disposition_block = (
                f"1. In view of the foregoing analysis and the gravity of the offences alleged, this Court finds no merit "
                f"in the present application.\n"
                f"2. The petition seeking {relief} stands DISMISSED.\n"
                f"3. The Learned Trial Court is directed to expedite the trial without being influenced by any observations recorded herein."
            )

        citations = [item.get("title", "") for item in statutes]

        opinion_text = f"""================================================================================
IN THE {court.upper()}
CRIMINAL ORIGINAL / APPELLATE JURISDICTION

CASE TITLE:
{petitioner}                                                  ... Petitioner/Applicant
                                  VERSUS
{respondent}                                                  ... Respondent/State

CORAM:
HON'BLE MR. JUSTICE (LEGAL AI JUDGMENT ENGINE)

FIR No.: {fir}
Police Station: {ps}
Under Sections: {sections}
Relief Sought: {relief}

================================================================================
JUDGMENT & RATIO DECIDENDI
================================================================================

1. FACTUAL MATRIX & PROCEDURAL BACKGROUND:
The present petition has been preferred seeking {relief} in connection with FIR No. {fir} registered at Police Station {ps} for offences punishable under {sections}. The Petitioner has undergone actual judicial custody of {custody} days.

2. SUBMISSIONS ON BEHALF OF THE APPLICANT:
Learned Senior Counsel for the Petitioner submits that:
(a) The Petitioner has been falsely implicated and has clean antecedents without any previous conviction;
(b) The investigation has been completed, chargesheet has been finalized, and all material evidence has already been seized by the investigating agency;
(c) Continued detention amounts to pre-trial punishment, violating the constitutional guarantee under Article 21.

3. SUBMISSIONS ON BEHALF OF THE STATE / RESPONDENT:
Learned Additional Public Prosecutor appearing for the State opposes the petition, submitting that:
(a) The offences alleged are grave and carry substantial statutory penalties;
(b) There exists a legitimate apprehension that the applicant may tamper with evidentiary material or influence vulnerable witnesses.

4. STATUTORY INTERPRETATION & DUAL-CODE CONSIDERATIONS:
This Court has examined the statutory scheme governing the subject offences. Under the transition from historical provisions ({sections}) to the contemporary statutory framework (Bharatiya Nyaya Sanhita / Bharatiya Nagarik Suraksha Sanhita), the procedural thresholds for grant of judicial relief remain firmly rooted in the golden principle that bail is the rule and jail is the exception (Satender Kumar Antil v. CBI; Sanjay Chandra v. CBI).

5. RATIO DECIDENDI:
{ratio}

6. FINAL OPERATIVE ORDER:
[Predicted by Dual-Stage Legal Engine: {outcome} with {prob}% Calibrated Confidence]

{disposition_block}

ORDER ACCORDINGLY.
DATED: (Bench of Judicature)
"""

        return {
            "opinion_text": opinion_text.strip(),
            "ratio_decidendi": ratio,
            "statutes_cited": citations,
            "generator": "Legal Jurisprudential Synthesizer (Structured Benchmark Engine)"
        }
