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

A legitimate free-model route has now been implemented: the selected sponsored model is google-cloud/gemini-3.8-flash and local LiteLLM is configured to serve that same model through the Google AI Studio Free Tier without billing. The dedicated no-inference proxy startup CI passed. The user's actual free-tier quota and Docker capacity have NOT yet been verified; there are no authentic artifacts until the official benchmark runs with real model outputs. See docs/FREE_GEMINI_RUNBOOK.md. Do not use simulated outputs or a different model under the selected model name. Do not invent task results, transfer another harness's artifacts, substitute simulator responses, or assert submission readiness without the official artifact validation.

Sources: https://github.com/google-research/ple/blob/main/docs/models.md and https://github.com/google-research/ple/blob/main/docs/artifacts.md
## Key-only check and data-policy gate

A non-inference model-metadata verifier and a GitHub Actions secret-backed workflow are available. They check only the Gemini model endpoint, never send benchmark files, and never prove project billing tier. See docs/FREE_GEMINI_RUNBOOK.md. Because Google Free Tier may use submitted content to improve products and the PLE gated access terms restrict training uses, genuine dev tasks remain blocked until the organizers authorize that processing route. This does not affect the documented no-billing requirement.

## Remote-only path for a PC with no available storage (18 November 2026)

The participant need not remove any local files, install Docker or download model weights. The project is public and its standard GitHub-hosted runner is free. Measured on a real ephemeral runner in Actions run 44248507186: 4 CPU, 15.61 GiB memory, 87.20 GiB free scratch disk initially, 105.86 GiB after deleting only unused tools in that *temporary runner*. No participant drive was touched; run results do not promise these sizes on later runners.

The 4-CPU machine falls short of the full PLE 6-CPU / 16.25-GiB recommendation, but one small task may fit. An official one-task evaluator workflow is now prepared at .github/workflows/ple-one-task-free-gated.yml, guarded behind **three independent manual affirmations**, including actual written organizer permission for sending restricted dev material to Gemini API Unpaid Services. It is NOT triggered. The user must not affirm a permission they do not possess. Results will never be passed off as a 29-task score; partial genuine artifacts may be accepted but unrun tasks receive zeros.

See docs/FREE_REMOTE_RUNNER_STRATEGY.md, the official artifacts rules, and the safe credential scanner. No paid cloud or local disk usage is required to continue the public CI/resource work.
