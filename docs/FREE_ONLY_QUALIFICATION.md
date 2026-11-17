# Free-only Aegis PLE qualification track

**Safety rule:** No Cloud billing activation, paid inference, paid hosted compute, or explicitly billable model experiments. The existing manual billable workflow must NOT be triggered under this constraint.

## What is actually free

- GitHub source, CI unit tests, official kit configuration/Docker-build checks, and the OFFLINE model-protocol simulator on a public GitHub repository, subject to GitHub-hosted runner availability.
- The approved gated Hugging Face dev dataset can be accessed by the user's read-only token. The CI token authentication check already succeeded; no engineering benchmark has been run.
- Google-sponsored models are free **when invoked by the competition evaluation server**. That entitlement does not mean unlimited free local model testing.

## Free OFFLINE official-kit protocol preflight

The file scripts/mock_model_proxy.py is a deterministic fake OpenAI-compatible server. It supports only the official kit's connectivity probe, hello.txt smoke test and secret_word MCP test, and explicitly rejects engineering tasks.

The GitHub Actions workflow .github/workflows/ple-free-protocol-check.yml starts this local simulator, runs its unit tests, then invokes the real official PLE Docker checker against it. The workflow reports model interface, WebSocket smoke and MCP stage results **as simulated integration tests**. It does not use the Google-sponsored model, makes no paid API calls and produces no real dev outputs.

Do not submit its results as an engineering benchmark score. The grader must receive authentic exported artifacts made by eval/run.py running real task materials with a model.

## What remains before genuine qualification

1. Execute the official 29-task development evaluation using an authorized real model, real task containers and graders.
2. Commit the unpacked 29-task artifacts and exporter manifest alongside the exact harness that produced them; run the full kit checker with a real endpoint.
3. Complete measured experiments, score-versus-cost and failure figures, and a real engineering case study; submit the Kaggle Writeup with the final 40-character commit SHA.

The local Google Cloud Vertex AI proxy is **billed to the user** according to upstream docs/models.md. It must remain disabled under this free-only constraint. A free open-weight model on hardware the user already owns could support experimentation, but would not reproduce the final Claude Opus 5.5 configuration and is not evidence of its score.

## Current unresolved limitation

A legitimate free-model route is now being prepared: change the selected sponsored model to google-cloud/gemini-3.8-flash and use the same Gemini 3.8 Flash model through the Google AI Studio Free Tier via a local LiteLLM proxy. The user's actual free-tier quota and Docker capacity have NOT yet been verified; there are no authentic artifacts until the official benchmark runs with real model outputs. See docs/FREE_GEMINI_RUNBOOK.md. Do not use simulated outputs or a different model under the selected model name. Do not invent task results, transfer another harness's artifacts, substitute simulator responses, or assert submission readiness without the official artifact validation.

Sources: https://github.com/google-research/ple/blob/main/docs/models.md and https://github.com/google-research/ple/blob/main/docs/artifacts.md