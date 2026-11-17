# Aegis PLE — finish qualification with genuine evidence

Current state: the public source passes 17 local protocol/integration tests, the official PLE configuration validator, and the official Docker image build. **This is NOT a complete competition submission.** No 29-task artifact export has been measured.


## Current dataset-access status

- The user has confirmed that Hugging Face approved access to the gated dev dataset.
- The user reported adding a Hugging Face access token to GitHub Actions secrets on 17 November 2026. **This report is not proof that `PLE_HF_TOKEN` is present or valid:** the separate non-billable GitHub Actions readiness workflow checks presence; the eventual official benchmark run must verify actual dataset access.
- Model proxy credentials and a suitable private Docker runner remain separate requirements. Never log tokens, paste them into chat, or commit them.

## Authorize benchmark access

1. On [Hugging Face](https://huggingface.co/datasets/google/physical-engineerings-last-exam), sign in, request and accept the dataset's gated access conditions, and create a **read-scoped** token for the approved account.
2. For free-only local PLE tests, use the documented Gemini 3.8 Flash AI Studio Free Tier via docs/FREE_GEMINI_RUNBOOK.md; never use a billing-enabled API key. The competition Stage 2 evaluator supplies sponsored Google Cloud model keys but does not provide local development keys. See [official PLE model setup](https://github.com/google-research/ple/blob/main/docs/models.md). Model/judge API usage can incur charges. Do not share keys in ChatGPT or Git.
3. Provision a Linux/WSL2 machine with Docker and the [official kit's required resources](https://github.com/google-research/ple/blob/main/eval/README.md). For GitHub Actions, register a self-hosted runner labelled **ple** (as well as linux/x64) with at least 6 CPUs, 20 GB RAM, and sufficient disk; higher resources are needed for concurrent trials.

## Option A — run on your own Linux / WSL2 machine

Clone these repositories next to each other:

    git clone https://github.com/google-research/ple.git
    git clone https://github.com/samertall/ple-aegis-harness.git

Install Harbor:

    uv tool install harbor==0.20.0 --with websockets

Set HF_TOKEN, MODEL_PROXY_URL and MODEL_PROXY_KEY as protected environment variables, *outside* the Git repository. From the official PLE directory:

    uv run python -m kit validate ../ple-aegis-harness
    uv run python -m kit check ../ple-aegis-harness
    uv run python eval/run.py ../ple-aegis-harness
    uv run python -m kit artifacts ../ple-aegis-harness
    python ../ple-aegis-harness/scripts/collect_observed_metrics.py --json

The first kit check can warn about missing artifacts before you run eval. After the exporter generates them, commit **only genuine, unpacked** artifacts together with the harness and repeat both official checks.

## Option B — manual GitHub Actions full evaluation

Add these encrypted repository Action secrets in **Settings → Secrets and variables → Actions**:

- PLE_HF_TOKEN — the approved dataset token
- PLE_MODEL_PROXY_URL — model endpoint reachable from the Docker host
- PLE_MODEL_PROXY_KEY — authorized model endpoint credential
- Optional PLE_JUDGE_BASE_URL **and** PLE_JUDGE_API_KEY (both together)
- Optional Actions variable PLE_JUDGE_MODEL (the exact local judge model used)

Select **Actions → PLE real 29-task dev evaluation (manual, billable) → Run workflow**. The workflow does **not** run automatically or without explicit `YES_I_AUTHORIZE_MODEL_COSTS` selection. It requires a dedicated self-hosted runner; it will reject incomplete results and will only push an artifacts-inclusive commit when all 29 task scores and the full checker pass. Sensitive tokens remain in GitHub Secrets. Use caution with unredacted evaluator logs on a persistent runner.

## Stage 1 scientific results and Kaggle submission

Even after authentic artifacts exist, finish these required research elements before submitting:

- Compare **at least two real development models**, preferably across different families; report model/judge setup, outcomes and token/cost differences.
- Run controlled inventory-only, verification-only and reduced-budget variants; log both improvements and failures.
- Audit actual 29-task trajectories, causes of failure and one detailed engineering case study, not hypothetical examples.
- Populate measured `metrics/dev_runs.csv` and `metrics/failures.csv` and regenerate figures 02/03. Never submit the no-data placeholder plots as performance results.
- Finalize the <2,000-word Kaggle Writeup with the cover image, three required figures, public GitHub URL, and **40-character SHA of the artifacts-inclusive commit**. Ensure Kaggle explicitly says **Submitted**, not Draft.

The project and its contributors do not claim real benchmark performance, engineering sign-off, or qualification until the official evaluator confirms them.