"""Run the optional pinned AgentDojo subset with local inference only."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agentguard.ollama import OllamaClient
from agentguard.agentdojo_bridge import PROMPT_PROFILES, UPSTREAM_COMMIT, run_subset

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--upstream", type=Path, required=True, help="Pinned AgentDojo source checkout")
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--prompt-profile", choices=list(PROMPT_PROFILES), default="original")
parser.add_argument("--mode", choices=("baseline", "prompt_only", "enforced"), action="append", dest="modes")
parser.add_argument("--clean-only", action="store_true")
parser.add_argument("--repeats", type=int, choices=(1, 2, 3), default=1)
parser.add_argument("--timeout", type=int, default=120)
parser.add_argument("--num-threads", type=int)
parser.add_argument("--require-evidence", action="store_true", help="Allow at most two host reminders when the model answers without retrieving records")
args = parser.parse_args()
if args.output.exists():
    parser.error("Output already exists; choose a new path to preserve previous results")
sha = subprocess.check_output(["git", "-C", str(args.upstream), "rev-parse", "HEAD"], text=True).strip()
if sha != UPSTREAM_COMMIT:
    parser.error("AgentDojo checkout does not match the pinned commit")
if subprocess.run(["git", "-C", str(args.upstream), "diff", "--quiet", "HEAD"]).returncode:
    parser.error("AgentDojo tracked source has local modifications")
import agentdojo
if not Path(agentdojo.__file__).resolve().is_relative_to(args.upstream.resolve()):
    parser.error("Installed AgentDojo must be editable from the specified checkout")
client = OllamaClient(args.model, timeout=args.timeout, max_tokens=1024, context_tokens=8192, num_threads=args.num_threads)
client.preflight()
args.output.parent.mkdir(parents=True, exist_ok=True)
def save_checkpoint(report):
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2))
    temporary.replace(args.output)
    last = report["runs"][-1]
    print(f"Completed {len(report['runs'])} runs: {last['mode']} {last['condition']}, utility={last['utility']}, calls={last['trace']['tool_calls']}", file=sys.stderr, flush=True)

report = run_subset(client, prompt_profile=args.prompt_profile,
                    modes=args.modes or ("baseline", "prompt_only", "enforced"),
                    clean_only=args.clean_only, repeats=args.repeats, checkpoint=save_checkpoint,
                    require_evidence=args.require_evidence)
args.output.write_text(json.dumps(report, indent=2))
print(json.dumps([{k: r[k] for k in ("mode", "condition", "utility", "attacker_success")} for r in report["runs"]], indent=2))
