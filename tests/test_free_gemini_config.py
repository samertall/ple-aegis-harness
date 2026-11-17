"""Free-only model identity and credential safety regression tests."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_sponsored_submission_uses_real_gemini_model():
    text=(ROOT/'submission.yaml').read_text()
    assert 'model_api: google-cloud/gemini-3.8-flash' in text
    assert 'google-cloud/claude' not in text

def test_proxy_aliases_are_same_actual_model():
    cfg=(ROOT/'scripts/free_gemini_proxy.yaml').read_text()
    assert 'model_name: gemini-3.8-flash' in cfg
    assert 'model_name: gemini-3.8-flash-judge' in cfg
    assert cfg.count('model: gemini/gemini-3.8-flash') == 2
    assert 'os.environ/GEMINI_API_KEY' in cfg
    assert 'vertex_ai/' not in cfg and 'anthropic/' not in cfg

def test_explicit_free_safety_gate():
    script=(ROOT/'scripts/start_free_gemini_proxy.sh').read_text()
    assert 'AEGIS_FREE_ONLY' in script
    assert 'GEMINI_API_KEY' in script and 'MODEL_PROXY_KEY' in script
    assert 'litellm' in script
    assert 'gcloud auth' not in script
