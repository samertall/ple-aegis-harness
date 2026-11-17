"""Offline, redacted summary of an official PLE kit check.json report.

Never connects to any model service, prints upstream response bodies, reveals
API keys, or claims engineering benchmark scores.
"""
import argparse
import json
import os
from pathlib import Path

PUBLIC_STAGES = ("submission.yaml", "files", "build", "model", "listen", "smoke", "mcp")
ALL_STAGES = PUBLIC_STAGES + ("artifacts",)


def classify_check(report):
    if not isinstance(report, dict) or not isinstance(report.get("stages"), list):
        raise ValueError("Invalid PLE check report")
    statuses, details = {}, {}
    for item in report["stages"]:
        if isinstance(item, dict) and item.get("name") in ALL_STAGES:
            name = item["name"]
            statuses[name] = str(item.get("status", "unknown"))
            details[name] = str(item.get("detail", ""))
    model_status = statuses.get("model", "not_run")
    detail = details.get("model", "").lower()
    if model_status == "fail":
        if any(x in detail for x in ("503", "unavailable", "overload")):
            code, advice = "UPSTREAM_503", "Gemini provider overload. Stop automatic retries and do not enable billing."
        elif any(x in detail for x in ("429", "quota", "rate limit")):
            code, advice = "FREE_QUOTA_LIMIT", "Rate limit or quota exhausted. Wait for Free Tier quota reset."
        elif any(x in detail for x in ("401", "403", "unauthorized", "permission")):
            code, advice = "MODEL_AUTH", "Verify secret and model entitlement without exposing credentials."
        elif "404" in detail or "not found" in detail:
            code, advice = "MODEL_NOT_FOUND", "Verify model name and proxy identity. Do not silently substitute."
        elif "timeout" in detail or "timed out" in detail:
            code, advice = "MODEL_TIMEOUT", "Provider did not respond in time. Live model connectivity not verified."
        else:
            code, advice = "MODEL_FAILURE", "Investigate proxy metadata; do not disclose raw sensitive diagnostics."
    elif model_status != "pass":
        code, advice = "MODEL_NOT_RUN", "Model connectivity stage not completed."
    elif any(statuses.get(s) != "pass" for s in ("listen", "smoke", "mcp")):
        code, advice = "PROTOCOL_NOT_PASSED", "Model available but public WebSocket/smoke/MCP stages incomplete."
    elif statuses.get("artifacts") != "pass":
        code, advice = "ARTIFACTS_MISSING", "Public protocol passes; genuine dev-set artifact export still required."
    else:
        code, advice = "KIT_CHECK_PASSED", "Kit stages pass; check task scores independently."
    return {
        "source": "official PLE kit check.json (sanitized, offline)",
        "stages": {name: statuses.get(name, "not_run") for name in ALL_STAGES},
        "blocker": code,
        "recommendation": advice,
        "public_protocol_pass": all(statuses.get(n) == "pass" for n in PUBLIC_STAGES),
        "artifacts_check_pass": statuses.get("artifacts") == "pass",
        "official_29_task_score_verified": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--github-summary", action="store_true")
    args = parser.parse_args(argv)
    if not args.path.is_file():
        print("No official checker report found")
        return 2
    try:
        results = classify_check(json.loads(args.path.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError):
        print("Invalid official checker report; raw content suppressed")
        return 2
    print(json.dumps(results, indent=2))
    if args.github_summary and os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("### Sanitized PLE checker status\n")
            f.write("- Current blocker: " + results["blocker"] + "\n")
            f.write("- Genuine 29-task measurement: **not established** by this report\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
