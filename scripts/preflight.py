"""Non-Docker repository preflight for Aegis PLE.

This cannot replace the official competition's ``kit check`` or ``kit artifacts``.
It deliberately treats placeholder ``artifacts/`` as NOT READY.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPONSORED = {
    'google-cloud/gemini-4-argon',
    'google-cloud/gemini-3.8-flash',
    'google-cloud/gemini-3.1-pro-preview',
    'google-cloud/claude-opus-5-5',
    'google-cloud/gpt-oss-120b',
    'google-cloud/glm-5.2',
    'google-cloud/gemma-4-26b',
    'google-cloud/llama-4-maverick',
}
REQUIRED = ('submission.yaml', 'serve.py', 'harness.py', 'protocol.py', 'mcp_bridge.py', 'LICENSE')


def status() -> dict:
    checks: dict[str, dict[str, object]] = {}

    def add(key: str, ok: bool, detail: str) -> None:
        checks[key] = {'pass': bool(ok), 'detail': detail}

    for name in REQUIRED:
        add('file:' + name, (ROOT / name).is_file(), 'Must exist in repository root')
    data = (ROOT / 'submission.yaml').read_text('utf-8') if (ROOT / 'submission.yaml').is_file() else ''
    # Keep this check dependency-free; YAML parser optional.
    m_name = re.search(r'^name:\s*([a-z0-9-]+)\s*$', data, re.M)
    m_api = re.search(r'^model_api:\s*(\S+)\s*$', data, re.M)
    name = m_name.group(1) if m_name else ''
    model = m_api.group(1) if m_api else ''
    add('entry_name', bool(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,37}[a-z0-9])?', name)), f'name={name or "missing"}')
    add('sponsored_model', model in SPONSORED, f'model_api={model or "missing"}')
    add('install_serve', bool(re.search(r'^install:\s*>-', data, re.M)) and bool(re.search(r'^serve:\s*.+', data, re.M)), 'Install and serve commands must be present')
    add('configuration_size', len(data.encode('utf-8')) < 16*1024, 'submission.yaml must be < 16 KiB')
    license_text = (ROOT / 'LICENSE').read_text('utf-8') if (ROOT / 'LICENSE').is_file() else ''
    add('license', 'MIT License' in license_text or 'Apache License' in license_text, 'MIT or Apache-2.0 license')
    gallery = ROOT / 'figures'
    for name in ('00_cover.png', '01_architecture.png', '02_score_vs_cost.png', '03_failure_breakdown.png'):
        p = gallery / name
        add('figure:' + name, p.is_file() and p.stat().st_size > 1000, 'Required image exists (NOT confirmation of measured evidence)')
    artifacts = ROOT / 'artifacts'
    files = [p for p in artifacts.rglob('*') if p.is_file()] if artifacts.is_dir() else []
    placeholder_only = all(p.name == 'README.md' for p in files)
    add('real_dev_artifacts', bool(files) and not placeholder_only,
        'FAIL until eval/run.py creates genuine unpacked artifacts for 29 tasks')
    add('artifact_limits', len(files) <= 10000 and sum(p.stat().st_size for p in files) <= 512*1024*1024,
        f'{len(files)} files, {sum(p.stat().st_size for p in files)} bytes')
    draft = (ROOT / 'KAGGLE_WRITEUP_DRAFT.md').read_text('utf-8') if (ROOT / 'KAGGLE_WRITEUP_DRAFT.md').exists() else ''
    placeholders = any(p in draft for p in ('[INSERT AFTER', '[ADD PUBLIC', '[measured]', '[model A]', '[IDENTIFY A SPECIFIC'))
    add('measured_writeup', bool(draft) and not placeholders, 'FAIL while draft contains unresolved benchmark placeholders')
    lines = [p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '.pytest_cache' not in p.parts and '__pycache__' not in p.parts]
    leak = [str(p.relative_to(ROOT)) for p in lines if p.name in ('.env', 'kaggle.json', 'credentials.json')]
    add('no_credentials_in_repo', not leak, 'Potential credential files: ' + ', '.join(leak) if leak else 'No obvious credential files')
    git = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], cwd=ROOT, text=True, capture_output=True)
    add('local_git_commit', git.returncode == 0 and bool(re.fullmatch(r'[0-9a-f]{40}', git.stdout.strip())),
        'Local commit SHA exists; it is NOT evidence of a remote GitHub push')
    return {'name': 'Aegis PLE local static preflight', 'official_kit_check': 'NOT RUN',
            'official_artifacts_check': 'NOT RUN', 'checks': checks,
            'ready_for_kaggle': all(v['pass'] for v in checks.values()) and False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    result = status()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for k, value in result['checks'].items():
            print(f"{'PASS' if value['pass'] else 'BLOCKED'} {k}: {value['detail']}")
        print('\nNOT READY. Official Docker, dev model runs, artifact validation, and Kaggle submission remain required.')
    return 0 if all(v['pass'] for v in result['checks'].values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
