"""Free Tier WSL2 runner privacy, shell syntax, and identity regression tests."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def test_interactive_credentials_stored_outside_git():
    t=(ROOT/'scripts/configure_free_local.sh').read_text()
    assert "read -r -s" in t
    assert 'chmod 600 "$CONFIG_PATH"' in t
    assert 'AEGIS_FREE_ONLY=YES' in t
    assert '%q' in t
    assert '$HOME/.config/aegis-ple' in t

def test_real_dev_runner_requires_private_config_and_docker():
    t=(ROOT/'scripts/run_free_dev.sh').read_text()
    assert '$HOME/.config/aegis-ple/free.env' in t
    assert 'docker info' in t
    assert 'RAM_KB' in t and 'CPUS' in t
    assert 'eval/run.py' in t
    assert 'uv run python -m kit artifacts' in t

def test_proxy_uses_protected_local_environment():
    t=(ROOT/'scripts/start_free_gemini_proxy.sh').read_text()
    assert 'source "$CONFIG_PATH"' in t
    assert 'AEGIS_FREE_ONLY' in t
    assert 'litellm' in t
    assert 'gcloud auth' not in t

def test_free_scripts_are_valid_bash():
    for name in ("configure_free_local.sh","run_free_dev.sh","start_free_gemini_proxy.sh"):
        path=ROOT/'scripts'/name
        check=subprocess.run(["bash","-n",str(path)],capture_output=True,text=True)
        assert check.returncode==0, check.stderr
