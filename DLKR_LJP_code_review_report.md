# Code Review Report: standalone_dlkr_ljp.py (DLKR-LJP)

*Reviewed 12 October 2026. 3,360 lines. Full read-through plus execution tests of the CPU-fallback pipeline.*

## 1. Executive summary

The file compiles and runs end to end without exceptions on all six built-in samples, and the knowledge base is internally consistent. However, **it is not a trained prediction network**. It is a hand-written rule engine (regex + bag-of-words matching + if/else) presented with machine-learning vocabulary. On realistic inputs outside the six demo buttons it produces confidently wrong legal outputs, and the confidence numbers shown in the UI are constants.

**27 findings: 7 Critical, 10 High, 6 Medium, 4 Low.**

The most serious problems:

1. The 'Legal Reasoner' falls through to **IPC 379 (Theft)** for murder, rape, dowry death, attempt to murder, intimidation and cruelty (F-01).
2. Any weapon mention is read as grievous hurt, and a gunpoint robbery is read as **attempt to murder at 95%** (F-02).
3. Negation is matched across the whole document, so 'the victim was unarmed' erases the accused's knife and turns a stabbing into theft (F-03).
4. 'No prior enmity' is read as premeditation, giving **Murder at 96%** (F-04).
5. Any narrative containing 'falsely implicated' is treated as a civil dispute and **quashed at 88%**, even an axe murder with witnesses (F-05).
6. 'Model confidence', 'probability', and the Judicial Consistency Index are hard-coded values (0.88, 0.96, 98.0, 94.5, `is_statutorily_valid=True`) (F-06).
7. The rules were written around the six demo cases, so the demos pass circularly (F-08).

## 2. Scope and method

- Read every section of the file; compiled it; programmatically validated the 44-entry knowledge base against the config vocabulary.
- Executed the pipeline in fallback mode (no torch, chromadb or gradio installed in my environment) on the 6 built-in samples plus 15 custom narratives, then ran targeted root-cause probes.
- **Not executed:** the GPU/Qwen path, the ChromaDB + MiniLM path, the InLegalBERT forward pass, and the Gradio UI. Findings there come from reading the code and are tagged **[inspection]**.
- Legal-content observations come from my own knowledge, not from primary sources. They are flagged for verification by a qualified person. This is a code review, not legal advice.
- Line numbers refer to the uploaded file.

## 3. What works

- Syntax is valid; no import errors in fallback mode.
- Knowledge base: 44 entries (20 statutes + 24 precedents), no duplicate IDs, every `article_code` is in `LAW_ARTICLES`, all 13 charges and all 20 articles are covered, and all entries share the same schema.
- The three simple demo cases (theft, sudden fight, cheating) give sensible output.
- The pipeline has a top-level error boundary in the UI handler.

## 4. Test evidence

| Input | Observed result |
|---|---|
| Gunpoint robbery, no injury | `attempt_murder_intent=True`; IPC 307 at 95%; 'Attempt to Murder' charge at 90% |
| Stabbing, victim 'died on the spot' | Weapon source set to 'Found at Spot / Casual'; top article 304 Part I (85%) above 302 (72%); Tier 4 predicted; reasoner card says IPC 379 Theft |
| Shot dead, 'no prior enmity', 'not planned' | `has_premeditation=True`; IPC 302 at 96% |
| Rape narrative with 'next morning' | Injury inferred as 'Fatal (Death)' (cosine 0.174 > 0.15); 304 Part I and 302 listed beside 376; reasoner card says IPC 379 |
| Husband strangles wife in an argument, no dowry mentioned | Dowry Death (304B) at 96% plus sudden-fight flag |
| Axe murder + 'claims he was falsely implicated' | 'No criminal offence made out' 88%, Tier 1 |
| Stabbing, 'the victim was unarmed' | Weapon erased; injury 'None'; IPC 379 Theft 65% |
| Cheating for cash on a job promise | Top article IPC 379 (95%) above 420 (93%); Tier 1; JCV shows 'RECONCILED' |
| Three accused beat victim to death, long grudge | 302 at 96%; IPC 34 / 120B never offered |
| Unrelated text (annual report, weather) | IPC 379 at 65%, Tier 1 at 88%; no abstention |
| Sample: Matrimonial | Head 1 lists IPC 379 Theft at 95% next to 498A; ratio card says theft |
| Sample: Knifepoint robbery | Injury 'Grievous (Fracture/Vital)' with no injury described; IPC 326 at 91% |
| Sample: Kakkanad (fatal) | IPC 326 at 55% and IPC 307 at 40% shown for a death case |
| Sample: Civil dispute | 0 candidates retrieved, so the 'filtered noise' table is empty |

## 5. Findings

### Critical

**F-01. Reasoner default branch returns Theft for everything unhandled** (lines 1314-1429). `_prober_reason` only has branches for theft, sudden-fight homicide, premeditated murder, robbery, civil, and cheating/forgery. Fatal-but-unclassified, rape, dowry death, 498A, attempt, intimidation, breach of trust, grievous and simple hurt all reach the 'Default Non-Violent Property' branch and are labelled IPC 379 with 'conduct alleged does not disclose violent or heinous crimes'. The Ratio Decidendi card therefore contradicts the Head 1 table (see J, K, D, B, Matrimonial above). **Fix:** add branches (or derive the ratio from the top predicted article), and return an explicit 'unsupported / insufficient facts' result instead of a default offence.

**F-02. Weapon and injury inference is wrong** (lines 1048, 1052). Any weapon match sets injury to 'Grievous (Fracture/Vital)' even when no injury is described, and any firearm without a fatal word sets `attempt_murder_intent`. A knifepoint robbery becomes grievous hurt; a gunpoint robbery becomes attempt to murder. **Fix:** require injury evidence (medical or wound language) for hurt grades, and require intent-to-kill language for attempt; brandishing alone is neither.

**F-03. Negation is document-wide, not scoped** (lines 984-986, 1023). Patterns such as `unarmed`, `secretly`, `no ... weapon`, `peacefully` are tested against the whole text. 'The victim was unarmed' nulls the accused's weapon; 'secretly followed ... held a knife at his throat' negates the robbery (verified: `is_robbery=False`). `secretly` is also not a negation of force. `no money.*transferred` (line 978) is a greedy cross-sentence match. **Fix:** scope negation to the clause or a few tokens around the target term (NegEx-style), or extract facts with an LLM and a validated schema.

**F-04. Premeditation and weapon-source regexes ignore negation and over-match** (lines 1028, 1064-1069). `no prior enmity`, `no prior planning`, `not planned` are treated as premeditation because only 'no prior animosity | no planning | heat of passion' are excluded. `on the spot` (even in 'died on the spot') marks the weapon as found at the spot, which feeds the Exception 4 logic. A long-standing `grudge` alone yields 302 at 96%.

**F-05. 'Falsely implicated' is treated as a civil dispute and discards all evidence** (lines 1132, 1645-1662, 2123-2154). `is_false_imp` sets `is_purely_civil`, which triggers the global exculpatory branch in the gate, the predictor and the reasoner: every candidate is rejected and the output is 'No Penal Provision Attracted' at 88%. A defence claim inside the narrative is not a finding and is not a civil dispute.

**F-06. Confidence values are constants, and the 'network' is not a model** (lines 2054-2516, 2817-2829, 2863). Head 3 always assigns 0.88 to one tier and 0.04 to the others; most branch probabilities are literals (0.96, 0.95, 0.85); JCI is 98.0 or 94.5 depending on one boolean; `is_statutorily_valid` is always `True`; reasoner confidence is 0.85-0.96 literals. The InLegalBERT 'boost' is the cosine between an un-fine-tuned CLS vector and CLS vectors of strings like 'ipc 302 bns 103', weighted 0.15, and in most branches `prob = ...` overwrites it. The UI labels these 'Model Confidence' and 'Consistency Index'. For a legal-outcome tool this is misleading. **Fix:** either train and calibrate real heads on labelled judgments, or relabel everything honestly as rule-derived scores and remove percentages that imply calibration.

**F-07. Keyword false positives drive the facts** (lines 1074, 1092, 1109-1118, 1101, 1045). Examples: any of `cash`, `money`, `phone`, `bag`, `gold`, `watch` sets theft (so a cheating case ranks IPC 379 above 420); `wife`, `husband` or `marriage` anywhere sets `is_matrimonial`, and a fatal case then becomes **Dowry Death** with no dowry mention (checked only for 'died' / 'death'), while a non-fatal one defaults to **498A cruelty**; modal `will` sets `is_valuable_security` (verified); `s_fatal > 0.15` fires on shared filler words ('victim', 'next morning').

### High

**F-08. Rules and tests are circular** (lines 881-947, 1038, 1103; 1536-1551). Prototype sentences reproduce the sample text ('phone sticking out of bag on bus', 'unpaid wages labourer shoved contractor ... iron rod lying nearby', 'unpaid consulting invoices ... arbitration clause'). Literals appear in code: `invest 85 lakhs`, `deceased landowner`, `tax deposit`, `three years of marriage`, `testified in court`. The six demo buttons therefore show the rules working on the cases they were written for, not generalisation. Build a held-out set that no rule author has seen.

**F-09. Scores depend on text length; no abstention** (lines 949-971). The 'dense' scorer is sparse TF cosine against hand-written prototypes. A theft sentence scores 0.458; the same sentence plus ~150 words of unrelated filler scores 0.132 (verified), while thresholds (0.15, 0.20, 0.25) are fixed. There is no out-of-domain detection, so unrelated text is predicted as theft (65%, Tier 1 at 88%).

**F-10. Head 3 and the JCV contradict each other, and the JCV has logic defects** (lines 2477-2484, 2773-2829, 2832-2841).
- Head 3 raises the tier when a secondary article is likely (compound sentencing); JCV Audit 1 then checks only the top article, flags the raised tier as a 'CRITICAL ceiling violation', and lowers it again (the cheating case above).
- Reconciliation picks `authorized_tiers[0]`, the lowest allowed tier, not the nearest valid one; the message always says 'exceeds ceiling' even when the tier is below it.
- `reconciled_head3 = list(head3_tiers)` is a shallow copy: the caller's dicts are mutated (verified), and the list is not re-sorted (Tier 1 at 0.88 ends up second).
- Exception 4 conversion changes `top_art_id` and the tier, but `head1_articles` still shows 302 (verified).
- `critical_count > 0 and not is_reconciled` can never be true (dead branch). `stat_floor` and `top_charge_name` are computed and never used. The docstring promises cross-head and floor auditing that does not exist.
- Unknown or missing articles skip the audit and are reported 'COMPLIANT' with JCI 98.0.
- Ceiling logic uses set membership of tier labels. A ceiling check should compare ordinal tiers (304 Part II allows Tier 1 or 2 as well; 307 and 326 allow life, i.e. Tier 4, per their own text).

**F-11. Head 1 / Head 2 rule anomalies** (lines 2268-2288, 2437, 2409-2425, 1794).
- IPC 307 gets 0.40 precisely when there is **no** attempt intent (`weapon_used and not attempt_murder_intent`), and 307 / 326 appear on fatal cases.
- The expected charge is forced to at least 0.85 regardless of the article probability (unrelated-text case: article 0.65, charge 0.85).
- Plain 'stabbed ... died' ranks 304 Part I (0.85) above 302 (0.72) (a systematic leniency bias), then Head 3 shows Tier 4 because the secondary article upgrades it, so the top article and the tier disagree.
- Line 1794: `(facts.is_sudden_fight or facts.injury_severity == 'Fatal (Death)')` is a tautology inside the Fatal branch.
- The fallback article display name differs in format ('IPC 379 BNS 303' vs 'IPC 379 | BNS 303').

**F-12. Dead or unreachable labels and fields** (lines 842-846, 2373-2381). `multiple_accused` and `is_conspiracy` are never set anywhere, so **IPC 120B and IPC 34 can never be predicted** (verified: no assignments). `mens_rea` is never populated. `s_cruelty`, `s_dowry_death`, `s_premed`, `s_attempt` are computed and unused. Two of the 20 advertised labels are dead.

**F-13. Statutory data issues** (verify with a qualified person; see Appendix). Notably IPC 324 is mapped to BNS 117 (BNS 117 is voluntarily causing grievous hurt; hurt by dangerous weapons is BNS 118(1)). Tier labels understate ceilings for offences that allow life imprisonment (304B, 304 Part I, 307 where hurt is caused, 326, 467). 'Bailable' is attached to Tier 1 although some Tier 1 offences (406, 498A) are, to my knowledge, non-bailable. IPC 34 is a rule of liability, not an offence, yet is mapped to the 'Criminal Conspiracy' charge. Procedural references are to CrPC / Evidence Act in most places although the file also targets post-July-2024 BNS (the reasoner mixes '482 CrPC' and '528 BNSS').

**F-14. Precedent entries need verification** (lines 144-780). I could not check these offline. Please verify citations and holdings before relying on them, in particular: Kalu Ram v. State of Rajasthan (reporter citation), Pulicherla Nagaraju (my recollection is that it concerns 302 vs 304 Part I and the factors for inferring intention, not a single-blow Exception 4 / Part II ratio), State of Maharashtra v. Joseph Mingel Koli (citation format), Anwarul Haq, Bishen Singh, Mathuradas, A.S. Krishnan. BNS 105 also differs from IPC 304 Part I (my understanding is that it introduces a five-year minimum); the KB treats them as identical.

**F-15. 'Matched Elements' column is always blank** (lines 1520, 1587 vs 1676). The retriever returns `elements`; the gate reads `essential_elements`, so the list is always empty (verified: `[]` in every run). If fixed, the matching heuristic at line 1741 would over-match, because it tests whether the first two words of an element (e.g. 'of') occur as substrings of the text.

**F-16. Gate calibration** (lines 1665-1669, config 59-63). The adaptive threshold `max(floor, min(tau, top-0.12))` can only land in 0.35-0.40 and is non-monotonic (top similarity 0.34 gives tau 0.40; 0.36 gives 0.35). `MIN_CONFIDENCE_FLOOR` is described as an absolute noise floor but is only a clamp. The fallback retriever's scores (0.6-0.95) and Chroma/MiniLM cosines (typically far lower on long legal text) sit on different scales, so the same thresholds behave differently by mode **[inspection for Chroma]**.

**F-17. LLM path defects [inspection, not run]** (lines 1199-1312). (a) `bool(parsed.get(...))` on strings makes the text 'false' truthy; (b) the `elif parsed.get('weapon_used') is None` branch also fires when the key is absent and wipes the weapon; (c) injury and article strings are not validated against the vocabularies; (d) the greedy regex `\{.*\}` can span several objects; (e) the ChatML prompt is hard-coded although `model_name` is configurable (use `apply_chat_template`); (f) pipeline output includes the prompt, and special tokens may be stripped so the `split('<|im_start|>assistant')` marker may not exist (use `return_full_text=False`); (g) `temperature` / `top_p` are ignored with `do_sample=False`; (h) the model is a general Qwen model, not a legal model.

### Medium

**F-18. Fallback retriever uses substring stems** (lines 1536-1565). `'bus'` matches 'business'; `'will'`, `'axe'` (taxes), `'dead'` (deadline), `'chest'`, `'bag'` (baggage) match inside other words. A 'business partners ... delayed shipment' narrative retrieved robbery, rape, theft and intimidation entries (verified). This contradicts the file's own claim of eliminating substring false alarms. Each matching domain adds +0.60, so scores saturate at 0.95 and discriminate poorly.

**F-19. Vector store [inspection].** The collection is seeded only when `count() == 0` (lines 1467-1468), so editing the KB leaves a stale persisted index. MiniLM-L6 truncates input at about 256 word-pieces, which cuts long entries and long narratives. The returned `content` differs between modes (composed document in Chroma, raw text in fallback).

**F-20. Prefix fusion and tokenisation** (lines 1968-2014, 2163-2191). `max_prefix_length` and `max_fact_length` are stored and never used. Text is cut by characters (1800), then `truncation=True` drops the tail of the narrative at 512 tokens while the prefix is kept. The prefix embeds the rule engine's own labels (e.g. 'EXCULPATORY: Exception 4'), so it is not independent evidence. Thirty-three label embeddings are recomputed on every request; they are static and should be cached. CLS vectors from an un-fine-tuned BERT are weak semantic embeddings.

**F-21. Deployment and security** (lines 3239-3243, 3361, 3158, 3183-3197). `share=True` with `server_name='0.0.0.0'` publishes a public link with no authentication to a tool that receives case facts (potentially personal data). Exception text, tracebacks and LLM output are interpolated into `gr.HTML` without escaping (HTML injection / XSS risk), and the traceback is returned to the client. The UI has no 'not legal advice / research prototype' notice.

**F-22. Environment and import-time hazards** (lines 25, 40-50, 1247, 1273, 3061). `IS_COLAB` is true on any machine that has a `/content` directory, which then creates `/content/drive/MyDrive/...`. `config = sys.modules[__name__]` raises `KeyError` when the file is exec'd or loaded without registering the module (verified). Directories are created at import (fails on read-only locations). `from gating.fact_factorizer import ...` refers to a module that does not exist in this standalone file; it is hit if `comprehend_and_reason` is called without a fallback extractor. `pipeline = DynamicLjpPipeline()` runs at import and may download and load a 7B model and InLegalBERT.

**F-23. Retrieval runs twice per request** (lines 2920 and 2929). The first result is discarded; log messages also print 'Step 1/5' twice. Verified: 2 calls per `run()`.

### Low

**F-24. Dead and duplicated code.** The civil-quash branch in `_prober_reason` appears twice, identically (lines 1375-1400); the second is unreachable. `reason()` is never called. Unused variables: `text_lower` (1316), `charge` (1774), `top_charge_name`, `stat_floor`. Imports are repeated in every section, and section descriptions are bare string literals.

**F-25. Naming does not match behaviour.** 'Dense Semantic' is sparse TF cosine; 'Pretrained Legal Reasoner' is a general Qwen model or a rule table; 'Multi-Head Prediction Network' has no trainable heads; the header cites a 'paper architecture' with no training or evaluation in the file.

**F-26. Structure and testing.** One 3,360-line module with CRLF line endings, no unit tests, and no metrics on any dataset. Prototype vectors are re-tokenised on every `score()` call.

**F-27. Latent crash and formatting.** `predictions.get('head1_articles', [{}])[0]` (line 3020) raises `IndexError` if the key exists but the list is empty. Tier labels use inconsistent strings between the KB ('Minor Misdemeanor / Discharge') and config / maps ('Minor Misdemeanor'), which would break any exact-match lookup; the KB tier for IPC 471 is Tier 1 while `ARTICLE_TO_TIER_MAP` says Tier 2.

## 6. Recommended fix order

1. **Stop presenting constants as confidence** (F-06) and add an explicit abstain / unsupported outcome (F-01, F-09). This is the biggest honesty issue.
2. **Fix extraction** (F-02 to F-05, F-07): scoped negation, injury evidence rules, no document-wide flags, no keyword-only theft or matrimonial triggers. Better: LLM extraction into a fixed JSON schema with validation, with rules only as a cross-check.
3. **Make the reasoner derive its ratio from the predicted article** so the cards cannot contradict each other (F-01).
4. **Repair the JCV** (F-10): ordinal tier ceilings, deep copies, apply conversions to Head 1, reconcile against the highest-tier article, and compute JCI from real checks.
5. **Correct the legal data** (F-13, F-14) with a lawyer; add statute text and holdings from primary sources.
6. **Remove demo leakage and build a held-out evaluation** (F-08, F-26). If a real model is intended, train the heads on labelled judgments and calibrate.
7. Fix wiring bugs: `elements` key (F-15), double retrieval (F-23), unreachable labels (F-12), dead branches (F-24).
8. Harden deployment (F-21, F-22): no `share=True` by default, escape HTML, lazy-load models, fix `IS_COLAB`.

Two small examples:

```python
# F-10: copy before mutating, then keep the list sorted
import copy
reconciled_head3 = copy.deepcopy(head3_tiers)
# ... update probabilities ...
reconciled_head3.sort(key=lambda t: t['probability'], reverse=True)

# F-15: use the key the retriever actually returns
elements = candidate.get('elements') or candidate.get('essential_elements', [])
```

## 7. Suggested regression tests

- Gunpoint robbery with no injury must not yield 307 or 326.
- 'The victim was unarmed' must not remove the accused's weapon.
- 'No prior enmity' must not set premeditation.
- 'Died on the spot' must not set weapon source.
- A fatal domestic case without any dowry mention must not yield 304B.
- A murder narrative containing 'falsely implicated' must not be quashed.
- A cheating narrative with 'cash' must rank 420 above 379.
- The same fact sentence with 150 words of filler appended must give a stable classification.
- Unrelated text must produce an abstain result.
- Any narrative with multiple accused must be able to reach IPC 34 / 120B.
- JCV must not mutate its input and must keep Head 3 sorted.
- Head 1 top article, Head 2 top charge and the ratio card must agree.

## Appendix: legal-data items to verify

| Item | In the file | Concern |
|---|---|---|
| IPC 324 to BNS | BNS 117 | BNS 117 is voluntarily causing grievous hurt; dangerous-weapon hurt is BNS 118(1) |
| IPC 326 | Tier 3 only; JCV excludes Tier 4 | Offence allows life imprisonment per the file's own text |
| IPC 307 | Tier 3; JCV excludes Tier 4 | Life imprisonment where hurt is caused (own text) |
| IPC 304 Part I | Tier 3 in map | Allows life imprisonment; BNS 105 may differ from IPC |
| IPC 304B | Tier 3 ('7 to 10 years') | Statute: minimum 7 years up to life |
| IPC 467 | Tier 3 | Statute: life or up to 10 years |
| IPC 392 | Tier 3 | 14-year highway case falls between Tier 3 and Tier 4; no tier covers it |
| IPC 471 | Tier 1 (KB) / Tier 2 (map) | Punishment follows the forged document; neither tier covers all cases |
| IPC 34 | Charge 'Criminal Conspiracy', Tier 2 | Common intention is a liability rule with no penalty of its own |
| IPC 120B | Tier 2 | Punishment tracks the principal offence |
| 'Bailable' in Tier 1 label | All Tier 1 offences | Verify bailability per offence (406, 498A) |
| Procedure references | CrPC 41A, 482; Evidence Act 113B | Post-July-2024 equivalents are in BNSS / BSA |
| Precedents | Several | Verify citations and holdings (see F-14) |
