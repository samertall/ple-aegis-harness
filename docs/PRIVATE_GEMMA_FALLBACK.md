# Private local-model fallback: Gemma 4 26B A4B (zero API charges)

**Optional research path only. No dev evaluation, real model deployment or artifacts are claimed.** Aegis main remains configured for `google-cloud/gemini-3.8-flash`. Never use Gemma under a Gemini alias or use artifacts made with Gemma under a Gemini submission.

## Why this may solve the external bottleneck

The official competition supports `google-cloud/gemma-4-26b`, the Gemma 4 26B A4B open-weight model. Running it privately on sufficiently capable hardware avoids Google Gemini Free Tier 503s and does not transmit gated task material to an unpaid public model service. Model weights, source licensing and exact model identity still need verification.

Sources: https://ple-bench.com/competition/guide ; https://ai.google.dev/gemma/docs/core ; https://github.com/google-research/ple/blob/main/docs/local-models.md

## Hardware feasibility check (no API calls, no downloads)

### Windows PowerShell 5.1 (no WSL required for this check)

From a PowerShell prompt, clone the repository once:

    cd $HOME
    git clone https://github.com/samertall/ple-aegis-harness.git
    cd .\\ple-aegis-harness
    py -3 .\\scripts\\check_private_gemma_readiness.py

If the repository has already been cloned, use `cd $HOME\\ple-aegis-harness` and `git pull` instead of cloning again. If the Python launcher `py` is not available, try `python .\\scripts\\check_private_gemma_readiness.py` and verify that Python is installed. Do not use Linux shell paths or commands in PowerShell.

The checker supports **Windows host memory** directly, without WSL. This only assesses physical host resources; Windows RAM does not establish WSL2/Docker-assigned memory. An actual PLE local Docker evaluation will still require Docker Desktop/WSL2 or another Linux/Docker-capable runtime.

### WSL2 Ubuntu


In WSL2 Ubuntu, with this repository cloned, run:

    cd ~/ple-aegis-harness
    python3 scripts/check_private_gemma_readiness.py

The script checks CPU count, Linux-visible RAM, home disk free space, largest NVIDIA GPU VRAM, and Docker availability. It does not access model credentials, gated tasks, cloud services or personal account details.

PLE dev tasks need about six CPUs, 16.25 GiB of Docker RAM per task, 10 GiB base images and roughly 17 GiB world images, plus task-data space. A quantized Gemma 4 26B A4B model is roughly 16 to 19 GiB of weights before KV cache and overhead, depending on format. The readiness tool uses advisory thresholds (60 GiB free disk, and 24 GiB GPU VRAM or 48 GiB host RAM alongside Docker). These are NOT certified requirements or proof of acceptable inference speed. CPU-only inference could be too slow for PLE task limits.

## Interpreting Windows hardware results

A physical Windows host with more than 16.25 GiB of RAM does **not** prove that WSL2/Docker Desktop has 16.25 GiB allocated. The JSON now reports `host_ram_at_least_16_25_gib` separately from `docker_memory_16_25_gib_verified` (false until verified by a running Docker environment).

`disk_shortfall_to_60_gib` is the difference from this project's conservative **advisory** 60 GiB free-space target, **not** an official fixed PLE minimum. The official documentation requires room for roughly 10 GB base images, ~17 GB world images and additional task data; the system needs more than 14.51 GiB available before a full run is realistic.

If the machine has under ~24 GiB host RAM, a 6 GiB NVIDIA GPU and no Docker, do **not** download or start the 26B local model. The ~18 GB model weights alone exceed that GPU's VRAM, and sharing host RAM with PLE's Docker requirements risks out-of-memory failures. Free disk cleanup can solve only the storage bottleneck, not the model-memory issue. Keep Gemini as the competition model and pursue verified free provider capacity/organizer-approved evaluation rather than secretly substituting a smaller model.

Never delete personal files automatically. If freeing disk, use Windows Settings → System → Storage and review Temporary files, Recycling Bin, and large unused applications; verify each item before removing it.
## Next steps if hardware meets requirements

Choose a genuine local inference runtime supporting OpenAI-compatible chat completions and tool calls, for example a properly configured Ollama or vLLM installation. Review model licensing and source, and use private local weights only; avoid cloud-hosted inference and paid GPU rentals. Model downloads are substantial and should not be attempted until capacity is confirmed.

Create a *separate* branch that explicitly selects the permitted `google-cloud/gemma-4-26b` sponsored model for Stage 2. Use the same genuine Gemma 4 26B A4B model in the local official PLE kit evaluation. Never secretly swap the model under a different sponsored alias, and never reuse a prior model's artifacts after changing the selected model. Commit genuine kit-produced artifacts together with the corresponding source.

This option has not yet been provisioned because the user's local hardware and available resources have not been checked. The current Kaggle entry remains unqualified without genuine dev artifacts and validated performance evidence.
