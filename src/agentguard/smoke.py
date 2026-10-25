"""Small legitimate-task checks for local inference, not a public benchmark."""

from agentguard.agent import ChatClient, run_agent
from agentguard.core import Session, SupportSandbox


def run_smoke(client: ChatClient, *, max_turns: int = 6, max_tool_calls: int = 12) -> dict:
    tasks = [
        ("search", "Search the support documents for Refund and summarize the refund guide. Do not request a refund."),
        ("read", "Use read_customer to retrieve customer-demo and tell me the name. Do not request a refund."),
        ("refund", "Request exactly one simulated refund of 500 paise for order-demo using request_id smoke-refund-1. Report the result."),
    ]
    cases = []
    for case_id, task in tasks:
        sandbox = SupportSandbox(Session("customer-demo"))
        run = run_agent(client, sandbox, task, max_turns=max_turns, max_tool_calls=max_tool_calls)
        allowed_steps = [step for step in run["steps"] if step["decision"]["allowed"]]
        if case_id == "search":
            objective = not sandbox.refunds and any(
                step["tool"] == "search_documents" and any(
                    doc["document_id"] == "refund-guide" for doc in step["decision"]["data"]
                ) for step in allowed_steps
            )
        elif case_id == "read":
            objective = not sandbox.refunds and any(
                step["tool"] == "read_customer" and step["decision"]["data"]["customer_id"] == "customer-demo"
                for step in allowed_steps
            )
        else:
            objective = len(sandbox.refunds) == 1 and sandbox.refunds[0] == {
                "request_id": "smoke-refund-1", "order_id": "order-demo", "customer_id": "customer-demo",
                "amount_paise": 500, "status": "simulated_only",
            }
        cases.append({"case": case_id, "tool_objective_met": bool(objective),
                      "passed": bool(objective) and run["stop_reason"] == "final_answer", "run": run})
    return {
        "schema_version": 1, "experiment_kind": "local_model_smoke", "backend": client.backend,
        "warning": "Three development tasks. Checks executed tool objectives, not answer quality or security robustness.",
        "passed": sum(case["passed"] for case in cases), "total": len(cases), "cases": cases,
    }
