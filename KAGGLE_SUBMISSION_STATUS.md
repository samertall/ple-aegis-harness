# Aegis PLE submission status — 2026-11-17

**NOT SUBMITTED. NOT READY FOR KAGGLE REVIEW.**

## Completed in the ChatGPT workspace

- Original harness with WebSocket protocol v1, file tools, MCP relay, model usage reporting, and verification loop.
- `submission.yaml` choosing the sponsored `google-cloud/claude-opus-5-5` model.
- MIT license, project documentation, Kaggle Writeup template.
- Four PNG illustrations (cover, architecture, two explicitly UNMEASURED placeholders).
- Local regression suite: 10 passed on 2026-11-17.
- Static preflight and CI workflow; official check runner that refuses to run without prerequisites.
- Local Git initialization and commit **(if present in the extracted bundle; not equivalent to GitHub publication)**.

## External access blockers verified in this session

- No Docker executable/daemon: official `kit check` cannot run in this container.
- No Hugging Face read token or accepted gated dataset terms: 29 dev tasks cannot be obtained here.
- No sponsored-model proxy URL/key or personally authorized alternative: no genuine model-backed dev runs or measurements.
- GitHub connection targets existing repositories only; `samertall/ple-aegis-harness` returns 404 as of the check.
- No connected Kaggle writeup submission action; the public website could be read but not operated as the account holder.

## Must be completed before submission

1. Create an empty public `samertall/ple-aegis-harness` repository at https://github.com/new.
2. Publish the project, **excluding secrets**.
3. Obtain authorized Docker/Hugging Face/model proxy access (see `README.md`).
4. Execute `bash scripts/official_commands.sh` on a host that meets prerequisites; correct any failures.
5. Produce genuine `artifacts/`, score and audit all 29 dev tasks, run cross-model ablations.
6. Fill `metrics/*.csv`, regenerate the measured plots, and complete the two thousand-word Writeup without fabricated data.
7. Push the final code **with real unpacked `artifacts/`**, get the exact remote commit SHA, attach three real figures and cover, then submit the Kaggle Writeup at https://www.kaggle.com/competitions/physical-engineerings-last-exam/writeups.

Deadline shown by the competition: **2027-01-05** (check the official local cutoff before submission). Draft writeups are not judged.
