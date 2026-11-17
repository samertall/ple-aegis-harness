#!/usr/bin/env bash
# No billing, no keys in shell history or git. Run interactively inside WSL2.
set -Eeuo pipefail
if [[ ! -t 0 ]]; then
  echo "Requires an interactive WSL2 terminal." >&2
  exit 2
fi
echo "Aegis PLE: free-tier Gemini 3.8 Flash only."
echo "Verify the Gemini API key's project says Free Tier at https://aistudio.google.com/projects"
read -r -p "Is the key's AI Studio project UNBILLED and Free Tier? Type YES: " CONFIRM
if [[ "$CONFIRM" != "YES" ]]; then
  echo "Cancelled: no billing-linked or paid API keys permitted." >&2
  exit 2
fi
read -r -s -p "Free Tier Gemini API key (hidden): " GEM_KEY
echo
read -r -s -p "Approved Hugging Face read token (hidden): " HF_READ
echo
if [[ -z "$GEM_KEY" || -z "$HF_READ" ]]; then
  echo "Both credentials are required; nothing saved." >&2
  exit 2
fi
command -v openssl >/dev/null || { echo "openssl required" >&2; exit 2; }
PROXY_SECRET="sk-$(openssl rand -hex 24)"
CONFIG_DIR="$HOME/.config/aegis-ple"
CONFIG_PATH="$CONFIG_DIR/free.env"
umask 077
mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"
{
  printf 'export AEGIS_FREE_ONLY=YES\n'
  printf 'export GEMINI_API_KEY=%q\n' "$GEM_KEY"
  printf 'export HF_TOKEN=%q\n' "$HF_READ"
  printf 'export MODEL_PROXY_KEY=%q\n' "$PROXY_SECRET"
  printf 'export MODEL_PROXY_URL=http://127.0.0.1:4000\n'
  printf 'export JUDGE_MODEL=gemini-3.8-flash\n'
} > "$CONFIG_PATH"
chmod 600 "$CONFIG_PATH"
unset GEM_KEY HF_READ PROXY_SECRET
echo "Saved private configuration with 600 permissions: $CONFIG_PATH"
echo "Keys were not printed, committed or written to shell history."
echo "Next: bash scripts/start_free_gemini_proxy.sh"
