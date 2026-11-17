# Genuine Gemini Free Tier public smoke — verified results

**Date:** 17 November 2026
**Workflow run:** https://github.com/samertall/ple-aegis-harness/actions/runs/44082068922
**Harness SHA tested:** 3f1932d5d9b514d3f80a74094080ca0c71930167
**Selected sponsored model:** google-cloud/gemini-3.8-flash

## Scope and spend controls

The user confirmed the Google AI Studio API key was attached to an unbilled Free Tier project. The repository secret PLE_GEMINI_API_KEY was used by a one-time GitHub-hosted public smoke workflow. The workflow used only the official PLE kit's public model-connectivity, hello.txt and MCP fixture stages. No HF_TOKEN or gated PLE task contents were used. This did NOT invoke eval/run.py or make scored engineering-task artifacts. The one-time automatic trigger was deleted after the run started; the reusable workflow stays manual-only.

## Attempt 1

- submission.yaml: PASS (google-cloud/gemini-3.8-flash)
- files: PASS
- Docker build: PASS (115 MiB)
- model: FAIL — HTTP 503 from upstream Gemini, `UNAVAILABLE`, reported high demand
- WebSocket listen / public smoke / MCP: NOT RUN because model probe failed
- artifacts: FAIL — expected (no authentic 29-task dev evaluation has occurred)

## Attempt 2 (one bounded retry)

- submission.yaml: PASS
- files: PASS
- Docker build: PASS (115 MiB)
- model: FAIL — timed out while attempting a real Gemini Free Tier model response through the proxy
- WebSocket listen / public smoke / MCP: NOT RUN because model probe failed
- No further live model calls made; stop rather than repeatedly consuming free-tier quota.

## What has NOT been established

These results do not prove the model/harness can complete the live smoke and MCP checks; the deterministic offline fixture previously passed them, but that is distinct from a genuine Gemini-backed result. No full 29-task run has been performed; no task scores, judge comparisons, cost curves or evaluator-generated artifacts exist. The user's Free Tier confirmation has not been independently verified against their billing account.

## Next actions

1. Retest the public model connection only after Gemini 3.8 Flash's Free Tier capacity becomes stable (Google documents that 503s represent service overload and recommends bounded exponential backoff).
2. Obtain organizer confirmation that the gated PLE tasks may be processed by Gemini API's Unpaid Services, which may use submitted content to improve products. Do not upload gated tasks before permitted.
3. Use the existing secure local runner on sufficiently provisioned WSL2/Docker, or another explicitly authorized no-cost option, to produce genuine dev artifacts; run kit artifacts and update the Kaggle writeup using measured evidence.

Sources: https://ai.google.dev/gemini-api/docs/api-errors and https://github.com/google-research/ple/blob/main/eval/README.md