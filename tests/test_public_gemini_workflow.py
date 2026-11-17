"""Guardrail tests for the manual, public-only live Gemini smoke workflow."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOW = ROOT / ".github" / "workflows" / "ple-gemini-public-smoke.yml"

def test_live_smoke_never_auto_runs_or_calls_dev_eval():
    yml = FLOW.read_text()
    assert "workflow_dispatch:" in yml
    assert "\n  push:" not in yml
    assert "\n  schedule:" not in yml
    assert "eval/run.py" not in yml
    assert "HF_TOKEN" not in yml
    assert "hf download" not in yml
    assert "kit check" in yml

def test_live_smoke_requires_explicit_billing_and_public_fixture_acknowledgment():
    yml = FLOW.read_text()
    assert "confirm_free_tier" in yml
    assert "confirm_public_input" in yml
    assert "YES_CONFIRMED_UNBILLED" in yml
    assert "YES_PUBLIC_FIXTURES_ONLY" in yml
    assert 'default: "NO"' in yml
    assert "if: ${{ inputs.confirm_free_tier" in yml
    assert "&& inputs.confirm_public_input" in yml

def test_keys_only_from_secret_and_no_output():
    yml = FLOW.read_text()
    assert "secrets.PLE_GEMINI_API_KEY" in yml
    assert 'echo "$GEMINI_API_KEY"' not in yml
    assert "generateContent" not in yml
    assert "upload-artifact" in yml
    assert "ple-public-check/check.json" in yml
