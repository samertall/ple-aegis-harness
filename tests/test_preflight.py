"""Static preflight intentionally never claims official competition readiness."""
import importlib.util
from pathlib import Path


def test_preflight_fails_for_placeholder_artifacts():
    path = Path(__file__).parents[1] / 'scripts' / 'preflight.py'
    spec = importlib.util.spec_from_file_location('aegis_preflight', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.status()
    assert result['checks']['sponsored_model']['pass']
    assert not result['checks']['real_dev_artifacts']['pass']
    assert not result['checks']['measured_writeup']['pass']
    assert result['ready_for_kaggle'] is False
