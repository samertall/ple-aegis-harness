# Aegis PLE — genuine Gemini 3.8 Flash with NO BILLING

This repository's sponsored competition model is **google-cloud/gemini-3.8-flash**. A local LiteLLM proxy calls the **same named Gemini 3.8 Flash model** through Google AI Studio's unbilled Free Tier. This is a real LLM, not the deterministic fake model used by protocol CI. It is not a claim that AI Studio and the competition gateway are configured identically.

Google source: https://aistudio.google.com/docs/pricing#gemini-3.8-flash (Free Tier standard input/output). Google-supported PLE model: https://github.com/google-research/ple/blob/main/docs/models.md. Official 29-task runner: https://github.com/google-research/ple/blob/main/eval/README.md.

## Hard zero-spending condition

Only use an API key from a project that shows **Free Tier**, with **no billing account linked**, at https://aistudio.google.com/projects. Do not choose Set up billing, upgrade, purchase credits, or use a Google Cloud Vertex AI key. Free Tier requests are rate-limited and may return 429; stop or resume after free quota resets rather than paying. Google says data sent through its Free Tier may be used to improve its products; check your Hugging Face gated-data commitments and eligibility before uploading any task contents. An API key's Free Tier status cannot be established from its prefix; confirm it visually in AI Studio first.

## Hardware

Use a computer you already own, not a paid virtual machine. The official PLE kit calls for at least 6 CPU cores and 16.25 GiB of Docker-available RAM, plus around 10 GiB for base images, around 17 GiB for world images, and additional task-data storage. A standard free hosted GitHub Actions runner is usually too small for the complete benchmark. On Windows use Docker Desktop with WSL2 integration and clone both repositories into the Linux filesystem under the home directory.

## Secure first-time setup (Windows WSL2 Ubuntu)

Install Docker Desktop with WSL2 integration, Git, Python/uv, and Harbor:

    uv tool install harbor==0.20.0 --with websockets

Clone the projects side-by-side inside WSL2:

    cd ~
    git clone https://github.com/google-research/ple.git
    git clone https://github.com/samertall/ple-aegis-harness.git
    cd ~/ple-aegis-harness
    bash scripts/configure_free_local.sh

The setup script asks you to confirm the AI Studio project is an UNBILLED Free Tier project. Enter the Gemini API key and approved Hugging Face dataset read token directly into the hidden terminal prompts. Credentials are stored only in ~/.config/aegis-ple/free.env, outside Git, with file permissions 600. Do not paste keys into ChatGPT, shell command history, screenshots, logs or the Git repository.

In terminal A run:

    cd ~/ple-aegis-harness
    bash scripts/start_free_gemini_proxy.sh

The proxy listens on port 4000; on Linux it must accept connections from Docker's bridge interface. Do not expose the port to the public Internet. If firewall settings are available, limit access to localhost and the trusted Docker bridge.

In terminal B run:

    cd ~/ple-aegis-harness
    bash scripts/run_free_dev.sh smoke

This uses **real Gemini Free Tier API requests** only after local Free Tier confirmation. The official kit performs model connectivity, WebSocket, a file-creation smoke task and MCP tool behavior. The full kit may still report not ready because authentic benchmark artifacts are absent.

To evaluate a single real task first, after smoke passes:

    bash scripts/run_free_dev.sh task data-center-site-model

Then complete all 29 tasks, one at a time to limit free-tier quota pressure:

    bash scripts/run_free_dev.sh all

The PLE exporter creates the required unpacked artifacts/ folder and original manifest. It may take many hours and several free-quota windows. Do not fabricate or modify the manifest. The free-tier model may fail on complex tasks; report failures accurately.

After completion:

    bash scripts/run_free_dev.sh artifacts
    cd ~/ple-aegis-harness
    git add -A artifacts
    git commit -m "Authentic PLE 29-task evaluator artifacts"
    git push

Then run the official real-model kit check again, calculate genuine scored metrics, regenerate score/cost and failure-breakdown figures from those metrics, and update Kaggle with the **new** 40-character final commit SHA. The competition's default rubric judge is Claude Opus 5.5; this free setup uses Gemini 3.8 Flash instead, so local rubric scores may differ from the official final judge.

## Important limitations

This is a **candidate path**, not proof that your AI Studio project offers enough free quota to finish all 29 tasks. Until the real model-backed run has completed and artifacts pass the official checker, Aegis PLE is not fully qualified. The no-billing requirement takes priority over finishing within a single day.
