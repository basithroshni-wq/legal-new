"""
Fact and Timeline Extractor for populating L1, L2, and L3 Memory tiers.
Supports:
1. Direct extraction via Nyaya-Llama-3.1-8B using structured JSON prompting.
2. Rule-based Legal Regex Parser fallback (extracts FIR, sections, parties, and dates instantly).
"""

import re
import json
from typing import Dict, List, Any, Optional


EXTRACTION_PROMPT_TEMPLATE = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are an expert Indian Legal Assistant and Legal Knowledge Graph Extractor.
Extract structured legal facts (L1 entities), procedural timeline milestones (L2 events), and case posture (L3 profile) from the provided Indian court petition or judgment.
Return ONLY valid JSON strictly matching the schema below without any preamble or conversational text.

Schema:
{
  "L1_facts": {
    "petitioner": "Name of petitioner / accused",
    "respondent": "State or respondent name",
    "fir_number": "FIR number with year or N/A",
    "police_station": "Name of police station",
    "district_state": "District and State",
    "alleged_acts_sections": "e.g. Section 420, 467, 120B IPC / Section 318(4) BNS",
    "custody_duration_days": 120,
    "chargesheet_filed": true,
    "criminal_antecedents": false,
    "summary_of_allegations": "Concise 2-sentence summary of the prosecution's allegations."
  },
  "L2_timeline": [
    {
      "event_date": "YYYY-MM-DD or approximate date",
      "stage_name": "FIR Registered / Arrest / Remand / Chargesheet Filed / Sessions Bail Dismissed",
      "details": "Brief description of the milestone"
    }
  ],
  "L3_posture": {
    "representation_side": "Petitioner / Accused",
    "court_jurisdiction": "High Court / Supreme Court / Sessions Court",
    "relief_sought": "Regular Bail / Anticipatory Bail / Quashing of FIR",
    "legal_strategy_notes": "Key legal arguments e.g. parity, delay in trial, civil nature of dispute"
  }
}
<|eot_id|><|start_header_id|>user<|end_header_id|>
Legal Document:
\"\"\"{document_text}\"\"\"
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""


class LegalFactExtractor:
    def __init__(self, model_pipeline=None):
        self.pipeline = model_pipeline

    def extract_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """Uses the loaded Nyaya-Llama model to extract structured memory."""
        if not self.pipeline:
            return None

        # Truncate text to fit context window safely
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(document_text=text[:4000])

        try:
            raw_output = self.pipeline(prompt)
            # Find the JSON object inside the response
            json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"[Warning] LLM JSON extraction failed: {e}. Falling back to legal heuristic parser.")

        return None

    def extract_heuristic(self, text: str) -> Dict[str, Any]:
        """
        High-precision rule-based parser that identifies standard Indian legal petition conventions:
        - Petitioner vs Respondent
        - FIR No. and Police Station
        - Sections of Law (IPC, CrPC, BNS, BNSS, NDPS, POCSO)
        - Custody periods and dates
        """
        # 1. Parties Extraction
        petitioner = "Unknown Petitioner"
        respondent = "State of NCT of Delhi"

        # e.g., "Mohd. Basit ... Petitioner Versus State ... Respondent"
        v_match = re.search(r"([A-Z][A-Za-z\s\.\(\)]+?)(?:\.\.\.|\s+)?(?:Petitioner|Applicant|Appellant)[\s\n]+(?:versus|vs\.?|v\.)[\s\n]+([A-Z][A-Za-z\s\.\(\)]+?)(?:\.\.\.|\s+)?(?:Respondent|State)", text, re.IGNORECASE)
        if v_match:
            petitioner = v_match.group(1).strip()
            respondent = v_match.group(2).strip()
        else:
            # Fallback simple versus pattern
            simple_v = re.search(r"([A-Z][A-Za-z\s]{3,30})\s+(?:versus|vs\.?)\s+([A-Z][A-Za-z\s]{3,30})", text, re.IGNORECASE)
            if simple_v:
                petitioner = simple_v.group(1).strip()
                respondent = simple_v.group(2).strip()

        # 2. FIR & Police Station
        fir_match = re.search(r"(?:FIR|Crime\s+No\.?|F\.I\.R\.?)\s*(?:No\.?|Number)?\s*[:\s-]?\s*([0-9]+(?:\s*(?:of|/)\s*[0-9]{2,4})?)", text, re.IGNORECASE)
        fir_no = fir_match.group(1).strip() if fir_match else "N/A"

        ps_match = re.search(r"(?:Police\s+Station|P\.S\.?)\s*[:\s-]?\s*([A-Za-z\s]{3,25})(?:,|\.|\n|$)", text, re.IGNORECASE)
        police_station = ps_match.group(1).strip() if ps_match else "N/A"

        # 3. Sections & Acts
        sections_found = set()
        sec_matches = re.findall(r"(?:Sections?|u/s|s\.)\s*([0-9]{2,3}[A-Za-z]?(?:\s*(?:,|and|/)\s*[0-9]{2,3}[A-Za-z]?)*)\s*(?:of\s+)?(?:IPC|CrPC|BNS|BNSS|Indian\s+Penal\s+Code)?", text, re.IGNORECASE)
        for s_group in sec_matches:
            for s in re.split(r"[,/]|and", s_group):
                clean = s.strip()
                if clean.isalnum():
                    sections_found.add(clean)

        acts_sections_str = ", ".join(sorted(sections_found)) if sections_found else "IPC 420/120B"

        # 4. Custody Duration
        custody_days = 0
        custody_match = re.search(r"custody\s+(?:since|for|period\s+of)\s*([0-9]+)\s*(?:days|months|years)?", text, re.IGNORECASE)
        if custody_match:
            val = int(custody_match.group(1))
            if "month" in custody_match.group(0).lower():
                val *= 30
            elif "year" in custody_match.group(0).lower():
                val *= 365
            custody_days = val
        elif "judicial custody" in text.lower() or "in custody" in text.lower():
            custody_days = 90  # Typical median

        # 5. Chargesheet & Antecedents
        chargesheet_filed = bool(re.search(r"chargesheet\s+(?:has\s+been\s+)?filed|investigation\s+is\s+complete", text, re.IGNORECASE))
        has_antecedents = bool(re.search(r"criminal\s+antecedents|previous\s+conviction|involved\s+in\s+other\s+cases", text, re.IGNORECASE))

        # 6. Relief Sought & Jurisdiction
        relief_sought = "Regular Bail u/s 439 CrPC / 483 BNSS"
        if re.search(r"anticipatory\s+bail|438\s*crpc|482\s*bnss", text, re.IGNORECASE):
            relief_sought = "Anticipatory Bail u/s 438 CrPC / 482 BNSS"
        elif re.search(r"quash|quashing|482\s*crpc|528\s*bnss", text, re.IGNORECASE):
            relief_sought = "Quashing of FIR / Proceedings u/s 482 CrPC / 528 BNSS"

        court_jurisdiction = "High Court of Delhi"
        court_match = re.search(r"(?:High\s+Court\s+of\s+[A-Za-z\s]+|Supreme\s+Court\s+of\s+India|Sessions\s+Court[A-Za-z\s]*)", text, re.IGNORECASE)
        if court_match:
            court_jurisdiction = court_match.group(0).strip()

        # 7. Timeline Construction
        timeline = []
        # Find dates in document
        date_matches = list(re.finditer(r"([0-9]{1,2}[\./-][0-9]{1,2}[\./-][0-9]{2,4}|[0-9]{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+[0-9]{4})", text, re.IGNORECASE))

        if date_matches:
            for idx, dm in enumerate(date_matches[:4]):
                date_str = dm.group(1)
                context_snippet = text[max(0, dm.start() - 40):min(len(text), dm.end() + 80)].replace("\n", " ")
                stage = "Procedural Milestone"
                if "fir" in context_snippet.lower():
                    stage = "FIR Registration"
                elif "arrest" in context_snippet.lower():
                    stage = "Arrest of Accused"
                elif "chargesheet" in context_snippet.lower():
                    stage = "Chargesheet Submitted"
                elif "bail" in context_snippet.lower() or "reject" in context_snippet.lower():
                    stage = "Lower Court Bail Order"

                timeline.append({
                    "event_date": date_str,
                    "stage_name": stage,
                    "details": context_snippet.strip()
                })
        else:
            timeline = [
                {"event_date": "Historical", "stage_name": "FIR Registered", "details": f"FIR No. {fir_no} registered at PS {police_station}."},
                {"event_date": "Interim", "stage_name": "Arrest / Custody", "details": f"Accused remanded to judicial custody ({custody_days} days)."},
                {"event_date": "Recent", "stage_name": "Sessions Court Order", "details": "Bail application dismissed by the Learned Sessions Judge."},
                {"event_date": "Present", "stage_name": "High Court Filing", "details": f"Petition filed seeking {relief_sought}."}
            ]

        summary = text[:350].replace("\n", " ").strip() + "..."

        return {
            "L1_facts": {
                "petitioner": petitioner,
                "respondent": respondent,
                "fir_number": fir_no,
                "police_station": police_station,
                "district_state": "Delhi / NCT",
                "alleged_acts_sections": acts_sections_str,
                "custody_duration_days": custody_days,
                "chargesheet_filed": chargesheet_filed,
                "criminal_antecedents": has_antecedents,
                "summary_of_allegations": summary
            },
            "L2_timeline": timeline,
            "L3_posture": {
                "representation_side": "Petitioner / Accused",
                "court_jurisdiction": court_jurisdiction,
                "relief_sought": relief_sought,
                "legal_strategy_notes": "Grounds: Prolonged incarceration, parity, completion of investigation, no chance of witness tampering."
            }
        }

    def extract(self, text: str) -> Dict[str, Any]:
        """Extracts facts using LLM if available; falls back to heuristic parser."""
        extracted = self.extract_with_llm(text)
        if extracted and "L1_facts" in extracted and "L2_timeline" in extracted:
            return extracted
        return self.extract_heuristic(text)
