"""
Interactive Gradio Dashboard for Indian Legal Judgment Prediction & 4-Tier Memory Engine.
Features:
- Dual-stage prediction (InLegalBERT + Nyaya-LLaMA)
- Visual 4-Tier Memory Inspector (L1 Facts, L2 Timeline, L3 Posture)
- Bi-directional Statutory Concordance Explorer (IPC <-> BNS, CrPC <-> BNSS)
- Google Drive automatic database snapshot sync
"""

import gradio as gr
import json
from typing import Tuple, Any
from pipeline import LegalJudgmentPipeline
from rag.concordance import lookup_concordance, extract_and_enrich_concordances

# Initialize pipeline instance (lazy loading on CPU/Colab)
pipeline = LegalJudgmentPipeline(load_gpu_models=False)

# Sample Landmark Petitions for instant one-click testing
SAMPLE_PETITION_BAIL = """IN THE HIGH COURT OF DELHI AT NEW DELHI
BAIL APPLN. NO. 1420 OF 2024

IN THE MATTER OF:
Mohd. Tariq ... Petitioner / Accused
VERSUS
State (NCT of Delhi) ... Respondent

FIR No.: 342/2023
Police Station: Connaught Place, New Delhi
Under Sections: 420, 467, 468, 471, 120B of the Indian Penal Code, 1860 (IPC)
[Corresponding Provisions: Sections 318(4), 338, 336(3), 340(2), 61(2) of Bharatiya Nyaya Sanhita, 2023]

APPLICATION UNDER SECTION 439 OF THE CODE OF CRIMINAL PROCEDURE, 1973
FOR GRANT OF REGULAR BAIL

MOST RESPECTFULLY SHOWETH:
1. The Petitioner has been in continuous judicial custody since 14.10.2023 (a period exceeding 165 days).
2. The allegations in FIR No. 342/2023 registered at PS Connaught Place pertain to alleged financial irregularities and forgery of commercial purchase orders.
3. It is respectfully submitted that the investigating officer has already concluded the investigation and filed the comprehensive Final Report / Chargesheet under Section 173 CrPC before the Learned Chief Metropolitan Magistrate on 10.01.2024.
4. All relevant computers, ledgers, and original documents have been formally seized by the police. No recovery remains to be effected from the applicant.
5. The Petitioner has no previous criminal antecedents of any nature whatsoever.
6. The Learned Sessions Judge erroneously dismissed the petitioner's regular bail application on 05.02.2024 without appreciating that continued pre-trial incarceration amounts to punitive detention, contrary to the law declared by the Hon'ble Supreme Court in Satender Kumar Antil v. CBI and Sanjay Chandra v. CBI.

PRAYER:
It is therefore respectfully prayed that this Hon'ble Court may be pleased to admit the Petitioner to regular bail on such terms and conditions as this Court deems fit and proper.
"""

SAMPLE_PETITION_HEINOUS = """IN THE HIGH COURT OF JUDICATURE AT ALLAHABAD
CRIMINAL MISC. BAIL APPLICATION NO. 8812 OF 2024

IN THE MATTER OF:
Rakesh Yadav ... Applicant / Accused
VERSUS
State of Uttar Pradesh ... Opposite Party

FIR No.: 112/2024
Police Station: Gomti Nagar, Lucknow
Under Sections: 302, 307, 34 of the Indian Penal Code, 1860
[Corresponding to Sections 103(1), 109, 3(5) of Bharatiya Nyaya Sanhita, 2023]

APPLICATION FOR BAIL UNDER SECTION 439 Cr.P.C.

FACTS:
1. FIR registered on 15.02.2024 alleging that the applicant along with co-accused fired upon the deceased causing instantaneous death.
2. The applicant was arrested on 20.02.2024 (in custody for 28 days).
3. The country-made firearm used in the crime has been recovered on the pointing out of the applicant under Section 27 of the Evidence Act.
4. Investigation is still in progress; eye-witness statements under Section 161 CrPC are being recorded, and ballistic analysis report is awaited. Chargesheet has not yet been submitted.
5. The applicant has two prior criminal cases registered against him under Section 307 IPC.
6. Applicant prays for grant of bail on grounds of false implication due to local village enmity.
"""


def process_case(petition_text: str, custom_case_id: str):
    """Executes the pipeline and formats outputs for Gradio display."""
    if not petition_text or not petition_text.strip():
        return (
            "⚠️ Please enter petition text or select one of the pre-loaded landmark samples.",
            "",
            [],
            [],
            "",
            "",
            ""
        )

    case_id = custom_case_id.strip() if custom_case_id and custom_case_id.strip() else None
    results = pipeline.run(petition_text, case_id=case_id)

    # 1. Outcome Display
    stage1 = results["stage1"]
    outcome = stage1["outcome"]
    p_allowed = stage1["probability_allowed"]
    p_dismissed = stage1["probability_dismissed"]

    if outcome == "PETITION ALLOWED":
        outcome_card = f"""
        <div style='background: linear-gradient(135deg, #0d5f35 0%, #178a4c 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 15px;'>
            <h2 style='margin:0; font-size: 24px;'>🟢 PREDICTION: PETITION ALLOWED</h2>
            <p style='margin: 8px 0 0 0; font-size: 16px;'>Confidence: <b>{int(p_allowed * 100)}%</b> | Model Engine: <b>{stage1['engine']}</b></p>
            <div style='background: rgba(255,255,255,0.2); border-radius: 8px; height: 12px; margin-top: 12px;'>
                <div style='background: #52ff9a; height: 12px; border-radius: 8px; width: {int(p_allowed * 100)}%;'></div>
            </div>
            <p style='font-size: 12px; margin-top: 6px;'>Allowed: {p_allowed:.1%} | Dismissed: {p_dismissed:.1%}</p>
        </div>
        """
    else:
        outcome_card = f"""
        <div style='background: linear-gradient(135deg, #7a1515 0%, #a82323 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 15px;'>
            <h2 style='margin:0; font-size: 24px;'>🔴 PREDICTION: PETITION DISMISSED</h2>
            <p style='margin: 8px 0 0 0; font-size: 16px;'>Confidence: <b>{int(p_dismissed * 100)}%</b> | Model Engine: <b>{stage1['engine']}</b></p>
            <div style='background: rgba(255,255,255,0.2); border-radius: 8px; height: 12px; margin-top: 12px;'>
                <div style='background: #ff6b6b; height: 12px; border-radius: 8px; width: {int(p_dismissed * 100)}%;'></div>
            </div>
            <p style='font-size: 12px; margin-top: 6px;'>Allowed: {p_allowed:.1%} | Dismissed: {p_dismissed:.1%}</p>
        </div>
        """

    # 2. Stage 2 Opinion & Ratio
    stage2 = results["stage2"]
    opinion_display = stage2["opinion_text"]
    ratio_display = stage2["ratio_decidendi"]

    # 3. L1 Atomic Facts Table
    l1 = results["L1_facts"]
    l1_data = [
        ["Petitioner / Accused", l1.get("petitioner", "N/A")],
        ["Respondent / State", l1.get("respondent", "N/A")],
        ["FIR Number & Year", l1.get("fir_number", "N/A")],
        ["Police Station", l1.get("police_station", "N/A")],
        ["Alleged Acts & Sections", l1.get("alleged_acts_sections", "N/A")],
        ["Custody Duration", f"{l1.get('custody_duration_days', 0)} days"],
        ["Chargesheet Filed?", "Yes (Investigation Complete)" if l1.get("chargesheet_filed") else "No (Investigation Pending)"],
        ["Criminal Antecedents?", "Yes (Prior Cases)" if l1.get("criminal_antecedents") else "No (Clean Record)"]
    ]

    # 4. L2 Timeline Table
    l2 = results["L2_timeline"]
    l2_data = [[item.get("event_date", "Undated"), item.get("stage_name", "Milestone"), item.get("details", "")] for item in l2]

    # 5. Concordance Table
    concordances = results["concordances"]
    concordance_data = []
    for c in concordances:
        concordance_data.append([
            c.get("statute_type", ""),
            c.get("old_law", ""),
            c.get("new_law", ""),
            c.get("title", ""),
            c.get("details", "")
        ])

    # 6. RAG Statutes
    rag_text = ""
    for idx, s in enumerate(results["retrieved_statutes"], 1):
        equiv = ""
        if s.get("concordance"):
            equiv = f" → Equivalent: {s['concordance'].get('new_law', s['concordance'].get('old_law', ''))}"
        rag_text += f"### {idx}. {s['title']}{equiv}\n**Category:** {s.get('category')} | **Act:** {s.get('act')}\n\n> {s['snippet']}\n\n---\n"

    # 7. JSON Export
    memory_json = results["memory_export_json"]

    return (
        outcome_card,
        ratio_display,
        opinion_display,
        l1_data,
        l2_data,
        concordance_data,
        rag_text,
        memory_json
    )


def lookup_statute_code(act_name: str, sec_num: str):
    """Explores bidirectional concordance table for any queried section."""
    if not sec_num:
        return "Please specify a section number (e.g. 302, 420, 438, 439, 103, 482)."
    res = lookup_concordance(act_name, sec_num)
    if not res:
        return f"No exact concordance mapping found for {act_name} Section {sec_num}."
    return json.dumps(res, indent=2)


def trigger_drive_backup():
    """Triggers WAL checkpoint and copies SQLite database to backup destination."""
    try:
        status = pipeline.backup_session()
        return f"✅ Database snapshot safely backed up:\n- File: {status['backup_file']}\n- Latest: {status['latest_file']}\n- Timestamp: {status['timestamp']}"
    except Exception as e:
        return f"❌ Backup failed: {str(e)}"


# Build Gradio Theme & Layout
custom_theme = gr.themes.Soft(
    primary_hue="emerald",
    neutral_hue="slate"
)

with gr.Blocks(title="Indian Legal Judgment & Memory Engine", theme=custom_theme) as demo:
    gr.HTML("""
    <div style='text-align: center; padding: 15px 0 10px 0;'>
        <h1 style='margin-bottom: 4px; font-size: 32px;'>⚖️ Indian Legal Judgment Prediction & 4-Tier Memory Engine</h1>
        <p style='font-size: 16px; color: #555; max-width: 900px; margin: 0 auto;'>
            Dual-Stage Legal AI combining <b>InLegalBERT</b> (Stage 1 Classifier), <b>4-Bit Nyaya-LLaMA-3.1-8B</b> (Stage 2 Judicial Reasoning),
            and a <b>TencentDB-inspired 4-Tier Memory Engine</b> with <b>BNS 2023 / BNSS 2023 Statutory Concordance</b>.
        </p>
    </div>
    """)

    with gr.Row():
        # LEFT COLUMN: Inputs & Case Controls
        with gr.Column(scale=5):
            gr.Markdown("### 📄 Case Submission & Transcripts (Tier L0)")
            custom_case_id_input = gr.Textbox(label="Custom Case ID (Optional)", placeholder="e.g. BAIL_APP_2024_01")
            petition_input = gr.Textbox(
                label="Court Petition / FIR / Judgment Text",
                placeholder="Paste the full petition, appeal grounds, or case facts here...",
                lines=14
            )

            with gr.Row():
                btn_load_sample1 = gr.Button("📋 Load Bail Sample (Cheating / IPC 420)", size="sm")
                btn_load_sample2 = gr.Button("📋 Load Heinous Sample (Murder / IPC 302)", size="sm")

            with gr.Row():
                submit_btn = gr.Button("⚖️ Adjudicate & Predict Judgment", variant="primary", size="lg")
                backup_btn = gr.Button("💾 Backup Memory to Drive", variant="secondary", size="lg")

            backup_status = gr.Textbox(label="Persistence & Backup Status", lines=2, interactive=False)

        # RIGHT COLUMN: Adjudication Results & 4-Tier Memory
        with gr.Column(scale=6):
            gr.Markdown("### 🏛️ Judicial Adjudication & Memory Inspection")
            outcome_display = gr.HTML(label="Stage 1 Outcome")

            with gr.Tabs():
                with gr.Tab("📜 Judicial Opinion & Ratio Decidendi"):
                    ratio_box = gr.Textbox(label="⚖️ Ratio Decidendi (Core Legal Ground)", lines=3, interactive=False)
                    opinion_box = gr.Textbox(label="🏛️ High Court Judicial Judgment Draft", lines=16, interactive=False)

                with gr.Tab("🧠 4-Tier Memory Visualizer (L1-L3)"):
                    gr.Markdown("#### Tier L1: Atomic Extracted Legal Entities")
                    l1_table = gr.Dataframe(
                        headers=["Legal Attribute", "Extracted Value"],
                        datatype=["str", "str"],
                        interactive=False
                    )
                    gr.Markdown("#### Tier L2: Procedural Timeline Milestones")
                    l2_table = gr.Dataframe(
                        headers=["Date", "Procedural Stage", "Details"],
                        datatype=["str", "str", "str"],
                        interactive=False
                    )

                with gr.Tab("🔄 Dual-Law Concordance (IPC ↔ BNS)"):
                    gr.Markdown("#### Cross-References Detected in Case Document")
                    concordance_table = gr.Dataframe(
                        headers=["Statute Type", "Historical Law", "New Law (2024)", "Title", "Details"],
                        datatype=["str", "str", "str", "str", "str"],
                        interactive=False
                    )
                    gr.Markdown("#### Live Statutory Concordance Explorer")
                    with gr.Row():
                        act_select = gr.Dropdown(choices=["IPC 1860", "CrPC 1973", "BNS 2023", "BNSS 2023", "IEA 1872"], value="IPC 1860", label="Select Act")
                        sec_input = gr.Textbox(label="Section Number (e.g. 302, 420, 438, 103, 482)", placeholder="302")
                        lookup_btn = gr.Button("🔍 Lookup", size="sm")
                    lookup_output = gr.Code(label="Concordance Details (JSON)", language="json")

                with gr.Tab("📚 RAG Statutory Precedents"):
                    rag_display = gr.Markdown("Retrieved statutory provisions and Supreme Court precedents will appear here.")

                with gr.Tab("💾 Raw Memory JSON Export"):
                    json_export_box = gr.Code(label="Full 4-Tier Case Memory Export", language="json")

    # Wire event handlers
    submit_btn.click(
        fn=process_case,
        inputs=[petition_input, custom_case_id_input],
        outputs=[
            outcome_display,
            ratio_box,
            opinion_box,
            l1_table,
            l2_table,
            concordance_table,
            rag_display,
            json_export_box
        ]
    )

    btn_load_sample1.click(
        fn=lambda: SAMPLE_PETITION_BAIL,
        inputs=[],
        outputs=[petition_input]
    )

    btn_load_sample2.click(
        fn=lambda: SAMPLE_PETITION_HEINOUS,
        inputs=[],
        outputs=[petition_input]
    )

    lookup_btn.click(
        fn=lookup_statute_code,
        inputs=[act_select, sec_input],
        outputs=[lookup_output]
    )

    backup_btn.click(
        fn=trigger_drive_backup,
        inputs=[],
        outputs=[backup_status]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
