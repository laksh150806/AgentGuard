# Threat model — foundation

## Assets and identities

- Synthetic customer records and internal document content.
- Integrity of a simulated refund ledger.
- Legitimate task completion and bounded execution cost.
- A host-created session for `customer-demo`; the agent does not authenticate itself.

## Attacker capabilities

An attacker can control text in an otherwise retrievable document, including
text updated during a session. In scripted tests we assume the attacker has
already induced a specific tool proposal and test the enforcement boundary.
Future model experiments must establish whether a real agent makes that proposal.

The attacker cannot change server-side session identity, policy, document access
labels, tool implementation, or the process itself. The model receives only the
three tool interfaces, not Python execution or direct references to stores.

## Security invariants

1. Customer reads and refunds are scoped to the trusted session's customer.
2. Internal documents do not appear in customer-facing search results.
3. Cumulative refunds for a customer do not exceed the host's configured cap.
4. Refunds do not exceed the order's paid amount, even in the vulnerable baseline.
5. A retried request has at most one effect. Reusing an ID with different arguments fails.
6. Unrecognized tools or argument fields are rejected before execution.
7. Document updates preserve access labels and cannot change authority.

## Deliberate limits

- The ledger is in memory and the lock is per sandbox. Restarting or creating a
  new sandbox resets it. Production use needs shared persistent transactions,
  authentication, session management, and durable idempotency.
- Audit events are minimal in-memory diagnostics, not tamper-evident records.
- A permitted action can still be contrary to user intent. An attacker-induced
  refund below the cap is not prevented merely by checking the cap.
- There is no final-answer filter. A model might disclose data it legitimately
  saw; current tests cover restricted retrieval/access, not every exfiltration path.
- No claim is made about denial-of-service, malicious code execution, model
  compromise, database attacks, production readiness, or universal injection resistance.
- The live-retrieval demo is a versioned in-memory update, not a streaming RAG
  integration. The model loop is implemented separately; real-model injection
  experiments and a streaming retrieval connector remain future work.
- The local inference server is trusted. AgentGuard rejects remote model metadata
  but cannot prove that a malicious or reconfigured server performs inference locally.
- `enforce=False` is intentionally insecure and is only for isolated synthetic experiments.
