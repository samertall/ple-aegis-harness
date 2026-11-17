# Aegis PLE: Evidence-First Engineering Agents With a Verification Gate

**GitHub repository:** https://github.com/samertall/ple-aegis-harness  
**Exact submission commit SHA (40 characters):** `[INSERT FINAL 40-CHAR SHA AFTER COMMITTING ACTUAL 29-TASK ARTIFACTS]`  
**Target sponsored model:** `google-cloud/gemini-3.8-flash`  
**Status:** **DRAFT — DO NOT SUBMIT WITHOUT OFFICIAL DEV EVALUATION**

> **Hypothesis, not yet a measured finding:** A long-horizon engineering agent can improve deliverable reliability by treating evidence collection and output verification as explicit phases rather than stopping after the first plausible answer.

## 1. Problem and architecture

Physical engineering projects require an agent to coordinate project folders, drawings, calculations, equipment tables, standards and output file formats. An engineering artifact may look plausible yet fail because a beam clearance, electrical phase conversion or required filename was overlooked. The core challenge is not just generating an answer: it is producing auditable deliverables with consistent assumptions and traceable calculations.

Aegis PLE is a model-agnostic tool-using harness configured for a single sponsored model in Stage 2. It accepts PLE v1 task messages over WebSocket, passes evaluator-scoped file and shell operations to the task container, and optionally calls tools advertised by task MCP servers. The model sees the task and a bounded file inventory, can inspect data and run task-installed solvers, then receives an independent output file listing on its first apparent completion. The verification prompt requests path, format and calculation checks before finalizing.

**Figure 1:** `figures/01_architecture.png` (implementation architecture).  
**Cover:** `figures/00_cover.png`.

## 2. Engineering reasoning and case study

**Required real case:** `[IDENTIFY A SPECIFIC PUBLIC DEV TASK THAT WAS RUN]`.

**Engineer baseline workflow:** `[DESCRIBE AN APPROPRIATE LICENSED-ENGINEER WORKFLOW WITH SOURCES/CONSTRAINTS; DO NOT MISREPRESENT LICENSED VALIDATION]`.

**Observed agent trajectory:** `[CITE ACTUAL TOOL STEPS, CALCULATION EVIDENCE, OUTPUT PATHS, ASSUMPTIONS, TEST RESULTS]`.

**Review:** `[STATE WHERE THE AGENT MATCHED THE EXPECTED WORKFLOW, WHERE IT MISREAD OR MISAPPLIED DATA, AND WHY]`.

The agent's system instructions require file inspection, explicit unit accounting, programmatic computation when possible, cross-sheet consistency and reopening deliverables. These are implemented instructions rather than evidence of successful execution; task-level outcomes must be drawn from real evaluation transcripts.

## 3. Controlled failure analysis

On the 29 development tasks, classify each observed failure into: missing deliverable, incorrect path/format, incorrect source interpretation, code/standard selection, unit/quantity error, solver/geometry error, premature finalization, and timeout/tool failure. Keep evidence snippets and task IDs. If a task has multiple independent failures, document the classification convention.

**Figure 3:** `figures/03_failure_breakdown.png` — **CURRENTLY A NO-DATA PLACEHOLDER**. Regenerate from measured `metrics/failures.csv`.

**Non-obvious observation supported by actual results:** `[INSERT AFTER AUDIT; DON'T INVENT]`.

**Failed intervention:** `[REPORT AT LEAST ONE REAL EXPERIMENT THAT DID NOT HELP; IF NONE, SAY NONE]`.

## 4. Cross-model generalizability and ablations

Evaluate at least two permitted development models, ideally different families, on identical public tasks. Compare three harness variants: baseline (`VERIFY_GATE=0`, `ENABLE_INVENTORY=0`), inventory only, and full verification gate. Maintain a record of judge model, evaluator version, token accounting and model proxy settings. Before final Stage 2 submission, restore the single designated sponsored `model_api`.

| Model | Variant | Mean dev score | Cost (USD) | Tokens / calls | Judge |
|---|---|---:|---:|---:|---|
| `[model A]` | baseline | `[measured]` | `[measured]` | `[measured]` | `[judge]` |
| `[model A]` | full | `[measured]` | `[measured]` | `[measured]` | `[judge]` |
| `[model B]` | baseline | `[measured]` | `[measured]` | `[measured]` | `[judge]` |
| `[model B]` | full | `[measured]` | `[measured]` | `[measured]` | `[judge]` |

**Ablation result:** `[DIFFERENCE IN MEASURED SCORES, COSTS AND PER-TASK PASSES]`.

## 5. Efficiency and scaling

Plot measured mean dev score against cost using `metrics/dev_runs.csv`. Also compare prompt/completion tokens, calls and runtime for each budget. Document the point at which further tool turns or verification passes stop adding measurable value; if the data do not establish a plateau, report that honestly.

**Figure 2:** `figures/02_score_vs_cost.png` — **CURRENTLY A NO-DATA PLACEHOLDER**. Replace before submission.

**Observed Pareto and headroom:** `[REPORT ACTUAL PERFORMANCE-COST POINTS AND LIMITATIONS]`.

## 6. Reliability and reproducibility

The implementation reports model token usage over the PLE protocol, bounds tool output for context control, retries transient API errors, reserves time for completion, and limits concurrent task commands. It does not embed answers to development or hidden tasks. The open-source harness and complete generated dev artifacts must be committed at the same exact Git SHA and validated using the official `kit check` and `kit artifacts` commands.

**Local development details:** `[KIT COMMIT, DATASET REVISION, MODEL/JUDGE VERSION, COST METHOD, HARDWARE AND REPRODUCIBILITY RUNS]`.

**Stage 1 evaluation results:** `[INSERT ONLY VERIFIED SCORES, CASE STUDY AND LIMITATIONS]`.

**Limitations:** Engineering correctness remains an empirical question until graded task outputs exist. No licensed engineering sign-off is provided. We do not claim hidden-task performance or actual accuracy gains from an unexecuted experiment.

---

*Do not submit this document with its bracketed fields, unmeasured plots or placeholder artifacts. Finish the official runs and replace these sections with observed, reproducible evidence first.*
