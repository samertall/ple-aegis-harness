"""Read genuine PLE artifacts/manifest.json; never fabricate benchmark scores."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'artifacts' / 'manifest.json'

def collect(manifest_path: Path = MANIFEST) -> dict:
    if not manifest_path.exists():
        raise FileNotFoundError(
            f'Official dev-set manifest missing: {manifest_path}. '
            'Run uv run python eval/run.py <entry> first. '
            'Do not create or modify this manifest manually.'
        )
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    if data.get('format') != 1 or not isinstance(data.get('tasks'), dict):
        raise ValueError('Not a PLE exporter format-1 task manifest')
    records = []
    for task, item in sorted(data['tasks'].items()):
        if not isinstance(item, dict):
            continue
        reward = item.get('reward')
        if isinstance(reward, bool) or not isinstance(reward, (int, float)):
            reward = None
        elif not 0 <= reward <= 1:
            raise ValueError(f'Out-of-range reward for {task}: {reward}')
        records.append({
            'task_id': task,
            'status': item.get('ended', 'unknown'),
            'local_reward': reward,
            'run': item.get('run', ''),
            'exported_files': len(item.get('files') or {}),
            'has_final_message': bool(item.get('final_message')),
            'skipped_files': len(item.get('skipped') or []),
        })
    measured = [x['local_reward'] for x in records if x['local_reward'] is not None]
    complete = len(records) == 29 and len(measured) == 29
    return {
        'origin': 'PLE exporter manifest; local grader, not final leaderboard',
        'recorded_tasks': len(records),
        'scored_tasks': len(measured),
        'expected_public_dev_tasks': 29,
        'mean_of_scored_tasks': sum(measured)/len(measured) if measured else None,
        'full_29_task_mean': sum(measured)/29 if complete else None,
        'model_api': (data.get('harness') or {}).get('model_api'),
        'records': records,
        'warnings': [] if complete else ['Incomplete evaluation: full 29-task mean unavailable.'],
    }

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, default=MANIFEST)
    ap.add_argument('--csv', type=Path)
    ap.add_argument('--json', action='store_true')
    args=ap.parse_args()
    try:
        summary=collect(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'NOT MEASURED: {exc}')
        return 2
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open('w',newline='',encoding='utf-8') as out:
            keys=list(summary['records'][0]) if summary['records'] else [
                'task_id','status','local_reward','run','exported_files','has_final_message','skipped_files']
            writer=csv.DictWriter(out,fieldnames=keys)
            writer.writeheader()
            writer.writerows(summary['records'])
    if args.json:
        print(json.dumps(summary,indent=2))
    else:
        print(f"Exported {summary['recorded_tasks']}/29 tasks; " +
              f"scored {summary['scored_tasks']}; full mean {summary['full_29_task_mean']}")
        for w in summary['warnings']:
            print('WARNING:',w)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
