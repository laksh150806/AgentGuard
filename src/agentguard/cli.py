"""Local commands; JSON output is suitable for saving and inspecting."""

import argparse
import json

from agentguard.experiments import run_demo, run_policy_checks


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentGuard — free local policy research foundation")
    parser.add_argument("command", choices=("demo", "check"), help="Run a scripted demo or policy smoke checks")
    args = parser.parse_args()
    output = run_demo() if args.command == "demo" else run_policy_checks()
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0
