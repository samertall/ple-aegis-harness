"""No-cost safety checks for the local Free Tier Gemini proxy."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_local_proxy_has_no_automatic_retry_fanout():
    config = (ROOT / "scripts/free_gemini_proxy.yaml").read_text()
    assert "router_settings:" in config
    assert "num_retries: 0" in config
    assert "litellm_settings:" in config
    assert "request_timeout: 120" in config
    assert "fallbacks:" not in config


def test_gemini_model_identity_is_preserved_without_paid_fallback():
    config = (ROOT / "scripts/free_gemini_proxy.yaml").read_text()
    assert config.count("model: gemini/gemini-3.8-flash") == 2
    assert "vertex_ai/" not in config
    assert "anthropic/" not in config
    assert "os.environ/GEMINI_API_KEY" in config


def test_public_workflow_has_ephemeral_proxy_secret_and_manual_guard():
    flow = (ROOT / ".github/workflows/ple-gemini-public-smoke.yml").read_text()
    assert "openssl rand -hex 24" in flow
    assert "GITHUB_ENV" in flow
    assert "sk-aegis-ephemeral-ci-local-proxy-not-user-key" not in flow
    assert "workflow_dispatch:" in flow
    assert "\n  push:" not in flow
    assert "confirm_free_tier" in flow and "confirm_public_input" in flow


def test_checker_diagnostics_are_offline_and_never_echo_raw_provider_errors():
    script = (ROOT / "scripts/diagnose_ple_check.py").read_text()
    assert "urlopen(" not in script
    assert "requests.post(" not in script
    assert 'detail not in' not in script
    assert "official_29_task_score_verified" in script
