#!/usr/bin/env bash
# Real, free-tier Gemini 3.8 Flash proxy — never runs if explicit safety gate is absent.
# Requires Gemini key attached to an UNBILLED Google AI Studio Free Tier project.
set -Eeuo pipefail
CONFIG_PATH="$HOME/.config/aegis-ple/free.env"
if [[ -f "$CONFIG_PATH" ]]; then
  source "$CONFIG_PATH"
fi
if [[ "$(printenv AEGIS_FREE_ONLY || true)" != "YES" ]]; then
  echo "Refusing to start: set AEGIS_FREE_ONLY=YES only after verifying AI Studio displays Free Tier (no billing)." >&2
  exit 2
fi
if [[ -z "$(printenv GEMINI_API_KEY || true)" ]]; then
  echo "Missing GEMINI_API_KEY: store a free-tier Google AI Studio API key outside this repo." >&2
  exit 2
fi
if [[ -z "$(printenv MODEL_PROXY_KEY || true)" ]]; then
  echo "Missing MODEL_PROXY_KEY: generate a local random key, never commit it." >&2
  exit 2
fi
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
echo "Starting local Gemini 3.8 Flash Free Tier proxy. NO Google Cloud Vertex AI or billing integration."
echo "Only proceed if your AI Studio key's project still reports Free Tier."
exec uv run --no-project --python 3.11 --with 'litellm[proxy]==1.108.0' litellm \
  --config "$SCRIPT_DIR/free_gemini_proxy.yaml" \
  --host 0.0.0.0 --port 4000
