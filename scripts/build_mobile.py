"""Export a static, dependency-free viewer of actual saved research artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from agentguard.experiments import run_demo, run_policy_checks

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/mobile')
args = parser.parse_args()
out = args.output.resolve()
if out == ROOT or out in ROOT.parents or out == ROOT / 'web':
    parser.error('Choose a separate output directory')
out.mkdir(parents=True, exist_ok=True)
for name in ('index.html', 'style.css', 'app.js'):
    shutil.copyfile(ROOT / 'web' / name, out / name)
reports = {}
for folder in ('2026-10-25', '2026-10-25-tool-use'):
    for path in sorted((ROOT / 'reports' / folder).glob('*.json')):
        rel = f'reports/{folder}/{path.name}'
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        reports[rel] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'data': json.loads(path.read_text())}
data = {'source_commit': __import__('subprocess').check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'demo': run_demo(), 'checks': run_policy_checks(), 'reports': reports}
(out / 'data.js').write_text('window.AG_DATA = ' + json.dumps(data).replace('<', '\\u003c') + ';\n')
(out / 'replay.json').write_text(json.dumps(data['demo'], indent=2) + '\n')
print(f'Built static viewer: {out}')
