#!/usr/bin/env bash
# Run on a local machine/VM with Docker, Hugging Face access, and a configured
# authorized model proxy. Creates no fabricated artifacts or scores.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KIT="${PLE_KIT_DIR:-$(dirname "$ROOT")/ple}"
if ! command -v docker >/dev/null; then echo >&2 'Docker required'; exit 2; fi
if ! docker info >/dev/null 2>&1; then echo >&2 'Docker daemon unavailable'; exit 2; fi
if [[ ! -f "$KIT/eval/run.py" ]]; then echo >&2 "Clone https://github.com/google-research/ple to $KIT"; exit 2; fi
if [[ -z "${HF_TOKEN:-}" ]]; then echo >&2 'HF_TOKEN required (gated data license)'; exit 2; fi
if [[ -z "${MODEL_PROXY_URL:-}" || -z "${MODEL_PROXY_KEY:-}" ]]; then
 echo >&2 'MODEL_PROXY_URL and MODEL_PROXY_KEY required for selected sponsored model'; exit 2;
fi
if ! command -v harbor >/dev/null; then echo >&2 'Install harbor: uv tool install harbor==0.20.0 --with websockets'; exit 2; fi
cd "$KIT"
uv run python -m kit check "$ROOT"
uv run python eval/run.py "$ROOT"
uv run python -m kit artifacts "$ROOT"
cat <<'EOF'
Official commands finished. Inspect all output manifests, write down real scores
and run two-model ablations before changing the Kaggle writeup. Do not modify
exported artifacts by hand; commit the unpacked directory to GitHub.
EOF
