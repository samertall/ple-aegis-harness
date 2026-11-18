# Remote-only, NO-BILLING PLE development path

**No changes to the participant's PC or local storage.** The repository is public, so GitHub's standard hosted runners are free per GitHub's public-repository rules. Larger runners or paid cloud instances are NOT allowed under the user's zero-billing requirement.

## Measured successful hosted runner audit — 18 November 2026

Source: https://github.com/samertall/ple-aegis-harness/actions/runs/44248507186

| Metric | Before removing hosted-runner SDKs | After |
| --- | ---: | ---: |
| Free ephemeral root disk | 87.20 GiB | **105.86 GiB** |
| Physical memory | 15.61 GiB | 15.61 GiB |
| CPUs | 4 | 4 |

18.66 GiB were reclaimed solely from preinstalled SDKs on the ephemeral GitHub runner. These measured disk numbers may change by runner image/version and are **not** a GitHub capacity guarantee. No personal files, local drives, secrets or gated benchmark content were touched. No model inference was performed.

**Crucial limitation:** the full 29-task benchmark recommends at least six CPUs and 16.25 GiB Docker RAM; the measured hosted runner has only four CPUs and 15.61 GiB RAM. It cannot be certified for a complete PLE run, regardless of how much temporary disk we recover. Some individual tasks may still run if their own resource requirements fit; a successful resource audit is NOT evidence of such a task succeeding.

## One-task real-evaluation alternative (prepared, disabled by default)

Manual GitHub Actions workflow: https://github.com/samertall/ple-aegis-harness/actions/workflows/ple-one-task-free-gated.yml

Unlike the offline simulated test, this uses the official PLE dev-set evaluator and a real Gemini model, but **will not run** until all three explicit workflow inputs approve (1) an unbilled Free Tier project, (2) *actual written organizer clearance* to process gated PLE task contents with Gemini API's Unpaid Services, and (3) the limitations of an undersized free runner. It also requires the previously configured PLE_HF_TOKEN and PLE_GEMINI_API_KEY secrets.

The workflow selects exactly one task, keeps all task files and Docker images on the ephemeral runner, validates the genuine evaluator-generated artifacts, and uploads the result for review. The runner is not allowed to publish them automatically or change model identities. A 503 or quota/rate-limit failure is reported as a failure, never as an evaluation score.

**Before the organizer replies:** do not manually confirm a permission you do not have, start the gated workflow, move a gated dataset through unpaid Gemini, or enable Google Cloud billing. A local-only private model is also currently impractical on the participant's physical hardware.

## Why a partial evaluation matters

Official PLE artifact rules say missing dev task folders receive score zero while other task folders are graded; an entry is rejected if it has **no usable artifacts at all**. Thus one *genuine* task may yield a technically usable artifact folder if the actual grader and provenance checks pass. It is not a complete 29-task demonstration and would be a low-scoring partial entry. **Never fabricate a task manifest or substitute the deterministic test model.**

Sources:
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://github.com/google-research/ple/blob/main/docs/artifacts.md
- https://github.com/google-research/ple/blob/main/eval/README.md
- https://github.com/google-research/ple/blob/main/docs/models.md

## Remaining outside dependencies

1. Explicit confirmation from PLE organizers at ple-bench@google.com whether gated dataset processing through Gemini API Unpaid Services is permitted, or an authorized free development inference endpoint they provide.
2. A real model response that is available within free quotas; prior public smoke returned provider 503 and timeout.
3. A task workload that fits within 4 CPUs and 15.61 GiB RAM and GitHub's six-hour maximum job duration.
4. Authentic official evaluator output and artifact checker validation; repository currently has no real dev task artifacts.

No payment, hosted upgrade, or local file removal is required to continue the free infrastructure checks.
