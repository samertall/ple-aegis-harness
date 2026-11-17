# Aegis PLE: official evaluation runbook

**Status: NOT COMPETITION-READY until officially generated 29-task artifacts and measured results exist.** The current artifacts/README.md is an explicit placeholder.

## Access requirements

- A Docker-capable Linux or WSL2 machine with adequate CPU, memory and disk (see https://github.com/google-research/ple/blob/main/eval/README.md).
- Accept gated https://huggingface.co/datasets/google/physical-engineerings-last-exam access and set HF_TOKEN outside this repository.
- Configure an authorized model endpoint: for google-cloud/* use the official Google Cloud model proxy and set MODEL_PROXY_URL / MODEL_PROXY_KEY locally. This is not supplied by Kaggle for local development.
- Configure an authorized judge for rubric tasks, and identify JUDGE_MODEL in the writeup when non-official.
- Avoid committing credentials, datasets, or any local environment files.

## Reproducible commands

Clone the kit adjacent to this repository:

    git clone https://github.com/google-research/ple.git ../ple
    cd ../ple
    uv tool install harbor==0.20.0 --with websockets
    uv run python -m kit validate ../ple-aegis-harness

After setting HF_TOKEN, model and judge settings:

    uv run python -m kit check ../ple-aegis-harness
    uv run python eval/run.py ../ple-aegis-harness
    uv run python -m kit artifacts ../ple-aegis-harness
    uv run python eval/run.py --artifacts ../ple-aegis-harness
    python ../ple-aegis-harness/scripts/collect_observed_metrics.py --json --csv ../ple-aegis-harness/metrics/observed_tasks.csv

The evaluator writes and hashes artifacts/manifest.json. Do not synthesize it, tamper with artifacts, or hard-code task outputs.

## Required measured research

Run on all 29 public tasks for two models, ideally from different model families. Compare controlled inventory+verification ablations, report real scores, inference cost, runtime, and at least one concrete engineering trajectory and failure. Maintain separate run directories; do not overwrite final artifacts while testing. Audit failures with task IDs and actual transcripts. Update metrics/dev_runs.csv and metrics/failures.csv and regenerate plots with figures/build_figures.py only after data exists.

Finally commit the unpacked official artifacts alongside the exact harness that generated them, verify kit check prints "ready to submit", push the commit, copy its 40-character SHA to the Kaggle Writeup and submit. The GitHub static validation job is NOT a substitute for the Docker-backed official checker.
