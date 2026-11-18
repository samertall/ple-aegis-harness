# Kaggle Writeup — organizer starter baseline (draft, NOT submitted)

**Suggested title:** PLE Official Starter Baseline — Pi on Claude Opus 5.5

**Suggested subtitle:** Reproducibility and artifact review of the organizers' unchanged 29-task engineering-agent starter

**Public GitHub project link:** https://github.com/samertall/ple-aegis-harness/tree/official-template-baseline

**Exact entry commit SHA:** `22c26a93a9e4974b16e4351faab0e860ff9fb24f`

**Original source and license:** https://github.com/physical-engineerings-last-exam/submission-template — Apache 2.0

## Summary

This is a baseline entry based on the official Physical-Engineering's Last Exam submission template. It uses the Pi coding agent connected to the Google-sponsored Claude Opus 5.5 model and the official WebSocket task protocol. The template was published by the competition organizers, and its README explicitly permits submitting the template unchanged.

The repository branch linked above preserves the original starter **byte for byte and at the identical commit SHA**, including its original `submission.yaml`, `serve.py`, Pi harness, task bridge and pre-existing development-set artifacts. It is not a newly invented or independently re-run system. All work and credit for the starter implementation and artifact generation belong to the original template authors.

## Agent architecture

The provided starter runs Pi in a dedicated `serve.py` container. The task is delivered over the PLE WebSocket protocol; a task bridge maps Pi's bash, read, write and edit operations into the evaluator's isolated engineering task container. The model selected by `submission.yaml` is `google-cloud/claude-opus-5-5`, and model credentials are supplied by the competition evaluator. The harness writes physical engineering deliverables to the task's required file paths and returns a closing result. Task grading is performed by the official PLE verifiers and rubric judges.

## Artifact provenance and results

The organizer-supplied `artifacts/manifest.json` records **29 development-task entries** from its own historical run, created October 20, 2026. The manifest's task rewards average approximately **0.4912** across the 29 entries; **25 rewards are above zero and four are zero**. This mean is calculated from the historical rewards in the original manifest and is **not a newly executed or independently regraded benchmark result**.

On November 18, 2026, I validated the unchanged starter with the current official PLE `kit validate` and `kit artifacts` commands on a temporary free GitHub-hosted runner. The artifact checker found **28 usable task folders and one empty folder**, with a **warning that the original artifact manifest refers to an earlier dev-set revision**. This does not establish a current dev-set score, and no Stage 2 hidden evaluation score is claimed. The official kit Docker build is being verified separately; only mark it passed when the linked GitHub run is green.

## Reproducibility and limitations

Reproduce the input exactly from the public branch and the commit SHA above. Use the official PLE kit `uv run python -m kit validate <entry>`, `uv run python -m kit artifacts <entry>`, and `uv run python -m kit build <entry>`. A full live `kit check` additionally needs an authorized model connection; that has **not** been completed for this starter under this entry's account. Running the entire 29-task evaluation again requires the gated dataset, sufficient Docker resources, model access and local judge configuration.

The entry is explicitly a published baseline, not an original model orchestration improvement. No 2026 Stage 2 result, novel model comparison, newly generated dev artifacts, or independently validated cost/score tradeoff is claimed. The custom Aegis PLE engineering harness is developed separately on the repository's `main` branch; its 73+ no-inference tests and experimental Gemini attempts are **not** mixed with this starter's Claude artifacts or attributed to this submitted baseline.

## Files and links

- Unmodified entry: https://github.com/samertall/ple-aegis-harness/tree/official-template-baseline
- Exact submission commit: https://github.com/samertall/ple-aegis-harness/commit/22c26a93a9e4974b16e4351faab0e860ff9fb24f
- Organizer template: https://github.com/physical-engineerings-last-exam/submission-template
- Official PLE rules: https://github.com/google-research/ple/blob/main/docs/rules.md
- Official artifact documentation: https://github.com/google-research/ple/blob/main/docs/artifacts.md
- Aegis independent R&D (not part of baseline): https://github.com/samertall/ple-aegis-harness/tree/main

## Submission status

**NOT SUBMITTED.** This is a copy-ready Kaggle writeup draft, not an accepted submission or guarantee of Stage 1 selection. An authorized Kaggle account must create/save a Writeup, choose the correct competition track, provide this public project link and exact commit SHA, and explicitly click **Submit**. The result must show `Submitted` (not `Draft`). No Kaggle action can be inferred from GitHub's passing checks.
