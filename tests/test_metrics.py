import json
from pathlib import Path
import pytest
from scripts.collect_observed_metrics import collect

def test_requires_real_manifest(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match='Official'):
        collect(tmp_path/'missing.json')

def test_incomplete_run_has_no_full_mean(tmp_path: Path):
    path=tmp_path/'manifest.json'
    path.write_text(json.dumps({'format':1,'harness':{'model_api':'google-cloud/claude-opus-5-5'},
                                'tasks':{'a':{'reward':0.5, 'ended':'ok'}}}))
    result=collect(path)
    assert result['mean_of_scored_tasks']==0.5
    assert result['full_29_task_mean'] is None
    assert result['warnings']

def test_invalid_reward_rejected(tmp_path: Path):
    path=tmp_path/'manifest.json'
    path.write_text(json.dumps({'format':1,'tasks':{'a':{'reward':2.0}}}))
    with pytest.raises(ValueError,match='Out-of-range'):
        collect(path)

def test_complete_29_run_can_compute_mean(tmp_path: Path):
    path=tmp_path/'manifest.json'
    path.write_text(json.dumps({'format':1,'tasks':{str(i):{'reward':i/28} for i in range(29)}}))
    result=collect(path)
    assert result['full_29_task_mean']==pytest.approx(0.5)
    assert not result['warnings']
