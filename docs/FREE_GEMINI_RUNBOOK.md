# Genuine FREE Gemini 3.8 Flash evaluation — Aegis PLE

This strategy replaces the previous sponsored Claude configuration. The committed submission specifies **google-cloud/gemini-3.8-flash**. A local LiteLLM proxy connects the *same actual model* available on Google AI Studio Free Tier, using a model-alias named gemini-3.8-flash. It is **not** acceptable to label one model as another; this setup explicitly keeps both endpoints on Gemini 3.8 Flash.

Sources:
- Google's official PLE models: https://github.com/google-research/ple/blob/main/docs/models.md
- PLE local evaluation: https://github.com/google-research/ple/blob/main/eval/README.md
- Gemini 3.8 Flash pricing: https://aistudio.google.com/docs/pricing#gemini-3.8-flash
- Google AI Studio API keys: https://aistudio.google.com/api-keys

## Absolute no-spending guard

1. In Google AI Studio https://aistudio.google.com/projects ensure the project holding the key explicitly says **Free Tier**, without a billing account. An existing billing-linked Google Cloud project is **not acceptable** for this free-only run.
2. Use a new or existing API key from that **unbilled** Free Tier project. Do not share a key in chat, commits, or CI logs.
3. Gemini 3.8 Flash currently lists free-of-charge standard inference up to project-specific rate and daily limits. Limits vary. When reached, stop and wait until the free quota resets. Do NOT upgrade billing to continue.
4. Google may use Free Tier prompts and responses to improve its products. Check this against your legal/benchmark restrictions and privacy requirements.
5. The PLE judge can use Gemini 3.8 Flash through the same proxy, but the official leaderboard judge is Claude Opus 5.5; local rubric results are therefore approximations, not official leaderboard grades.

## Machine requirements — local only

A Windows WSL2/Docker Desktop machine is the practical zero-rental-cost route. The official kit recommends at least 6 available CPUs, 16.25GB memory to Docker and approximately 10GB base-image space plus about 17GB world images and free space for task data. Have adequate additional free disk space and install git, uv, Docker Desktop/WSL2 and Harbor 0.20.0. GitHub free hosted runners are generally too small for the full 29-task job; do not provision any paid runner.

The PLE tasks are gated; you must already have HF approval and a read token (already verified in GitHub Actions). Keep secrets outside Git.

## Local installation

Clone the public projects SIDE BY SIDE in your WSL2 Linux home directory:

    cd ~
    git clone https://github.com/google-research/ple.git
    git clone https://github.com/samertall/ple-aegis-harness.git
    uv tool install harbor==0.20.0 --with websockets

Set the following only in the WSL2 shell (not in any tracked file):

    export HF_TOKEN='your Hugging Face read token'
    export GEMINI_API_KEY='API key from a Free Tier AI Studio project WITHOUT billing'
    export MODEL_PROXY_KEY="sk-$(openssl rand -hex 24)"
    export AEGIS_FREE_ONLY=YES

**Do not put the literal placeholder strings above into a shell as real credentials.**
Never upload this shell's history, environment, or secrets to GitHub.

Start the **real** Gemini 3.8 Flash proxy in terminal A:

    cd ~/ple-aegis-harness
    bash scripts/start_free_gemini_proxy.sh

Then in terminal B, reuse the same MODEL_PROXY_KEY created in terminal A (must be exactly the same secret) and the HF token:

    export MODEL_PROXY_URL=http://127.0.0.1:4000
    export MODEL_PROXY_KEY='same random local proxy key used to start proxy'
    export HF_TOKEN='your Hugging Face read token'
    export JUDGE_MODEL=gemini-3.8-flash
    cd ~/ple
    uv run python -m kit validate ../ple-aegis-harness
    uv run python -m kit check ../ple-aegis-harness

The first full kit check can finish with an artifacts warning because the real dev export has not yet been generated. Model, listen, smoke and MCP stages must pass with the **real Gemini API**, not the offline mock.

For the first genuinely measured dev task:

    uv run python eval/run.py ../ple-aegis-harness --tasks data-center-site-model --trials 1

This is a legitimate engineering task and may take hours. Do not describe an artifact as measured before the evaluator finishes. The official dev task documents are private/gated; keep those files out of public logs and repository source.

For all 29 tasks, with actual Free Tier usage within quota:

    uv run python eval/run.py ../ple-aegis-harness --trials 1
    uv run python -m kit artifacts ../ple-aegis-harness

When the run completes, commit original unpacked artifacts/ from the evaluator and run the full official checks again. Some tasks use an LLM judge; pass JUDGE_MODEL=gemini-3.8-flash to the same proxy. Its judge rubric scores are only approximations of the competition's Claude Opus 5.5 judge.

## Expected limits

- The free Gemini API may throttle or reject sustained requests (429/503). Respect the rate limits; pausing between tasks or retries can be necessary.
- Each public task allows up to six hours. A complete sequential run may need substantial wall-clock time and local electricity. Local electricity charges, if any, are not model/API charges.
- Official exporter must create manifest.json. Do not synthesize or edit grader artifacts, borrow other entrants' outputs, or substitute the deterministic mock.
- Free Tier access and quota are **not yet verified for this particular AI Studio key**; no real dev score is claimed by committing this configuration alone.
