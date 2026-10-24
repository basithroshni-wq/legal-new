"""
Statutory Concordance Engine for Indian Criminal Laws.
Provides bidirectional mapping and equivalence resolution between:
- IPC 1860 <-> BNS 2023 (Bharatiya Nyaya Sanhita)
- CrPC 1973 <-> BNSS 2023 (Bharatiya Nagarik Suraksha Sanhita)
- IEA 1872 <-> BSA 2023 (Bharatiya Sakshya Adhiniyam)

Crucial for Indian legal NLP since historical court judgments (e.g. ILDC) reference
old statutes, whereas current legal petitions require new provisions.
"""

import re
from typing import Dict, List, Optional, Any

# Primary Concordance Mapping: IPC 1860 <-> BNS 2023
IPC_TO_BNS: Dict[str, Dict[str, str]] = {
    "302": {
        "title": "Punishment for Murder",
        "new_act": "BNS 2023",
        "new_section": "103(1)",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine."
    },
    "307": {
        "title": "Attempt to Murder",
        "new_act": "BNS 2023",
        "new_section": "109",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Whoever does any act with such intention or knowledge that causing death would amount to murder."
    },
    "304": {
        "title": "Culpable Homicide not amounting to murder",
        "new_act": "BNS 2023",
        "new_section": "105",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Punishment for culpable homicide not amounting to murder."
    },
    "304B": {
        "title": "Dowry Death",
        "new_act": "BNS 2023",
        "new_section": "80",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Death of a woman caused by burns or bodily injury occurring within 7 years of marriage under cruelty/harassment for dowry."
    },
    "304A": {
        "title": "Causing Death by Negligence (Rash or Negligent Act)",
        "new_act": "BNS 2023",
        "new_section": "106",
        "bailable": "Bailable",
        "cognizable": "Cognizable",
        "summary": "Causing death of any person by doing any rash or negligent act not amounting to culpable homicide."
    },
    "376": {
        "title": "Punishment for Rape",
        "new_act": "BNS 2023",
        "new_section": "64",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Sexual offences punishable with rigorous imprisonment not less than 10 years extending to life."
    },
    "420": {
        "title": "Cheating and dishonestly inducing delivery of property",
        "new_act": "BNS 2023",
        "new_section": "318(4)",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Cheating and dishonestly inducing person deceived to deliver any property."
    },
    "406": {
        "title": "Criminal Breach of Trust",
        "new_act": "BNS 2023",
        "new_section": "316",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Dishonest misappropriation or conversion of entrusted property to own use."
    },
    "467": {
        "title": "Forgery of valuable security, will, etc.",
        "new_act": "BNS 2023",
        "new_section": "338",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Forgery of valuable security, will, or authority to make or transfer valuable security."
    },
    "468": {
        "title": "Forgery for purpose of cheating",
        "new_act": "BNS 2023",
        "new_section": "336(3)",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Committing forgery intending that the document forged shall be used for cheating."
    },
    "471": {
        "title": "Using as genuine a forged document",
        "new_act": "BNS 2023",
        "new_section": "340(2)",
        "bailable": "Bailable",
        "cognizable": "Cognizable",
        "summary": "Fraudulently or dishonestly using as genuine any document known to be forged."
    },
    "498A": {
        "title": "Husband or relative of husband subjecting woman to cruelty",
        "new_act": "BNS 2023",
        "new_section": "85/86",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Harassment of woman with a view to coercing her or any person related to her to meet unlawful demand for property."
    },
    "34": {
        "title": "Acts done by several persons in furtherance of common intention",
        "new_act": "BNS 2023",
        "new_section": "3(5)",
        "bailable": "Varies by principal offence",
        "cognizable": "Varies",
        "summary": "Joint criminal liability when a criminal act is done by several persons in furtherance of common intention."
    },
    "120B": {
        "title": "Punishment of Criminal Conspiracy",
        "new_act": "BNS 2023",
        "new_section": "61(2)",
        "bailable": "Non-Bailable if offence is non-bailable",
        "cognizable": "Cognizable",
        "summary": "Agreement between two or more persons to commit an illegal act."
    },
    "323": {
        "title": "Voluntarily causing hurt",
        "new_act": "BNS 2023",
        "new_section": "115(2)",
        "bailable": "Bailable",
        "cognizable": "Non-Cognizable",
        "summary": "Voluntarily causing hurt punishable with imprisonment up to 1 year or fine."
    },
    "324": {
        "title": "Voluntarily causing hurt by dangerous weapons or means",
        "new_act": "BNS 2023",
        "new_section": "117",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Causing hurt by means of any instrument for shooting, stabbing, or cutting."
    },
    "326": {
        "title": "Voluntarily causing grievous hurt by dangerous weapons",
        "new_act": "BNS 2023",
        "new_section": "118",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Causing grievous hurt with lethal instruments or corrosive substances."
    },
    "506": {
        "title": "Punishment for criminal intimidation",
        "new_act": "BNS 2023",
        "new_section": "351(2)",
        "bailable": "Bailable",
        "cognizable": "Non-Cognizable",
        "summary": "Threatening another with injury to person, reputation, or property."
    },
    "379": {
        "title": "Punishment for Theft",
        "new_act": "BNS 2023",
        "new_section": "303(2)",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Dishonestly taking any movable property out of the possession of any person without consent."
    },
    "392": {
        "title": "Punishment for Robbery",
        "new_act": "BNS 2023",
        "new_section": "309",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Theft or extortion with wrongful restraint or causing fear of death/hurt."
    },
    "395": {
        "title": "Punishment for Dacoity",
        "new_act": "BNS 2023",
        "new_section": "310",
        "bailable": "Non-Bailable",
        "cognizable": "Cognizable",
        "summary": "Robbery committed conjointly by five or more persons."
    }
}

# Primary Concordance Mapping: CrPC 1973 <-> BNSS 2023
CRPC_TO_BNSS: Dict[str, Dict[str, str]] = {
    "438": {
        "title": "Direction for grant of bail to person apprehending arrest (Anticipatory Bail)",
        "new_act": "BNSS 2023",
        "new_section": "482",
        "forum": "High Court or Court of Session",
        "summary": "Pre-arrest bail where a person has reason to believe they may be arrested on accusation of having committed a non-bailable offence."
    },
    "439": {
        "title": "Special powers of High Court or Court of Session regarding bail (Regular / Interim Bail)",
        "new_act": "BNSS 2023",
        "new_section": "483",
        "forum": "High Court or Court of Session",
        "summary": "Post-arrest release of accused in custody on bail with or without conditions."
    },
    "437": {
        "title": "When bail may be taken in case of non-bailable offence",
        "new_act": "BNSS 2023",
        "new_section": "480",
        "forum": "Magistrate Court",
        "summary": "Bail for non-bailable offences subject to statutory restrictions (e.g. offences punishable with death/life imprisonment)."
    },
    "482": {
        "title": "Saving of inherent powers of High Court (Quashing of FIR / Proceedings)",
        "new_act": "BNSS 2023",
        "new_section": "528",
        "forum": "High Court",
        "summary": "Inherent jurisdiction of High Court to prevent abuse of the process of any court and secure ends of justice (Bhajan Lal principles)."
    },
    "167": {
        "title": "Procedure when investigation cannot be completed in 24 hours (Remand / Default Bail)",
        "new_act": "BNSS 2023",
        "new_section": "187",
        "forum": "Magistrate Court",
        "summary": "Police custody / judicial remand and statutory right to indefeasible default bail after 60/90 days."
    },
    "173": {
        "title": "Report of police officer on completion of investigation (Chargesheet)",
        "new_act": "BNSS 2023",
        "new_section": "193",
        "forum": "Magistrate Court",
        "summary": "Final report forwarded by investigating officer to magistrate upon completing investigation."
    },
    "154": {
        "title": "Information in cognizable cases (First Information Report - FIR)",
        "new_act": "BNSS 2023",
        "new_section": "173",
        "forum": "Police Station / Station House Officer",
        "summary": "Mandatory registration of FIR for cognizable offences (Lalita Kumari guidelines)."
    },
    "161": {
        "title": "Examination of witnesses by police",
        "new_act": "BNSS 2023",
        "new_section": "180",
        "forum": "Investigating Agency",
        "summary": "Recording statements of persons acquainted with facts during police investigation."
    },
    "164": {
        "title": "Recording of confessions and statements",
        "new_act": "BNSS 2023",
        "new_section": "183",
        "forum": "Judicial / Metropolitan Magistrate",
        "summary": "Voluntary confession or statement recorded under solemn judicial oversight."
    },
    "313": {
        "title": "Power to examine the accused",
        "new_act": "BNSS 2023",
        "new_section": "351",
        "forum": "Trial Court",
        "summary": "Personal examination of the accused to enable them to explain incriminating circumstances."
    },
    "389": {
        "title": "Suspension of sentence pending appeal; release of appellant on bail",
        "new_act": "BNSS 2023",
        "new_section": "430",
        "forum": "Appellate Court (Sessions / High Court / Supreme Court)",
        "summary": "Suspension of substantive sentence and grant of bail to convicted appellant pending final appeal."
    },
    "397": {
        "title": "Calling for records to exercise powers of revision",
        "new_act": "BNSS 2023",
        "new_section": "438",
        "forum": "Sessions Court or High Court",
        "summary": "Criminal revision examining correctness, legality, or propriety of any finding or sentence."
    }
}

# Primary Concordance Mapping: IEA 1872 <-> BSA 2023
IEA_TO_BSA: Dict[str, Dict[str, str]] = {
    "27": {
        "title": "How much of information received from accused may be proved (Discovery of Fact)",
        "new_act": "BSA 2023",
        "new_section": "23",
        "summary": "Admissibility of confessional statement strictly limited to discovery of physical fact/weapon."
    },
    "65B": {
        "title": "Admissibility of electronic records (Mandatory Certificate)",
        "new_act": "BSA 2023",
        "new_section": "63",
        "summary": "Mandatory certification required for secondary electronic evidence (Arjun Panditrao guidelines)."
    },
    "32": {
        "title": "Cases in which statement of relevant fact by person who is dead is relevant (Dying Declaration)",
        "new_act": "BSA 2023",
        "new_section": "26",
        "summary": "Admissibility of statements made by deceased regarding cause of death."
    },
    "113B": {
        "title": "Presumption as to dowry death",
        "new_act": "BSA 2023",
        "new_section": "118",
        "summary": "Statutory legal presumption of dowry death once cruelty soon before death is established."
    }
}

# Build Inverse Mappings (BNS -> IPC, BNSS -> CrPC, BSA -> IEA)
BNS_TO_IPC: Dict[str, Dict[str, str]] = {}
for ipc_sec, data in IPC_TO_BNS.items():
    clean_bns = data["new_section"].split("(")[0].strip()
    BNS_TO_IPC[clean_bns] = {
        "old_act": "IPC 1860",
        "old_section": ipc_sec,
        "title": data["title"],
        "summary": data["summary"]
    }

BNSS_TO_CRPC: Dict[str, Dict[str, str]] = {}
for crpc_sec, data in CRPC_TO_BNSS.items():
    clean_bnss = data["new_section"].split("(")[0].strip()
    BNSS_TO_CRPC[clean_bnss] = {
        "old_act": "CrPC 1973",
        "old_section": crpc_sec,
        "title": data["title"],
        "summary": data["summary"]
    }


def lookup_concordance(act: str, section: str) -> Optional[Dict[str, Any]]:
    """
    Look up concordance mapping for a given act and section.
    Normalizes inputs (e.g. 'Section 302', '302', 's. 302').
    """
    clean_sec = re.sub(r"[^\d\w]", "", section).upper()
    clean_act = act.upper()

    if "IPC" in clean_act:
        if clean_sec in IPC_TO_BNS:
            entry = IPC_TO_BNS[clean_sec].copy()
            entry["query_act"] = "IPC 1860"
            entry["query_section"] = clean_sec
            return entry
    elif "BNS" in clean_act:
        base_sec = re.match(r"^\d+", clean_sec)
        num = base_sec.group(0) if base_sec else clean_sec
        if num in BNS_TO_IPC:
            entry = BNS_TO_IPC[num].copy()
            entry["query_act"] = "BNS 2023"
            entry["query_section"] = clean_sec
            return entry
    elif "CRPC" in clean_act:
        if clean_sec in CRPC_TO_BNSS:
            entry = CRPC_TO_BNSS[clean_sec].copy()
            entry["query_act"] = "CrPC 1973"
            entry["query_section"] = clean_sec
            return entry
    elif "BNSS" in clean_act:
        base_sec = re.match(r"^\d+", clean_sec)
        num = base_sec.group(0) if base_sec else clean_sec
        if num in BNSS_TO_CRPC:
            entry = BNSS_TO_CRPC[num].copy()
            entry["query_act"] = "BNSS 2023"
            entry["query_section"] = clean_sec
            return entry
    elif "EVIDENCE" in clean_act or "IEA" in clean_act:
        if clean_sec in IEA_TO_BSA:
            entry = IEA_TO_BSA[clean_sec].copy()
            entry["query_act"] = "IEA 1872"
            entry["query_section"] = clean_sec
            return entry

    return None


def extract_and_enrich_concordances(text: str) -> List[Dict[str, Any]]:
    """
    Scans a legal text for statutory mentions (IPC, CrPC, BNS, BNSS, IEA)
    and returns rich concordance cross-references for both old and new law.
    """
    results: List[Dict[str, Any]] = []
    seen = set()

    # Pattern for IPC: e.g. "Section 302 IPC", "302 of IPC", "u/s 420 IPC"
    ipc_pattern = re.compile(r"(?:section|sec|u/s|s\.)?\s*([0-9]{2,3}[A-Za-z]?)\s*(?:of\s+the\s+)?(?:IPC|Indian\s+Penal\s+Code)", re.IGNORECASE)
    for match in ipc_pattern.finditer(text):
        sec = match.group(1).upper()
        if sec in IPC_TO_BNS and sec not in seen:
            seen.add(sec)
            info = IPC_TO_BNS[sec]
            results.append({
                "statute_type": "Substantive Criminal Law",
                "old_law": f"IPC Section {sec}",
                "new_law": f"BNS Section {info['new_section']}",
                "title": info["title"],
                "details": f"{info['bailable']} | {info['cognizable']}",
                "summary": info["summary"]
            })

    # Pattern for CrPC: e.g. "Section 438 CrPC", "u/s 482 of Cr.P.C."
    crpc_pattern = re.compile(r"(?:section|sec|u/s|s\.)?\s*([0-9]{2,3}[A-Za-z]?)\s*(?:of\s+the\s+)?(?:CrPC|Cr\.P\.C\.|Code\s+of\s+Criminal\s+Procedure)", re.IGNORECASE)
    for match in crpc_pattern.finditer(text):
        sec = match.group(1).upper()
        if sec in CRPC_TO_BNSS and sec not in seen:
            seen.add(sec)
            info = CRPC_TO_BNSS[sec]
            results.append({
                "statute_type": "Procedural Criminal Law",
                "old_law": f"CrPC Section {sec}",
                "new_law": f"BNSS Section {info['new_section']}",
                "title": info["title"],
                "details": f"Forum: {info['forum']}",
                "summary": info["summary"]
            })

    # Pattern for BNS: e.g. "Section 103 BNS", "103(1) of BNS"
    bns_pattern = re.compile(r"(?:section|sec|u/s|s\.)?\s*([0-9]{1,3}(?:\([0-9]+\))?)\s*(?:of\s+the\s+)?(?:BNS|Bharatiya\s+Nyaya\s+Sanhita)", re.IGNORECASE)
    for match in bns_pattern.finditer(text):
        raw_sec = match.group(1).upper()
        clean = raw_sec.split("(")[0].strip()
        if clean in BNS_TO_IPC and clean not in seen:
            seen.add(clean)
            info = BNS_TO_IPC[clean]
            results.append({
                "statute_type": "Substantive Criminal Law",
                "old_law": f"IPC Section {info['old_section']}",
                "new_law": f"BNS Section {raw_sec}",
                "title": info["title"],
                "details": "Post-July 2024 Reference",
                "summary": info["summary"]
            })

    # Pattern for BNSS: e.g. "Section 482 BNSS", "BNSS 528"
    bnss_pattern = re.compile(r"(?:section|sec|u/s|s\.)?\s*([0-9]{1,3})\s*(?:of\s+the\s+)?(?:BNSS|Bharatiya\s+Nagarik\s+Suraksha\s+Sanhita)", re.IGNORECASE)
    for match in bnss_pattern.finditer(text):
        sec = match.group(1).upper()
        if sec in BNSS_TO_CRPC and sec not in seen:
            seen.add(sec)
            info = BNSS_TO_CRPC[sec]
            results.append({
                "statute_type": "Procedural Criminal Law",
                "old_law": f"CrPC Section {info['old_section']}",
                "new_law": f"BNSS Section {sec}",
                "title": info["title"],
                "details": "Post-July 2024 Reference",
                "summary": info["summary"]
            })

    return results
