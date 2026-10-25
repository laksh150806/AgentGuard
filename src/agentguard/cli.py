"""Local commands; JSON output is suitable for saving and inspecting."""

import argparse
import json

from agentguard.agent import run_agent
from agentguard.core import Session, SupportSandbox
from agentguard.experiments import run_demo, run_policy_checks
from agentguard.ollama import ModelError, OllamaClient
from agentguard.smoke import run_smoke


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentGuard — free local policy research foundation")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="Run the scripted policy demo (no model)")
    commands.add_parser("check", help="Run scripted policy smoke checks (no model)")
    for name in ("doctor", "run", "smoke"):
        sub = commands.add_parser(name, help="Check a local model" if name == "doctor" else "Run a real local agent")
        sub.add_argument("--model", required=True, help="Already installed Ollama model; no automatic downloads")
        sub.add_argument("--port", type=int, default=11434, help="Local Ollama port on 127.0.0.1")
        sub.add_argument("--timeout", type=int, default=60)
        sub.add_argument("--max-tokens", type=int, default=512)
        if name in ("run", "smoke"):
            if name == "run":
                sub.add_argument("--task", required=True)
            sub.add_argument("--max-turns", type=int, default=6)
            sub.add_argument("--max-tool-calls", type=int, default=12)
    args = parser.parse_args()
    exit_code = 0
    try:
        if args.command in ("demo", "check"):
            output = run_demo() if args.command == "demo" else run_policy_checks()
        else:
            client = OllamaClient(args.model, port=args.port, timeout=args.timeout, max_tokens=args.max_tokens)
            if args.command == "doctor":
                output = {"status": "ready", "backend": client.backend, "model_metadata": client.preflight(),
                          "note": "Metadata verified; inference quality has not been tested"}
            elif args.command == "smoke":
                client.preflight()
                output = run_smoke(client, max_turns=args.max_turns, max_tool_calls=args.max_tool_calls)
                exit_code = 0 if output["passed"] == output["total"] else 1
            else:
                output = run_agent(client, SupportSandbox(Session("customer-demo")), args.task,
                                   max_turns=args.max_turns, max_tool_calls=args.max_tool_calls)
                exit_code = 0 if output["stop_reason"] == "final_answer" else 1
    except (ValueError, ModelError) as exc:
        output = {"status": "error", "error": str(exc)}
        exit_code = 1
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return exit_code
