# Competition submission gate

- [x] Original open-source harness code and MIT license prepared
- [x] `submission.yaml` selects a permitted `google-cloud/gemini-3.8-flash` sponsored model for the free-tier strategy
- [x] WebSocket protocol, task tools, MCP support implemented
- [x] Local unit/protocol tests run (73 passing on 2026-11-18)
- [x] Cover and architecture figures created
- [x] Local static preflight and guarded official check script prepared
- [x] GitHub Actions mocked tests and official PLE configuration validation passed
- [x] Official PLE Docker serve-image build passed
- [x] Manual, explicit cost-approved dev evaluation workflow published (NOT triggered under free-only instructions)
- [x] OFFLINE deterministic fake model checks and free Docker protocol preflight added (NOT real benchmark)
- [ ] Official `uv run python -m kit check ../ple-aegis-harness` passes
- [x] Gated development dataset read access approved and authenticated via GitHub Actions
- [x] Gemini Free Tier key authenticates to model metadata without inference
- [x] Official Docker package and files accepted in both genuine public smoke attempts
- [x] Private Gemma 4 26B fallback documented and offline hardware checker added (NOT deployed)
- [ ] Genuine model inference stable (Gemini returned HTTP 503, then timeout on public fixture)
- [ ] Organizer approves gated PLE data processing on unpaid Gemini API, or another privacy-compatible no-cost model is used
- [x] Free public GitHub hosted runner provisioned with temporary storage audit (105.86 GiB free after SDK cleanup; 4 CPU / 15.61 GiB RAM)
- [x] Manual genuine single-task workflow prepared with Free Tier, organizer-permission and CPU-limit gates; NEVER triggered yet
- [ ] Free hosted runner confirmed adequate for a genuine individual PLE task (4 CPU / 15.61 GiB may be insufficient)
- [ ] Reliable real model inference restored without charges and gated data transmission approved
- [ ] Genuine full dev run produces `artifacts/` using `uv run python eval/run.py`
- [ ] `uv run python -m kit artifacts ../ple-aegis-harness` passes
- [ ] Two-model experimental comparison + genuine controlled ablations done
- [ ] Dev score vs cost measured; plot 02 regenerated
- [ ] All 29 tasks reviewed; failure breakdown plot 03 regenerated
- [ ] Real engineering case study and observed failures added to Writeup
- [x] Public GitHub repository populated with source code
- [ ] Public GitHub repository contains unpacked evaluator-generated 29-task artifacts
- [ ] Committed GitHub SHA copied from `git rev-parse HEAD`
- [ ] Kaggle Writeup ≤ 2,000 words, figures attached, repo Project Link included
- [x] Aegis PLE Kaggle Writeup visibly **Submitted** in participant screenshot on 18 Nov 2026 (Project Link / commit SHA not shown)

## Separate organizer-starter baseline path

- [x] Exact unchanged published Pi/Claude organizer template imported to `official-template-baseline` (distinct from Aegis main)
- [x] Offline `kit validate` and `kit artifacts` passed for this template (28 usable + 1 empty, **old dev-set version warning**)
- [x] Kaggle Writeup drafted with attribution and exact upstream commit; **not yet submitted**
- [x] Official Docker packaging check for the template **PASSED** on unchanged upstream SHA (Actions run 44251894365)
- [ ] Baseline Kaggle Writeup saved, correct track selected and **Submit** clicked by an authenticated participant
- [x] Kaggle UI screenshot confirms an **Aegis PLE** Writeup shows **Submitted**
- [ ] Confirm the submitted Writeup's **Project Link** and exact 40-character commit SHA; cannot assert that it points to the organizer-starter baseline
- [ ] Organizer decision on eligibility and advancement to Stage 2

The organizer template's original manifest must not be mixed with the custom Aegis harness. The original Aegis qualification checkboxes above remain unresolved. 
