#!/usr/bin/env bash
# Local free-tier Gemini 3.8 Flash + genuine PLE evaluator; NEVER paid compute.
set -Eeuo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
HARNESS_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
CONFIG_PATH="$HOME/.config/aegis-ple/free.env"
if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Missing protected config. Run: bash scripts/configure_free_local.sh" >&2
  exit 2
fi
source "$CONFIG_PATH"
if [[ "$AEGIS_FREE_ONLY" != "YES" ]]; then
  echo "Free-only confirmation missing. Refusing model calls." >&2
  exit 2
fi
# Free/metadata-only authentication check. Never sends prompts, PLE data, or model calls.
if [[ "${1:-}" == "metadata" ]]; then
  python3 "$HARNESS_DIR/scripts/check_gemini_metadata.py"
  exit $?
fi
[[ -n "$GEMINI_API_KEY" && -n "$HF_TOKEN" && -n "$MODEL_PROXY_KEY" ]] ||
  { echo "Incomplete private config. Re-run interactive setup." >&2; exit 2; }
command -v docker >/dev/null || { echo "Docker required" >&2; exit 2; }
command -v uv >/dev/null || { echo "uv required" >&2; exit 2; }
docker info >/dev/null || { echo "Start Docker Desktop with WSL2 integration." >&2; exit 2; }
CPUS="$(nproc)"
RAM_KB="$(awk '/MemTotal/{print $2}' /proc/meminfo)"
if (( CPUS < 6 || RAM_KB < 17039360 )); then
  echo "Need at least 6 CPUs and 16.25 GiB of available Docker/WSL memory." >&2
  echo "Detected CPUs=$CPUS memory_kB=$RAM_KB" >&2
  exit 2
fi
PLE_DIR="$HOME/ple"
[[ -f "$PLE_DIR/eval/run.py" ]] || { echo "Clone https://github.com/google-research/ple into ~/ple" >&2; exit 2; }
MODE=""
if (( $# > 0 )); then MODE="$1"; fi
cd "$PLE_DIR"
case "$MODE" in
  smoke)
    echo "Running authentic Free Tier Gemini model, WebSocket, hello.txt and MCP smoke."
    # The full kit may still reject missing real artifacts; evaluate stages separately.
    set +e
    uv run python -m kit check "$HARNESS_DIR" --work "$HOME/.cache/plebench/aegis-free-smoke"
    set -e
    python3 - <<'PY'
import json,pathlib,sys
p=pathlib.Path.home()/".cache/plebench/aegis-free-smoke/check.json"
if not p.exists(): sys.exit("Official kit check report missing")
data=json.loads(p.read_text())
stages={s["name"]:s["status"] for s in data.get("stages",[])}
required=("model","listen","smoke","mcp")
bad={x:stages.get(x) for x in required if stages.get(x)!="pass"}
if bad: sys.exit("Real model protocol tests NOT verified: "+str(bad))
print("Real Gemini Free Tier API and protocol stages PASS.")
print("Still not ready: authentic dev-set artifacts required.")
PY
    ;;
  task)
    if (( $# < 2 )); then
      echo "Usage: bash scripts/run_free_dev.sh task TASK_ID" >&2
      exit 2
    fi
    if [[ "${PLE_GATED_DATA_PROCESSING_APPROVED:-}" != "YES" ]]; then
      echo "BLOCKED: confirm with PLE organizers that sending restricted task material to Google AI Studio Unpaid Services is allowed." >&2
      echo "Until confirmed, do not run task or all. Metadata and public smoke can still be tested." >&2
      exit 2
    fi
    uv run python eval/run.py "$HARNESS_DIR" --trials 1 --tasks "$2"
    ;;
  all)
    echo "29 genuine PLE tasks; Free Tier quotas may interrupt. No paid API key permitted."
    if [[ "${PLE_GATED_DATA_PROCESSING_APPROVED:-}" != "YES" ]]; then
      echo "BLOCKED: confirm with PLE organizers that sending restricted task material to Google AI Studio Unpaid Services is allowed." >&2
      echo "Until confirmed, do not run task or all. Metadata and public smoke can still be tested." >&2
      exit 2
    fi
    uv run python eval/run.py "$HARNESS_DIR" --trials 1
    uv run python -m kit artifacts "$HARNESS_DIR"
    ;;
  artifacts)
    uv run python -m kit artifacts "$HARNESS_DIR"
    ;;
  *)
    echo "Usage: bash scripts/run_free_dev.sh metadata | smoke | task TASK_ID | all | artifacts" >&2
    exit 2
    ;;
esac
