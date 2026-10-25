"""Run the optional pinned AgentDojo subset with local inference only."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agentguard.ollama import OllamaClient
from agentguard.agentdojo_bridge import UPSTREAM_COMMIT, run_subset

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--upstream", type=Path, required=True, help="Pinned AgentDojo source checkout")
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
sha = subprocess.check_output(["git", "-C", str(args.upstream), "rev-parse", "HEAD"], text=True).strip()
if sha != UPSTREAM_COMMIT:
    parser.error("AgentDojo checkout does not match the pinned commit")
if subprocess.run(["git", "-C", str(args.upstream), "diff", "--quiet", "HEAD"]).returncode:
    parser.error("AgentDojo tracked source has local modifications")
import agentdojo
if not Path(agentdojo.__file__).resolve().is_relative_to(args.upstream.resolve()):
    parser.error("Installed AgentDojo must be editable from the specified checkout")
client = OllamaClient(args.model, timeout=120, max_tokens=1024, context_tokens=8192)
client.preflight()
report = run_subset(client)
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2))
print(json.dumps([{k: r[k] for k in ("mode", "condition", "utility", "attacker_success")} for r in report["runs"]], indent=2))
